"""DQ testleri — Görev 1 (tests/test-cases.md içindeki TC-01..TC-07).

Kullanım:
    python src/dq_test.py                      # varsayılan: data/siparisler.csv
    python src/dq_test.py yol/dosya.csv

Her senaryo için GEÇTİ/KALDI ve gerçekleşen sonucu yazdırır.
Çıkış kodu: tüm testler geçerse 0, aksi halde 1.
"""
import os
import sys

import pandas as pd

# --- Şema (docs/veri-sozlugu-g1.md ile aynı tutulmalı) ---
SUTUNLAR = ["siparis_id", "tarih", "kategori", "urun", "adet", "birim_fiyat", "sehir"]
HEDEF_SATIR = 100
KATEGORILER = {"Elektronik", "Giyim", "Ev & Yaşam", "Kozmetik", "Kitap"}
ADET_ARALIK = (1, 10)
FIYAT_ARALIK = (20, 5000)
TARIH_ARALIK = ("2026-09-01", "2026-09-30")


def tc01(yol):
    if not os.path.exists(yol):
        return False, "dosya yok"
    boyut = os.path.getsize(yol)
    if boyut == 0:
        return False, "dosya 0 bayt"
    df = pd.read_csv(yol)
    return len(df) > 0, f"{boyut} bayt, {len(df)} veri satırı"


def tc02(df):
    return len(df) >= HEDEF_SATIR, f"{len(df)} satır (hedef ≥ {HEDEF_SATIR})"


def tc03(df):
    gercek = list(df.columns)
    return gercek == SUTUNLAR, f"sütunlar: {gercek}"


def tc04(df):
    hatalar = []
    for alan in ("siparis_id", "adet"):
        if not pd.api.types.is_integer_dtype(df[alan]):
            hatalar.append(f"{alan} tam sayı değil")
    fiyat = pd.to_numeric(df["birim_fiyat"], errors="coerce")
    if fiyat.isna().any():
        hatalar.append(f"birim_fiyat sayısal olmayan: {int(fiyat.isna().sum())}")
    adet = pd.to_numeric(df["adet"], errors="coerce")
    n = int((~adet.between(*ADET_ARALIK)).sum())
    if n:
        hatalar.append(f"adet aralık dışı: {n}")
    n = int((~fiyat.between(*FIYAT_ARALIK)).sum())
    if n:
        hatalar.append(f"birim_fiyat aralık dışı: {n}")
    tarih = pd.to_datetime(df["tarih"], format="%Y-%m-%d", errors="coerce")
    n = int(tarih.isna().sum())
    if n:
        hatalar.append(f"tarih ayrıştırılamayan: {n}")
    n = int((~tarih.between(*TARIH_ARALIK)).sum()) - n
    if n:
        hatalar.append(f"tarih aralık dışı: {n}")
    return not hatalar, "; ".join(hatalar) or "tüm tip ve aralıklar doğru"


def tc05(df):
    degerler = set(df["kategori"].dropna().unique())
    fazla = degerler - KATEGORILER
    ok = not fazla and len(degerler) >= 4
    return ok, f"{len(degerler)} farklı değer; şema dışı: {sorted(fazla) or 'yok'}"


def tc06(df):
    eksik = df.isna().sum() + (df.astype(str).apply(lambda s: s.str.strip()) == "").sum()
    toplam = int(eksik.sum())
    detay = {k: int(v) for k, v in eksik.items() if v}
    return toplam == 0, f"toplam eksik: {toplam} {detay or ''}".strip()


def tc07(df):
    tekrar_id = int(df["siparis_id"].duplicated().sum())
    tekrar_satir = int(df.duplicated().sum())
    return tekrar_id == 0 and tekrar_satir == 0, (
        f"tekrarlanan id: {tekrar_id}, tekrarlanan satır: {tekrar_satir}"
    )


def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "data/siparisler.csv"
    sonuclar = []
    ok, mesaj = tc01(yol)
    sonuclar.append(("TC-01", ok, mesaj))
    if ok:
        df = pd.read_csv(yol)
        for ad, fn in [("TC-02", tc02), ("TC-03", tc03), ("TC-04", tc04),
                       ("TC-05", tc05), ("TC-06", tc06), ("TC-07", tc07)]:
            try:
                ok, mesaj = fn(df)
            except KeyError as e:
                ok, mesaj = False, f"sütun bulunamadı: {e}"
            sonuclar.append((ad, ok, mesaj))

    print(f"Dosya: {yol}\n")
    print("| ID | Gerçekleşen sonuç | Geçti/Kaldı |")
    print("|---|---|---|")
    for ad, ok, mesaj in sonuclar:
        print(f"| {ad} | {mesaj} | {'Geçti' if ok else 'Kaldı'} |")
    gecen = sum(ok for _, ok, _ in sonuclar)
    print(f"\nÖzet: {gecen}/{len(sonuclar)} geçti")
    sys.exit(0 if gecen == len(sonuclar) else 1)


if __name__ == "__main__":
    main()
