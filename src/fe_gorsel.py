"""FE görselleştirme — Görev 1 (#15): data/siparisler.csv'den 2 PNG grafik üretir.

Kullanım:
    python src/fe_gorsel.py                      # varsayılan: data/siparisler.csv → visuals/
    python src/fe_gorsel.py yol/dosya.csv
    python src/fe_gorsel.py --taslak             # yalnızca grafik taslaklarını üretir (veri kullanmaz)

Grafikler (metrik tanımları docs/analiz-g1.md ile aynı):
    visuals/haftalik-ciro.png       Zaman serisi — M4 Haftalık ciro trendi
                                    (pazartesi başlangıçlı hafta, Σ toplam_tutar, bin TL)
    visuals/kategori-ciro-payi.png  Kırılım — M3 Kategori bazlı ciro (bin TL + toplam ciro içindeki pay %)

Taslak modu (--taslak) visuals/taslak/ altına eksen, başlık ve gösterilecek metriği
gösteren elle çizim görünümlü şablonlar üretir; gerçek veri içermez.
Aynı veri dosyası → aynı PNG (rastgelelik yok).
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import pandas as pd  # noqa: E402

VERI = "data/siparisler.csv"
CIKTI_KLASORU = "visuals"
ZAMAN_SERISI = "haftalik-ciro.png"
KIRILIM = "kategori-ciro-payi.png"
DPI = 150

RENK_ANA = "#2a6f97"      # çizgi / çubuk
RENK_VURGU = "#c8553d"    # en yüksek iki kategori, kısmi hafta notu
RENK_GRI = "#8d99ae"      # ortalama çizgisi, ikincil kategoriler
KAYNAK = "Kaynak: data/siparisler.csv (simülasyon, seed 42) · Sepetix Analitik — Grup A"


def bin_tl(x, _pos=None):
    """12345.6 → '12' (bin TL, Türkçe binlik ayırıcı)."""
    return f"{x / 1000:,.0f}".replace(",", ".")


def tl(x):
    """1234567.8 → '1.234.568 TL'"""
    return f"{x:,.0f}".replace(",", ".") + " TL"


def yuzde(x):
    return f"%{x:.1f}".replace(".", ",")


def stil():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",   # Türkçe karakterleri (ş, ğ, İ) destekler
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.titlelocation": "left",
    })


def haftalik(df):
    """M4: pazartesi başlangıçlı haftalara göre ciro (dq_analiz.py ile aynı kural)."""
    h = (df.set_index("siparis_tarihi")["toplam_tutar"]
           .resample("W-MON", label="left", closed="left").agg(["count", "sum"]))
    ilk, son = df["siparis_tarihi"].min(), df["siparis_tarihi"].max()
    kismi = [d for d in (h.index[0], h.index[-1])
             if d < ilk.normalize() or d + pd.Timedelta(days=6) > son.normalize()]
    return h, kismi


def zaman_serisi(df, yol):
    h, kismi = haftalik(df)
    tam = h.drop(index=kismi)
    ort = h["sum"].mean()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(h.index, h["sum"], color=RENK_ANA, lw=2, marker="o", ms=4, label="Haftalık ciro")
    if kismi:
        ax.plot(kismi, h.loc[kismi, "sum"], ls="none", marker="o", ms=8, mfc="white",
                mec=RENK_VURGU, mew=2, label="Kısmi hafta (7 günün tamamı veride yok)")
    ax.axhline(ort, color=RENK_GRI, ls="--", lw=1.2,
               label=f"Ortalama (40 hafta): {tl(ort)}")

    en_iyi = tam["sum"].idxmax()
    ax.annotate(f"En yüksek: {en_iyi:%d.%m.%Y} haftası\n{tl(tam['sum'].max())}",
                xy=(en_iyi, tam["sum"].max()), xytext=(15, 0), textcoords="offset points",
                fontsize=9, va="center", color=RENK_ANA)

    ax.set_title("Haftalık ciro trendi — Ocak–Eylül 2026")
    ax.set_xlabel("Hafta (pazartesi başlangıçlı)")
    ax.set_ylabel("Ciro (bin TL)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(bin_tl))
    ax.set_ylim(0, h["sum"].max() * 1.15)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m.%Y"))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    fig.text(0.01, 0.01, f"{KAYNAK} · {len(h)} hafta, {len(df)} sipariş · Metrik: M4",
             fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)


def kirilim(df, yol):
    ciro = df["toplam_tutar"].sum()
    k = df.groupby("kategori")["toplam_tutar"].sum().sort_values()
    pay = k / ciro * 100
    renkler = [RENK_VURGU if i >= len(k) - 2 else RENK_ANA for i in range(len(k))]

    fig, ax = plt.subplots(figsize=(9, 5))
    cubuk = ax.barh(k.index, k.values, color=renkler, height=0.6)
    for b, v, p in zip(cubuk, k.values, pay.values):
        ax.text(b.get_width() + ciro * 0.006, b.get_y() + b.get_height() / 2,
                f"{bin_tl(v)} bin TL · {yuzde(p)}", va="center", fontsize=9)

    ax.set_title("Kategori bazlı ciro ve toplam içindeki payı")
    ax.set_xlabel("Ciro (bin TL)")
    ax.set_ylabel("Kategori")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(bin_tl))
    ax.set_xlim(0, k.max() * 1.3)
    ax.grid(axis="x", alpha=0.3)
    ilk_iki = pay.iloc[-2:].sum()
    fig.text(0.01, 0.01, f"{KAYNAK} · Toplam ciro {tl(ciro)} · "
             f"Turuncu: ilk iki kategori ({yuzde(ilk_iki)}) · Metrik: M3",
             fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)


def taslaklar(klasor):
    """Veri kullanmadan, elle çizim görünümlü grafik taslakları üretir."""
    os.makedirs(klasor, exist_ok=True)
    with plt.xkcd(scale=0.8, length=120, randomness=2):
        plt.rcParams["font.family"] = "DejaVu Sans"
        # 1) Zaman serisi
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = list(range(40))
        y = [60 + 25 * ((i * 7) % 5) / 4 for i in x]
        ax.plot(x, y, color="black", lw=1.5)
        ax.plot([0, 39], [y[0], y[39]], "o", mfc="white", mec="black", ms=8)
        ax.axhline(sum(y) / len(y), ls="--", color="gray")
        ax.set_title("TASLAK 1 — Haftalık ciro trendi (zaman serisi)")
        ax.set_xlabel("x: Hafta (pazartesi başlangıçlı, Oca–Eyl 2026)")
        ax.set_ylabel("y: Ciro (bin TL)")
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(1, 95, "Metrik: M4 = haftaya göre Σ toplam_tutar\n"
                       "• çizgi + nokta: her hafta\n• kesikli çizgi: ortalama\n"
                       "• boş daire: kısmi ilk/son hafta\n• en yüksek hafta etiketlenecek",
                fontsize=8, va="top")
        ax.set_ylim(40, 100)
        fig.tight_layout()
        fig.savefig(os.path.join(klasor, "taslak-1-haftalik-ciro.png"), dpi=110)
        plt.close(fig)

        # 2) Kırılım
        fig, ax = plt.subplots(figsize=(9, 4.5))
        kat = ["Kategori E", "Kategori D", "Kategori C", "Kategori B", "Kategori A"]
        ax.barh(kat, [1, 3, 5, 9, 10], color=["white"] * 3 + ["lightgray"] * 2,
                edgecolor="black")
        for i, v in enumerate([1, 3, 5, 9, 10]):
            ax.text(v + 0.2, i, "… bin TL · %…", va="center", fontsize=8)
        ax.set_title("TASLAK 2 — Kategori bazlı ciro payı (kırılım)")
        ax.set_xlabel("x: Ciro (bin TL)")
        ax.set_ylabel("y: Kategori (5 kategori)")
        ax.set_xticks([])
        ax.set_xlim(0, 14)
        ax.text(7.5, 0.3, "Metrik: M3 = kategoriye göre Σ toplam_tutar\n"
                          "+ toplam ciro içindeki pay (%)\n"
                          "• büyükten küçüğe yatay çubuk\n• ilk iki kategori vurgulu",
                fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(klasor, "taslak-2-kategori-ciro-payi.png"), dpi=110)
        plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dosya", nargs="?", default=VERI)
    p.add_argument("--klasor", default=CIKTI_KLASORU, help="PNG'lerin yazılacağı klasör")
    p.add_argument("--taslak", action="store_true", help="yalnızca taslak şablonları üret")
    a = p.parse_args()

    if a.taslak:
        taslaklar(os.path.join(a.klasor, "taslak"))
        print(f"Taslaklar yazıldı: {a.klasor}/taslak/")
        return

    stil()
    df = pd.read_csv(a.dosya, parse_dates=["siparis_tarihi"])
    os.makedirs(a.klasor, exist_ok=True)
    zs, kr = os.path.join(a.klasor, ZAMAN_SERISI), os.path.join(a.klasor, KIRILIM)
    zaman_serisi(df, zs)
    kirilim(df, kr)
    print(f"Yazıldı: {zs}\nYazıldı: {kr}")


if __name__ == "__main__":
    main()
