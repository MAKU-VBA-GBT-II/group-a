"""IKEA site parçası: Masa Lambaları kategori sayfasındaki kartları okur.

28 Kasım incelemesi:
- robots.txt kategori sayfalarına izin veriyor (yalnız /arama/ ve üyelik sayfaları yasak),
  Crawl-delay yok.
- Sayfa ilk açıldığında hiç ürün kartı yok; liste görünür alana kaydırıldıkça JavaScript'le
  24'er 24'er yükleniyor (adres ?page=2, ?page=3 ... olarak değişiyor; Masa Lambaları'nda 93 ürün).
  Sayfayı tek seferde en alta atlatmak bir şey yüklemiyor; adım adım kaydırmak gerekiyor.
  Bu yüzden Playwright şart (ajan1-alma, girdi kontrolü).
- Kart satırları: seri adı (FADO) / tür ve ölçü (abajur, 23 cm) / '2.499₺' ...
  İndirimde: '1.399₺' / '1.199₺' / '%14' / 'indirim' /
  'İndirimli fiyat 02.11.26 - 29.11.26 tarihleri arasında geçerlidir.' — kampanyanın
  bitişi kategori sayfasında görünüyor (ajan1-isleme §5).
"""
import re

from . import ortak

SITE = "IKEA"
ALAN = "https://www.ikea.com.tr"

KATEGORILER = {  # bizim ürün -> (IKEA kategori adı, adres)
    "Masa Lambası": ("Masa Lambaları", f"{ALAN}/kategori/masa-lambalari"),
}

ROZET_YOK = True  # IKEA kartlarında resim rozeti yok

KART_JS = r"""
() => [...document.querySelectorAll('.product-bottom-wrapper')].map(w => {
  let c = w;
  while (c.parentElement && c.parentElement.querySelectorAll('.product-bottom-wrapper').length === 1)
    c = c.parentElement;
  const a = c.querySelector('a[href*="/urun/"]');
  const s = c.innerText.split('\n').map(x => x.trim()).filter(Boolean);
  return {
    ad: s.length > 1 ? (s[0] + ' ' + s[1]) : (s[0] || ''),
    url: a ? a.getAttribute('href') : null,
    satirlar: s,
    rozet: [],
    ustu_cizili: [],
  };
})
"""

FIYAT = re.compile(r"^[\d.,]+\s*₺$")
KAMPANYA = re.compile(r"(\d{2})\.(\d{2})\.(\d{2})\s*-\s*(\d{2})\.(\d{2})\.(\d{2})\s*tarihleri arasında geçerli", re.I)
KOSULLU = re.compile(r"family|üye|uye|kart|kupon", re.I)


def kart_fiyatlari(satirlar, ad, ustu_cizili=()):
    """IKEA kartından karşılaştırma fiyatı (ajan1-isleme §1).

    İndirimde iki fiyat yan yana yazılır: önce eski (liste), sonra indirimli.
    İndirim herkese açıksa (üyelik şartı yazmıyorsa) karşılaştırmaya indirimli girer.
    """
    fiyatlar = [s for s in satirlar if FIYAT.match(s)]
    if not fiyatlar:
        return None
    kosullu = [("şartlı fiyat", s) for s in satirlar if KOSULLU.search(s) and "₺" in s]
    degerler = [ortak.fiyat_oku(f) for f in fiyatlar]
    liste = max(degerler)
    indirimli = min(degerler) if len(set(degerler)) > 1 else None
    ham = fiyatlar[degerler.index(indirimli if indirimli else liste)]
    bitis = None
    for s in satirlar:
        m = KAMPANYA.search(s)
        if m:
            g, a, y = m.group(4), m.group(5), m.group(6)
            bitis = f"20{y}-{a}-{g}"
    return {
        "liste": liste,
        "indirimli": indirimli,
        "ham": ham,
        "kosullu": kosullu,
        "bilinmeyen": [],
        "ustu_cizili_dogrulandi": True,
        "kampanya_bitis": bitis,
    }


def kategori_oku(sayfa, urun, robots, bekleyici, iz):
    """Sayfayı açar, adım adım kaydırarak en fazla 100 ürüne kadar yükler."""
    kat_adi, taban = KATEGORILER[urun]
    kayit = {"adres": taban, "zaman": ortak.simdi(), "robots": robots.izin_var_mi(taban[len(ALAN):])}
    iz.append(kayit)
    if not kayit["robots"]:
        kayit["sonuc"] = "robots.txt yasaklıyor, açılmadı"
        return kat_adi, []
    kayit["bekleme_sn"] = bekleyici.bekle()
    durum = _ac(sayfa, taban, bekleyici, kayit)
    if durum != 200:
        return kat_adi, []

    # Adım adım kaydır; her yeni 24'lük yük siteye yeni bir istek olduğu için arada 3-5 sn beklenir.
    kayit["yuklemeler"] = []
    say = lambda: sayfa.locator(".product-bottom-wrapper").count()
    onceki, durgun = say(), 0
    for _ in range(400):                       # güvenlik sınırı
        sayfa.mouse.wheel(0, 900)
        sayfa.wait_for_timeout(900)
        simdi = say()
        if simdi > onceki:
            kayit["yuklemeler"].append({"kart": simdi, "zaman": ortak.simdi(),
                                        "sonraki_bekleme_sn": bekleyici.bekle()})
            onceki, durgun = simdi, 0
            if simdi >= ortak.URUN_SINIRI:
                break
            continue
        en_altta = sayfa.evaluate("window.scrollY + window.innerHeight >= document.body.scrollHeight - 50")
        durgun = durgun + 1 if en_altta else 0
        if durgun >= 5:                        # sayfanın sonunda 5 adım boyunca yeni ürün gelmedi
            break

    kartlar = sayfa.evaluate(KART_JS)
    # Girdi kontrolü: kaydırma/yükleme gerçekten çalıştı mı? (ajan1-alma)
    if len(kartlar) <= 4:
        kayit["sonuc"] = f"liste yüklenmedi: yalnız {len(kartlar)} kart (JavaScript listesi gelmedi)"
        return kat_adi, []
    zaman = ortak.simdi()
    for i, k in enumerate(kartlar):
        k["bulma_yolu"] = f"{taban} s.{i // 24 + 1}"   # IKEA her yüklemede 24 ürün ekliyor (?page=N)
        k["cekilme_zamani"] = zaman
    kayit["okunan"] = len(kartlar)
    return kat_adi, kartlar[: ortak.URUN_SINIRI]


def _ac(sayfa, adres, bekleyici, kayit):
    """Gratis'teki kurallarla aynı: 429 ve zaman aşımında site işaretine uyulur."""
    from .gratis import _ac as ortak_ac
    return ortak_ac(sayfa, adres, bekleyici, kayit)
