"""FE görselleştirme — Görev 2 (#63): data/siparisler-g2.csv'den 3 PNG grafik üretir.

Kullanım:
    python src/fe_gorsel.py                      # varsayılan: data/siparisler-g2.csv → visuals/
    python src/fe_gorsel.py yol/dosya.csv
    python src/fe_gorsel.py --klasor cikti/      # PNG'lerin yazılacağı klasör

Grafikler (metrik tanımları docs/veri-sozlugu.md ile aynı):
    visuals/haftalik-net-ciro.png         Zaman serisi — M3 Haftalık net ciro trendi
                                          (pazartesi başlangıçlı hafta, Σ toplam_tutar, bin TL)
    visuals/kanal-ciro-payi.png           Kırılım — M4 Kanal bazlı net ciro (bin TL + pay %)
    visuals/siparis-tutari-dagilimi.png   Dağılım — toplam_tutar histogramı, M2 dikey çizgiyle

Para metrikleri yalnızca durum == "Teslim Edildi" satırlarından hesaplanır (şema kuralı).
Aynı veri dosyası → aynı PNG (rastgelelik yok).
"""
import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

VERI = "data/siparisler-g2.csv"
CIKTI_KLASORU = "visuals"
ZAMAN_SERISI = "haftalik-net-ciro.png"
KIRILIM = "kanal-ciro-payi.png"
DAGILIM = "siparis-tutari-dagilimi.png"
DPI = 150

# Şema alan adları (docs/veri-sozlugu.md) — şema değişirse yalnızca burası güncellenir.
SUTUN_TARIH = "siparis_tarihi"
SUTUN_TUTAR = "toplam_tutar"
SUTUN_KANAL = "kanal"
SUTUN_DURUM = "durum"
GEREKLI_SUTUNLAR = (SUTUN_TARIH, SUTUN_TUTAR, SUTUN_KANAL, SUTUN_DURUM)
DURUM_TESLIM = "Teslim Edildi"

# Kampanya dönemleri — şemadaki kampanya_donemleri varsayılanı (BAŞ, SON, dahil)
KAMPANYA_DONEMLERI = (("2026-03-09", "2026-03-15"), ("2026-05-11", "2026-05-17"))

# Histogram: kuyruk uzun (en yüksek sipariş ~18.000 TL), son kova taşma kovasıdır.
HIST_UST_SINIR = 7000
HIST_KOVA_GENISLIGI = 250

RENK_ANA = "#2a6f97"      # çizgi / çubuk
RENK_VURGU = "#c8553d"    # kampanya bandı, ortalama çizgisi
RENK_GRI = "#8d99ae"      # ikincil çubuk, medyan çizgisi
AYLAR = ("Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem",
         "Ağu", "Eyl", "Eki", "Kas", "Ara")
KAYNAK = "Kaynak: data/siparisler-g2.csv (simülasyon) · durum = Teslim Edildi · Sepetix Analitik — Grup A"


def bin_tl(x, _pos=None):
    """1234567.8 → '1.235' (bin TL, Türkçe binlik ayırıcı)."""
    return f"{x / 1000:,.0f}".replace(",", ".")


def tl(x):
    """1234567.8 → '1.234.568 TL'"""
    return f"{x:,.0f}".replace(",", ".") + " TL"


def yuzde(x):
    """44.28 → '%44,3'"""
    return f"%{x:.1f}".replace(".", ",")


def ay_etiketi(x, _pos=None):
    """Tarih sayısını 'Oca' gibi tek biçimli bir ay adına çevirir (#29: biçim karıştırma)."""
    return AYLAR[mdates.num2date(x).month - 1]


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


def veri_oku(yol):
    """CSV'yi okur ve teslim edilen siparişleri ayırır; sorun varsa ValueError verir."""
    if not os.path.exists(yol):
        raise ValueError(
            f"Veri dosyası bulunamadı: {yol}\n"
            f"BE'nin 'Veri hazır' yorumundaki dosyayı çekmek için 'git pull' çalıştır."
        )
    try:
        df = pd.read_csv(yol, parse_dates=[SUTUN_TARIH])
    except ValueError as hata:
        raise ValueError(f"'{yol}' okunamadı — {SUTUN_TARIH} alanı tarih biçiminde değil: {hata}")

    eksik = [s for s in GEREKLI_SUTUNLAR if s not in df.columns]
    if eksik:
        raise ValueError(
            f"'{yol}' şemaya uymuyor. Eksik sütun(lar): {', '.join(eksik)}\n"
            f"Beklenen sütunlar docs/veri-sozlugu.md içinde tanımlı."
        )

    teslim = df[df[SUTUN_DURUM] == DURUM_TESLIM]
    if teslim.empty:
        raise ValueError(
            f"'{yol}' içinde durum == \"{DURUM_TESLIM}\" olan satır yok; "
            f"para metrikleri hesaplanamaz."
        )
    return df, teslim


def haftalik(teslim):
    """M3: pazartesi başlangıçlı haftalara göre net ciro (dq_analiz ile aynı kural)."""
    return (teslim.set_index(SUTUN_TARIH)[SUTUN_TUTAR]
            .resample("W-MON", label="left", closed="left").sum())


def zaman_serisi(teslim, yol):
    """M3 — haftalık net ciro trendi; kampanya haftaları bant olarak işaretli."""
    h = haftalik(teslim)
    ort = h.mean()

    fig, ax = plt.subplots(figsize=(11, 5))

    # Kampanya haftalarının tamamını kapsayan bant (DQ notu #63)
    for i, (bas, son) in enumerate(KAMPANYA_DONEMLERI):
        ax.axvspan(pd.Timestamp(bas), pd.Timestamp(son) + pd.Timedelta(days=1),
                   color=RENK_VURGU, alpha=0.14,
                   label="Kampanya haftası" if i == 0 else None)

    ax.plot(h.index, h.values, color=RENK_ANA, lw=2, marker="o", ms=4,
            label="Haftalık net ciro")

    # Kampanya haftasının kendi noktası da işaretlenir: bandın sol kenarındaki
    # nokta o haftaya aittir, vurgu olmadan hangi hafta olduğu okunmuyor.
    kampanya_baslari = [pd.Timestamp(bas) for bas, _ in KAMPANYA_DONEMLERI]
    kampanya_noktalari = h[h.index.isin(kampanya_baslari)]
    if not kampanya_noktalari.empty:
        ax.plot(kampanya_noktalari.index, kampanya_noktalari.values, ls="none",
                marker="o", ms=9, mfc="white", mec=RENK_VURGU, mew=2.5, zorder=5)

    ax.axhline(ort, color=RENK_GRI, ls="--", lw=1.2,
               label=f"Ortalama ({len(h)} hafta): {tl(ort)}")

    ax.set_title("Haftalık net ciro trendi — Ocak–Temmuz 2026")
    ax.set_xlabel("Hafta (pazartesi başlangıçlı)")
    ax.set_ylabel("Net ciro (bin TL)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(bin_tl))
    ax.set_ylim(0, h.max() * 1.15)          # y ekseni 0'dan başlar (DQ notu)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(ay_etiketi))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="lower right", frameon=False, fontsize=9, ncol=3)
    fig.text(0.01, 0.01, f"{KAYNAK} · {len(h)} hafta, {len(teslim)} sipariş · Metrik: M3",
             fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)
    return len(h)


def kirilim(teslim, yol):
    """M4 — kanal bazlı net ciro ve toplam içindeki payı."""
    ciro = teslim[SUTUN_TUTAR].sum()
    k = teslim.groupby(SUTUN_KANAL)[SUTUN_TUTAR].sum().sort_values()
    pay = k / ciro * 100
    renkler = [RENK_ANA if i >= len(k) - 2 else RENK_GRI for i in range(len(k))]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    cubuk = ax.barh(k.index, k.values, color=renkler, height=0.6)
    for b, v, p in zip(cubuk, k.values, pay.values):
        ax.text(b.get_width() + ciro * 0.006, b.get_y() + b.get_height() / 2,
                f"{bin_tl(v)} bin TL · {yuzde(p)}", va="center", fontsize=9)

    ax.set_title("Kanal bazlı net ciro ve toplam içindeki payı")
    ax.set_xlabel("Net ciro (bin TL)")
    ax.set_ylabel("Kanal")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(bin_tl))
    ax.set_xlim(0, k.max() * 1.35)
    ax.grid(axis="x", alpha=0.3)
    fig.text(0.01, 0.01, f"{KAYNAK} · Toplam net ciro {tl(ciro)} · Metrik: M4",
             fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)
    return len(k)


def dagilim(teslim, yol):
    """toplam_tutar histogramı; M2 (ortalama sepet) dikey çizgiyle, son kova taşma kovası."""
    tutar = teslim[SUTUN_TUTAR]
    ortalama, medyan = tutar.mean(), tutar.median()
    tasan = int((tutar > HIST_UST_SINIR).sum())

    # Üst sınırın üstündeki siparişler son kovada toplanır (DQ notu: kuyruk çok uzun)
    kirpik = tutar.clip(upper=HIST_UST_SINIR)
    kenarlar = np.arange(0, HIST_UST_SINIR + HIST_KOVA_GENISLIGI, HIST_KOVA_GENISLIGI)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.hist(kirpik, bins=kenarlar, color=RENK_ANA, alpha=0.75, edgecolor="white", lw=0.5)
    ax.axvline(ortalama, color=RENK_VURGU, ls="--", lw=1.8,
               label=f"M2 ortalama sepet: {tl(ortalama)}")
    ax.axvline(medyan, color=RENK_GRI, ls=":", lw=1.5,
               label=f"Medyan: {tl(medyan)}")

    ax.set_title("Sipariş tutarı dağılımı")
    ax.set_xlabel("Sipariş tutarı (TL)")
    ax.set_ylabel("Sipariş sayısı")
    ax.set_xlim(0, HIST_UST_SINIR)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1000))
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _p: f"{x:,.0f}".replace(",", ".")
                              + ("+" if x >= HIST_UST_SINIR else "")))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    fig.text(0.01, 0.01,
             f"{KAYNAK} · {len(tutar)} sipariş · kova {HIST_KOVA_GENISLIGI} TL · "
             f"{HIST_UST_SINIR:,}".replace(",", ".")
             + f" TL üstü {tasan} sipariş son kovada · Metrik: M2",
             fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)
    return tasan


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dosya", nargs="?", default=VERI, help="sipariş verisi (CSV)")
    p.add_argument("--klasor", default=CIKTI_KLASORU, help="PNG'lerin yazılacağı klasör")
    a = p.parse_args()

    try:
        df, teslim = veri_oku(a.dosya)
    except ValueError as hata:
        print(f"HATA: {hata}", file=sys.stderr)
        return 1

    stil()
    os.makedirs(a.klasor, exist_ok=True)
    zs = os.path.join(a.klasor, ZAMAN_SERISI)
    kr = os.path.join(a.klasor, KIRILIM)
    dg = os.path.join(a.klasor, DAGILIM)

    hafta = zaman_serisi(teslim, zs)
    kanal = kirilim(teslim, kr)
    tasan = dagilim(teslim, dg)

    print(f"Okunan: {a.dosya} — {len(df)} satır, {len(df.columns)} sütun")
    print(f"Filtre: {SUTUN_DURUM} == \"{DURUM_TESLIM}\" → {len(teslim)} satır")
    print(f"Yazıldı: {zs}  (M3, {hafta} hafta)")
    print(f"Yazıldı: {kr}  (M4, {kanal} kanal)")
    print(f"Yazıldı: {dg}  (M2 çizgisiyle, {tasan} sipariş taşma kovasında)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
