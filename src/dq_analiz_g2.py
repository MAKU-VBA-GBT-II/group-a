#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — DQ: Görev 2 metrik analizi (M1–M6)

docs/veri-sozlugu.md'deki metrik tanımlarını data/siparisler-g2.csv üzerinde hesaplar ve
Markdown tabloları olarak yazdırır. Çıktı docs/analiz-g2.md'ye aktarılır (#62).

Kullanım (depo kökünde):
    python src/dq_analiz_g2.py                      # M1–M6 tabloları
    python src/dq_analiz_g2.py --ek                 # + yorum ve bulgular için ek istatistikler
    python src/dq_analiz_g2.py --ek --cikti analiz-cikti-g2.md
    python src/dq_analiz_g2.py yol/dosya.csv        # başka bir simülasyon çıktısı

Skill: skills/dq-analiz/SKILL.md · Şema: docs/veri-sozlugu.md (#60) · Issue: #62
"""

import argparse
import sys

import pandas as pd

VERI = "data/siparisler-g2.csv"
KAMPANYA_DONEMLERI = [("2026-03-09", "2026-03-15"), ("2026-05-11", "2026-05-17")]  # sözlük varsayılanı
TESLIM = "Teslim Edildi"
TOP_N = 5

LISTE_FIYATI = {
    "Kablosuz Kulaklık": 1299, "Bluetooth Hoparlör": 899, "Powerbank": 599, "Akıllı Saat": 3499, "Klavye": 749,
    "Tişört": 249, "Kot Pantolon": 699, "Sweatshirt": 549, "Spor Ayakkabı": 1899, "Mont": 2299,
    "Kahve Makinesi": 2999, "Battaniye": 449, "Masa Lambası": 399, "Saklama Kabı Seti": 299, "Halı": 1799,
    "Nemlendirici": 189, "Şampuan": 129, "Parfüm": 999, "Güneş Kremi": 279, "Ruj": 159,
    "Roman": 149, "Deneme": 129, "Ders Kitabı": 349, "Çocuk Kitabı": 99, "Şiir Kitabı": 119,
}


# --------------------------------------------------------------------------- biçim yardımcıları
def tl(x, ondalik=2):
    """1234567.891 -> '1.234.567,89 TL' (Türkçe biçim)."""
    s = f"{x:,.{ondalik}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " TL"


def sayi(x, ondalik=0):
    s = f"{x:,.{ondalik}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def yuzde(x, ondalik=1):
    """12.34 -> '%12,3'; -20.8 -> '-%20,8' (Türkçe yazım)."""
    return ("-" if x < 0 else "") + "%" + sayi(abs(x), ondalik)


def tablo(basliklar, satirlar):
    out = ["| " + " | ".join(basliklar) + " |", "|" + "|".join("---" for _ in basliklar) + "|"]
    out += ["| " + " | ".join(str(h) for h in s) + " |" for s in satirlar]
    return "\n".join(out)


# --------------------------------------------------------------------------- veri
def oku(yol):
    df = pd.read_csv(yol)
    if df.empty:
        raise ValueError(f"{yol} boş; analiz yapılamaz")
    gerekli = {"siparis_tarihi", "musteri_id", "kanal", "kategori", "urun", "adet",
               "toplam_tutar", "kampanya", "indirim_orani", "durum"}
    eksik = gerekli - set(df.columns)
    if eksik:
        raise ValueError(f"{yol} sözlükteki sütunları içermiyor, eksik: {sorted(eksik)}")
    df["siparis_tarihi"] = pd.to_datetime(df["siparis_tarihi"], format="%Y-%m-%d")
    return df


def haftalik(t):
    return t.set_index("siparis_tarihi").resample("W-MON", label="left", closed="left")["toplam_tutar"]


def kampanya_haftasi_mi(hafta_basi):
    son = hafta_basi + pd.Timedelta(days=6)
    return any(pd.Timestamp(a) <= son and hafta_basi <= pd.Timestamp(b) for a, b in KAMPANYA_DONEMLERI)


# --------------------------------------------------------------------------- metrikler
def metrikler(df):
    t = df[df["durum"] == TESLIM]
    out = []
    m1 = t["toplam_tutar"].sum()
    out.append("### M1 — Toplam net ciro\n")
    out.append(tablo(["Ölçü", "Değer"], [
        ["Net ciro (teslim edilen)", tl(m1)],
        ["Teslim edilen sipariş", sayi(len(t))],
        ["Tüm siparişler", sayi(len(df))],
    ]))

    out.append("\n### M2 — Ortalama sepet tutarı\n")
    out.append(tablo(["Ölçü", "Değer"], [
        ["Ortalama sepet (M1 / teslim edilen sipariş)", tl(t["toplam_tutar"].mean())],
        ["Medyan sepet", tl(t["toplam_tutar"].median())],
    ]))

    h = haftalik(t)
    hs = h.sum()
    adet = h.count()
    out.append("\n### M3 — Haftalık net ciro trendi (W-MON)\n")
    satirlar = []
    for hb, v in hs.items():
        satirlar.append([hb.strftime("%Y-%m-%d"), sayi(adet[hb]), tl(v), "✓" if kampanya_haftasi_mi(hb) else ""])
    out.append(tablo(["Hafta başı", "Teslim edilen sipariş", "Net ciro", "Kampanya"], satirlar))
    out.append(f"\nHafta sayısı: {len(hs)} · Haftalık ortalama: {tl(hs.mean())} · "
               f"En yüksek: {hs.idxmax():%Y-%m-%d} haftası ({tl(hs.max())}) · "
               f"En düşük: {hs.idxmin():%Y-%m-%d} haftası ({tl(hs.min())})")

    k = t.groupby("kanal")["toplam_tutar"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    out.append("\n### M4 — Kanal bazlı net ciro ve payı\n")
    out.append(tablo(["Kanal", "Teslim edilen sipariş", "Net ciro", "Pay"], [
        [kn, sayi(r["count"]), tl(r["sum"]), yuzde(r["sum"] / m1 * 100)] for kn, r in k.iterrows()
    ]))

    u = t.groupby("urun").agg(ciro=("toplam_tutar", "sum"), siparis=("toplam_tutar", "count"))
    u = u.sort_values("ciro", ascending=False).head(TOP_N)
    out.append(f"\n### M5 — Ciroda ilk {TOP_N} ürün\n")
    out.append(tablo(["Sıra", "Ürün", "Liste fiyatı", "Teslim edilen sipariş", "Net ciro", "Pay"], [
        [i + 1, ur, tl(LISTE_FIYATI.get(ur, float("nan")), 0), sayi(r["siparis"]), tl(r["ciro"]), yuzde(r["ciro"] / m1 * 100)]
        for i, (ur, r) in enumerate(u.iterrows())
    ]))
    out.append(f"\nİlk {TOP_N} ürünün toplam payı: {yuzde(u['ciro'].sum() / m1 * 100)}")

    kayip = df["durum"] != TESLIM
    kk = df.assign(kayip=kayip).groupby("kategori")["kayip"].agg(["mean", "sum", "count"]).sort_values("mean", ascending=False)
    out.append("\n### M6 (ek) — İade + iptal oranı\n")
    out.append(f"Genel: {yuzde(kayip.mean() * 100)} ({sayi(kayip.sum())} / {sayi(len(df))}) · "
               f"İade {yuzde((df['durum'] == 'İade').mean() * 100)} · İptal {yuzde((df['durum'] == 'İptal').mean() * 100)}\n")
    out.append(tablo(["Kategori", "Sipariş", "İade + iptal", "Oran"], [
        [kt, sayi(r["count"]), sayi(r["sum"]), yuzde(r["mean"] * 100)] for kt, r in kk.iterrows()
    ]))
    return "\n".join(out)


def ek_istatistikler(df):
    t = df[df["durum"] == TESLIM]
    out = ["\n## Ek istatistikler (yorum ve bulgular için)\n"]
    x = t["toplam_tutar"]
    out.append(f"- Sepet tutarı: ortalama {tl(x.mean())} · medyan {tl(x.median())} · %95 dilimi {tl(x.quantile(0.95))} · "
               f"en yüksek {tl(x.max())} · 5.000 TL üstü sipariş {yuzde((x > 5000).mean() * 100)}")

    hs = haftalik(t).sum()
    kamp = pd.Series({hb: kampanya_haftasi_mi(hb) for hb in hs.index})
    normal = hs[~kamp]
    out.append(f"- Normal hafta ortalaması {tl(normal.mean())} (n={len(normal)}) · kampanya haftaları: "
               + ", ".join(f"{hb:%Y-%m-%d} {tl(v)} ({yuzde((v / normal.mean() - 1) * 100)})" for hb, v in hs[kamp].items()))
    out.append(f"- Haftalık net ciro değişim katsayısı (std/ortalama): {yuzde(hs.std() / hs.mean() * 100)}")
    for hb in hs[kamp].index:
        sonraki = hb + pd.Timedelta(days=7)
        if sonraki in hs.index:
            out.append(f"- Kampanya sonrası hafta {sonraki:%Y-%m-%d}: {tl(hs[sonraki])} ({yuzde((hs[sonraki] / normal.mean() - 1) * 100)} normal ortalamaya göre)")

    tk = t[t["kampanya"] == 1]
    tn = t[t["kampanya"] == 0]
    out.append(f"- Sipariş başına net tutar: kampanyalı {tl(tk['toplam_tutar'].mean())} (n={sayi(len(tk))}, ort. indirim {yuzde(tk['indirim_orani'].mean() * 100)}) · "
               f"kampanyasız {tl(tn['toplam_tutar'].mean())}")
    brut = (tk["toplam_tutar"] / (1 - tk["indirim_orani"])).sum()
    out.append(f"- Kampanyalı siparişlerde indirimle verilen tutar: {tl(brut - tk['toplam_tutar'].sum())} (indirimsiz {tl(brut)} → net {tl(tk['toplam_tutar'].sum())})")

    g = t.groupby(t["siparis_tarihi"].dt.dayofweek >= 5)["toplam_tutar"].sum() / t.groupby(t["siparis_tarihi"].dt.dayofweek >= 5)["siparis_tarihi"].nunique()
    out.append(f"- Günlük ortalama net ciro: hafta içi {tl(g.get(False, 0))} · hafta sonu {tl(g.get(True, 0))}")

    us = t.groupby("urun").size()
    out.append(f"- Ürün başına teslim edilen sipariş: en az {sayi(us.min())} ({us.idxmin()}) · en çok {sayi(us.max())} ({us.idxmax()}) — ürünler eşit olasılıkla seçiliyor")
    uc = t.groupby("urun")["toplam_tutar"].sum()
    sira_c = uc.rank(ascending=False)
    sira_f = pd.Series(LISTE_FIYATI).rank(ascending=False).reindex(uc.index)
    out.append(f"- Ciro sırası ile liste fiyatı sırası arasındaki Spearman ilişkisi: {sayi(sira_c.corr(sira_f), 2)}")

    s = df.sort_values(["siparis_tarihi", "siparis_id"]) if "siparis_id" in df else df.sort_values("siparis_tarihi")
    tekrar = s.duplicated("musteri_id")
    hft = s.assign(tekrar=tekrar).set_index("siparis_tarihi").resample("W-MON", label="left", closed="left")["tekrar"].mean()
    tt = t.assign(tekrar=tekrar.reindex(t.index))
    out.append(f"- Müşteri: {sayi(df['musteri_id'].nunique())} farklı müşteri · 'tekrar' sipariş payı {yuzde(tekrar.mean() * 100)} · "
               f"haftalık tekrar payı ilk hafta {yuzde(hft.iloc[0] * 100)}, son hafta {yuzde(hft.iloc[-1] * 100)}")
    out.append(f"- Ortalama sepet: yeni müşteri {tl(tt.loc[~tt['tekrar'], 'toplam_tutar'].mean())} · tekrar {tl(tt.loc[tt['tekrar'], 'toplam_tutar'].mean())}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Görev 2 metrik analizi (docs/veri-sozlugu.md → Metrikler)")
    ap.add_argument("dosya", nargs="?", default=VERI)
    ap.add_argument("--ek", action="store_true", help="yorum/bulgular için ek istatistikler")
    ap.add_argument("--cikti", help="çıktıyı bu dosyaya da yaz")
    a = ap.parse_args(argv)
    df = oku(a.dosya)
    metin = f"Veri: {a.dosya} · {sayi(len(df))} satır · {df['siparis_tarihi'].min():%Y-%m-%d} … {df['siparis_tarihi'].max():%Y-%m-%d}\n\n" + metrikler(df)
    if a.ek:
        metin += "\n" + ek_istatistikler(df)
    print(metin)
    if a.cikti:
        with open(a.cikti, "w", encoding="utf-8") as f:
            f.write(metin + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError) as hata:
        print(f"Hata: {hata}", file=sys.stderr)
        sys.exit(1)
