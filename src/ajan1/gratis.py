"""Gratis site parçası: yalnızca kategori sayfasındaki kartları okur.

28 Kasım incelemesi (Şampuanlar sayfası):
- robots.txt kategori sayfalarına izin veriyor, Crawl-delay yok; ?sort=, ?brand= gibi
  filtre adresleri yasak, ?page= serbest.
- Sayfa başına 24 ürün, sayfalar ?page=2, ?page=3 ...
- Kart satırları: [varyant sayısı] / ad / (yorum sayısı) / satış adedi / '149,00 TL' /
  'Gold&Platinum Ozel Fiyat' / '59,50 TL'. İkinci fiyat kart üyeliğine bağlı (şartlı).
- Rozetler yazı değil resim; anlamları data/ajan1-rozet-sozlugu.csv'de.
"""
import re
import time

from . import ortak

SITE = "Gratis"
ALAN = "https://www.gratis.com"

KATEGORILER = {  # bizim ürün -> (Gratis kategori adı, adres); ajan1-alma kaynak tablosu
    "Nemlendirici": ("Yüz Nemlendirici Gece Kremleri", f"{ALAN}/cilt-bakim/yuz-nemlendirici-gece-kremleri-c-5020132"),
    "Şampuan": ("Şampuanlar", f"{ALAN}/sac-bakim/sampuanlar-c-50301"),
    "Parfüm": ("Parfüm", f"{ALAN}/parfum-deodorant/parfum-c-50401"),
    "Güneş Kremi": ("Güneş Ürünleri", f"{ALAN}/gunes-urunleri-c-516"),
    "Ruj": ("Ruj", f"{ALAN}/makyaj/ruj-c-5010101"),
}

KART_SECICI = "div[data-page] .grid > div"

KART_JS = """
() => [...document.querySelectorAll('%s')].map(c => {
  const a = c.querySelector('a[href*="-p-"]');
  return {
    ad: (c.querySelector('h5')?.innerText || '').trim(),
    url: a ? a.getAttribute('href') : null,
    satirlar: c.innerText.split('\\n').map(s => s.trim()).filter(Boolean),
    rozet: [...c.querySelectorAll('img[alt^="Badge"]')].map(i => i.src.split('/').pop().split('_')[0]),
    ustu_cizili: [...c.querySelectorAll('del, s, .line-through')].map(e => e.innerText.trim()),
  };
})
""" % KART_SECICI

FIYAT = re.compile(r"^[\d.,]+\s*TL$")
KOSULLU = re.compile(r"gold|platinum|kart|kupon|banka|üye|uye|tutar|2\.|ikinci", re.I)
SEPETTE = re.compile(r"sepet", re.I)


def kart_fiyatlari(satirlar, ad, ustu_cizili=()):
    """Kart satırlarından karşılaştırma fiyatını çıkarır (ajan1-isleme §1).

    Karşılaştırma fiyatı: herkesin şartsız, peşin, tek ürün için ödediği ve
    sayfada görebildiğimiz en düşük fiyat. Şartlı fiyatlar yalnızca not olur.
    """
    duz, kosullu, bilinmeyen = [], [], []
    onceki = None
    for s in satirlar:
        if FIYAT.match(s):
            etiket = onceki if onceki and re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]{3,}", onceki) \
                and onceki != ad and not re.search(r"Tür$|B\+$", onceki) else None
            if etiket is None:
                duz.append(s)
            elif KOSULLU.search(etiket):
                kosullu.append((etiket, s))
            elif SEPETTE.search(etiket):
                duz.append(s)  # şartsız sepette indirim sayılır
            else:
                bilinmeyen.append((etiket, s))
        onceki = s
    if not duz:
        return None
    degerler = sorted({ortak.fiyat_oku(x) for x in duz}, reverse=True)
    liste = degerler[0]
    indirimli = degerler[-1] if len(degerler) > 1 else None
    ham = next(x for x in duz if ortak.fiyat_oku(x) == (indirimli or liste))
    return {
        "liste": liste,
        "indirimli": indirimli,
        "ham": ham,
        "kosullu": kosullu,
        "bilinmeyen": bilinmeyen,
        "ustu_cizili_dogrulandi": (not indirimli) or any(
            ortak.fiyat_oku(u) == liste for u in ustu_cizili),
    }


def sayfa_adresi(taban, n):
    return taban if n == 1 else f"{taban}?page={n}"


def kategori_oku(sayfa, urun, robots, bekleyici, iz):
    """Bir kategorinin sayfalarını gezer; ham kartları döner. Hata olursa iz'e yazar."""
    kat_adi, taban = KATEGORILER[urun]
    kartlar = []
    n = 1
    while len(kartlar) < ortak.URUN_SINIRI:
        adres = sayfa_adresi(taban, n)
        yol = adres[len(ALAN):]
        kayit = {"adres": adres, "zaman": ortak.simdi(), "robots": robots.izin_var_mi(yol)}
        iz.append(kayit)
        if not kayit["robots"]:
            kayit["sonuc"] = "robots.txt yasaklıyor, açılmadı"
            break
        kayit["bekleme_sn"] = bekleyici.bekle()
        durum = _ac(sayfa, adres, bekleyici, kayit)
        if durum != 200:
            break
        try:
            sayfa.wait_for_selector(KART_SECICI, timeout=15000)
        except Exception:
            kayit["sonuc"] = "ürün kartı bulunamadı"
            break
        yeni = sayfa.evaluate(KART_JS)
        for k in yeni:
            k["bulma_yolu"] = f"{taban} s.{n}"
            k["cekilme_zamani"] = kayit["zaman"]
        kayit["okunan"] = len(yeni)
        kartlar.extend(yeni)
        if not sayfa.query_selector(f'a[href*="page={n + 1}"]'):
            break
        n += 1
    return kat_adi, kartlar[: ortak.URUN_SINIRI]


def _ac(sayfa, adres, bekleyici, kayit):
    """Sayfayı açar; sitenin işaretlerine göre bekler.

    - 429: sitenin istediği kadar beklenir, ikinci 429'da site bırakılır.
    - Zaman aşımı / bağlantı hatası (28 Kasım, Ruj): site "yavaşla" diyor sayılır;
      30 sn beklenip bir kez daha denenir, ikinci zaman aşımında site bırakılır.
    - 5xx: bir kez daha denenir (28 Kasım'da ilk denemede 502 alındı).
    """
    tekrar_5xx = False
    while True:
        try:
            yanit = sayfa.goto(adres, wait_until="domcontentloaded", timeout=45000)
        except Exception as hata:  # Playwright TimeoutError ya da net::ERR_...
            bekleyici.sayac_zaman_asimi += 1
            kayit.setdefault("zaman_asimi", []).append(str(hata).splitlines()[0][:200])
            if bekleyici.sayac_zaman_asimi >= 2:
                raise ortak.SiteBirakildi(f"ikinci zaman aşımı: {adres}")
            kayit["zaman_asimi_bekleme_sn"] = ortak.ZAMAN_ASIMI_BEKLEME
            time.sleep(ortak.ZAMAN_ASIMI_BEKLEME)
            continue
        durum = yanit.status if yanit else 0
        kayit["durum"] = durum
        if durum == 429:
            bekleyici.sayac_429 += 1
            if bekleyici.sayac_429 >= 2:
                raise ortak.SiteBirakildi(f"ikinci 429: {adres}")
            sure = int(yanit.headers.get("retry-after", "60") or 60)
            kayit["429_bekleme_sn"] = sure
            time.sleep(sure)
            continue
        if durum >= 500 and not tekrar_5xx:
            tekrar_5xx = True
            kayit["tekrar_deneme"] = True
            bekleyici.bekle()
            continue
        if durum != 200:
            kayit["sonuc"] = f"sayfa açılmadı (HTTP {durum})"
        return durum
