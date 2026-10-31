#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — BE: Görev 2 parametreli sipariş simülasyonu

DQ'nun şemasına (docs/veri-sozlugu.md) birebir uyan, parametreli, sabit tohumlu
ve tekrarlanabilir sentetik sipariş verisi üretir.
Çıktı: data/siparisler-g2.csv  (14 sütun; varsayılan parametrelerle 8.208 satır)

Şema kaynağı: docs/veri-sozlugu.md (#60) · Skill: skills/be-simulasyon/SKILL.md
Issue:        #61 (G2-veri — Parametreli simülasyon)

Kullanım (depo kökünde):
    python src/simulasyon.py
    python src/simulasyon.py --gun_sayisi 10 --cikti /tmp/deneme.csv
    python src/simulasyon.py --help

Geçersiz parametrede (aralık dışı, yanlış tip, bozuk tarih, BAŞ > SON) betik çökmez:
"Hata (ValueError): <parametre> <izinli aralık>, verilen: <değer>" yazar, 1 ile çıkar
ve dosya yazmaz.
"""

import argparse
import hashlib
import io
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Simülasyon parametreleri (varsayılanlar) — docs/veri-sozlugu.md → Simülasyon parametreleri
# Komut satırından değiştirilebilir (bkz. --help).
# ----------------------------------------------------------------------------

GUN_SAYISI = 182  # 26 hafta
GUNLUK_SIPARIS = 40  # normal bir hafta içi gündeki sipariş sayısı
HAFTA_SONU_KATSAYISI = 1.3
KAMPANYA_KATSAYISI = 1.5
KAMPANYA_DONEMLERI = "2026-03-09:2026-03-15,2026-05-11:2026-05-17"
BASLANGIC_TARIHI = "2026-01-05"  # Pazartesi
MUSTERI_SAYISI = 1500
TOHUM = 42

CIKTI = "data/siparisler-g2.csv"

# İzinli aralıklar — docs/veri-sozlugu.md → Simülasyon parametreleri (alt, üst; None = sınırsız)
PARAMETRE_ARALIKLARI = {
    "gun_sayisi": (int, 1, 366),
    "gunluk_siparis": (int, 1, 500),
    "hafta_sonu_katsayisi": (float, 0.1, 5.0),
    "kampanya_katsayisi": (float, 1.0, 5.0),
    "musteri_sayisi": (int, 1, 9999),
    "tohum": (int, 0, None),
}

# ----------------------------------------------------------------------------
# Şema sabitleri — değişirse skills/be-simulasyon/SKILL.md de güncellenmeli
# ----------------------------------------------------------------------------

SUTUNLAR = [
    "siparis_id",
    "siparis_tarihi",
    "musteri_id",
    "kanal",
    "kategori",
    "urun",
    "adet",
    "birim_fiyat",
    "indirim_orani",
    "kampanya",
    "toplam_tutar",
    "sehir",
    "odeme_tipi",
    "durum",
]

# kategori -> [(ürün, liste fiyatı TL)]; ürünler eşit olasılıkla seçilir
KATEGORI_URUN = {
    "Elektronik": [
        ("Kablosuz Kulaklık", 1299),
        ("Bluetooth Hoparlör", 899),
        ("Powerbank", 599),
        ("Akıllı Saat", 3499),
        ("Klavye", 749),
    ],
    "Giyim": [
        ("Tişört", 249),
        ("Kot Pantolon", 699),
        ("Sweatshirt", 549),
        ("Spor Ayakkabı", 1899),
        ("Mont", 2299),
    ],
    "Ev & Yaşam": [
        ("Kahve Makinesi", 2999),
        ("Battaniye", 449),
        ("Masa Lambası", 399),
        ("Saklama Kabı Seti", 299),
        ("Halı", 1799),
    ],
    "Kozmetik": [
        ("Nemlendirici", 189),
        ("Şampuan", 129),
        ("Parfüm", 999),
        ("Güneş Kremi", 279),
        ("Ruj", 159),
    ],
    "Kitap": [
        ("Roman", 149),
        ("Deneme", 129),
        ("Ders Kitabı", 349),
        ("Çocuk Kitabı", 99),
        ("Şiir Kitabı", 119),
    ],
}
# 25 ürünlük düz liste: (kategori, ürün, liste fiyatı) — sıra yukarıdaki gibi
URUNLER = [(kat, ad, fiyat) for kat, liste in KATEGORI_URUN.items() for ad, fiyat in liste]

FIYAT_SAPMA = 0.05  # birim_fiyat = liste fiyatı × [0,95 – 1,05]

ADET_DEGERLERI = [1, 2, 3, 4, 5]
ADET_OLASILIK = [0.50, 0.25, 0.12, 0.08, 0.05]

KANALLAR = ["Web", "Mobil", "Pazaryeri"]
KANAL_OLASILIK = [0.45, 0.40, 0.15]

SEHIRLER = ["İstanbul", "Ankara", "İzmir", "Antalya", "Burdur"]
SEHIR_OLASILIK = [0.35, 0.20, 0.20, 0.15, 0.10]

ODEME_TIPLERI = ["Kredi Kartı", "Banka Kartı", "Kapıda Ödeme", "Havale/EFT"]
ODEME_OLASILIK = [0.50, 0.25, 0.15, 0.10]

DURUMLAR = ["Teslim Edildi", "İade", "İptal"]
DURUM_OLASILIK = [0.90, 0.06, 0.04]

INDIRIM_ORANLARI = [0.10, 0.15, 0.20, 0.25, 0.30]  # yalnızca kampanya günlerinde, eşit olasılık

PARA_DESENI = r"^\d+\.\d{2}$"  # para alanları ham metinde tam 2 ondalık (#27)


# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------


def kontrol(kosul, mesaj):
    """assert yerine: python -O ile çalıştırılsa bile atlanmaz."""
    if not kosul:
        raise ValueError(mesaj)


def aralik_metni(alt, ust):
    return f"{alt} veya büyük" if ust is None else f"{alt}–{ust} arasında"


def sayiyi_coz(ad, deger):
    """Sayısal parametreyi tipine çevirir ve izinli aralıkta mı bakar; değilse ValueError."""
    tip, alt, ust = PARAMETRE_ARALIKLARI[ad]
    tip_adi = "tamsayı" if tip is int else "sayı"
    try:
        sayi = tip(deger)
    except (TypeError, ValueError):
        raise ValueError(
            f"{ad} {tip_adi} olmalı ({aralik_metni(alt, ust)}), verilen: {deger!r}"
        ) from None
    # NaN hiçbir karşılaştırmayı geçmez, bu yüzden aralık dışı sayılır
    if not (alt <= sayi and (ust is None or sayi <= ust)):
        raise ValueError(f"{ad} {aralik_metni(alt, ust)} olmalı, verilen: {deger}")
    return sayi


def tarihi_coz(ad, metin):
    try:
        return date.fromisoformat(str(metin).strip())
    except ValueError:
        raise ValueError(f"{ad} geçerli bir YYYY-MM-DD tarihi olmalı, verilen: {metin!r}") from None


def kampanya_donemlerini_coz(metin):
    """'BAŞ:SON,BAŞ:SON' metnini [(date, date), ...] listesine çevirir; bozuksa ValueError."""
    bicim = "her dönem BAŞ:SON (YYYY-MM-DD:YYYY-MM-DD) biçiminde, dönemler virgülle ayrılmış olmalı"
    donemler = []
    for parca in metin.split(","):
        parca = parca.strip()
        if not parca:
            continue
        uclar = parca.split(":")
        if len(uclar) != 2:
            raise ValueError(f"kampanya_donemleri {bicim}, verilen: {parca!r}")
        try:
            bas, son = (date.fromisoformat(u.strip()) for u in uclar)
        except ValueError:
            raise ValueError(f"kampanya_donemleri {bicim}; geçersiz tarih, verilen: {parca!r}") from None
        if bas > son:
            raise ValueError(f"kampanya_donemleri içinde başlangıç sondan sonra olamaz, verilen: {parca!r}")
        donemler.append((bas, son))
    return donemler


def kampanyada_mi(gun, donemler):
    return any(bas <= gun <= son for bas, son in donemler)


def gun_adetleri(p):
    """Her gün için (tarih, kampanya mı, sipariş adedi) — docs/veri-sozlugu.md → Satır sayısı."""
    gunler = []
    for k in range(p.gun_sayisi):
        gun = p.baslangic + timedelta(days=k)
        kampanya = kampanyada_mi(gun, p.donemler)
        gun_k = 1.0
        if gun.weekday() >= 5:  # Cumartesi (5) veya Pazar (6)
            gun_k *= p.hafta_sonu_katsayisi
        if kampanya:
            gun_k *= p.kampanya_katsayisi
        adet = math.floor(p.gunluk_siparis * gun_k + 0.5)  # en yakın tamsayı, .5 yukarı
        gunler.append((gun, kampanya, adet))
    return gunler


# ----------------------------------------------------------------------------
# Üretim
# ----------------------------------------------------------------------------


def uret(p):
    gunler = gun_adetleri(p)
    n = sum(adet for _, _, adet in gunler)

    # Tarih ve kampanya bayrağı gün sırasıyla açılır → dosya zaten tarihe göre artan
    tarih = np.repeat([g.isoformat() for g, _, _ in gunler], [a for _, _, a in gunler])
    kampanya = np.repeat([int(k) for _, k, _ in gunler], [a for _, _, a in gunler])

    # Tüm rastgele değerler tek rng'den, bu sırayla çekilir (sıra değişirse dosya değişir)
    rng = np.random.default_rng(p.tohum)
    urun_idx = rng.integers(0, len(URUNLER), size=n)
    liste_fiyat = np.array([URUNLER[i][2] for i in urun_idx], dtype=np.int64)
    # Fiyat kuruş cinsinden tamsayı çekilir: [liste × 95, liste × 105] kuruş, uçlar dahil
    kurus = rng.integers(liste_fiyat * 95, liste_fiyat * 105 + 1)
    adet = rng.choice(ADET_DEGERLERI, size=n, p=ADET_OLASILIK)
    kanal = rng.choice(KANALLAR, size=n, p=KANAL_OLASILIK)
    sehir = rng.choice(SEHIRLER, size=n, p=SEHIR_OLASILIK)
    odeme = rng.choice(ODEME_TIPLERI, size=n, p=ODEME_OLASILIK)
    durum = rng.choice(DURUMLAR, size=n, p=DURUM_OLASILIK)
    musteri = rng.integers(1, p.musteri_sayisi + 1, size=n)
    indirim = rng.choice(INDIRIM_ORANLARI, size=n)
    indirim = np.where(kampanya == 1, indirim, 0.0)

    birim_fiyat = kurus / 100
    toplam_tutar = np.round(adet * birim_fiyat * (1 - indirim), 2)

    df = pd.DataFrame(
        {
            "siparis_id": np.arange(1, n + 1),
            "siparis_tarihi": tarih,
            "musteri_id": [f"M{m:04d}" for m in musteri],
            "kanal": kanal,
            "kategori": [URUNLER[i][0] for i in urun_idx],
            "urun": [URUNLER[i][1] for i in urun_idx],
            "adet": adet,
            "birim_fiyat": birim_fiyat,
            "indirim_orani": indirim,
            "kampanya": kampanya,
            "toplam_tutar": toplam_tutar,
            "sehir": sehir,
            "odeme_tipi": odeme,
            "durum": durum,
        },
        columns=SUTUNLAR,
    )
    return df, n


def csv_metni(df):
    tampon = io.StringIO()
    df.to_csv(tampon, index=False, float_format="%.2f", lineterminator="\n")
    return tampon.getvalue()


# ----------------------------------------------------------------------------
# İç kontroller — docs/veri-sozlugu.md → Veri kalitesi kuralları 1–11 (12: ikinci çalıştırma, MD5)
# ----------------------------------------------------------------------------


def dogrula(df, p, beklenen_n):
    son_tarih = p.baslangic + timedelta(days=p.gun_sayisi - 1)

    # Kural 1 — boş değer yok
    kontrol(df.isna().sum().sum() == 0, "Kural 1: boş değer var")
    kontrol(not (df.astype(str) == "").any().any(), "Kural 1: boş metin var")
    # Kural 2 — sütunlar
    kontrol(list(df.columns) == SUTUNLAR, f"Kural 2: sütunlar şemayla aynı değil: {list(df.columns)}")
    # Kural 3 — satır sayısı formülle aynı
    kontrol(len(df) == beklenen_n, f"Kural 3: satır sayısı {len(df)}, beklenen {beklenen_n}")
    # Kural 4 — siparis_id 1…N ardışık, tarih artan
    kontrol(df["siparis_id"].tolist() == list(range(1, len(df) + 1)), "Kural 4: siparis_id 1…N ardışık değil")
    kontrol(df["siparis_tarihi"].is_monotonic_increasing, "Kural 4: dosya tarihe göre artan değil")
    # Kural 5 — tarih aralığı ve farklı gün sayısı
    tarihler = pd.to_datetime(df["siparis_tarihi"], format="%Y-%m-%d")
    kontrol(
        tarihler.min().date() >= p.baslangic and tarihler.max().date() <= son_tarih,
        "Kural 5: tarih aralık dışında",
    )
    kontrol(df["siparis_tarihi"].nunique() == p.gun_sayisi, "Kural 5: farklı tarih sayısı gun_sayisi değil")
    # Kural 6 — kategorik değerler listelerde
    for alan, izinli in [
        ("kanal", KANALLAR),
        ("kategori", list(KATEGORI_URUN)),
        ("urun", [u for _, u, _ in URUNLER]),
        ("sehir", SEHIRLER),
        ("odeme_tipi", ODEME_TIPLERI),
        ("durum", DURUMLAR),
    ]:
        fazla = set(df[alan]) - set(izinli)
        kontrol(not fazla, f"Kural 6: {alan} listede olmayan değer içeriyor: {fazla}")
    # musteri_id biçimi ve havuzu
    kontrol(df["musteri_id"].str.fullmatch(r"M\d{4}").all(), "musteri_id biçimi M + 4 hane değil")
    no = df["musteri_id"].str[1:].astype(int)
    kontrol(no.between(1, p.musteri_sayisi).all(), "musteri_id havuz dışında")
    # adet aralığı
    kontrol(df["adet"].between(1, 5).all(), "adet 1–5 dışında")
    # Kural 7 — ürün kendi kategorisinde
    urun_kategori = {u: k for k, u, _ in URUNLER}
    kontrol((df["urun"].map(urun_kategori) == df["kategori"]).all(), "Kural 7: ürün kendi kategorisinde değil")
    # Kural 8 — fiyat liste fiyatının [%95, %105] aralığında (kuruş cinsinden, yuvarlama payı yok)
    liste = df["urun"].map({u: f for _, u, f in URUNLER})
    kurus = (df["birim_fiyat"] * 100).round().astype(int)
    kontrol(
        ((kurus >= liste * 95) & (kurus <= liste * 105)).all(),
        "Kural 8: birim_fiyat liste fiyatının ±%5'i dışında",
    )
    # Kural 10 — hesaplanan alan
    hesap = (df["adet"] * df["birim_fiyat"] * (1 - df["indirim_orani"])).round(2)
    kontrol((df["toplam_tutar"] - hesap).abs().max() < 0.005, "Kural 10: toplam_tutar hesapla uyuşmuyor")
    kontrol((df["toplam_tutar"] > 0).all(), "Kural 10: toplam_tutar > 0 değil")
    # Kural 11 — kampanya tutarlılığı
    gunluk = {g.isoformat(): int(k) for g, k, _ in gun_adetleri(p)}
    kontrol((df["siparis_tarihi"].map(gunluk) == df["kampanya"]).all(), "Kural 11: kampanya bayrağı tarihle uyuşmuyor")
    kontrol((df.loc[df["kampanya"] == 0, "indirim_orani"] == 0).all(), "Kural 11: kampanya dışında indirim var")
    kontrol(
        df.loc[df["kampanya"] == 1, "indirim_orani"].round(2).isin(INDIRIM_ORANLARI).all(),
        "Kural 11: kampanyada indirim oranı listede değil",
    )


def metni_dogrula(metin):
    """Kural 9 — para alanları ham metinde tam 2 ondalık (sayıya çevirince görünmez)."""
    ham = pd.read_csv(io.StringIO(metin), dtype=str, keep_default_na=False)
    for alan in ["birim_fiyat", "toplam_tutar", "indirim_orani"]:
        kontrol(ham[alan].str.fullmatch(PARA_DESENI).all(), f"Kural 9: {alan} tam 2 ondalık değil")


# ----------------------------------------------------------------------------
# Komut satırı
# ----------------------------------------------------------------------------


def parametreleri_al(argv=None):
    ap = argparse.ArgumentParser(description="Görev 2 parametreli sipariş simülasyonu (docs/veri-sozlugu.md)")
    # Tipler burada çevrilmez: yanlış tip de aralık dışı değer gibi Türkçe ValueError versin
    ap.add_argument("--gun_sayisi", default=GUN_SAYISI, help=f"simüle edilen gün (vars. {GUN_SAYISI})")
    ap.add_argument("--gunluk_siparis", default=GUNLUK_SIPARIS, help=f"hafta içi günlük sipariş (vars. {GUNLUK_SIPARIS})")
    ap.add_argument("--hafta_sonu_katsayisi", default=HAFTA_SONU_KATSAYISI, help=f"vars. {HAFTA_SONU_KATSAYISI}")
    ap.add_argument("--kampanya_katsayisi", default=KAMPANYA_KATSAYISI, help=f"vars. {KAMPANYA_KATSAYISI}")
    ap.add_argument("--kampanya_donemleri", default=KAMPANYA_DONEMLERI, help=f"'BAŞ:SON,BAŞ:SON' (vars. {KAMPANYA_DONEMLERI})")
    ap.add_argument("--baslangic_tarihi", default=BASLANGIC_TARIHI, help=f"YYYY-MM-DD (vars. {BASLANGIC_TARIHI})")
    ap.add_argument("--musteri_sayisi", default=MUSTERI_SAYISI, help=f"vars. {MUSTERI_SAYISI}")
    ap.add_argument("--tohum", default=TOHUM, help=f"rastgelelik tohumu (vars. {TOHUM})")
    ap.add_argument("--cikti", default=CIKTI, help=f"çıktı dosyası (vars. {CIKTI})")
    p = ap.parse_args(argv)
    parametreleri_dogrula(p)
    return p


def parametreleri_dogrula(p):
    """Üretimden önce tüm parametreleri sözlükteki aralıklarla kontrol eder (Hafta 6, hata yönetimi).

    Geçersiz bir değerde parametrenin adını, izinli aralığı ve verilen değeri söyleyen bir
    ValueError verir; bu noktada henüz hiçbir dosya yazılmamıştır.
    """
    for ad in PARAMETRE_ARALIKLARI:
        setattr(p, ad, sayiyi_coz(ad, getattr(p, ad)))
    p.baslangic = tarihi_coz("baslangic_tarihi", p.baslangic_tarihi)
    p.donemler = kampanya_donemlerini_coz(p.kampanya_donemleri)


def main(argv=None):
    p = parametreleri_al(argv)
    df, n = uret(p)

    # Yazmadan önce: veri çerçevesi ve ham metin kontrolleri; biri kalırsa dosya yazılmaz
    dogrula(df, p, n)
    metin = csv_metni(df)
    metni_dogrula(metin)

    cikti = Path(p.cikti)
    cikti.parent.mkdir(parents=True, exist_ok=True)
    cikti.write_bytes(metin.encode("utf-8"))

    # Yazdıktan sonra: diskten geri oku, aynı metin mi?
    kontrol(cikti.read_bytes().decode("utf-8") == metin, "Geri okuma: diskteki dosya üretilen metinle aynı değil")

    teslim = df[df["durum"] == "Teslim Edildi"]
    md5 = hashlib.md5(metin.encode("utf-8")).hexdigest()
    print(f"Dosya: {cikti}")
    print(
        f"Parametreler: gun_sayisi={p.gun_sayisi}, gunluk_siparis={p.gunluk_siparis}, "
        f"hafta_sonu_katsayisi={p.hafta_sonu_katsayisi}, kampanya_katsayisi={p.kampanya_katsayisi}, "
        f"kampanya_donemleri={p.kampanya_donemleri}, baslangic_tarihi={p.baslangic_tarihi}, "
        f"musteri_sayisi={p.musteri_sayisi}, tohum={p.tohum}"
    )
    print(f"Satır: {len(df)}  ·  Sütun: {len(df.columns)}")
    print(f"Tarih: {df['siparis_tarihi'].iloc[0]} .. {df['siparis_tarihi'].iloc[-1]}  ·  Farklı gün: {df['siparis_tarihi'].nunique()}")
    print(f"Kampanyalı sipariş: {int(df['kampanya'].sum())}  ·  Teslim edilen: {len(teslim)}")
    print(f"Net ciro (teslim edilen, M1): {teslim['toplam_tutar'].sum():,.2f} TL")
    print(f"MD5: {md5}")
    print("Tüm iç kontroller geçti (veri sözlüğü kalite kuralları 1–11; kural 12 için ikinci çalıştırmada MD5'i karşılaştır).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as hata:
        # Çökme yerine anlaşılır mesaj ve 1 çıkış kodu; hata yutulmaz, dosya yazılmamıştır
        print(f"Hata (ValueError): {hata}", file=sys.stderr)
        sys.exit(1)
