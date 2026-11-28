"""Ajan 1 ortak iskelet: her site için aynı kalan parçalar.

Skill'ler: skills/ajan1-alma, skills/ajan1-isleme, skills/ajan1-teslim.
Site parçaları (gratis.py, ileride ikea.py ...) yalnızca kartları okur;
bekleme, robots.txt, fiyat okuma, eşleştirme, eleme ve tablo burada.
"""
import csv
from functools import lru_cache
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


# İngilizce ifadeler yazıldığı gibi aranır, Türkçe ifadeler ek alabilir (#123 karar 7).
# Bir ifadenin bütün kelimeleri bu listedeyse İngilizce sayılır; eşleşme tanımlarındaki
# İngilizce ifadelerin kelimeleri. Yeni İngilizce ifade eklenince kelimesi de buraya eklenir.
INGILIZCE = set("""after balm body bronzer car carpet cat conditioner contour cream de dog dry eau edp
edt eye foundation gloss hair hand humidifier lip lipstick liner liquid lotion mask matte mist
moisturiser moisturizer moisturizing night parfum perfume pet protection room self set shampoo
spray stick sun sunblock sunglasses sunscreen tan tanning tester toilette""".split())

TR_HARF = "a-zçğıöşü"
YUMUSAMA = {"k": "ğ", "p": "b", "t": "d", "ç": "c"}   # stik -> stiği, kitap -> kitabı


# Türkçe ad ve isim ekleri (iyelik, tamlama, durum, çoğul, -lı): "şampuanı", "kremi",
# "güneşten", "lambaları", "pudrası", "nemlendiricili". Yalnız bu ekler kabul edilir; rastgele
# devam kabul edilmez, yoksa "ayt" kökü "Aydınlatıcı"yı yakalar.
EK = (r"(?:lar|ler|ları|leri|sı|si|su|sü|nın|nin|nun|nün|ın|in|un|ün|ı|i|u|ü|dan|den|tan|ten|"
      r"da|de|ta|te|ya|ye|yı|yi|yu|yü|a|e|la|le|yla|yle|lı|li|lu|lü|lık|lik)")
UNLU = "aeıioöuü"


def _kelime_deseni(kelime, turkce):
    son = rf"(?![{TR_HARF}\d])"
    if not turkce:
        return re.escape(kelime) + son
    govde = re.escape(kelime) + rf"(?:'?{EK}){{0,3}}"
    if kelime[-1] in YUMUSAMA:   # ünsüz yumuşaması yalnız ünlüyle başlayan ekten önce: stik / stiği
        yumusak = re.escape(kelime[:-1] + YUMUSAMA[kelime[-1]]) + rf"(?=[{UNLU}])(?:{EK}){{1,3}}"
        govde = f"(?:{govde}|{yumusak})"
    return govde + son


@lru_cache(maxsize=None)
def ifade_deseni(ifade):
    """Bir dahil/hariç ifadesinin düzenli ifadesi (karar 7).

    Kelime başından aranır; önünde harf olamaz ("Pahalı" içindeki "halı"), rakam olabilir
    ("50SPF"). Türkçe ifadelerin her kelimesi ek alabilir ("güneşten koruyucu" →
    "güneş koruyucu"); İngilizce ifadeler ek almaz ("car shampoo", "Care Shampoo"yu yakalamaz).
    """
    kelimeler = ifade.split()
    turkce = not all(k in INGILIZCE for k in kelimeler)
    govde = r"\s+".join(_kelime_deseni(k, turkce) for k in kelimeler)
    return re.compile(rf"(?<![{TR_HARF}])" + govde)


def _iki_kucuk(ad):
    """Büyük "I" Türkçede "ı", İngilizcede "i" olur ("LIPSTICK"): iki okuma da denenir."""
    return {_kucuk(ad), ad.replace("İ", "i").lower()}


def _var(ifade, okumalar):
    d = ifade_deseni(ifade)
    return any(d.search(k) for k in okumalar)


# ---------------------------------------------------------------- baş isim (karar 11)
GENEL_ISIMLER = ["krem", "losyon", "serum", "sprey", "jel", "süt", "stik", "cream", "lotion", "spray"]
# Eşleşme tanımlarında olmayan ama ürün adlarında baş isim olarak geçen kozmetik ürünleri
# (#123 incelemesindeki örnekler: "Güneş Pudrası", "Nemlendirici Duş Jeli"). Bunlar bizim
# ürünümüz değil; baş isim bunlardan biriyse ürün bizim kategorimize girmez.
BASKA_URUNLER = ["pudra", "duş jeli", "allık", "maskara", "oje", "tonik", "yüz yıkama jeli",
                 "temizleme jeli", "makyaj bazı", "kapatıcı", "fondöten", "foundation", "deodorant",
                 "conditioner", "bronzer", "bronzlaştırıcı"]
BIRIMLER = {"ml", "gr", "g", "cm", "mm", "lt", "l", "kg", "adet", "spf", "w", "mah", "x"}
BAGLAC = re.compile(r"\s(?:&|ve|\+|and)\s|2'?si\s*1\s*arada", re.I)


def bas_isim_sozlugu(tanimlar, kategori=None):
    """İfade -> sahibi (bizim ürün adı ya da 'başka'); yalnız aynı kategorinin ürünleri.

    Dahil ifadeleri ürünün kendisidir. Hariç listelerinden yalnız çok kelimeli ifadeler
    ("saç kremi", "duş jeli", "kuru şampuan") başka bir ürün sayılır; tek kelimelik hariç
    ifadeler ("saç", "dudak", "vücut") çoğu zaman bir niteliktir ("Yağlı Saç Derisi İçin"),
    baş isim sayılmaz. Bilinen başka ürünler BASKA_URUNLER'dedir.
    """
    sozluk = {}
    secili = {u: t for u, t in tanimlar.items() if kategori is None or t["kategori"] == kategori}
    for urun, t in secili.items():
        for h in t["haric"]:
            if len(h.split()) > 1:
                sozluk.setdefault(h, "başka")
    for b in BASKA_URUNLER:
        sozluk.setdefault(b, "başka")
    for urun, t in secili.items():
        for d in t["dahil"]:
            if not d.startswith("d&r kategori"):
                sozluk[d] = urun
    return sozluk


def _sadelestir(ad, markalar=()):
    """Marka, sayı ve birimler atılır (karar 11, adım 1–2). Kelime listesi döner."""
    k = ad
    adaylar = {v for x in markalar if x for v in _iki_kucuk(x)}
    for m in sorted(adaylar, key=len, reverse=True):
        if k.startswith(m + " ") or k == m:
            k = k[len(m):]
            break
    kelimeler = re.findall(rf"[{TR_HARF}0-9'&+.%]+", k)
    return [w for w in kelimeler if not re.search(r"\d", w) and w.strip(".") not in BIRIMLER
            and w not in {"&", "+", "%"}]


def _genel_mi(kelime):
    return any(re.fullmatch(_kelime_deseni(g, g not in INGILIZCE), kelime) for g in GENEL_ISIMLER)


def _bas_isim_parca(kelimeler, sozluk):
    """Kelimeleri sondan başa okur; ilk ürün adı baş isimdir (karar 11, adım 3–5).

    Genel isimler (krem, serum, sprey...) tek başına baş isim sayılmaz, tür önündeki
    tamlayandan gelir: "Güneş Serumu" → güneş, "Nemlendirici Gündüz Kremi" → nemlendirici.
    Çok kelimeli ifadeler önce denenir ("saç kremi", "night cream").
    Döner: (ifade, sahibi) ya da None (belirsiz).
    """
    ifadeler = sorted(sozluk, key=lambda x: -len(x.split()))
    j = len(kelimeler)
    while j > 0:
        for ifade in ifadeler:
            n = len(ifade.split())
            if n > j or (n == 1 and _genel_mi(kelimeler[j - 1])):
                continue
            if ifade_deseni(ifade).fullmatch(" ".join(kelimeler[j - n:j])):
                return ifade, sozluk[ifade]
        j -= 1
    return None


def bas_isimler(ad, sozluk, markalar=()):
    """Ürün adının baş isim(ler)i. Bağlaçla birleşen iki baş isim (karar 11, adım 6) çok
    işlevli ürün demektir; her parça ayrı okunur."""
    en_iyi = []
    for okuma in sorted(_iki_kucuk(ad)):   # "LIPSTICK" hem "lıpstıck" hem "lipstick" okunur
        okuma = re.split(r"\s[-–]\s", okuma)[0]   # "Ad - açıklama": açıklama baş isim taşımaz
        parcalar = BAGLAC.split(" " + okuma + " ")
        sonuc = []
        for i, parca in enumerate(parcalar):
            b = _bas_isim_parca(_sadelestir(parca, markalar if i == 0 else ()), sozluk)
            if b:
                sonuc.append(b)
        if len(sonuc) > len(en_iyi):
            en_iyi = sonuc
    return en_iyi


SPF = re.compile(r"\d+\s*\+?\s*spf|spf\s*\d+|güneş\s+koru(?:yucu|malı|ma)|uv\s+koruma", re.I)
CILT_BAKIM = {"Nemlendirici"}   # karar 10: SPF'li cilt bakım ürünü Güneş Kremi'nde de yer alır


def eslestir(ad, tanim, site_kategorisi=None, sozluk=None, markalar=(), urun=None):
    """Döner: ('dahil', True|False|'cok_islevli') / ('haric', gerekçe) / ('kararsiz', None).

    Kelime listeleri ürünü bulur, baş isim kuralı doğrular (karar 11.7). sozluk verilmezse
    baş isim kuralı uygulanmaz (eski davranış, testler için).
    """
    okumalar = _iki_kucuk(ad)
    for h in tanim["haric"]:
        if _var(h, okumalar):
            return "haric", h
    dahil = any(_var(d, okumalar) for d in tanim["dahil"])
    kategori = bool(tanim.get("gratis_kategori") and site_kategorisi == tanim["gratis_kategori"])
    if sozluk is not None and urun is not None:
        basl = bas_isimler(ad, sozluk, markalar)
        sahipler = {s for _, s in basl}
        # 11.7 istisnası: baş ismi cilt bakım ürünü olan SPF'li ürün Güneş Kremi'nde orta güvenle
        if urun == "Güneş Kremi" and SPF.search(_kucuk(ad)) and (
                sahipler & CILT_BAKIM or (not basl and any(_genel_mi(w) for w in _sadelestir(_kucuk(ad), markalar)))):
            return "dahil", "cok_islevli"
        if basl and urun not in sahipler:
            return "haric", f"baş isim: {basl[0][0]}"
    if dahil:
        return "dahil", True
    # Kategori kuralı (#122): Gratis'in kendi kategorisi dahil sayılır, ad tutmasa da.
    if kategori:
        return "dahil", False
    return "kararsiz", None


def guven(dahil_ifadesi, birim_ok, karsilastirma, makul):
    """eslesme-tanimlari kural 4; çok işlevli ürün ikinci kategorisinde orta (karar 8)."""
    if not (makul[0] <= karsilastirma <= makul[1]):
        return "dusuk"
    if dahil_ifadesi == "cok_islevli":
        return "orta"
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
