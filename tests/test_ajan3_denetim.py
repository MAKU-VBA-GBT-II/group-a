"""Ajan 3 denetim kodu testleri (#116). Bütün girdiler sentetik test verisidir.

python3 -m unittest discover -s tests -p 'test_ajan3_denetim.py'
"""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
import ajan3_denetim as a3  # noqa: E402

REFERANS = "2026-11-29T18:00:00+03:00"


class Ajan3Test(unittest.TestCase):
    def setUp(self):
        gecici = tempfile.TemporaryDirectory()
        self.addCleanup(gecici.cleanup)
        self.tmp = Path(gecici.name)
        with (KOK / "data/ornek-ajan1.csv").open(encoding="utf-8", newline="") as f:
            self.satirlar = list(csv.DictReader(f))
        self.veri = json.loads((KOK / "data/ajan2-cikti-ornek.json").read_text(encoding="utf-8"))
        self.zarf = json.loads((KOK / "data/ajan2-zarf-ornek.json").read_text(encoding="utf-8"))

    def calistir(self, referans=REFERANS):
        ajan1, girdi, zarf = self.tmp / "a1.csv", self.tmp / "a2.json", self.tmp / "a2-zarf.json"
        with ajan1.open("w", encoding="utf-8", newline="") as f:
            yazici = csv.DictWriter(f, list(self.satirlar[0]), lineterminator="\n")
            yazici.writeheader()
            yazici.writerows(self.satirlar)
        girdi.write_text(json.dumps(self.veri, ensure_ascii=False), encoding="utf-8")
        zarf.write_text(json.dumps(self.zarf, ensure_ascii=False), encoding="utf-8")
        argv = ["--girdi", str(girdi), "--zarf", str(zarf), "--ajan1", str(ajan1),
                "--rapor", str(self.tmp / "rapor.json"), "--cikis_zarf", str(self.tmp / "zarf.json"),
                "--iz_klasoru", str(self.tmp / "runs")]
        if referans:
            argv += ["--referans", referans]
        return a3.main(argv)

    def oku(self, ad):
        yol = self.tmp / ad
        return json.loads(yol.read_text(encoding="utf-8")) if yol.exists() else None

    def red_bekle(self, hedef, alan):
        self.assertEqual(self.calistir(), 2)
        zarf = self.oku("zarf.json")
        self.assertEqual((zarf["durum"], zarf["hedef_ajan"]), ("red", hedef))
        self.assertIn(alan, zarf["sorunlu_alanlar"])
        self.assertIsNone(self.oku("rapor.json"))

    def test_dogru_girdi_beklemede_kalir_onay_uretmez(self):
        self.assertEqual(self.calistir(), 3)
        self.assertEqual(self.oku("rapor.json")["durum"], "beklemede")
        self.assertIsNone(self.oku("zarf.json"))
        self.assertEqual(len(list((self.tmp / "runs").glob("*-beklemede.json"))), 1)

    def test_degistirilmis_medyan_ajan2ye_doner(self):
        self.veri["urunler"][0]["rakip_medyan_fiyati"] += 1
        self.red_bekle("ajan2", "urunler[0].rakip_medyan_fiyati")

    def test_degistirilmis_iliski_ajan2ye_doner(self):
        self.veri["iliskiler"]["pearson_fark_adet"] = 0.5
        self.red_bekle("ajan2", "iliskiler.pearson_fark_adet")

    def test_eksik_kaynak_ajan2ye_doner(self):
        self.veri["urunler"][0]["kaynaklar"].pop()
        self.red_bekle("ajan2", "urunler[0].kaynaklar")

    def test_maliyetsiz_kar_iddiasi_reddedilir(self):
        self.veri["urunler"][1]["oneri"]["kar_durumu"] = "denetim_bekliyor"
        self.red_bekle("ajan2", "urunler[1].oneri.kar_durumu")

    def test_sonlu_olmayan_sayi_reddedilir(self):
        self.veri["urunler"][0]["ciro"] = float("nan")
        self.red_bekle("ajan2", "girdi")

    def test_ajan2_red_zarfi_kabul_edilmez(self):
        self.zarf["durum"] = "red"
        self.red_bekle("ajan2", "girdi")

    def test_ham_fiyat_izi_ajan1e_doner(self):
        self.satirlar[0]["ham_fiyat_metni"] = "₺701,00"
        self.red_bekle("ajan1", "satir[2].ham_fiyat_metni")

    def test_baska_alan_adi_ajan1e_doner(self):
        self.satirlar[0]["urun_url"] = "https://ikea.example.com/urun/lamba-a"
        self.red_bekle("ajan1", "satir[2].urun_url")

    def test_bayat_veri_ajan1e_doner(self):
        self.assertEqual(self.calistir("2026-12-01T12:00:00+03:00"), 2)
        zarf = self.oku("zarf.json")
        self.assertEqual(zarf["hedef_ajan"], "ajan1")
        self.assertIn("satir[2].cekilme_zamani", zarf["sorunlu_alanlar"])

    def test_iki_ajan_da_hataliysa_once_ajan1(self):
        self.satirlar[0]["liste_fiyati"] = "NaN"
        self.veri["urunler"][0]["ciro"] = 1
        self.red_bekle("ajan1", "satir[2].liste_fiyati")

    def test_gercek_veride_referans_kullanilamaz_ve_eski_sonuc_silinir(self):
        self.assertEqual(self.calistir(), 3)
        for satir in self.satirlar:
            satir["arac"] = "playwright"
        with self.assertRaises(SystemExit) as hata:
            self.calistir()
        self.assertEqual(hata.exception.code, 1)
        self.assertIsNone(self.oku("rapor.json"))
        self.assertIsNone(self.oku("zarf.json"))


if __name__ == "__main__":
    unittest.main()
