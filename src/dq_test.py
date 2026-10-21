"""DQ testleri — Görev 1 (tests/test-cases.md içindeki TC-01..TC-09).

Kullanım:
    python src/dq_test.py                      # varsayılan: data/siparisler.csv
    python src/dq_test.py yol/dosya.csv

Her senaryo için GEÇTİ/KALDI ve gerçekleşen sonucu yazdırır.
Çıkış kodu: tüm testler geçerse 0, aksi halde 1.
"""
import os
import re
import sys

import pandas as pd

# --- Şema (docs/veri-sozlugu-g1.md ile aynı tutulmalı) ---
SUTUNLAR = ["siparis_id", "siparis_tarihi", "kategori", "urun", "adet",
            "birim_fiyat", "toplam_tutar", "sehir", "odeme_tipi"]
MIN_SATIR = 100      # ödevdeki alt sınır
SEMA_SATIR = 400     # docs/veri-sozlugu-g1.md'deki satır sayısı
KATEGORILER = {"Elektronik", "Giyim", "Kitap", "Ev & Yaşam", "Kozmetik"}
ADET_ARALIK = (1, 10)
FIYAT_ARALIK = (50, 5000)
TUTAR_ARALIK = (50, 50000)
TARIH_ARALIK = ("2026-01-01", "2026-09-30")
TUTAR_TOLERANS = 0.01  # TL


def tc01(yol):
    if not os.path.exists(yol):
        return False, "dosya yok"
    boyut = os.path.getsize(yol)
    if boyut == 0:
        return False, "dosya 0 bayt"
    df = pd.read_csv(yol)
    return len(df) > 0, f"{boyut} bayt, {len(df)} veri satırı"


def tc02(df):
    ok = len(df) >= MIN_SATIR and len(df) == SEMA_SATIR
    return ok, f"{len(df)} satır (hedef: ≥ {MIN_SATIR} ve = {SEMA_SATIR})"


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
    tutar = pd.to_numeric(df["toplam_tutar"], errors="coerce")
    if tutar.isna().any():
        hatalar.append(f"toplam_tutar sayısal olmayan: {int(tutar.isna().sum())}")
    n = int((~tutar.between(*TUTAR_ARALIK)).sum())
    if n:
        hatalar.append(f"toplam_tutar aralık dışı: {n}")
    tarih = pd.to_datetime(df["siparis_tarihi"], format="%Y-%m-%d", errors="coerce")
    n = int(tarih.isna().sum())
    if n:
        hatalar.append(f"siparis_tarihi ayrıştırılamayan: {n}")
    n = int((~tarih.between(*TARIH_ARALIK)).sum()) - n
    if n:
        hatalar.append(f"siparis_tarihi aralık dışı: {n}")
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


def tc08(df):
    adet = pd.to_numeric(df["adet"], errors="coerce")
    fiyat = pd.to_numeric(df["birim_fiyat"], errors="coerce")
    tutar = pd.to_numeric(df["toplam_tutar"], errors="coerce")
    n = int((~((adet * fiyat - tutar).abs() <= TUTAR_TOLERANS)).sum())
    return n == 0, f"adet × birim_fiyat ile uyuşmayan satır: {n}"


def tc09(yol):
    """Para alanları dosyada tam 2 ondalıkla mı yazılmış? (sözlük: "float, 2 ondalık")"""
    ham = pd.read_csv(yol, dtype=str, keep_default_na=False)
    desen = re.compile(r"^\d+\.\d{2}$")
    hatali = {}
    for alan in ("birim_fiyat", "toplam_tutar"):
        n = int((~ham[alan].str.match(desen)).sum())
        if n:
            hatali[alan] = n
    satir = int((~ham["birim_fiyat"].str.match(desen) | ~ham["toplam_tutar"].str.match(desen)).sum())
    return satir == 0, f"2 ondalıklı olmayan satır: {satir} {hatali or ''}".strip()


def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "data/siparisler.csv"
    sonuclar = []
    ok, mesaj = tc01(yol)
    sonuclar.append(("TC-01", ok, mesaj))
    if ok:
        df = pd.read_csv(yol)
        for ad, fn in [("TC-02", tc02), ("TC-03", tc03), ("TC-04", tc04),
                       ("TC-05", tc05), ("TC-06", tc06), ("TC-07", tc07),
                       ("TC-08", tc08)]:
            try:
                ok, mesaj = fn(df)
            except KeyError as e:
                ok, mesaj = False, f"sütun bulunamadı: {e}"
            sonuclar.append((ad, ok, mesaj))
        try:
            ok, mesaj = tc09(yol)
        except KeyError as e:
            ok, mesaj = False, f"sütun bulunamadı: {e}"
        sonuclar.append(("TC-09", ok, mesaj))

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
