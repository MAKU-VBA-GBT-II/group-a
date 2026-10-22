#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — BE: sipariş verisi üretici

Şemaya uygun, sabit tohumlu ve tekrarlanabilir sentetik sipariş verisi üretir.
Çıktı: data/siparisler.csv  (temiz: eksik değer, aralık dışı değer, tutarsız kategori yok)

Şema kaynağı: skills/be-veri/SKILL.md ve docs/veri-sozlugu-g1.md
Testler:      tests/test-cases.md (TC-01 … TC-09)
Issue:        #13 (üretim), #27 (para alanları tam 2 ondalık)

Kullanım: depo kökünde  python src/veri_uret.py
"""

import io
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Şema sabitleri — değişirse SKILL.md ve docs/veri-sozlugu-g1.md de güncellenmeli
# ----------------------------------------------------------------------------

SEED = 42
SATIR_SAYISI = 400

SUTUNLAR = [
    "siparis_id",
    "siparis_tarihi",
    "kategori",
    "urun",
    "adet",
    "birim_fiyat",
    "toplam_tutar",
    "sehir",
    "odeme_tipi",
]

TARIH_BASLANGIC = "2026-01-01"
TARIH_BITIS = "2026-09-30"

ADET_MIN, ADET_MAX = 1, 10
FIYAT_MIN, FIYAT_MAX = 50.00, 5000.00

# kategori -> (ürünler, kategoriye özgü fiyat aralığı); aralıklar FIYAT_MIN–FIYAT_MAX içinde kalır
KATEGORI_URUN = {
    "Elektronik": (
        ["Kablosuz Kulaklık", "Bluetooth Hoparlör", "Powerbank", "Akıllı Saat", "Klavye"],
        (300.00, 5000.00),
    ),
    "Giyim": (
        ["Tişört", "Kot Pantolon", "Sweatshirt", "Spor Ayakkabı", "Mont"],
        (100.00, 2500.00),
    ),
    "Ev & Yaşam": (
        ["Kahve Makinesi", "Battaniye", "Masa Lambası", "Saklama Kabı Seti", "Halı"],
        (80.00, 4000.00),
    ),
    "Kozmetik": (
        ["Nemlendirici", "Şampuan", "Parfüm", "Güneş Kremi", "Ruj"],
        (50.00, 1200.00),
    ),
    "Kitap": (
        ["Roman", "Deneme", "Ders Kitabı", "Çocuk Kitabı", "Şiir Kitabı"],
        (50.00, 400.00),
    ),
}

KATEGORILER = list(KATEGORI_URUN)
SEHIRLER = ["İstanbul", "Ankara", "İzmir", "Burdur", "Antalya"]
ODEME_TIPLERI = ["Kredi Kartı", "Banka Kartı", "Havale/EFT", "Kapıda Ödeme"]

CIKTI = Path(__file__).resolve().parent.parent / "data" / "siparisler.csv"


def uret() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)

    # Her kategori, şehir ve ödeme tipi en az bir kez geçsin: listenin tamamı bir kez
    # eklenir, kalan satırlar rastgele seçilir, sonra karıştırılır (TC-05 güvencesi)
    kategori = np.array(
        KATEGORILER
        + list(rng.choice(KATEGORILER, size=SATIR_SAYISI - len(KATEGORILER))),
        dtype=object,
    )
    sehir = np.array(
        SEHIRLER + list(rng.choice(SEHIRLER, size=SATIR_SAYISI - len(SEHIRLER))),
        dtype=object,
    )
    odeme = np.array(
        ODEME_TIPLERI
        + list(rng.choice(ODEME_TIPLERI, size=SATIR_SAYISI - len(ODEME_TIPLERI))),
        dtype=object,
    )
    rng.shuffle(kategori)
    rng.shuffle(sehir)
    rng.shuffle(odeme)

    # Ürün ve fiyat, satırın kategorisinden türetilir — kategoriler arası karışma yok
    urun = np.empty(SATIR_SAYISI, dtype=object)
    birim_fiyat = np.empty(SATIR_SAYISI, dtype=float)
    for i, kat in enumerate(kategori):
        urunler, (alt, ust) = KATEGORI_URUN[kat]
        urun[i] = urunler[int(rng.integers(len(urunler)))]
        birim_fiyat[i] = round(float(rng.uniform(alt, ust)), 2)

    adet = rng.integers(ADET_MIN, ADET_MAX + 1, size=SATIR_SAYISI)
    toplam_tutar = np.round(adet * birim_fiyat, 2)

    gun_sayisi = (pd.Timestamp(TARIH_BITIS) - pd.Timestamp(TARIH_BASLANGIC)).days
    tarihler = pd.Timestamp(TARIH_BASLANGIC) + pd.to_timedelta(
        rng.integers(0, gun_sayisi + 1, size=SATIR_SAYISI), unit="D"
    )

    df = pd.DataFrame(
        {
            "siparis_tarihi": tarihler,
            "kategori": kategori,
            "urun": urun,
            "adet": adet,
            "birim_fiyat": birim_fiyat,
            "toplam_tutar": toplam_tutar,
            "sehir": sehir,
            "odeme_tipi": odeme,
        }
    )

    # Tarihe göre sırala, siparis_id 1'den başlayarak 1'er artsın (TC-07)
    df = df.sort_values("siparis_tarihi", kind="mergesort").reset_index(drop=True)
    df.insert(0, "siparis_id", range(1, len(df) + 1))
    df["siparis_tarihi"] = df["siparis_tarihi"].dt.strftime("%Y-%m-%d")

    return df[SUTUNLAR]


def dogrula(df: pd.DataFrame) -> None:
    """Dosyayı yazmadan önce şemayı kendi içimizde kontrol et (DQ testlerinin aynası)."""
    assert list(df.columns) == SUTUNLAR, "TC-03: sütun adı/sırası şemayla uyuşmuyor"
    assert len(df) == SATIR_SAYISI, f"TC-02: satır sayısı {len(df)}, beklenen {SATIR_SAYISI}"
    assert df.isna().sum().sum() == 0, "TC-06: eksik değer var"
    assert (df.astype(str) == "").sum().sum() == 0, "TC-06: boş metin var"
    assert df["siparis_id"].duplicated().sum() == 0, "TC-07: siparis_id tekrar ediyor"
    assert df.duplicated().sum() == 0, "TC-07: birebir tekrar eden satır var"
    assert df["siparis_id"].min() == 1, "siparis_id 1'den başlamalı"
    assert df["adet"].between(ADET_MIN, ADET_MAX).all(), "TC-04: adet aralık dışı"
    assert df["birim_fiyat"].between(FIYAT_MIN, FIYAT_MAX).all(), "TC-04: birim_fiyat aralık dışı"
    fark = (df["toplam_tutar"] - (df["adet"] * df["birim_fiyat"]).round(2)).abs()
    assert (fark > 0.01).sum() == 0, "TC-08: toplam_tutar tutarsız"
    assert set(df["kategori"]) == set(KATEGORILER), "TC-05: kategori kümesi şemayla uyuşmuyor"
    # == : hem şema dışı değer yok hem de her değer en az bir kez geçiyor
    assert set(df["sehir"]) == set(SEHIRLER), "sehir kümesi şemayla uyuşmuyor"
    assert set(df["odeme_tipi"]) == set(ODEME_TIPLERI), "odeme_tipi kümesi şemayla uyuşmuyor"
    tarih = pd.to_datetime(df["siparis_tarihi"], format="%Y-%m-%d", errors="raise")
    assert tarih.between(TARIH_BASLANGIC, TARIH_BITIS).all(), "TC-04: tarih aralık dışı"


def csv_metni(df: pd.DataFrame) -> str:
    """CSV'yi önce bellekte metin olarak üret.

    round(x, 2) yetmez: pandas yazarken sondaki sıfırı düşürür (1667.40 -> 1667.4).
    float_format="%.2f" para alanlarını her zaman tam 2 ondalıkla yazar (#27).
    """
    return df.to_csv(index=False, lineterminator="\n", float_format="%.2f")


def metni_dogrula(metin: str) -> None:
    """Dosyaya yazılacak metni, DQ'nun okuyacağı gibi ham metin olarak kontrol et (TC-09 aynası)."""
    ham = pd.read_csv(io.StringIO(metin), dtype=str, keep_default_na=False)
    for alan in ("birim_fiyat", "toplam_tutar"):
        hatali = (~ham[alan].str.fullmatch(r"\d+\.\d{2}")).sum()
        assert hatali == 0, f"TC-09: {alan} alanında 2 ondalıkla yazılmamış {hatali} değer var"


def main() -> None:
    df = uret()
    dogrula(df)
    metin = csv_metni(df)
    metni_dogrula(metin)  # bir kontrol kalırsa dosya hiç yazılmaz
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_bytes(metin.encode("utf-8"))  # UTF-8, \n satır sonu, her işletim sisteminde aynı bayt

    print(f"Yazıldı: {CIKTI.relative_to(CIKTI.parent.parent)}")
    print(f"  Satır      : {len(df)}")
    print(f"  Sütun      : {len(df.columns)} -> {', '.join(df.columns)}")
    print(f"  Tohum      : {SEED}")
    print(f"  Tarih      : {df.siparis_tarihi.min()} .. {df.siparis_tarihi.max()}")
    print(f"  Ciro       : {df.toplam_tutar.sum():,.2f} TL")
    print("  Tüm iç kontroller geçti (TC-02…TC-09 aynası).")


if __name__ == "__main__":
    main()
