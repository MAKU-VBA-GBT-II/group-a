"""Tek ajan için Zed ACP v1 terminal istemcisi."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import queue
import re
import select
import shlex
import signal
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit

MAX_FRAME = 8 * 1024 * 1024
DEMO_COMMAND = """python3 -c 'from pathlib import Path; print(len(Path("docs/oneri.md").read_text().splitlines()))'"""
DEMO_PROMPT = (
    "Sadece Bash aracıyla aşağıdaki salt okunur komutu aynen bir kez çalıştır. "
    "Başka araç kullanma ve dosya değiştirme. Sonuçta yalnız satır sayısını söyle.\n"
    + DEMO_COMMAND
)
TOOL_KINDS = {
    "read", "edit", "delete", "move", "search", "execute", "think", "fetch",
    "switch_mode", "other",
}
TOOL_STATUSES = {"pending", "in_progress", "completed", "failed"}
PERMISSION_KINDS = ("allow_once", "reject_once")


class ACPError(Exception):
    pass


def terminal_text(value):
    return "".join(c for c in value if c in "\n\t" or c.isprintable())


def trace_url(value):
    """Kullanıcı bilgisi, sorgu ve parçayı günlükten çıkar."""
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return "[maskeli]"
        host = parsed.hostname
        if ":" in host:
            host = f"[{host}]"
        port = f":{parsed.port}" if parsed.port else ""
        return f"{parsed.scheme}://{host}{port}" + ("/[yol]" if parsed.path.strip("/") else "/")
    except ValueError:
        return "[maskeli]"


def trace_command(value):
    if value == DEMO_COMMAND:
        return value
    try:
        words = shlex.split(value)
    except ValueError:
        return "[maskeli]"
    if not words:
        return "[maskeli]"
    # Serbest argümanlar; kod, belirteç veya kişisel dosya yolu içerebilir.
    programs = {"python", "python3", "git", "curl", "node", "npm", "ls", "cat", "wc", "head", "grep", "playwright"}
    program = words[0] if words[0] in programs else "[maskeli]"
    safe = [program]
    for index, word in enumerate(words[1:], 1):
        if (index == 1 and program in {"python", "python3"}
                and re.fullmatch(r"(?:src|tests)/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.py", word)):
            safe.append(word)
        elif word.startswith(("https://", "http://")):
            safe.append(trace_url(word))
        elif word in {"-m", "-c", "-l", "--version", "status", "diff", "log", "show", "unittest", "discover"}:
            safe.append(word)
        else:
            safe.append("[maskeli]")
    return " ".join(safe)


def trace_input(tool):
    raw = tool.get("rawInput")
    raw = raw if isinstance(raw, dict) else {}
    fields = {}
    command = raw.get("command")
    if isinstance(command, str):
        fields["komut"] = trace_command(command)
    elif tool.get("title") == DEMO_COMMAND:
        fields["komut"] = DEMO_COMMAND
    url = raw.get("url")
    if isinstance(url, str):
        fields["url"] = trace_url(url)
    return fields


def choose_permission(tool, options, timeout):
    if not sys.stdin.isatty() or timeout <= 0:
        return None
    title = terminal_text(str(tool.get("title", "Araç isteği")))
    raw = tool.get("rawInput")
    print(f"\nİzin isteği — {title}", file=sys.stderr)
    if raw is not None:
        print(terminal_text(json.dumps(raw, ensure_ascii=False)), file=sys.stderr)
    for number, option in enumerate(options, 1):
        action = {"allow_once": "Bir kez izin ver", "reject_once": "Bir kez reddet"}
        print(f"  {number}. {action[option['kind']]}", file=sys.stderr)
    print("  0. İptal (varsayılan)\nSeçim> ", end="", flush=True, file=sys.stderr)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        answer = sys.stdin.readline().strip()
        return {str(i): o["optionId"] for i, o in enumerate(options, 1)}.get(answer)
    print("\nİzin süresi doldu.", file=sys.stderr)
    return None


class ACPClient:
    def __init__(self, process, timeout, record, permission=choose_permission):
        self.process = process
        self.timeout = timeout
        self.record = record
        self.permission = permission
        self.frames = queue.Queue(maxsize=256)
        self.session = None
        self.request_id = 0
        self.tools = {}
        self.closed = threading.Event()
        self.reader = threading.Thread(target=self.read_frames, daemon=True)
        os.set_blocking(process.stdin.fileno(), False)
        self.reader.start()

    def queue_frame(self, item):
        while not self.closed.is_set():
            try:
                self.frames.put(item, timeout=0.1)
                return
            except queue.Full:
                continue

    def close(self):
        self.closed.set()
        stop_process(self.process)
        self.reader.join(timeout=2)
        if not self.reader.is_alive():
            self.process.stdout.close()

    def read_frames(self):
        try:
            while not self.closed.is_set() and (frame := self.process.stdout.readline(MAX_FRAME + 1)):
                if len(frame) > MAX_FRAME or not frame.endswith(b"\n"):
                    self.queue_frame(ACPError("ACP iletisi çok uzun veya eksik."))
                    return
                try:
                    self.queue_frame(json.loads(frame.decode("utf-8")))
                except (ValueError, RecursionError):
                    self.queue_frame(ACPError("Bozuk ACP JSON iletisi."))
                    return
            self.queue_frame(ACPError("ACP süreci yanıtı tamamlamadan kapandı."))
        except OSError:
            self.queue_frame(ACPError("ACP çıktısı okunamadı."))

    def send(self, deadline, **message):
        data = json.dumps({"jsonrpc": "2.0", **message}, ensure_ascii=False)
        pending = memoryview(data.encode("utf-8") + b"\n")
        stream = self.process.stdin.fileno()
        while pending:
            remaining = max(0, deadline - time.monotonic())
            if not select.select([], [stream], [], remaining)[1]:
                raise ACPError("ACP sürecine yazma zaman aşımı.")
            try:
                sent = os.write(stream, pending)
            except BlockingIOError:
                continue
            except OSError:
                raise ACPError("ACP sürecine yazılamadı.") from None
            pending = pending[sent:]

    def request(self, method, **params):
        self.request_id += 1
        request_id = self.request_id
        deadline = time.monotonic() + self.timeout
        self.record("istek", metot=method)
        self.send(deadline, id=request_id, method=method, params=params)
        while (remaining := deadline - time.monotonic()) > 0:
            try:
                message = self.frames.get(timeout=remaining)
            except queue.Empty:
                break
            if isinstance(message, Exception):
                raise message
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                raise ACPError("Geçersiz JSON-RPC 2.0 iletisi.")
            if "method" in message:
                self.handle_agent(message, deadline)
                continue
            if type(message.get("id")) is not int or message["id"] != request_id:
                raise ACPError("ACP yanıt kimliği beklenen istekle eşleşmiyor.")
            if "error" in message:
                error = message["error"]
                code = error.get("code") if isinstance(error, dict) else None
                code = code if type(code) is int else "bilinmiyor"
                raise ACPError(f"{method} başarısız (JSON-RPC kodu: {code}).")
            result = message.get("result")
            if not isinstance(result, dict):
                raise ACPError(f"{method} sonucu nesne olmalı.")
            return result
        raise ACPError(f"{method} zaman aşımına uğradı.")

    def handle_agent(self, message, deadline):
        method = message["method"]
        params = message.get("params", {})
        if not isinstance(method, str) or not isinstance(params, dict):
            raise ACPError("Geçersiz ACP yöntem iletisi.")
        if "id" in message:
            if method != "session/request_permission":
                self.send(deadline, id=message["id"], error={"code": -32601, "message": "Method not found"})
                return
            if not self.session or params.get("sessionId") != self.session:
                self.send(deadline, id=message["id"], error={"code": -32602, "message": "Invalid session"})
                return
            self.handle_permission(message["id"], params, deadline)
        elif method == "session/update" and self.session and params.get("sessionId") == self.session:
            update = params.get("update")
            if not isinstance(update, dict):
                raise ACPError("Geçersiz oturum güncellemesi.")
            self.show_update(update)

    def handle_permission(self, request_id, params, deadline):
        tool, offered = params.get("toolCall"), params.get("options")
        if not isinstance(tool, dict) or not isinstance(offered, list):
            self.send(deadline, id=request_id, error={"code": -32602, "message": "Invalid permission request"})
            return
        options = [
            item for item in offered
            if isinstance(item, dict) and item.get("kind") in PERMISSION_KINDS
            and isinstance(item.get("optionId"), str)
        ]
        self.record("izin_istendi", **trace_input(tool))
        selected = self.permission(tool, options, deadline - time.monotonic()) if options else None
        decision = next((option for option in options if option["optionId"] == selected), None)
        outcome = {"outcome": "cancelled"}
        if decision:
            outcome = {"outcome": "selected", "optionId": decision["optionId"]}
        self.send(deadline, id=request_id, result={"outcome": outcome})
        self.record("izin_yaniti", karar=decision["kind"] if decision else "cancelled")

    def show_update(self, update):
        update_type = update.get("sessionUpdate")
        if update_type == "agent_message_chunk":
            content = update.get("content")
            if isinstance(content, dict) and content.get("type") == "text":
                value = content.get("text")
                if isinstance(value, str):
                    print(terminal_text(value), end="", flush=True)
        elif update_type in ("tool_call", "tool_call_update"):
            tool_id = update.get("toolCallId")
            if not isinstance(tool_id, str) or not tool_id:
                raise ACPError("ACP araç çağrısı kimliği eksik.")
            tool = self.tools.setdefault(tool_id, {"sira": len(self.tools) + 1})
            kind = update.get("kind")
            status = update.get("status")
            if isinstance(kind, str) and kind in TOOL_KINDS:
                tool["tur"] = kind
            if isinstance(status, str) and status in TOOL_STATUSES:
                tool["durum"] = status
            tool.update(trace_input(update))
            title = update.get("title")
            label = terminal_text(title) if isinstance(title, str) else tool.get("tur", "araç")
            print(f"\n[Araç {tool['sira']}] {label} · {tool.get('durum', 'güncellendi')}", flush=True)
            self.record(update_type, **tool)

    def run(self, cwd, prompt):
        initialized = self.request("initialize", protocolVersion=1, clientCapabilities={},
                                   clientInfo={"name": "sepetix-analitik", "version": "0.1"})
        version = initialized.get("protocolVersion")
        if type(version) is not int or version != 1:
            raise ACPError("Ajan ACP v1 protokolünü kabul etmedi.")
        self.record("baglandi", protokol=1)
        session = self.request("session/new", cwd=str(cwd), mcpServers=[])
        self.session = session.get("sessionId")
        if not isinstance(self.session, str) or not self.session:
            raise ACPError("Ajan geçerli oturum kimliği döndürmedi.")
        self.record("oturum_acildi")
        result = self.request("session/prompt", sessionId=self.session,
                              prompt=[{"type": "text", "text": prompt}])
        reason = result.get("stopReason")
        if reason not in ("end_turn", "max_tokens", "max_turn_requests", "refusal", "cancelled"):
            raise ACPError("Ajan geçerli bir durma nedeni döndürmedi.")
        self.record("oturum_sonu", neden=reason)
        print(f"\n[Oturum sonucu] {reason}")
        return reason


def load_agent(path):
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
        agent = config["ajanlar"][config["ajan"]]
        command = agent["komut"]
        timeout = config["zaman_asimi_saniye"]
        if not isinstance(command, list) or not command or not all(
            isinstance(arg, str) and arg and "\0" not in arg for arg in command
        ):
            raise ValueError
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        raise ACPError("Ayar dosyasını, seçili ajanı, komutu ve pozitif zaman aşımını kontrol edin.") from None
    return command, timeout


def local_login_environment():
    blocked = {
        "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "CODEX_API_KEY",
        "GEMINI_API_KEY", "GOOGLE_API_KEY", "MISTRAL_API_KEY", "CLAUDECODE",
        "CLAUDE_CODE_SESSION_ACCESS_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def stop_process(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS, çıkmış fakat henüz beklenmemiş grup liderinde EPERM döndürebilir.
        process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            process.kill()
        process.wait()
    process.stdin.close()


def private_log(path, flags):
    return os.open(path, flags, 0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.example.json"))
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--log", type=Path, required=True)
    task = parser.add_mutually_exclusive_group(required=True)
    task.add_argument("--prompt")
    task.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    try:
        command, timeout = load_agent(args.config)
        with open(args.log, "x", encoding="utf-8", opener=private_log) as log:
            def record(event, **fields):
                row = {"zaman": datetime.now(timezone.utc).isoformat(), "olay": event, **fields}
                print(json.dumps(row, ensure_ascii=False), file=log, flush=True)

            record("baslangic", gorev="satir_sayimi_demo" if args.demo else "kullanici_gorevi")
            try:
                process = subprocess.Popen(
                    command, cwd=args.cwd.resolve(), env=local_login_environment(),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                client = ACPClient(process, timeout, record)
                try:
                    reason = client.run(args.cwd.resolve(), DEMO_PROMPT if args.demo else args.prompt)
                    return 0 if reason == "end_turn" else 1
                finally:
                    client.close()
            except (ACPError, OSError, KeyboardInterrupt) as error:
                record("hata", tur=type(error).__name__)
                raise
    except ACPError as error:
        print(f"Hata: {error}", file=sys.stderr)
    except FileExistsError:
        print("Hata: kayıt zaten var; yeni bir kayıt yolu seçin.", file=sys.stderr)
    except OSError:
        print("Hata: ajan başlatılamadı veya kayıt yazılamadı; komutu ve yolları kontrol edin.", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nOturum kullanıcı tarafından kesildi.", file=sys.stderr)
        return 130
    return 1


if __name__ == "__main__":
    sys.exit(main())
