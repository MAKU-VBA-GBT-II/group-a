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
                       "--cikti", str(self.tmp / "cikti.json"), "--zarf", str(self.tmp / "zarf.json"),
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
