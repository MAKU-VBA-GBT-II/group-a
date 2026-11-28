"""Ajan 1 toplama kodu (src/ajan1/) için testler. Issue #114.

Ağa ve tarayıcıya çıkmaz: kart okuma, eşleştirme, eleme, fiyat değişimi notu ve teslim
kontrolleri, sayfalardan alınmış örnek kart satırlarıyla denenir.

Çalıştırma: python3 -m unittest discover -s tests -p 'test_ajan1.py'
"""
from datetime import datetime, timedelta
from pathlib import Path
import sys
import unittest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from src.ajan1 import calistir, gratis, ikea, ortak, teslim  # noqa: E402

TANIM = {  # docs/eslesme-tanimlari.md'deki satırların bu testler için yeterli kısmı
    "Şampuan": {"dahil": ["şampuan", "shampoo"], "haric": ["kuru şampuan", "halı", "car shampoo"],
                "birim": "1 adet; 300–600 ml", "makul": (110.0, 670.0), "gratis_kategori": None},
    "Güneş Kremi": {"dahil": ["güneş", "spf"], "haric": ["güneş sonrası"],
                    "birim": "1 adet; 30–200 ml", "makul": (250.0, 1550.0), "gratis_kategori": None},
    "Masa Lambası": {"dahil": ["masa lambası", "çalışma lambası", "abajur"], "haric": ["abajur başlığı"],
                     "birim": "1 adet", "makul": (160.0, 1000.0), "gratis_kategori": None},
}
LISTE = {"Şampuan": ("Kozmetik", 269.0), "Masa Lambası": ("Ev & Yaşam", 399.0)}


def kart(ad, satirlar, url="/urun-p-1", rozet=(), ustu_cizili=()):
    return {"ad": ad, "url": url, "satirlar": list(satirlar), "rozet": list(rozet),
            "ustu_cizili": list(ustu_cizili), "bulma_yolu": "https://www.gratis.com/x s.1",
            "cekilme_zamani": "2026-11-28T21:50:58+03:00"}


class FiyatOkuma(unittest.TestCase):
    def test_turkce_bicim(self):
        self.assertEqual(ortak.fiyat_oku("1.299,90 TL"), 1299.90)
        self.assertEqual(ortak.fiyat_oku("₺149,5"), 149.50)
        self.assertEqual(ortak.fiyat_oku("2.499₺"), 2499.00)
        self.assertIsNone(ortak.fiyat_oku("fiyat yok"))

    def test_gratis_kosullu_fiyat_karsilastirmaya_girmez(self):
        # Gold&Platinum fiyatı üyeliğe bağlı: yalnız rapora yazılır (ajan1-isleme §1)
        f = gratis.kart_fiyatlari(["Elseve Şampuan 400 ml", "149,00 TL", "Gold&Platinum Ozel Fiyat",
                                   "59,50 TL"], "Elseve Şampuan 400 ml")
        self.assertEqual(f["liste"], 149.0)
        self.assertIsNone(f["indirimli"])
        self.assertEqual(f["kosullu"], [("Gold&Platinum Ozel Fiyat", "59,50 TL")])

    def test_ikea_kampanya_bitisi(self):
        s = ["TERTIAL", "çalışma lambası", "1.399₺", "1.199₺", "%14", "indirim",
             "İndirimli fiyat 02.11.26 - 29.11.26 tarihleri arasında geçerlidir."]
        f = ikea.kart_fiyatlari(s, "TERTIAL çalışma lambası")
        self.assertEqual((f["liste"], f["indirimli"], f["ham"]), (1399.0, 1199.0, "1.199₺"))
        self.assertEqual(f["kampanya_bitis"], "2026-11-29")


class Eslestirme(unittest.TestCase):
    def test_kelime_basi(self):
        # "Pahalı" içindeki "halı" hariç kelimesi sayılmaz
        self.assertEqual(ortak.eslestir("Pahalı Şampuan 400 ml", TANIM["Şampuan"])[0], "dahil")
        self.assertEqual(ortak.eslestir("Halı Şampuanı 1 lt", TANIM["Şampuan"])[0], "haric")

    def test_rakamdan_sonra_nitelik(self):
        # "50SPF": nitelikler sayı + birim olarak yazılır (#123 karar 7)
        self.assertEqual(ortak.eslestir("Yüz Kremi 50SPF 50 ml", TANIM["Güneş Kremi"])[0], "dahil")

    def test_es_anlamli_ve_parca(self):
        self.assertEqual(ortak.eslestir("FADO abajur", TANIM["Masa Lambası"])[0], "dahil")
        self.assertEqual(ortak.eslestir("Kumaş abajur başlığı", TANIM["Masa Lambası"])[0], "haric")


class ElemeVeBirim(unittest.TestCase):
    def test_coklu_paket(self):
        e = lambda ad: ortak.eleme_gerekcesi("Şampuan", ad, 300, 269, "var")
        self.assertEqual(e("Elseve Şampuan 2x400 ml"), "çoklu paket")
        self.assertEqual(e("Pantene Şampuan 3'lü Set"), "çoklu paket")
        self.assertEqual(e("Loreal Revitalift Lazer X3 Krem 50 ml"), "")   # ürün adı, paket değil
        self.assertEqual(ortak.eleme_gerekcesi("Masa Lambası", "SAMBORD çalışma lambası, 46x13 cm",
                                               399, 399, "var"), "")          # ölçü, paket değil

    def test_fiyat_bandi_sinirlari_dahil(self):
        self.assertEqual(ortak.eleme_gerekcesi("Şampuan", "Şampuan", 80.70, 269, "var"), "")
        self.assertEqual(ortak.eleme_gerekcesi("Şampuan", "Şampuan", 80.69, 269, "var"), "fiyat bandı dışı")
        self.assertEqual(ortak.eleme_gerekcesi("Şampuan", "Şampuan", 300, 269, "yok"), "stok yok")

    def test_birim_uyumu(self):
        self.assertTrue(ortak.birim_uyumlu("1 adet; 300–600 ml", "Elseve Şampuan 400 ml"))
        self.assertFalse(ortak.birim_uyumlu("1 adet; 300–600 ml", "Şampuan 50 ml"))
        self.assertIsNone(ortak.birim_uyumlu("1 adet; 300–600 ml", "Şampuan"))
        self.assertTrue(ortak.birim_uyumlu("1 adet; 10.000–20.000 mAh", "Anker 10.000 mAh"))
        self.assertTrue(ortak.birim_uyumlu("1 adet", "Maybelline Ruj"))   # Sema'nın #124 notu


class Robots(unittest.TestCase):
    def test_en_uzun_kural_ve_joker(self):
        r = ortak.Robots("User-agent: *\nAllow: /\nDisallow: /*?sort=\nDisallow: /arama/\nCrawl-delay: 2\n")
        self.assertTrue(r.izin_var_mi("/sac-bakim/sampuanlar-c-50301?page=2"))
        self.assertFalse(r.izin_var_mi("/sac-bakim/sampuanlar-c-50301?sort=fiyat"))
        self.assertFalse(r.izin_var_mi("/arama/sampuan"))
        self.assertEqual(r.crawl_delay, 2.0)


class Isleme(unittest.TestCase):
    def isle(self, kartlar, urun="Şampuan", onceki=None):
        return calistir.isle(urun, "Şampuanlar", kartlar, TANIM, LISTE, {}, "Gratis", gratis, onceki)

    def test_tekrar_ve_stok(self):
        kartlar = [kart("Elseve Şampuan 400 ml", ["Elseve Şampuan 400 ml", "149,00 TL"], "/a-p-1"),
                   kart("Elseve Şampuan 400 ml", ["Elseve Şampuan 400 ml", "149,00 TL"], "/a-p-1"),
                   kart("Dove Şampuan 400 ml", ["Dove Şampuan 400 ml", "189,00 TL", "Gelince Haber Ver"],
                        "/b-p-2"),
                   kart("Kuru Şampuan 200 ml", ["Kuru Şampuan 200 ml", "99,00 TL"], "/c-p-3")]
        satirlar, rapor = self.isle(kartlar)
        self.assertEqual(rapor["tekrar"], 1)
        self.assertEqual(rapor["haric"], {"kuru şampuan": 1})
        self.assertEqual(len(satirlar), 2)
        self.assertEqual(satirlar[1]["elendi"], "stok yok")
        self.assertEqual(satirlar[0]["urun_url"], "https://www.gratis.com/a-p-1")
        self.assertEqual(satirlar[0]["eslesme_guveni"], "yuksek")

    def test_fiyat_degisimi_onceki_taramayla(self):
        onceki = {("Şampuan", "Gratis"): {"medyan": "266", "n": "24"}}
        k = lambda f: [kart("Elseve Şampuan 400 ml", ["Elseve Şampuan 400 ml", f], "/a-p-1")]
        self.assertIn("aynı düzeyde", self.isle(k("269,00 TL"), onceki=onceki)[1]["fiyat_degisimi"]["neden"])
        self.assertIn("düştü", self.isle(k("199,00 TL"), onceki=onceki)[1]["fiyat_degisimi"]["neden"])
        self.assertIn("yükseldi", self.isle(k("349,00 TL"), onceki=onceki)[1]["fiyat_degisimi"]["neden"])
        self.assertIn("karşılaştırılamadı", self.isle(k("269,00 TL"), onceki={})[1]["fiyat_degisimi"]["neden"])


class Teslim(unittest.TestCase):
    def satir(self, urun, url, saat_once=1):
        zaman = (datetime.now(ortak.TR) - timedelta(hours=saat_once)).replace(microsecond=0)
        return {"bizim_urun": urun, "urun_url": url, "arac": "playwright", "cekilme_zamani": zaman.isoformat()}

    def test_cift_sayim_kurali(self):
        # Karar 9: aynı adres farklı ürünümüzde olabilir (çok işlevli), aynı ürünümüzde olamaz
        referans = datetime.now(ortak.TR)
        cok_islevli = [self.satir("Nemlendirici", "https://www.gratis.com/x-p-1"),
                       self.satir("Güneş Kremi", "https://www.gratis.com/x-p-1")]
        self.assertEqual(teslim.ajan1_kontrolleri(cok_islevli, referans)[0], [])
        tekrar = cok_islevli + [self.satir("Nemlendirici", "https://www.gratis.com/x-p-1")]
        self.assertTrue(any(s.startswith("tekrar:") for s in teslim.ajan1_kontrolleri(tekrar, referans)[0]))

    def test_tazelik_kapisi(self):
        referans = datetime.now(ortak.TR)
        satirlar = [self.satir("Ruj", "https://www.gratis.com/r-p-1", saat_once=25),
                    self.satir("Şampuan", "https://www.gratis.com/s-p-1", saat_once=2)]
        sorunlar, _ = teslim.ajan1_kontrolleri(satirlar, referans)
        self.assertTrue(any("24 saatten eski" in s for s in sorunlar))
        self.assertEqual(teslim.bayat_urunler(satirlar, referans), ["Ruj"])   # yalnız Ruj yeniden toplanır

    def test_gercek_arac(self):
        s = self.satir("Ruj", "https://www.gratis.com/r-p-1")
        s["arac"] = "sentetik-fixture"
        self.assertTrue(any(".arac" in x for x in teslim.ajan1_kontrolleri([s], datetime.now(ortak.TR))[0]))


if __name__ == "__main__":
    unittest.main()
