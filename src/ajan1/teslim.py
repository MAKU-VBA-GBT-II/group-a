"""Ajan 1 teslim: tabloyu Ajan 2 ve Ajan 3'ün kapılarından geçirir (skills/ajan1-teslim).

Kullanım (repo kökünden):  python -m src.ajan1.teslim
Girdi: data/ajan1-cikti.csv ve runs/ajan1/ altındaki en son çalışma raporu.
Çıktı: ekrana özet; rapora "teslim" bölümü (MD5, sonuç, 72 saatin dolacağı zaman).
Kontrollerden biri düşerse dosya devredilmez ve çıkış kodu 1 olur.
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from . import ortak

CIKTI = ortak.KOK / "data" / "ajan1-cikti.csv"
KATALOG = ortak.KOK / "data" / "urun-listesi-web.csv"
RAPORLAR = ortak.KOK / "runs" / "ajan1"
TAZELIK = timedelta(hours=24)   # Ajan 1'in kendi eşiği (ajan1-teslim §2, 28 Kasım kararı)
AJAN23_SURESI = timedelta(hours=72)
GERCEK_ARAC = "playwright"


def ajan2_kapisi(yol, referans):
    """Ajan 2'nin kendi alma() fonksiyonu: iki kapının kuralları hiç ayrışmasın diye
    kopyalanmadan doğrudan çağrılır (ajan1-teslim §1)."""
    from src import ajan2_analiz
    try:
        satirlar, _ = ajan2_analiz.alma(str(yol), str(KATALOG), referans)
        return [], satirlar
    except ajan2_analiz.Red as red:
        return [f"Ajan 2: {red.gerekce}"] + [f"  {a}" for a in red.alanlar[:20]], None


def ajan3_kapisi(yol, satirlar):
    """Ajan 3'ün (PR #120) Ajan 1 tablosuna uyguladığı, Ajan 2'de olmayan kural:
    gerçek veride CSV repo içinde durmalı (MD5 yolu bu dosyaya göre doğrulanır)."""
    sorunlar = []
    if any(s["arac"] != "sentetik-fixture" for s in satirlar):
        try:
            Path(yol).resolve().relative_to(ortak.KOK)
        except ValueError:
            sorunlar.append("Ajan 3: gerçek veride Ajan 1 CSV'si repo içinde olmalı")
    return sorunlar


def ajan1_kontrolleri(satirlar, referans):
    """Ajan 1'in kendi kuralları: gerçek araç ve 24 saatlik tazelik kapısı."""
    sorunlar = []
    for no, s in enumerate(satirlar, 2):
        if s["arac"] != GERCEK_ARAC:
            sorunlar.append(f"satir[{no}].arac: '{s['arac']}' (beklenen {GERCEK_ARAC})")
        if referans - datetime.fromisoformat(s["cekilme_zamani"]) > TAZELIK:
            sorunlar.append(f"satir[{no}].cekilme_zamani: 24 saatten eski, yeniden toplanmalı")
    # Aynı ürün aynı ürünümüzde iki kez olamaz; farklı ürünümüzde ancak çok işlevliyse (karar 8)
    gorulen = defaultdict(list)
    for no, s in enumerate(satirlar, 2):
        gorulen[s["urun_url"]].append((no, s["bizim_urun"]))
    for url, liste in gorulen.items():
        urunler = [u for _, u in liste]
        if len(urunler) != len(set(urunler)):
            sorunlar.append(f"tekrar: {url} aynı ürünümüzde birden çok satırda")
    return sorunlar, gorulen


def son_rapor():
    raporlar = sorted(RAPORLAR.glob("*.json"))
    return raporlar[-1] if raporlar else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    referans = datetime.now(ortak.TR).replace(microsecond=0)
    if not CIKTI.exists():
        print(f"Tablo yok: {CIKTI}")
        return 1

    sorunlar, satirlar = ajan2_kapisi(CIKTI, referans)
    if satirlar is None:  # Ajan 2 kapısı dosyayı okuyamadıysa diğer kontroller için yine oku
        import csv
        with open(CIKTI, encoding="utf-8", newline="") as f:
            satirlar = list(csv.DictReader(f))
    sorunlar += ajan3_kapisi(CIKTI, satirlar)
    a1, gorulen = ajan1_kontrolleri(satirlar, referans)
    sorunlar += a1

    md5 = hashlib.md5(CIKTI.read_bytes()).hexdigest()
    en_eski = min(datetime.fromisoformat(s["cekilme_zamani"]) for s in satirlar)
    cok_islevli = {u: sorted({x for _, x in l}) for u, l in gorulen.items() if len({x for _, x in l}) > 1}
    ozet = {
        "zaman": referans.isoformat(),
        "sonuc": "gecti" if not sorunlar else "dustu",
        "dosya": CIKTI.relative_to(ortak.KOK).as_posix(),
        "md5": md5,
        "satir": len(satirlar),
        "tekil_urun": len(gorulen),           # karar 9: çift sayımı önlemek için
        "cok_islevli": cok_islevli,
        "elenmeyen_satir": sum(1 for s in satirlar if not s["elendi"]),
        "urun_basina": dict(Counter(s["bizim_urun"] for s in satirlar)),
        "en_eski_cekilme": en_eski.isoformat(),
        "ajan1_tazelik_sonu": (en_eski + TAZELIK).isoformat(),
        "ajan2_ajan3_72_saat_sonu": (en_eski + AJAN23_SURESI).isoformat(),
        "sorunlar": sorunlar,
    }

    rapor = son_rapor()
    if rapor:
        veri = json.loads(rapor.read_text(encoding="utf-8"))
        veri["teslim"] = ozet
        rapor.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Teslim kontrolü: {'GEÇTİ' if not sorunlar else 'DÜŞTÜ'}")
    print(f"  {ozet['satir']} satır, {ozet['tekil_urun']} tekil ürün, {ozet['elenmeyen_satir']} satır elenmedi")
    print(f"  MD5: {md5}")
    print(f"  En eski çekilme: {ozet['en_eski_cekilme']}")
    print(f"  Ajan 1 tazelik sınırı (24 sa): {ozet['ajan1_tazelik_sonu']}")
    print(f"  Ajan 2 ve Ajan 3 için 72 saat: {ozet['ajan2_ajan3_72_saat_sonu']}")
    if cok_islevli:
        print(f"  Çok işlevli ürün: {len(cok_islevli)}")
    for s in sorunlar[:30]:
        print("  -", s)
    if rapor:
        print(f"Rapor güncellendi: {rapor}")
    return 0 if not sorunlar else 1


if __name__ == "__main__":
    sys.exit(main())
