"""Ajan 2 analiz betiği (src/ajan2_analiz.py) için testler. Issue #115.

Çalıştırma: python3 -m unittest discover -s tests -p 'test_ajan2_analiz.py'
"""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
import ajan2_analiz as a2  # noqa: E402

ORNEK = KOK / "data/ornek-ajan1.csv"
REFERANS = "2026-11-29T18:00:00+03:00"


class Ajan2Test(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        with ORNEK.open(encoding="utf-8", newline="") as f:
            self.satirlar = list(csv.DictReader(f))

    def calistir(self, satirlar=None, referans=REFERANS):
        girdi = ORNEK
        if satirlar is not None:
            girdi = self.tmp / "girdi.csv"
            with girdi.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=a2.ALANLAR)
                w.writeheader()
                w.writerows(satirlar)
        kod = a2.main(["--girdi", str(girdi), "--referans", referans,
                       "--cikti", str(self.tmp / "cikti.json"), "--zarf", str(self.tmp / "zarf.json"), "--fiyat", str(self.tmp / "fiyat.csv"),
                       "--iz_klasoru", str(self.tmp / "runs")])
        zarf = json.loads((self.tmp / "zarf.json").read_text(encoding="utf-8"))
        cikti_yolu = self.tmp / "cikti.json"
        cikti = json.loads(cikti_yolu.read_text(encoding="utf-8")) if cikti_yolu.exists() else None
        return kod, zarf, cikti

    def test_ornek_girdi_sozlesme_ornegini_uretir(self):
        kod, zarf, cikti = self.calistir()
        self.assertEqual(kod, 0)
        self.assertEqual((zarf["durum"], zarf["hedef_ajan"], zarf["sorunlu_alanlar"]), ("onay", "ajan3", []))
        beklenen = json.loads((KOK / "data/ornek-ajan2.json").read_text(encoding="utf-8"))
        for d in (cikti, beklenen):
            for u in d["urunler"]:
                u["oneri"].pop("gerekce")
        self.assertEqual(cikti, beklenen)
        self.assertEqual(len(list((self.tmp / "runs").glob("*-onay.json"))), 1)

    def fiyat_oku(self):
        with (self.tmp / "fiyat.csv").open(encoding="utf-8", newline="") as f:
            okuyucu = csv.DictReader(f)
            return okuyucu.fieldnames, list(okuyucu)

    def test_onerilen_fiyat_eylemle_uyumlu(self):
        kod, zarf, cikti = self.calistir()
        self.assertEqual(kod, 0)
        alanlar, satirlar = self.fiyat_oku()
        self.assertEqual(alanlar, ["urun", "onerilen_fiyat_tl", "kaynak", "uretim_zamani"])
        fiyatlar = {s["urun"]: s for s in satirlar}
        for u in cikti["urunler"]:
            eylem = u["oneri"]["eylem"]
            if eylem == "veri_topla":
                self.assertNotIn(u["urun"], fiyatlar)
                continue
            s = fiyatlar[u["urun"]]
            self.assertRegex(s["onerilen_fiyat_tl"], r"^[0-9]+\.[0-9]{2}$")
            self.assertEqual(s["uretim_zamani"], cikti["uretim_zamani"])
            fiyat = float(s["onerilen_fiyat_tl"])
            if eylem == "fiyati_koru":
                self.assertEqual(fiyat, u["bizim_liste_fiyati"])
                self.assertIn("liste_fiyati", s["kaynak"])
            else:
                self.assertEqual(fiyat, u["rakip_medyan_fiyati"])
                self.assertLess(fiyat, u["bizim_liste_fiyati"])
                self.assertIn("rakip_medyan_fiyati", s["kaynak"])
        self.assertEqual(len(satirlar), sum(u["oneri"]["eylem"] != "veri_topla" for u in cikti["urunler"]))

    def test_kampanya_fiyati_rakip_medyani(self):
        u = {"urun": "X", "bizim_liste_fiyati": 1000.0, "rakip_medyan_fiyati": 849.5,
             "oneri": {"eylem": "kampanya_test_et"}}
        k = {"urun": "Y", "bizim_liste_fiyati": 250.0, "rakip_medyan_fiyati": 245.0,
             "oneri": {"eylem": "fiyati_koru"}}
        v = {"urun": "Z", "bizim_liste_fiyati": 399.0, "rakip_medyan_fiyati": None,
             "oneri": {"eylem": "veri_topla"}}
        satirlar = a2.onerilen_fiyatlar([u, k, v], "c.json", "l.csv", REFERANS)
        self.assertEqual([(s["urun"], s["onerilen_fiyat_tl"]) for s in satirlar],
                         [("X", "849.50"), ("Y", "250.00")])

    def test_redde_eski_fiyat_dosyasi_silinir(self):
        self.assertEqual(self.calistir()[0], 0)
        self.assertTrue((self.tmp / "fiyat.csv").exists())
        kod, zarf, _ = self.calistir(referans="2026-12-05T12:00:00+03:00")
        self.assertEqual((kod, zarf["durum"]), (2, "red"))
        self.assertFalse((self.tmp / "fiyat.csv").exists())

    def test_cikti_yolu_girdiyle_ya_da_baska_ciktiyla_cakisamaz(self):
        girdi = self.tmp / "girdi.csv"
        girdi.write_bytes(ORNEK.read_bytes())
        c, z, f = (str(self.tmp / ad) for ad in ("c.json", "z.json", "f.csv"))
        for cikti, zarf_, fiyat in ((c, z, str(girdi)), (c, z, c), (c, c, f), (str(girdi), z, f)):
            with self.assertRaises(SystemExit) as hata:
                a2.main(["--girdi", str(girdi), "--referans", REFERANS, "--cikti", cikti, "--zarf", zarf_,
                         "--fiyat", fiyat, "--iz_klasoru", str(self.tmp / "runs")])
            self.assertEqual(hata.exception.code, 1)
            self.assertEqual(girdi.read_bytes(), ORNEK.read_bytes())

    def test_ayni_urunde_tekrarlanan_adres_reddedilir(self):
        satirlar = [dict(s) for s in self.satirlar]
        kopya = dict(satirlar[0])
        satirlar.append(kopya)
        kod, zarf, cikti = self.calistir(satirlar)
        self.assertEqual((kod, zarf["durum"], zarf["hedef_ajan"]), (2, "red", "ajan1"))
        self.assertEqual(zarf["sorunlu_alanlar"], [f"satir[{len(satirlar) + 1}].urun_url"])
        self.assertIsNone(cikti)

    def test_farkli_urunde_ayni_adres_kabul_edilir(self):
        satirlar = [dict(s) for s in self.satirlar]
        a, b = satirlar[0], next(s for s in satirlar if s["bizim_urun"] != satirlar[0]["bizim_urun"])
        b["urun_url"], b["rakip_site"] = a["urun_url"], a["rakip_site"]
        kod, zarf, _ = self.calistir(satirlar)
        self.assertEqual((kod, zarf["durum"]), (0, "onay"), zarf)

    def test_yalniz_yuksek_guven_medyana_girer(self):
        satirlar = [dict(s) for s in self.satirlar]
        sampuan = next(s for s in satirlar if s["bizim_urun"] == "Şampuan")
        for guven, fiyat in (("orta", "199.00"), ("dusuk", "149.00")):
            ek = dict(sampuan)
            ek.update(eslesme_guveni=guven, liste_fiyati=fiyat, ham_fiyat_metni=f"{fiyat.replace('.', ',')} TL",
                      urun_url=sampuan["urun_url"] + guven)
            satirlar.append(ek)
        kod, zarf, cikti = self.calistir(satirlar)
        self.assertEqual(kod, 0, zarf)
        u = next(u for u in cikti["urunler"] if u["urun"] == "Şampuan")
        self.assertEqual((u["rakip_medyan_fiyati"], u["kullanilan_rakip_sayisi"], u["elenen_rakip_sayisi"]),
                         (239.0, 1, 2))
        secimler = [k["secim"] for k in u["kaynaklar"]]
        self.assertEqual(sum("güven yüksek değil" in s for s in secimler), 2)

    def test_git_z_zaman_bicimi_normalize_edilir(self):
        from unittest import mock
        gercek = a2.subprocess.run

        def sahte(komut, **kw):
            sonuc = gercek(komut, **kw)
            if "log" in komut:
                sonuc.stdout = sonuc.stdout.strip().replace("+00:00", "Z") + "\n"
            return sonuc
        with mock.patch.object(a2.subprocess, "run", side_effect=sahte):
            self.test_ornek_girdi_sozlesme_ornegini_uretir()
        self.assertEqual(a2.datetime.fromisoformat("2026-11-24T12:25:43+00:00").isoformat(),
                         "2026-11-24T12:25:43+00:00")

    def test_tam_72_saat_gecerli_bir_saniye_fazlasi_red(self):
        # en eski satır 2026-11-27T15:00 → sınır 2026-11-30T15:00
        self.assertEqual(self.calistir(referans="2026-11-30T15:00:00+03:00")[0], 0)
        kod, zarf, cikti = self.calistir(referans="2026-11-30T15:00:01+03:00")
        self.assertEqual(kod, 2)
        self.assertEqual((zarf["durum"], zarf["hedef_ajan"]), ("red", "ajan1"))
        self.assertIn("satir[2].cekilme_zamani", zarf["sorunlu_alanlar"])
        self.assertIsNone(cikti)  # red durumunda çıktı yazılmaz

    def test_gelecek_tarih_ve_bozuk_zaman_red(self):
        kod, zarf, _ = self.calistir(referans="2026-11-27T14:00:00+03:00")
        self.assertEqual(kod, 2)
        for zaman in ("dün", "2026-11-27T15:00:00"):
            satirlar = [dict(s) for s in self.satirlar]
            satirlar[1]["cekilme_zamani"] = zaman
            kod, zarf, _ = self.calistir(satirlar)
            self.assertEqual((kod, zarf["sorunlu_alanlar"]), (2, ["satir[3].cekilme_zamani"]))

    def test_eksik_zorunlu_alan_ve_bilinmeyen_urun_red(self):
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[0]["urun_url"] = ""
        satirlar[2]["bizim_urun"] = "Olmayan Ürün"
        kod, zarf, _ = self.calistir(satirlar)
        self.assertEqual(kod, 2)
        self.assertEqual(zarf["sorunlu_alanlar"], ["satir[2].urun_url", "satir[4].bizim_urun"])

    def test_bos_ve_yanlis_baslikli_girdi_red(self):
        kod, zarf, _ = self.calistir([])
        self.assertEqual((kod, zarf["sorunlu_alanlar"]), (2, ["girdi"]))
        yanlis = self.tmp / "yanlis.csv"
        yanlis.write_text("a,b\n1,2\n", encoding="utf-8")
        with self.assertRaises(a2.Red):
            a2.alma(yanlis, KOK / "data/urun-listesi-web.csv", a2.datetime.fromisoformat(REFERANS))

    def test_arama_sayfasi_bulma_yolu_ham_fiyat_ve_elendi_red(self):
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[0]["urun_url"] = "https://ikea.example/search?q=lamba"
        satirlar[1]["bulma_yolu"] = "https://ikea.example/kategori/masa-lambalari"
        satirlar[2]["ham_fiyat_metni"] = "₺699,00"   # indirimli 599 olmalı
        satirlar[3]["elendi"] = "pahalı"
        kod, zarf, _ = self.calistir(satirlar)
        self.assertEqual(kod, 2)
        self.assertEqual(zarf["sorunlu_alanlar"], ["satir[2].urun_url", "satir[3].bulma_yolu",
                                                   "satir[4].ham_fiyat_metni", "satir[5].elendi"])

    def test_nan_fiyat_red_ve_eski_cikti_silinir(self):
        self.assertEqual(self.calistir()[0], 0)  # önce onaylı çıktı ve zarf oluşur
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[0]["liste_fiyati"] = "NaN"
        satirlar[1]["indirimli_fiyat"] = "NaN"
        kod, zarf, cikti = self.calistir(satirlar)
        self.assertEqual(kod, 2)
        self.assertIn("satir[2].liste_fiyati", zarf["sorunlu_alanlar"])
        self.assertIn("satir[3].indirimli_fiyat", zarf["sorunlu_alanlar"])
        self.assertIsNone(cikti)

    def test_alan_adi_rakip_site_ile_uyumlu(self):
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[0]["urun_url"] = "https://koctas.example/urun/lamba-a"  # rakip_site IKEA
        kod, zarf, _ = self.calistir(satirlar)
        self.assertEqual((kod, zarf["sorunlu_alanlar"]), (2, ["satir[2].urun_url"]))

    def test_referans_gercek_veride_kabul_edilmez(self):
        satirlar = [dict(s) for s in self.satirlar]
        for s in satirlar:
            s["arac"] = "playwright"
        self.calistir()  # eski onaylı dosyalar
        with self.assertRaises(SystemExit):
            self.calistir(satirlar)
        self.assertFalse((self.tmp / "cikti.json").exists())
        self.assertFalse((self.tmp / "zarf.json").exists())

    def test_siparis_donemi_birlikte_ve_sirali_olmali(self):
        ortak = ["--girdi", str(ORNEK), "--referans", REFERANS, "--cikti", str(self.tmp / "c.json"),
                 "--zarf", str(self.tmp / "z.json"), "--fiyat", str(self.tmp / "fiyat.csv"), "--iz_klasoru", str(self.tmp / "runs")]
        for ek in (["--baslangic", "2026-07-01", "--bitis", "2026-01-01"], ["--baslangic", "2026-01-01"],
                   ["--bitis", "2026-07-01"], ["--baslangic", "dün", "--bitis", "2026-07-01"]):
            with self.assertRaises(SystemExit):
                a2.main(ortak + ek)
        self.assertEqual(a2.main(ortak + ["--baslangic", "2026-01-05", "--bitis", "2026-01-05"]), 0)

    def test_kullanim_hatasi_1_doner_ve_eski_onay_zarfi_kalmaz(self):
        ortak = ["--girdi", str(ORNEK), "--cikti", str(self.tmp / "cikti.json"),
                 "--zarf", str(self.tmp / "zarf.json"), "--fiyat", str(self.tmp / "fiyat.csv"), "--iz_klasoru", str(self.tmp / "runs")]
        for ek in (["--referans", REFERANS, "--baslangic", "2026-07-01", "--bitis", "2026-01-01"],
                   ["--referans", REFERANS, "--baslangic", "2026-01-01"],
                   ["--referans", REFERANS, "--baslangic", "dün", "--bitis", "2026-07-01"],
                   ["--referans", "2026-11-29T18:00:00"], ["--referans", "yarın"]):
            self.assertEqual(self.calistir()[0], 0)  # eski onay zarfı ve çıktı
            with self.assertRaises(SystemExit) as hata:
                a2.main(ortak + ek)
            self.assertEqual(hata.exception.code, 1, ek)
            self.assertFalse((self.tmp / "zarf.json").exists(), ek)
            self.assertFalse((self.tmp / "cikti.json").exists(), ek)
            self.assertFalse((self.tmp / "fiyat.csv").exists(), ek)

    def test_alan_adi_sonek_eslesmesi(self):
        f = a2._site_uyumlu
        self.assertTrue(f("https://www.ikea.com.tr/urun/x", "IKEA"))
        self.assertTrue(f("https://ikea.com.tr/urun/x", "IKEA"))
        self.assertFalse(f("https://ikea.example.com/urun/x", "IKEA"))
        self.assertFalse(f("https://kotuikea.com.tr/urun/x", "IKEA"))
        self.assertFalse(f("https://ikea.example/urun/x", "IKEA"))  # sentetik değilse
        self.assertTrue(f("https://ikea.example/urun/x", "IKEA", sentetik=True))
        self.assertTrue(f("https://www.dr.com.tr/urun/x", "D&R"))

    def test_stok_yok_ve_kdv_haric_medyana_girmez(self):
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[2]["stok_durumu"] = "yok"      # Saklama set-a
        satirlar[3]["kdv_dahil"] = "hayir"      # Saklama set-b
        _, _, cikti = self.calistir(satirlar)
        saklama = next(u for u in cikti["urunler"] if u["urun"] == "Saklama Kabı Seti")
        self.assertIsNone(saklama["rakip_medyan_fiyati"])
        self.assertIsNone(saklama["fiyat_farki_yuzde"])
        self.assertEqual((saklama["kullanilan_rakip_sayisi"], saklama["elenen_rakip_sayisi"]), (0, 2))
        self.assertEqual(saklama["oneri"]["eylem"], "veri_topla")
        secimler = [k["secim"] for k in saklama["kaynaklar"]]
        self.assertTrue(any("elendi: stok yok" in s for s in secimler))
        self.assertTrue(any("KDV temeli" in s for s in secimler))
        self.assertEqual(cikti["iliskiler"]["urun_sayisi"], 2)

    def test_saklama_kabi_seti_istisnasi(self):
        satirlar = [dict(s) for s in self.satirlar]
        satirlar[2]["elendi"] = "çoklu paket"
        _, _, cikti = self.calistir(satirlar)
        saklama = next(u for u in cikti["urunler"] if u["urun"] == "Saklama Kabı Seti")
        self.assertEqual(saklama["kullanilan_rakip_sayisi"], 2)

    def test_masa_lambasi_sinirlamasi_veri_topla(self):
        _, _, cikti = self.calistir()
        lamba = next(u for u in cikti["urunler"] if u["urun"] == "Masa Lambası")
        self.assertEqual(lamba["oneri"]["eylem"], "veri_topla")
        self.assertIn("karar 5", lamba["oneri"]["gerekce"])
        self.assertEqual(lamba["elenen_rakip_sayisi"], 1)

    def test_tek_urunde_pearson_null(self):
        _, _, cikti = self.calistir([self.satirlar[4]])
        self.assertEqual(cikti["iliskiler"]["urun_sayisi"], 1)
        self.assertIsNone(cikti["iliskiler"]["pearson_fark_adet"])
        self.assertIsNone(cikti["iliskiler"]["pearson_fark_ciro"])

    def test_kar_iddiasi_yok(self):
        _, _, cikti = self.calistir()
        self.assertTrue(all(u["oneri"]["kar_durumu"] == "maliyet_eksik" for u in cikti["urunler"]))


if __name__ == "__main__":
    unittest.main()
