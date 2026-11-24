#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — DQ: Görev 2 test koşucusu (tests/test-cases.md → G2-TC-01…34)

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
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

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
# Görev 3 (PR #95): urun_agirliklari senaryoları. Sıra = sözlükteki "Ürün sırası" (1–25) = LISTE sırası
URUN_W = [1, 1, 2, 0.5, 1, 4, 3, 4, 1, 1, 1, 3, 2, 3, 1, 4, 4, 1, 3, 3, 2, 2, 1, 3, 1]
URUN_TOL = 1.5  # puan; ürün payı beklenen w_i/Σw'nin ±1,5 puan içinde olmalı
# Görev 3 (PR #102): urun_listesi ve fiyat_sapmasi senaryoları (G2-TC-26…34)
ORNEK_LISTE = "data/urun-listesi-ornek.csv"   # betikteki 25 ürün; varsayılan dosyayı aynen üretir
WEB_LISTE = "data/urun-listesi-web.csv"       # liste fiyatları Ajan 1'in web taramasına göre
WEB_VERI = "data/siparisler-web.csv"          # WEB_LISTE ile üretilmiş repodaki dosya
LISTE_BASLIK = "kategori,urun,liste_fiyati\n"
LISTE_SAPMALI = "kategori,urun,liste_fiyati,fiyat_sapmasi\n"


def liste_yukle(yol):
    """--urun_listesi CSV'sini okur → ({kategori: {urun: liste_fiyati}}, {urun: fiyat_sapmasi ya da None}). Sıra = dosya sırası."""
    d = pd.read_csv(yol, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    kat, sap = {}, {}
    for _, r in d.iterrows():
        kat.setdefault(r["kategori"], {})[r["urun"]] = float(r["liste_fiyati"])
        sap[r["urun"]] = float(r["fiyat_sapmasi"]) if "fiyat_sapmasi" in d.columns and r["fiyat_sapmasi"] != "" else None
    return kat, sap


def fiyat_siniri(liste, sapma):
    """Sözlük kural 8: birim_fiyat ∈ [liste × (1 − sapma), liste × (1 + sapma)], kuruş cinsinden tam ondalıkla; sınır içe yuvarlanır."""
    l, s = Decimal(str(liste)), Decimal(str(sapma))
    ince = Decimal("0.01")
    return float((l * (1 - s)).quantize(ince, ROUND_CEILING)), float((l * (1 + s)).quantize(ince, ROUND_FLOOR))


def agirlik_metni(w):
    return ",".join(f"{x:g}" for x in w)


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
def veri_testleri(yol, p=None, gruplar=("A", "B"), liste=None, sapma=0.05):
    """liste: {kategori: {urun: fiyat}} — dosyayı üreten ürün listesi (verilmezse sözlükteki 25 ürün);
    sapma: birim_fiyat'ın liste fiyatından izinli sapması (sayı ya da {urun: sapma}). Sözlük kural 6, 7, 8."""
    p = {**VARSAYILAN, **(p or {})}
    urunler = liste or URUNLER
    liste_f = {u: f for d in urunler.values() for u, f in d.items()}
    urun_kat = {u: k for k, d in urunler.items() for u in d}
    degerler = {**DEGERLER, "kategori": list(urunler), "urun": list(liste_f)}
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
        fazla = {c: sorted(set(df[c]) - set(v)) for c, v in degerler.items() if set(df[c]) - set(v)}
        eksik = {c: sorted(set(v) - set(df[c])) for c, v in degerler.items() if set(v) - set(df[c])}
        out.append(sonuc("G2-TC-09", not fazla and not eksik, f"liste dışı: {fazla or 'yok'}; hiç geçmeyen: {eksik or 'yok'}"))
        uy = (df["urun"].map(urun_kat) != df["kategori"]).sum()
        out.append(sonuc("G2-TC-10", uy == 0, f"ürün–kategori uyuşmayan: {uy}"))
        lp = df["urun"].map(liste_f)
        sp = df["urun"].map(sapma) if isinstance(sapma, dict) else sapma
        dis = ((df["birim_fiyat"] < (lp * (1 - sp)).round(2) - 1e-9) | (df["birim_fiyat"] > (lp * (1 + sp)).round(2) + 1e-9)).sum()
        etiket = "ürün başı sapma" if isinstance(sapma, dict) else f"liste ±%{sapma * 100:g}"
        out.append(sonuc("G2-TC-11", dis == 0, f"{etiket} dışı: {dis}; birim_fiyat {df['birim_fiyat'].min():.2f} – {df['birim_fiyat'].max():.2f}"))
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

        # G2-TC-23: ağırlıklı ürün seçimi — N aynı, MD5 farklı, ürün payları w_i/Σw'ye uyuyor, A/B kuralları geçiyor
        r, y = calistir(["--urun_agirliklari", agirlik_metni(URUN_W)], tmp, "c8.csv")
        if r.returncode == 0:
            df = pd.read_csv(y)
            pay = df["urun"].value_counts(normalize=True)
            toplam_w = sum(URUN_W)
            sapma = [f"{u} %{pay.get(u, 0) * 100:.1f}≠%{w / toplam_w * 100:.1f}" for u, w in zip(LISTE, URUN_W)
                     if abs(pay.get(u, 0) - w / toplam_w) * 100 > URUN_TOL]
            ic = veri_testleri(y)
            kalan = [x[0] for x in ic if not x[1] and x[0] not in ("G2-TC-15",)]
            ok = len(df) == beklenen_n() and md5(y) != md5(veri_yolu) and not sapma and not kalan
            out.append(sonuc("G2-TC-23", ok, f"{len(df):,} satır (beklenen {beklenen_n():,}); MD5 farklı: {md5(y) != md5(veri_yolu)}; "
                                             f"±{URUN_TOL} puan dışı ürün: {', '.join(sapma) or 'yok'}; A/B kalan: {kalan or 'yok'}"))
        else:
            out.append(sonuc("G2-TC-23", False, f"çalışmadı: {r.stderr.strip()[-120:]}"))

        # G2-TC-24: boş ağırlık = varsayılan dosya; ağırlıklar normalize edilir (×2 aynı dosya)
        r1, a = calistir(["--urun_agirliklari", ""], tmp, "c9.csv")
        r2, b = calistir(["--urun_agirliklari", agirlik_metni([x * 2 for x in URUN_W])], tmp, "c10.csv")
        if r1.returncode == 0 and r2.returncode == 0 and r.returncode == 0:
            ok = md5(a) == md5(veri_yolu) and md5(b) == md5(y)
            out.append(sonuc("G2-TC-24", ok, f"boş → MD5 {md5(a)[:8]} (repo {md5(veri_yolu)[:8]}); ağırlık×2 → {md5(b)[:8]} (×1 {md5(y)[:8]})"))
        else:
            out.append(sonuc("G2-TC-24", False, f"çalışmadı: {(r1.stderr or r2.stderr).strip()[-120:]}"))
        out += liste_testleri(veri_yolu, tmp)
    return out


def yaz(klasor, ad, metin, kodlama="utf-8"):
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, ad)
    with open(yol, "wb") as f:
        f.write(metin.encode(kodlama))
    return yol


def pay_sapmasi(df, adlar, agirliklar):
    """Ürün paylarının w_i / Σw'den ±URUN_TOL puandan fazla saptığı ürünler."""
    pay = df["urun"].value_counts(normalize=True)
    return [f"{u} %{pay.get(u, 0) * 100:.1f}≠%{w / sum(agirliklar) * 100:.1f}" for u, w in zip(adlar, agirliklar)
            if abs(pay.get(u, 0) - w / sum(agirliklar)) * 100 > URUN_TOL]


# ------------------------------------------------------------------ C (Görev 3 eki, PR #102): urun_listesi ve fiyat_sapmasi
def liste_testleri(veri_yolu, tmp):
    out = []
    n = beklenen_n()
    UC = LISTE_BASLIK + "A,U1,100\nA,U2,200.50\nB,U3,300\n"   # 3 ürün, 2 kategori, ondalıklı fiyat
    uc = yaz(tmp, "uc.csv", UC)
    kat_uc, _ = liste_yukle(uc)

    # G2-TC-26: örnek liste ve açık varsayılan sapma, varsayılan dosyanın aynısını üretir
    r1, a = calistir(["--urun_listesi", ORNEK_LISTE], tmp, "l1.csv")
    r2, b = calistir(["--fiyat_sapmasi", "0.05"], tmp, "l2.csv")
    if r1.returncode == 0 and r2.returncode == 0:
        out.append(sonuc("G2-TC-26", md5(a) == md5(veri_yolu) == md5(b),
                         f"örnek liste → MD5 {md5(a)[:8]}; --fiyat_sapmasi 0.05 → {md5(b)[:8]} (repo {md5(veri_yolu)[:8]})"))
    else:
        out.append(sonuc("G2-TC-26", False, f"çalışmadı: {(r1.stderr or r2.stderr).strip()[-120:]}"))

    # G2-TC-27: web fiyatlı liste — satır sayısı aynı, kural 1–11 listeye göre, tekrarlanabilir, repodaki dosyayla aynı
    kat_web, _ = liste_yukle(WEB_LISTE)
    r1, a = calistir(["--urun_listesi", WEB_LISTE], tmp, "l3.csv")
    r2, b = calistir(["--urun_listesi", WEB_LISTE], tmp, "l4.csv")
    if r1.returncode == 0 and r2.returncode == 0 and os.path.exists(WEB_VERI):
        df = pd.read_csv(a)
        kalan = [x[0] for x in veri_testleri(a, liste=kat_web) if not x[1]]
        urun_sayisi = sum(len(d) for d in kat_web.values())
        ok = len(df) == n and df["urun"].nunique() == urun_sayisi and not kalan and md5(a) == md5(b) == md5(WEB_VERI)
        out.append(sonuc("G2-TC-27", ok, f"{len(df):,} satır (beklenen {n:,}); {df['urun'].nunique()} ürün, {df['kategori'].nunique()} kategori; "
                                         f"birim_fiyat {df['birim_fiyat'].min():.2f} – {df['birim_fiyat'].max():.2f}; A/B kalan: {kalan or 'yok'}; "
                                         f"MD5 1/2/repo: {md5(a)[:8]} / {md5(b)[:8]} / {md5(WEB_VERI)[:8]}"))
    else:
        out.append(sonuc("G2-TC-27", False, f"çalışmadı ya da {WEB_VERI} yok: {(r1.stderr or r2.stderr).strip()[-120:]}"))

    # G2-TC-28: 3 ürünlük küçük liste — satır sayısı değişmez, yalnız listedeki ürün ve kategoriler
    r, y = calistir(["--urun_listesi", uc], tmp, "l5.csv")
    if r.returncode == 0:
        df = pd.read_csv(y)
        kalan = [x[0] for x in veri_testleri(y, liste=kat_uc) if not x[1]]
        ok = len(df) == n and set(df["urun"]) == {"U1", "U2", "U3"} and set(df["kategori"]) == {"A", "B"} and not kalan
        out.append(sonuc("G2-TC-28", ok, f"{len(df):,} satır (beklenen {n:,}); ürünler {sorted(set(df['urun']))}, kategoriler {sorted(set(df['kategori']))}; "
                                         f"birim_fiyat {df['birim_fiyat'].min():.2f} – {df['birim_fiyat'].max():.2f}; A/B kalan: {kalan or 'yok'}"))
    else:
        out.append(sonuc("G2-TC-28", False, f"çalışmadı: {r.stderr.strip()[-120:]}"))

    # G2-TC-29: fiyat_sapmasi sınırları — 0 → tam liste fiyatı; 0.10 ve 0.5 → sınır içinde ve parametre gerçekten etkili
    notlar, hepsi = [], True
    for s in ("0", "0.1", "0.5"):
        r, y = calistir(["--fiyat_sapmasi", s], tmp, f"s{s}.csv")
        if r.returncode != 0:
            hepsi = False
            notlar.append(f"--fiyat_sapmasi {s} → çalışmadı")
            continue
        df = pd.read_csv(y)
        sinir = df["urun"].map(lambda u: fiyat_siniri(LISTE[u], float(s)))
        dis = ((df["birim_fiyat"] < sinir.map(lambda t: t[0]) - 1e-9) | (df["birim_fiyat"] > sinir.map(lambda t: t[1]) + 1e-9)).sum()
        oran = df["birim_fiyat"] / df["urun"].map(LISTE)
        etkili = (df["birim_fiyat"] == df["urun"].map(LISTE)).all() if s == "0" else ((oran > 1.05) | (oran < .95)).any()
        ok = len(df) == n and dis == 0 and bool(etkili)
        hepsi &= ok
        notlar.append(f"--fiyat_sapmasi {s} → {len(df):,} satır, sınır dışı {dis}, oran {oran.min():.3f} – {oran.max():.3f}")
    out.append(sonuc("G2-TC-29", hepsi, " · ".join(notlar)))

    # G2-TC-30: ürün başına fiyat_sapmasi genel değere üstün gelir; boş hücre genel değeri kullanır
    pp = yaz(tmp, "pp.csv", LISTE_SAPMALI + "A,U1,100,0\nA,U2,200,0.5\nB,U3,300,\n")
    r, y = calistir(["--urun_listesi", pp, "--fiyat_sapmasi", "0.1"], tmp, "l6.csv")
    if r.returncode == 0:
        df = pd.read_csv(y)
        u1, u2, u3 = (df[df["urun"] == u]["birim_fiyat"] for u in ("U1", "U2", "U3"))
        (l2, h2), (l3, h3) = fiyat_siniri(200, 0.5), fiyat_siniri(300, 0.1)
        ok1 = bool((u1 == 100).all())
        ok2 = bool(u2.between(l2, h2).all() and (u2 > 220).any() and (u2 < 180).any())
        ok3 = bool(u3.between(l3, h3).all() and ((u3 > 315) | (u3 < 285)).any())
        out.append(sonuc("G2-TC-30", len(df) == n and ok1 and ok2 and ok3,
                         f"U1 (sapma 0) {u1.min():.2f} – {u1.max():.2f}; U2 (0.5) {u2.min():.2f} – {u2.max():.2f}; U3 (boş → genel 0.1) {u3.min():.2f} – {u3.max():.2f}"))
    else:
        out.append(sonuc("G2-TC-30", False, f"çalışmadı: {r.stderr.strip()[-120:]}"))

    # G2-TC-31: urun_listesi × urun_agirliklari — ağırlık sayısı listedeki ürün sayısına bağlı
    r1, y1 = calistir(["--urun_listesi", uc, "--urun_agirliklari=1,2,3"], tmp, "l7.csv")
    r2, y2 = calistir(["--urun_listesi", uc, "--urun_agirliklari=" + ",".join(["1"] * 25)], os.path.join(tmp, "G2-TC-31-b"), "x.csv")
    r3, y3 = calistir(["--urun_listesi", uc, "--urun_agirliklari=0,0,1"], tmp, "l8.csv")
    if r1.returncode == 0 and r3.returncode == 0:
        sapma = pay_sapmasi(pd.read_csv(y1), ["U1", "U2", "U3"], [1, 2, 3])
        mesaj = (r2.stderr.strip().splitlines() or ["(mesaj yok)"])[-1]
        hata_ok = (r2.returncode == 1 and not os.path.exists(y2) and mesaj.startswith("Hata (ValueError)")
                   and "urun_agirliklari" in mesaj and "3" in mesaj and "25" in mesaj and "Traceback" not in r2.stderr)
        d3 = pd.read_csv(y3)
        sifir_ok = len(d3) == n and set(d3["urun"]) == {"U3"} and "A" not in set(d3["kategori"])
        out.append(sonuc("G2-TC-31", not sapma and hata_ok and sifir_ok,
                         f"1,2,3 → ±{URUN_TOL} puan dışı ürün: {', '.join(sapma) or 'yok'}; 25 değer → çıkış {r2.returncode}, dosya {'var' if os.path.exists(y2) else 'yok'}; "
                         f"0,0,1 → ürünler {sorted(set(d3['urun']))}, kategoriler {sorted(set(d3['kategori']))}"))
    else:
        out.append(sonuc("G2-TC-31", False, f"çalışmadı: {(r1.stderr or r3.stderr).strip()[-120:]}"))

    # G2-TC-32: BOM'lu UTF-8, farklı sütun sırası, Türkçe adlar; ürün sırası = dosya sırası (urun_agirliklari bu sırayı izler)
    bom = yaz(tmp, "bom.csv", "﻿urun,liste_fiyati,kategori\nŞapka,99.9,Giyim\nÇay,59.5,Gıda\n")
    kat_bom, _ = liste_yukle(bom)
    r1, y1 = calistir(["--urun_listesi", bom], tmp, "l9.csv")
    r2, y2 = calistir(["--urun_listesi", bom, "--urun_agirliklari=1,0"], tmp, "l10.csv")
    if r1.returncode == 0 and r2.returncode == 0:
        d1, d2 = pd.read_csv(y1), pd.read_csv(y2)
        kalan = [x[0] for x in veri_testleri(y1, liste=kat_bom) if not x[1]]
        ok = set(d1["urun"]) == {"Şapka", "Çay"} and set(d2["urun"]) == {"Şapka"} and not kalan
        out.append(sonuc("G2-TC-32", ok, f"ürünler {sorted(set(d1['urun']))}, kategoriler {sorted(set(d1['kategori']))}; A/B kalan: {kalan or 'yok'}; "
                                         f"--urun_agirliklari=1,0 → {sorted(set(d2['urun']))} (dosyadaki ilk ürün)"))
    else:
        out.append(sonuc("G2-TC-32", False, f"çalışmadı: {(r1.stderr or r2.stderr).strip()[-120:]}"))
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

        # G2-TC-25: geçersiz urun_agirliklari → ValueError, mesajda parametre adı, çıkış 1, dosya yok
        bir = ["1"] * 25
        gecersiz = {"3 değer": "1,2,3", "sayı değil": ",".join(["a"] + bir[1:]), "negatif": ",".join(["-1"] + bir[1:]),
                    "nan": ",".join(["nan"] + bir[1:]), "inf": ",".join(["inf"] + bir[1:]), "hepsi 0": ",".join(["0"] * 25)}
        notlar, hepsi = [], True
        for i, (ad, deger) in enumerate(gecersiz.items()):
            r, y = calistir([f"--urun_agirliklari={deger}"], os.path.join(tmp, f"G2-TC-25-{i}"), "x.csv")
            mesaj = (r.stderr.strip().splitlines() or ["(mesaj yok)"])[-1]
            ok = (r.returncode == 1 and not os.path.exists(y) and mesaj.startswith("Hata (ValueError)")
                  and "urun_agirliklari" in mesaj and "Traceback" not in r.stderr)
            hepsi &= ok
            notlar.append(f"{ad} → çıkış {r.returncode}, dosya {'var' if os.path.exists(y) else 'yok'}")
        out.append(sonuc("G2-TC-25", hepsi, " · ".join(notlar)))

        # G2-TC-25+: izinli uç değerler — çok büyük ağırlık taşmamalı (PR #95 incelemesi); ağırlığı 0 olan ürün hiç geçmemeli
        r1, y1 = calistir([f"--urun_agirliklari={','.join(['1e308'] * 25)}"], tmp, "buyuk.csv")
        r2, y2 = calistir([f"--urun_agirliklari={','.join(['0'] + bir[1:])}"], tmp, "sifir.csv")
        yok = r2.returncode == 0 and "Kablosuz Kulaklık" not in set(pd.read_csv(y2)["urun"])
        out.append(sonuc("G2-TC-25+", r1.returncode == 0 and yok,
                         f"25 × 1e308 → çıkış {r1.returncode}"
                         + (f" \"{(r1.stderr.strip().splitlines() or [''])[-1][:60]}\"" if r1.returncode else "")
                         + f"; 1. ürüne 0 → çıkış {r2.returncode}, Kablosuz Kulaklık dosyada yok: {yok}"))

        # G2-TC-33 ve G2-TC-34 (Görev 3 eki, PR #102): bozuk urun_listesi / fiyat_sapmasi → ValueError, mesajda parametre adı, çıkış 1, dosya yok
        S = LISTE_SAPMALI
        bozuk_liste = {
            "dosya yok": os.path.join(tmp, "yok.csv"),
            "UTF-8 değil": yaz(tmp, "b1.csv", LISTE_BASLIK + "Giyim,Tişört,249\n", "cp1254"),
            "eksik sütun": yaz(tmp, "b2.csv", "kategori,urun\nGiyim,Tisort\n"),
            "boş liste": yaz(tmp, "b3.csv", LISTE_BASLIK),
            "boş kategori": yaz(tmp, "b4.csv", LISTE_BASLIK + ",Tisort,249\n"),
            "boş ürün": yaz(tmp, "b5.csv", LISTE_BASLIK + "Giyim,,249\n"),
            "tekrarlı ürün": yaz(tmp, "b6.csv", LISTE_BASLIK + "Giyim,Tisort,249\nGiyim,Tisort,300\n"),
            "fiyat 0": yaz(tmp, "b7.csv", LISTE_BASLIK + "Giyim,Tisort,0\n"),
            "fiyat negatif": yaz(tmp, "b8.csv", LISTE_BASLIK + "Giyim,Tisort,-5\n"),
            "fiyat 3 ondalık": yaz(tmp, "b9.csv", LISTE_BASLIK + "Giyim,Tisort,249.999\n"),
            "fiyat sayı değil": yaz(tmp, "b10.csv", LISTE_BASLIK + "Giyim,Tisort,abc\n"),
            "ürün sapması 0.7": yaz(tmp, "b11.csv", S + "Giyim,Tisort,249,0.7\n"),
            "ürün sapması -0.1": yaz(tmp, "b12.csv", S + "Giyim,Tisort,249,-0.1\n"),
            "ürün sapması sayı değil": yaz(tmp, "b13.csv", S + "Giyim,Tisort,249,x\n"),
        }
        bozuk_sapma = {"0.6": "0.6", "-0.1": "-0.1", "sayı değil": "abc"}
        for tc, parametre, durumlar, arg in (("G2-TC-33", "urun_listesi", bozuk_liste, lambda d: ["--urun_listesi", d]),
                                             ("G2-TC-34", "fiyat_sapmasi", bozuk_sapma, lambda d: [f"--fiyat_sapmasi={d}"])):
            notlar, hepsi = [], True
            for i, (ad, deger) in enumerate(durumlar.items()):
                r, y = calistir(arg(deger), os.path.join(tmp, f"{tc}-{i}"), "x.csv")
                mesaj = (r.stderr.strip().splitlines() or ["(mesaj yok)"])[-1]
                ok = (r.returncode == 1 and not os.path.exists(y) and mesaj.startswith("Hata (ValueError)")
                      and parametre in mesaj and "Traceback" not in r.stderr)
                hepsi &= ok
                notlar.append(f"{ad} → çıkış {r.returncode}, dosya {'var' if os.path.exists(y) else 'yok'}")
            out.append(sonuc(tc, hepsi, " · ".join(notlar)))
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
