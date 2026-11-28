"""Mock ACP alt süreciyle istemci ve izin protokolünü sınar."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from src.acp_cekirdek import ACPClient, ACPError, DEMO_COMMAND, local_login_environment, trace_command

AGENT = """
import json
import os
import sys
import time

def receive():
    msg = json.loads(sys.stdin.readline())
    assert msg["jsonrpc"] == "2.0"
    return msg

def send(**message):
    print(json.dumps({"jsonrpc": "2.0", **message}), flush=True)

def update(**fields):
    send(method="session/update", params={"sessionId": "test", "update": fields})

mode = sys.argv[1]
if mode == "blocked_write":
    time.sleep(10)
assert receive()["method"] == "initialize"
if mode == "bad_json":
    print("{broken", flush=True)
    sys.exit(0)
if mode == "eof":
    sys.exit(0)
if mode == "timeout":
    time.sleep(10)
if mode == "rpc_error":
    send(id=1, error={"code": -32603, "message": "PRIVATE_VALUE"})
    sys.exit(0)
if mode == "wrong_id":
    send(id=99, result={"protocolVersion": 1})
    sys.exit(0)
send(id=1, result={"protocolVersion": 1})
session = receive()
assert session["method"] == "session/new" and session["params"]["mcpServers"] == []
assert os.path.isabs(session["params"]["cwd"])
send(id=2, result={"sessionId": "test"})
prompt = receive()
assert prompt["method"] == "session/prompt" and prompt["params"]["sessionId"] == "test"
send(id=30, method="fs/read_text_file", params={})
assert receive()["error"]["code"] == -32601
update(sessionUpdate="tool_call", toolCallId="private-id", kind="execute", status="pending",
       rawInput={"command": "PRIVATE_VALUE"})
send(id=3, method="session/request_permission", params={
    "sessionId": "test", "toolCall": {"rawInput": {"command": "PRIVATE_VALUE"}},
    "options": [{"kind": "allow_once", "optionId": "approve"},
                {"kind": "allow_always", "optionId": "forever"},
                {"kind": "reject_once", "optionId": "reject"}]})
reply = receive()
assert reply["id"] == 3
outcome = reply["result"]["outcome"]
if mode == "cancel":
    assert outcome == {"outcome": "cancelled"}
else:
    assert outcome == {"outcome": "selected", "optionId": mode}
update(sessionUpdate="tool_call_update", toolCallId="private-id", status="completed",
       rawInput={"command": sys.argv[2]})
update(sessionUpdate="agent_message_chunk", content={"type": "text", "text": "Canlı yanıt"})
send(id=3, result={"stopReason": "end_turn"})
"""


class ACPPipeTest(unittest.TestCase):
    def client(self, mode, timeout=3, permission=None):
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", AGENT, mode, DEMO_COMMAND],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, start_new_session=True,
        )
        events = []
        kwargs = {"permission": permission} if permission else {}
        client = ACPClient(process, timeout, lambda event, **fields: events.append((event, fields)), **kwargs)
        self.addCleanup(client.close)
        return client, events

    def verify_turn(self, mode, expected_decision, selection):
        def choose(tool, options, timeout):
            self.assertEqual(tool["rawInput"]["command"], "PRIVATE_VALUE")
            self.assertEqual([o["optionId"] for o in options], ["approve", "reject"])
            self.assertGreater(timeout, 0)
            return selection

        client, events = self.client(mode, permission=choose)
        with redirect_stdout(StringIO()) as output:
            self.assertEqual(client.run(Path.cwd(), "görev"), "end_turn")
        self.assertIn("Canlı yanıt", output.getvalue())
        self.assertIn(("izin_yaniti", {"karar": expected_decision}), events)
        self.assertNotIn("PRIVATE_VALUE", repr(events))
        self.assertNotIn("private-id", repr(events))
        self.assertIn(("tool_call_update", {"sira": 1, "tur": "execute", "durum": "completed",
                                            "komut": DEMO_COMMAND}), events)
        self.assertEqual([fields["metot"] for event, fields in events if event == "istek"],
                         ["initialize", "session/new", "session/prompt"])

    def test_relative_script_trace(self):
        for script in ("src/ajan3_denetim.py", "src/dq_test_g2.py", "tests/test_acp_cekirdek.py"):
            with self.subTest(script=script):
                self.assertEqual(trace_command(f"python3 {script} --csv data/private.csv"),
                                 f"python3 {script} [maskeli] [maskeli]")

    def test_private_paths_stay_masked(self):
        for path in ("/home/private/test.py", "src/../private.py", "data/private.py",
                     "src/private.txt", "src//private.py", "src/.private.py"):
            with self.subTest(path=path):
                self.assertEqual(trace_command("python " + path), "python [maskeli]")
        self.assertEqual(trace_command("python3 -c src/private.py"), "python3 -c [maskeli]")

    def test_general_tool_trace(self):
        client, events = self.client("eof")
        url = "https://user:secret@example.org/private?token=private#private"
        with redirect_stdout(StringIO()):
            client.show_update({"sessionUpdate": "tool_call", "toolCallId": "x",
                                "kind": "execute", "rawInput": {"command": "curl " + url, "url": url}})
            client.show_update({"sessionUpdate": "tool_call_update", "toolCallId": "x",
                                "status": "completed"})
        for _, fields in events:
            self.assertEqual(fields["komut"], "curl https://example.org/[yol]")
            self.assertEqual(fields["url"], "https://example.org/[yol]")
        self.assertEqual(len(events), 2)

    def test_approval_once(self):
        self.verify_turn("approve", "allow_once", "approve")

    def test_rejection_once(self):
        self.verify_turn("reject", "reject_once", "reject")

    def test_permanent_approval_cannot_be_selected(self):
        self.verify_turn("cancel", "cancelled", "forever")

    def test_noninteractive_permission_cancels(self):
        client, events = self.client("cancel")
        with patch("sys.stdin", StringIO()), redirect_stdout(StringIO()):
            self.assertEqual(client.run(Path.cwd(), "görev"), "end_turn")
        self.assertIn(("izin_yaniti", {"karar": "cancelled"}), events)

    def test_malformed_json(self):
        client, _ = self.client("bad_json")
        with self.assertRaisesRegex(ACPError, "Bozuk"):
            client.run(Path.cwd(), "görev")

    def test_process_ends_without_response(self):
        client, _ = self.client("eof")
        with self.assertRaisesRegex(ACPError, "kapandı"):
            client.run(Path.cwd(), "görev")

    def test_response_timeout(self):
        client, _ = self.client("timeout", timeout=0.2)
        with self.assertRaisesRegex(ACPError, "initialize zaman aşımına"):
            client.run(Path.cwd(), "görev")

    def test_write_timeout(self):
        client, _ = self.client("blocked_write", timeout=0.2)
        with self.assertRaisesRegex(ACPError, "yazma zaman aşımı"):
            client.request("session/prompt", prompt="x" * (1024 * 1024))

    def test_invalid_response_id(self):
        client, _ = self.client("wrong_id")
        with self.assertRaisesRegex(ACPError, "kimliği"):
            client.run(Path.cwd(), "görev")

    def test_error_excludes_server_message(self):
        client, _ = self.client("rpc_error")
        with self.assertRaisesRegex(ACPError, "JSON-RPC kodu: -32603\\)\\.$") as error:
            client.run(Path.cwd(), "görev")
        self.assertNotIn("PRIVATE_VALUE", str(error.exception))

    def test_local_login_environment(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test", "GEMINI_API_KEY": "test"}):
            env = local_login_environment()
        self.assertIn("PATH", env)
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertNotIn("GEMINI_API_KEY", env)
