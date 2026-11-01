#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — DQ: Görev 2 test koşucusu (tests/test-cases.md → G2-TC-01…22)

Veri dosyasını docs/veri-sozlugu.md kurallarına göre sınar; parametre ve hata yönetimi
senaryolarında src/simulasyon.py'yi geçici bir klasöre çalıştırır (geçici dosyalar silinir).

Kullanım (depo kökünde):
    python src/dq_test_g2.py                 # A–D tüm gruplar
    python src/dq_test_g2.py --grup A B C    # yalnızca seçili gruplar
    python src/dq_test_g2.py --dosya yol.csv --grup A B

Çıktı: senaryo başına "| ID | gerçekleşen | Geçti/Kaldı |" satırı + özet. Tümü geçerse çıkış 0, değilse 1.
Skill: skills/dq-test/SKILL.md · Issue: #64
"""

import argparse
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import pandas as pd

VERI = "data/siparisler-g2.csv"
SIM = "src/simulasyon.py"
SUTUNLAR = ["siparis_id", "siparis_tarihi", "musteri_id", "kanal", "kategori", "urun", "adet", "birim_fiyat",
            "indirim_orani", "kampanya", "toplam_tutar", "sehir", "odeme_tipi", "durum"]
VARSAYILAN = dict(gun_sayisi=182, gunluk_siparis=40, hafta_sonu_katsayisi=1.3, kampanya_katsayisi=1.5,
                  kampanya_donemleri=(("2026-03-09", "2026-03-15"), ("2026-05-11", "2026-05-17")),
                  baslangic_tarihi="2026-01-05", musteri_sayisi=1500)
URUNLER = {
    "Elektronik": {"Kablosuz Kulaklık": 1299, "Bluetooth Hoparlör": 899, "Powerbank": 599, "Akıllı Saat": 3499, "Klavye": 749},
    "Giyim": {"Tişört": 249, "Kot Pantolon": 699, "Sweatshirt": 549, "Spor Ayakkabı": 1899, "Mont": 2299},
    "Ev & Yaşam": {"Kahve Makinesi": 2999, "Battaniye": 449, "Masa Lambası": 399, "Saklama Kabı Seti": 299, "Halı": 1799},
    "Kozmetik": {"Nemlendirici": 189, "Şampuan": 129, "Parfüm": 999, "Güneş Kremi": 279, "Ruj": 159},
    "Kitap": {"Roman": 149, "Deneme": 129, "Ders Kitabı": 349, "Çocuk Kitabı": 99, "Şiir Kitabı": 119},
}
LISTE = {u: f for d in URUNLER.values() for u, f in d.items()}
URUN_KAT = {u: k for k, d in URUNLER.items() for u in d}
DEGERLER = {"kanal": ["Web", "Mobil", "Pazaryeri"], "kategori": list(URUNLER), "urun": list(LISTE),
            "sehir": ["İstanbul", "Ankara", "İzmir", "Antalya", "Burdur"],
            "odeme_tipi": ["Kredi Kartı", "Banka Kartı", "Kapıda Ödeme", "Havale/EFT"],
            "durum": ["Teslim Edildi", "İade", "İptal"]}
AGIRLIK = {"adet": {1: .50, 2: .25, 3: .12, 4: .08, 5: .05}, "kanal": {"Web": .45, "Mobil": .40, "Pazaryeri": .15},
           "sehir": {"İstanbul": .35, "Ankara": .20, "İzmir": .20, "Antalya": .15, "Burdur": .10},
           "odeme_tipi": {"Kredi Kartı": .50, "Banka Kartı": .25, "Kapıda Ödeme": .15, "Havale/EFT": .10},
           "durum": {"Teslim Edildi": .90, "İade": .06, "İptal": .04}}
PARA = re.compile(r"^\d+\.\d{2}$")


def beklenen_n(gun_sayisi=182, gunluk_siparis=40, hafta_sonu_katsayisi=1.3, kampanya_katsayisi=1.5,
               kampanya_donemleri=VARSAYILAN["kampanya_donemleri"], baslangic_tarihi="2026-01-05", **_):
    """Sözlükteki satır sayısı formülü: gun_adet = max(1, floor(g × k + 0.5))."""
    bas = date.fromisoformat(baslangic_tarihi)
    donem = [(date.fromisoformat(a), date.fromisoformat(b)) for a, b in kampanya_donemleri]
    n = 0
    for i in range(gun_sayisi):
        g = bas + timedelta(days=i)
        k = (hafta_sonu_katsayisi if g.weekday() >= 5 else 1.0) * (kampanya_katsayisi if any(a <= g <= b for a, b in donem) else 1.0)
        n += max(1, math.floor(gunluk_siparis * k + 0.5))
    return n


def md5(yol):
    with open(yol, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def sonuc(tc, gecti, metin):
    return (tc, gecti, metin)


# ------------------------------------------------------------------ A + B: veri dosyası
def veri_testleri(yol, p=None, gruplar=("A", "B")):
    p = {**VARSAYILAN, **(p or {})}
    out = []
    if not os.path.exists(yol) or os.path.getsize(yol) == 0:
        return [sonuc("G2-TC-01", False, f"{yol} yok ya da boş")]
    ham = pd.read_csv(yol, dtype=str, keep_default_na=False, encoding="utf-8")
    df = pd.read_csv(yol, encoding="utf-8")
    bas = date.fromisoformat(p["baslangic_tarihi"])
    son = bas + timedelta(days=p["gun_sayisi"] - 1)
    if "A" in gruplar:
        tr = all(any(ch in s for ch in "İıŞşĞğÇçÖöÜü") for s in ["İstanbul", "Kapıda Ödeme"]) and "İstanbul" in set(df["sehir"])
        out.append(sonuc("G2-TC-01", len(df) > 0 and tr, f"{os.path.getsize(yol):,} bayt, {len(df):,} satır; Türkçe karakterler okunuyor: {'evet' if tr else 'hayır'}"))
        out.append(sonuc("G2-TC-02", list(df.columns) == SUTUNLAR, f"{len(df.columns)} sütun, sıra {'sözlükle aynı' if list(df.columns) == SUTUNLAR else 'farklı: ' + ','.join(df.columns)}"))
        n = beklenen_n(**p)
        out.append(sonuc("G2-TC-03", len(df) == n, f"{len(df):,} satır (beklenen {n:,})"))
        hatali = 0
        for c in ["siparis_id", "adet", "kampanya"]:
            hatali += (~ham[c].str.fullmatch(r"-?\d+")).sum()
        for c in ["birim_fiyat", "indirim_orani", "toplam_tutar"]:
            hatali += pd.to_numeric(ham[c], errors="coerce").isna().sum()
        hatali += pd.to_datetime(ham["siparis_tarihi"], format="%Y-%m-%d", errors="coerce").isna().sum()
        out.append(sonuc("G2-TC-04", hatali == 0, f"çevrilemeyen değer: {hatali}"))
        no = pd.to_numeric(df["musteri_id"].str[1:], errors="coerce")
        dis = (~df["adet"].between(1, 5)).sum() + (~df["kampanya"].isin([0, 1])).sum() \
            + (~df["indirim_orani"].round(2).isin([0.0, .10, .15, .20, .25, .30])).sum() + (df["toplam_tutar"] <= 0).sum() \
            + (~df["musteri_id"].str.fullmatch(r"M\d{4}")).sum() + (~no.between(1, p["musteri_sayisi"])).sum()
        out.append(sonuc("G2-TC-05", dis == 0, f"aralık/biçim dışı: {dis}"))
        bos = int(df.isna().sum().sum() + (ham == "").sum().sum())
        out.append(sonuc("G2-TC-06", bos == 0, f"boş değer: {bos}"))
        ok7 = df["siparis_id"].tolist() == list(range(1, len(df) + 1)) and pd.to_datetime(df["siparis_tarihi"]).is_monotonic_increasing
        out.append(sonuc("G2-TC-07", ok7, f"siparis_id 1…{len(df):,} ardışık ve tarih artan: {'evet' if ok7 else 'hayır'}"))
        t = pd.to_datetime(df["siparis_tarihi"])
        ok8 = t.min().date() == bas and t.max().date() == son and t.nunique() == p["gun_sayisi"]
        out.append(sonuc("G2-TC-08", ok8, f"{t.min():%Y-%m-%d} … {t.max():%Y-%m-%d}, {t.nunique()} farklı gün (beklenen {bas} … {son}, {p['gun_sayisi']})"))
    if "B" in gruplar:
        fazla = {c: sorted(set(df[c]) - set(v)) for c, v in DEGERLER.items() if set(df[c]) - set(v)}
        eksik = {c: sorted(set(v) - set(df[c])) for c, v in DEGERLER.items() if set(v) - set(df[c])}
        out.append(sonuc("G2-TC-09", not fazla and not eksik, f"liste dışı: {fazla or 'yok'}; hiç geçmeyen: {eksik or 'yok'}"))
        uy = (df["urun"].map(URUN_KAT) != df["kategori"]).sum()
        out.append(sonuc("G2-TC-10", uy == 0, f"ürün–kategori uyuşmayan: {uy}"))
        lp = df["urun"].map(LISTE)
        dis = ((df["birim_fiyat"] < (lp * .95).round(2) - 1e-9) | (df["birim_fiyat"] > (lp * 1.05).round(2) + 1e-9)).sum()
        out.append(sonuc("G2-TC-11", dis == 0, f"liste ±%5 dışı: {dis}; birim_fiyat {df['birim_fiyat'].min():.2f} – {df['birim_fiyat'].max():.2f}"))
        bic = sum((~ham[c].str.fullmatch(PARA)).sum() for c in ["birim_fiyat", "toplam_tutar", "indirim_orani"])
        out.append(sonuc("G2-TC-12", bic == 0, f"2 ondalık dışı: {bic}"))
        fark = ((df["adet"] * df["birim_fiyat"] * (1 - df["indirim_orani"])).round(2) - df["toplam_tutar"]).abs()
        out.append(sonuc("G2-TC-13", (fark >= .005).sum() == 0, f"formülle uyuşmayan: {(fark >= .005).sum()}"))
        d = pd.to_datetime(df["siparis_tarihi"]).dt.date
        donem = [(date.fromisoformat(a), date.fromisoformat(b)) for a, b in p["kampanya_donemleri"]]
        icinde = d.map(lambda g: any(a <= g <= b for a, b in donem))
        k1 = (icinde != (df["kampanya"] == 1)).sum()
        k2 = ((df["kampanya"] == 0) & (df["indirim_orani"] != 0)).sum()
        k3 = ((df["kampanya"] == 1) & ~df["indirim_orani"].round(2).isin([.10, .15, .20, .25, .30])).sum()
        out.append(sonuc("G2-TC-14", k1 + k2 + k3 == 0, f"aykırı: bayrak {k1}, kampanyasız indirim {k2}, oran {k3}; kampanya günü {d[icinde].nunique()}"))
        sapma = []
        for c, ag in AGIRLIK.items():
            oran = df[c].value_counts(normalize=True)
            for v, w in ag.items():
                if abs(oran.get(v, 0) - w) > .03:
                    sapma.append(f"{c}={v} %{oran.get(v, 0) * 100:.1f}")
        out.append(sonuc("G2-TC-15", not sapma, f"±3 puan dışı: {', '.join(sapma) or 'yok'}"))
    return out


# ------------------------------------------------------------------ C + D: simülasyonu çalıştır
def calistir(arglar, klasor, ad):
    cikti = os.path.join(klasor, ad)
    r = subprocess.run([sys.executable, SIM, *arglar, "--cikti", cikti], capture_output=True, text=True)
    return r, cikti


def parametre_testleri(veri_yolu):
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        r1, a = calistir([], tmp, "a.csv")
        r2, b = calistir([], tmp, "b.csv")
        ok = r1.returncode == 0 and r2.returncode == 0 and md5(a) == md5(b) == md5(veri_yolu)
        out.append(sonuc("G2-TC-16", ok, f"MD5 çalıştırma 1/2/repo: {md5(a)[:8]} / {md5(b)[:8]} / {md5(veri_yolu)[:8]}" if r1.returncode == 0 else f"çalışmadı: {r1.stderr.strip()[-120:]}"))

        def n_ve_son(args, ad, p):
            r, y = calistir(args, tmp, ad)
            if r.returncode != 0:
                return False, f"{' '.join(args)} → hata: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}"
            df = pd.read_csv(y)
            n = beklenen_n(**{**VARSAYILAN, **p})
            return len(df) == n, f"{' '.join(args)} → {len(df):,} satır (beklenen {n:,}), son {df['siparis_tarihi'].iloc[-1]}"

        a1 = n_ve_son(["--gun_sayisi", "10"], "c1.csv", {"gun_sayisi": 10})
        a2 = n_ve_son(["--gun_sayisi", "7"], "c2.csv", {"gun_sayisi": 7})
        out.append(sonuc("G2-TC-17", a1[0] and a2[0], f"{a1[1]}; {a2[1]}"))
        b1 = n_ve_son(["--gun_sayisi", "10", "--gunluk_siparis", "10"], "c3.csv", {"gun_sayisi": 10, "gunluk_siparis": 10})
        out.append(sonuc("G2-TC-18", b1[0], b1[1]))
        c = [n_ve_son(["--hafta_sonu_katsayisi", "1.0"], "c4.csv", {"hafta_sonu_katsayisi": 1.0}),
             n_ve_son(["--kampanya_katsayisi", "1.0"], "c5.csv", {"kampanya_katsayisi": 1.0}),
             n_ve_son(["--baslangic_tarihi", "2026-03-09", "--gun_sayisi", "14"], "c6.csv", {"baslangic_tarihi": "2026-03-09", "gun_sayisi": 14})]
        out.append(sonuc("G2-TC-19", all(x[0] for x in c), "; ".join(x[1] for x in c)))
        r, y = calistir(["--tohum", "7"], tmp, "c7.csv")
        if r.returncode == 0:
            ic = veri_testleri(y)
            kalan = [x[0] for x in ic if not x[1] and x[0] not in ("G2-TC-15",)]
            ok = len(pd.read_csv(y)) == beklenen_n() and md5(y) != md5(veri_yolu) and not kalan
            out.append(sonuc("G2-TC-20", ok, f"8.208 satır: {len(pd.read_csv(y)) == beklenen_n()}; MD5 farklı: {md5(y) != md5(veri_yolu)}; A/B kalan: {kalan or 'yok'}"))
        else:
            out.append(sonuc("G2-TC-20", False, f"çalışmadı: {r.stderr.strip()[-120:]}"))
    return out


def hata_testleri():
    durumlar = {
        "G2-TC-21": [["--gun_sayisi", "0"], ["--gun_sayisi", "-3"], ["--musteri_sayisi", "10000"], ["--gunluk_siparis", "0"]],
        "G2-TC-22": [["--kampanya_donemleri", "2026-03-09"], ["--kampanya_donemleri", "2026-03-15:2026-03-09"], ["--baslangic_tarihi", "2026-13-01"]],
    }
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for tc, liste in durumlar.items():
            notlar, hepsi = [], True
            for i, args in enumerate(liste):
                klasor = os.path.join(tmp, f"{tc}-{i}")
                r, y = calistir(args, klasor, "x.csv")
                mesaj = (r.stderr.strip().splitlines() or ["(mesaj yok)"])[-1]
                adi = args[0].lstrip("-")
                ok = r.returncode == 1 and not os.path.exists(y) and mesaj.startswith("Hata (ValueError)") and adi in mesaj and "Traceback" not in r.stderr
                hepsi &= ok
                notlar.append(f"{' '.join(args)} → çıkış {r.returncode}, dosya {'var' if os.path.exists(y) else 'yok'}, \"{mesaj[:70]}\"")
            out.append(sonuc(tc, hepsi, " · ".join(notlar)))
        # Sınır: izinli aralıktaki parametrelerle iç kontrol hatası olmamalı (PR #72 incelemesi)
        r, y = calistir(["--gunluk_siparis", "1", "--hafta_sonu_katsayisi", "0.4", "--gun_sayisi", "7"], tmp, "sinir.csv")
        out.append(sonuc("G2-TC-21+", r.returncode == 0, f"--gunluk_siparis 1 --hafta_sonu_katsayisi 0.4 (izinli) → çıkış {r.returncode}"
                         + (f", \"{(r.stderr.strip().splitlines() or [''])[-1][:70]}\"" if r.returncode else ", dosya yazıldı")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Görev 2 test koşucusu (tests/test-cases.md)")
    ap.add_argument("--dosya", default=VERI)
    ap.add_argument("--grup", nargs="+", default=["A", "B", "C", "D"], choices=["A", "B", "C", "D"])
    a = ap.parse_args(argv)
    sonuclar = veri_testleri(a.dosya, gruplar=a.grup)
    if "C" in a.grup:
        sonuclar += parametre_testleri(a.dosya)
    if "D" in a.grup:
        sonuclar += hata_testleri()
    print("| ID | Gerçekleşen | Geçti/Kaldı |\n|---|---|---|")
    for tc, ok, m in sonuclar:
        print(f"| {tc} | {m} | {'✅ Geçti' if ok else '❌ Kaldı'} |")
    g = sum(1 for _, ok, _ in sonuclar if ok)
    print(f"\nÖzet: {g}/{len(sonuclar)} geçti · veri {a.dosya} · MD5 {md5(a.dosya)}")
    return 0 if g == len(sonuclar) else 1


if __name__ == "__main__":
    sys.exit(main())
