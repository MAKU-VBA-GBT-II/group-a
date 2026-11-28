"""Ajan 1 ortak iskelet: her site için aynı kalan parçalar.

Skill'ler: skills/ajan1-alma, skills/ajan1-isleme, skills/ajan1-teslim.
Site parçaları (gratis.py, ileride ikea.py ...) yalnızca kartları okur;
bekleme, robots.txt, fiyat okuma, eşleştirme, eleme ve tablo burada.
"""
import csv
import random
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parents[2]
TR = timezone(timedelta(hours=3))

SUTUNLAR = [
    "bizim_urun", "kategori", "rakip_urun_adi", "eslesme_yontemi", "eslesme_guveni",
    "birim_miktar", "ham_fiyat_metni", "liste_fiyati", "indirimli_fiyat", "fiyat_turu",
    "kdv_dahil", "para_birimi", "stok_durumu", "rakip_site", "urun_url", "bulma_yolu",
    "cekilme_zamani", "arac", "elendi",
]

URUN_SINIRI = 100          # kategori başına en fazla ürün (ajan1-alma, kural 3)
BEKLEME_ARALIGI = (3, 5)   # site bir şey söylemiyorsa (ajan1-alma, kural 2)
ZAMAN_ASIMI_BEKLEME = 30   # sayfa hiç cevap vermezse "yavaşla" işareti sayılır (28 Kasım, Ruj)


def simdi():
    return datetime.now(TR).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------- robots.txt
class Robots:
    """Basit robots.txt okuyucu: '*' ve '$' destekli, en uzun kural kazanır.

    Python'un urllib.robotparser'ı '*' joker karakterini tanımıyor ve ilk
    eşleşen kuralı uyguluyor; Gratis'te en başta 'Allow: /' olduğu için her
    adresi serbest sanardı. Bu yüzden Google'ın kullandığı kural uygulanır.
    """

    def __init__(self, metin, ajan="*"):
        self.kurallar = []
        grup, aktif = [], False
        for satir in metin.splitlines():
            satir = satir.split("#", 1)[0].strip()
            if ":" not in satir:
                continue
            anahtar, deger = [s.strip() for s in satir.split(":", 1)]
            anahtar = anahtar.lower()
            if anahtar == "user-agent":
                if grup and self.kurallar:
                    break  # '*' grubu bitti
                aktif = deger == ajan
                grup.append(deger)
            elif aktif and anahtar in ("allow", "disallow") and deger:
                self.kurallar.append((anahtar == "allow", deger))
        self.crawl_delay = None
        m = re.search(r"(?im)^crawl-delay:\s*([\d.]+)", metin)
        if m:
            self.crawl_delay = float(m.group(1))

    @staticmethod
    def _desen(kural):
        r = re.escape(kural).replace(r"\*", ".*")
        if r.endswith(r"\$"):
            r = r[:-2] + "$"
        return re.compile(r)

    def izin_var_mi(self, yol):
        en_iyi = None  # (uzunluk, izin)
        for izin, kural in self.kurallar:
            if self._desen(kural).match(yol):
                aday = (len(kural), izin)
                if en_iyi is None or aday > en_iyi:
                    en_iyi = aday
        return True if en_iyi is None else en_iyi[1]


# ---------------------------------------------------------------- bekleme
class Bekleyici:
    """Sıra: Crawl-delay > 429'un istediği süre > 3-5 sn rastgele."""

    def __init__(self, crawl_delay=None):
        self.crawl_delay = crawl_delay
        self.sayac_429 = 0
        self.sayac_zaman_asimi = 0

    def bekle(self):
        if self.crawl_delay:
            sure = max(self.crawl_delay, BEKLEME_ARALIGI[0])
        else:
            sure = random.uniform(*BEKLEME_ARALIGI)
        time.sleep(sure)
        return round(sure, 1)


class SiteBirakildi(Exception):
    """İkinci 429'da ya da ikinci zaman aşımında site bırakılır (ajan1-alma, kural 2)."""


# ---------------------------------------------------------------- fiyat
def fiyat_oku(metin):
    """'1.299,90 TL' / '₺1.299,90' -> 1299.90 ; okunamazsa None."""
    m = re.search(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{1,2}))?", metin or "")
    if not m:
        return None
    tam = m.group(1).replace(".", "")
    kurus = (m.group(2) or "0").ljust(2, "0")
    return round(float(f"{tam}.{kurus}"), 2)


def iki_ondalik(x):
    return "" if x is None else f"{x:.2f}"


# ---------------------------------------------------------------- eşleştirme
def _kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def eslesme_tanimlari(yol=KOK / "docs" / "eslesme-tanimlari.md"):
    """docs/eslesme-tanimlari.md tablosunu okur: ürün -> kurallar."""
    tanim = {}
    for satir in Path(yol).read_text(encoding="utf-8").splitlines():
        h = [s.strip() for s in satir.strip().strip("|").split("|")]
        if len(h) != 9 or not h[0].isdigit():
            continue
        _, kategori, urun, liste, dahil, haric, birim, makul, _ = h
        gratis_kat = None
        m = re.match(r"Gratis kategori:\s*([^;]+);\s*(.*)", dahil)
        if m:
            gratis_kat, dahil = m.group(1).strip(), m.group(2)
        a, b = [float(x.replace(".", "").replace(",", ".")) for x in re.findall(r"[\d.,]+", makul)[:2]]
        tanim[urun] = {
            "kategori": kategori,
            "liste": float(liste),
            "dahil": [_kucuk(x.strip()) for x in dahil.split(",") if x.strip()],
            "haric": [_kucuk(x.strip()) for x in haric.split(",") if x.strip()],
            "birim": birim,
            "makul": (a, b),
            "gratis_kategori": gratis_kat,
        }
    return tanim


def web_liste_fiyatlari(yol=KOK / "data" / "urun-listesi-web.csv"):
    with open(yol, encoding="utf-8") as f:
        return {r["urun"]: (r["kategori"], float(r["liste_fiyati"])) for r in csv.DictReader(f)}


def birim_miktar(ad):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ml|gr|g|lt|l|adet)\b", _kucuk(ad))
    return f"{m.group(1)} {m.group(2)}" if m else ""


def birim_uyumlu(beklenen, ad):
    """Beklenen birim/miktar (eşleşme tanımları) ile ürün adındaki miktarı karşılaştırır.

    - Aralık verilmişse ("300–600 ml", "10.000–20.000 mAh") adındaki aynı birimli sayı aralıkta mı?
      Adında o birim yoksa bilinemez (None).
    - Yalnız "1 adet" / "1 kitap" gibi tek parça bekleniyorsa uyumludur; çoklu paket ayrıca
      elenir (kural 5). (28 Kasım: önceki sürüm bu ürünlerde None döndürüp Ruj ve Masa
      Lambası'na hiç "yuksek" vermiyordu; Sema'nın #124 incelemesi.)
    """
    k = _kucuk(ad)
    aralik = re.search(r"([\d.]+)\s*[–-]\s*([\d.]+)\s*(ml|mah|gr|g|cm)\b", _kucuk(beklenen))
    if aralik:
        birim = aralik.group(3)
        miktar = re.search(r"(\d+(?:[.,]\d+)?)\s*" + birim + r"\b", k)
        if not miktar:
            return None
        sayi = lambda x: float(x.replace(".", "").replace(",", ".")) if "." in x and len(x.split(".")[-1]) == 3 \
            else float(x.replace(",", "."))
        return sayi(aralik.group(1)) <= sayi(miktar.group(1)) <= sayi(aralik.group(2))
    if re.match(r"\s*1\s+(adet|kitap|çift)\b", _kucuk(beklenen)):
        return True
    return None


def eslestir(ad, tanim, site_kategorisi=None):
    """Döner: ('dahil', dahil_ifadesi_var_mi) / ('haric', kelime) / ('kararsiz', None)."""
    k = _kucuk(ad)
    # Önünde harf varsa sayılmaz ("Pahalı" içindeki "halı"); önünde rakam varsa
    # sayılır ("50SPF" içindeki "spf": nitelikler sayı + birim olarak yazılır).
    # Ek almış hali ("şampuanı") sayılır.
    var = lambda ifade: re.search(r"(?<![^\W\d_])" + re.escape(ifade), k) is not None
    for h in tanim["haric"]:
        if var(h):
            return "haric", h
    if any(var(d) for d in tanim["dahil"]):
        return "dahil", True
    # Kategori kuralı (#122): Gratis'in kendi kategorisi dahil sayılır, ad tutmasa da.
    if tanim.get("gratis_kategori") and site_kategorisi == tanim["gratis_kategori"]:
        return "dahil", False
    return "kararsiz", None


def guven(dahil_ifadesi, birim_ok, karsilastirma, makul):
    """eslesme-tanimlari kural 4."""
    if not (makul[0] <= karsilastirma <= makul[1]):
        return "dusuk"
    return "yuksek" if (dahil_ifadesi and birim_ok) else "orta"


# Çoklu paket: "3'lü", "3x", "2x400 ml", "400 ml x 2", "set", "paket".
# "x" ile sayı yan yana olması tek başına yetmez: "Lazer X3", "X5 Max" ürün adıdır;
# "60x20 cm" ölçüdür (28 Kasım, Nemlendirici'de tek krem yanlışlıkla eleniyordu).
COKLU = re.compile(r"\b(\d+\s*'?\s*(li|lı|lu|lü)|\d+\s*x\s*\d+\s*(ml|gr|g|adet)|\d+\s*x\b"
                   r"|(ml|gr|g|adet)\s*x\s*\d+|set|paket|ikili|üçlü)\b")


def eleme_gerekcesi(urun, ad, karsilastirma, liste, stok):
    """eslesme-tanimlari kural 2, 5, 6; bant web fiyatlı listeye göre, katı."""
    if not (0.3 * liste <= karsilastirma <= 3 * liste):
        return "fiyat bandı dışı"
    if urun != "Saklama Kabı Seti" and COKLU.search(_kucuk(ad)):
        return "çoklu paket"
    if stok == "yok":
        return "stok yok"
    return ""


# ---------------------------------------------------------------- rozetler
def rozet_sozlugu(yol=KOK / "data" / "ajan1-rozet-sozlugu.csv"):
    with open(yol, encoding="utf-8") as f:
        return {(r["site"], r["rozet_id"]): r for r in csv.DictReader(f)}


# ---------------------------------------------------------------- tablo
def tablo_yaz(satirlar, yol):
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUTUNLAR, lineterminator="\n")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: s.get(k, "") for k in SUTUNLAR})
