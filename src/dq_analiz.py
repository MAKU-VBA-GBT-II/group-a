"""DQ analizi — Görev 1 (#14): docs/analiz-g1.md için metrikleri hesaplar.

Kullanım:
    python src/dq_analiz.py                          # varsayılan: data/siparisler.csv
    python src/dq_analiz.py yol/dosya.csv
    python src/dq_analiz.py --cikti sonuc.md         # çıktıyı dosyaya da yazar

Metrikler (formüller docs/analiz-g1.md'de):
    M1 Toplam ciro                 = Σ toplam_tutar
    M2 Sipariş başına ortalama adet = Σ adet / sipariş sayısı
    M3 Kategori bazlı ciro         = kategoriye göre Σ toplam_tutar (+ pay %)
    M4 Haftalık ciro trendi        = haftaya göre Σ toplam_tutar
    M5 Top-3 ürün                  = ürüne göre Σ toplam_tutar, büyükten küçüğe ilk 3

Çıktı Markdown'dır; tablolar docs/analiz-g1.md'deki ilgili bölümlere aktarılır.
Aynı veri dosyası → aynı çıktı (rastgelelik yok).
"""
import argparse
import subprocess

import pandas as pd


def tl(x):
    """1234567.8 → '1.234.567,80 TL'"""
    return f"{x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " TL"


def yuzde(x):
    """24.43 → '%24,4'"""
    return f"%{x:.1f}".replace(".", ",")


def veri_commit(yol):
    """Veri dosyasını son değiştiren commit'in kısa hash'i (git yoksa '?')."""
    try:
        cikti = subprocess.run(["git", "log", "-1", "--format=%h", "--", yol],
                               capture_output=True, text=True, check=True).stdout.strip()
        return cikti or "commit'lenmemiş"
    except (OSError, subprocess.CalledProcessError):
        return "?"


def tablo(df):
    """DataFrame'i Markdown tablosuna çevirir (tabulate gerektirmez)."""
    satirlar = ["| " + " | ".join(df.columns) + " |",
                "|" + "---|" * len(df.columns)]
    for _, r in df.iterrows():
        satirlar.append("| " + " | ".join(str(v) for v in r) + " |")
    return "\n".join(satirlar)


def analiz(yol):
    df = pd.read_csv(yol, parse_dates=["siparis_tarihi"])
    ciro = df["toplam_tutar"].sum()
    out = []

    out.append(f"**Veri:** `{yol}` · commit `{veri_commit(yol)}` · {len(df)} satır · "
               f"{df['siparis_tarihi'].min():%Y-%m-%d} – {df['siparis_tarihi'].max():%Y-%m-%d}")

    # M1
    out.append(f"\n### M1 — Toplam ciro\n\n**{tl(ciro)}** ({len(df)} sipariş)")

    # M2
    ort = f"{df['adet'].mean():.2f}".replace(".", ",")
    out.append(f"\n### M2 — Sipariş başına ortalama adet\n\n"
               f"**{ort} adet** "
               f"(medyan {df['adet'].median():.0f}, toplam {int(df['adet'].sum())} adet)")

    # M3
    k = (df.groupby("kategori")
           .agg(siparis=("siparis_id", "count"), ciro=("toplam_tutar", "sum"))
           .sort_values("ciro", ascending=False))
    k["pay"] = k["ciro"] / ciro * 100
    m3 = pd.DataFrame({
        "Kategori": k.index,
        "Sipariş": k["siparis"].values,
        "Ciro": [tl(v) for v in k["ciro"]],
        "Pay": [yuzde(v) for v in k["pay"]],
    })
    out.append("\n### M3 — Kategori bazlı ciro\n\n" + tablo(m3))

    # M4 — haftalar pazartesi başlar
    h = (df.set_index("siparis_tarihi")["toplam_tutar"]
           .resample("W-MON", label="left", closed="left").agg(["count", "sum"]))
    m4 = pd.DataFrame({
        "Hafta başı": [d.strftime("%Y-%m-%d") for d in h.index],
        "Sipariş": h["count"].values,
        "Ciro": [tl(v) for v in h["sum"]],
    })
    # İlk/son hafta verinin dışına taşıyorsa kısmi haftadır; en düşük haftayı yanıltmasın
    ilk, son = df["siparis_tarihi"].min(), df["siparis_tarihi"].max()
    kismi = [d for d in (h.index[0], h.index[-1])
             if d < ilk.normalize() or d + pd.Timedelta(days=6) > son.normalize()]
    tam = h.drop(index=kismi) if len(h) > len(kismi) else h
    en_iyi, en_kotu = tam["sum"].idxmax(), tam["sum"].idxmin()
    out.append("\n### M4 — Haftalık ciro trendi\n\n" + tablo(m4) +
               f"\n\nHaftalık ortalama: {tl(h['sum'].mean())} · "
               f"en yüksek: {en_iyi:%Y-%m-%d} haftası ({tl(tam['sum'].max())}) · "
               f"en düşük: {en_kotu:%Y-%m-%d} haftası ({tl(tam['sum'].min())})" +
               (f"\n\nNot: {', '.join(f'{d:%Y-%m-%d}' for d in kismi)} haftası kısmi "
                "(7 günün tamamı veride yok); en yüksek/en düşük hesabına katılmadı."
                if kismi else ""))

    # M5
    if "urun" in df.columns:
        u = (df.groupby(["urun", "kategori"])["toplam_tutar"].sum()
               .sort_values(ascending=False).head(3).reset_index())
        m5 = pd.DataFrame({
            "Sıra": range(1, len(u) + 1),
            "Ürün": u["urun"],
            "Kategori": u["kategori"],
            "Ciro": [tl(v) for v in u["toplam_tutar"]],
            "Pay": [yuzde(v / ciro * 100) for v in u["toplam_tutar"]],
        })
        out.append("\n### M5 — Ciroya en çok katkı veren 3 ürün\n\n" + tablo(m5) +
                   f"\n\nTop-3'ün toplam payı: {yuzde(u['toplam_tutar'].sum() / ciro * 100)}")
    else:
        out.append("\n### M5 — Ciroya en çok katkı veren 3 ürün\n\n"
                   "⚠️ Veride `urun` sütunu yok; Top-3 ürün hesaplanamadı (bkz. #13).")

    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dosya", nargs="?", default="data/siparisler.csv")
    p.add_argument("--cikti", help="Markdown çıktısının yazılacağı dosya")
    a = p.parse_args()

    sonuc = analiz(a.dosya)
    print(sonuc)
    if a.cikti:
        with open(a.cikti, "w", encoding="utf-8") as f:
            f.write(sonuc + "\n")


if __name__ == "__main__":
    main()
