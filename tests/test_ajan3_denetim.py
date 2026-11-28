"""Ajan 3 denetim kodu testleri (#116). Bütün girdiler sentetik test verisidir.

python3 -m unittest discover -s tests -p 'test_ajan3_denetim.py'
"""

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
import ajan3_denetim as a3  # noqa: E402

REFERANS = "2026-11-29T18:00:00+03:00"
URETIM = "2026-11-29T17:00:00+03:00"


class Ajan3Test(unittest.TestCase):
    def setUp(self):
        gecici = tempfile.TemporaryDirectory()
        self.addCleanup(gecici.cleanup)
        self.tmp = Path(gecici.name)
        with (KOK / "data/ornek-ajan1.csv").open(encoding="utf-8", newline="") as f:
            self.satirlar = list(csv.DictReader(f))
        self.veri = json.loads((KOK / "data/ajan2-cikti-ornek.json").read_text(encoding="utf-8"))
        self.zarf = json.loads((KOK / "data/ajan2-zarf-ornek.json").read_text(encoding="utf-8"))

    def tablo(self, ad, deger_alani, satirlar):
        """satirlar: (urun, deger) ya da (urun, deger, kaynak, zaman). None → dosya verilmez."""
        if satirlar is None:
            return None
        yol = self.tmp / ad
        with yol.open("w", encoding="utf-8", newline="") as f:
            yazici = csv.writer(f, lineterminator="\n")
            yazici.writerow(["urun", deger_alani, "kaynak", "uretim_zamani"])
            for s in satirlar:
                yazici.writerow(s if len(s) == 4 else (*s, "sentetik_test:birim", URETIM))
        return yol

    def calistir(self, referans=REFERANS, fiyat=None, maliyet=None, md5=None, canli=None, ek=()):
        ajan1, girdi, zarf = self.tmp / "a1.csv", self.tmp / "a2.json", self.tmp / "a2-zarf.json"
        with ajan1.open("w", encoding="utf-8", newline="") as f:
            yazici = csv.DictWriter(f, list(self.satirlar[0]), lineterminator="\n")
            yazici.writeheader()
            yazici.writerows(self.satirlar)
        girdi.write_text(json.dumps(self.veri, ensure_ascii=False), encoding="utf-8")
        zarf.write_text(json.dumps(self.zarf, ensure_ascii=False), encoding="utf-8")
        argv = ["--girdi", str(girdi), "--zarf", str(zarf), "--ajan1", str(ajan1),
                "--ajan1_md5", md5 or hashlib.md5(ajan1.read_bytes()).hexdigest(),
                "--rapor", str(self.tmp / "rapor.json"), "--nihai_rapor", str(self.tmp / "nihai.json"),
                "--cikis_zarf", str(self.tmp / "zarf.json"), "--iz_klasoru", str(self.tmp / "runs")]
        for secenek, yol in (("--fiyat", self.tablo("fiyat.csv", "onerilen_fiyat_tl", fiyat)),
                             ("--maliyet", self.tablo("maliyet.csv", "birim_maliyet_tl", maliyet))):
            if yol:
                argv += [secenek, str(yol)]
        if canli is not None:
            argv += ["--canli_kontrol", str(self.canli_tablosu(canli))]
        if referans:
            argv += ["--referans", referans]
        return a3.main(argv + list(ek))

    def canli_tablosu(self, satirlar):
        """satirlar: (urun, urun_url, sayfa_fiyati, kaynak, zaman)."""
        yol = self.tmp / "canli.csv"
        with yol.open("w", encoding="utf-8", newline="") as f:
            yazici = csv.writer(f, lineterminator="\n")
            yazici.writerow(a3.CANLI_ALANLARI)
            yazici.writerows(satirlar)
        return yol

    def gercek_veri(self):
        """Sentetik örneği 'gerçek veri' biçimine çevirir (ağ isteği yok). Çekim zamanını döner."""
        gecici = tempfile.TemporaryDirectory(dir=KOK / "tests")  # gerçek veride CSV repo içinde olmalı
        self.addCleanup(gecici.cleanup)
        self.tmp = Path(gecici.name)
        simdi = datetime.now(a3.TR).replace(microsecond=0)
        cekim = (simdi - timedelta(hours=2)).isoformat()
        yeni_adres = {}
        for satir in self.satirlar:
            eski = satir["urun_url"]
            satir["urun_url"] = yeni_adres[eski] = (eski.replace("ikea.example", "ikea.com.tr")
                                                    .replace("koctas.example", "koctas.com.tr")
                                                    .replace("gratis.example", "gratis.com"))
            satir["cekilme_zamani"], satir["arac"] = cekim, "playwright"
        self.veri["veri_turu"] = "web_ve_sentetik_siparis"
        for urun in self.veri["urunler"]:
            for kayit in urun["kaynaklar"]:
                if kayit["kaynak"] in yeni_adres:
                    kayit.update(kaynak=yeni_adres[kayit["kaynak"]], uretim_zamani=cekim)
        return simdi

    def sampuan_kontrolu(self, an, **degisen):
        satir = next(s for s in self.satirlar if s["bizim_urun"] == "Şampuan")
        kayit = {"urun": "Şampuan", "urun_url": satir["urun_url"], "sayfa_fiyati_tl": "239.00",
                 "kaynak": "sentetik_test:elle-kontrol", "uretim_zamani": an.isoformat()}
        kayit.update(degisen)
        return tuple(kayit[a] for a in a3.CANLI_ALANLARI)

    def oku(self, ad):
        yol = self.tmp / ad
        return json.loads(yol.read_text(encoding="utf-8")) if yol.exists() else None

    def red_bekle(self, hedef, alan, **girdiler):
        self.assertEqual(self.calistir(**girdiler), 2)
        zarf = self.oku("zarf.json")
        self.assertEqual((zarf["durum"], zarf["hedef_ajan"]), ("red", hedef))
        self.assertIn(alan, zarf["sorunlu_alanlar"])
        self.assertIsNone(self.oku("rapor.json"))
        self.assertIsNone(self.oku("nihai.json"))

    def beklemede_bekle(self, neden, **girdiler):
        self.assertEqual(self.calistir(**girdiler), 3)
        self.assertIn(neden, self.oku("rapor.json")["bekleme_nedeni"])
        self.assertIsNone(self.oku("zarf.json"))
        self.assertIsNone(self.oku("nihai.json"))

    def test_kar_esigi_gecince_nihai_rapor_ve_onay_zarfi(self):
        self.assertEqual(self.calistir(fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")]), 0)
        zarf, rapor = self.oku("zarf.json"), self.oku("nihai.json")
        self.assertEqual((zarf["durum"], zarf["hedef_ajan"], zarf["sorunlu_alanlar"]), ("onay", None, []))
        self.assertEqual(rapor["zarf"], zarf)
        self.assertEqual([u["urun"] for u in rapor["urunler"]], ["Şampuan"])
        kalem = rapor["urunler"][0]
        self.assertEqual((kalem["birim_kar_tl"], kalem["esik_tl"], kalem["karar"]), (30.0, 0.0, "onay"))
        self.assertEqual(len(rapor["ajan1_csv"]["md5"]), 32)
        self.assertEqual(rapor["yapilmayan_kontroller"], [a3.CANLI])
        self.assertIsNone(self.oku("rapor.json"))
        self.assertEqual(len(list((self.tmp / "runs").glob("*-onay.json"))), 1)

    def test_sifir_ve_negatif_kar_ajan2ye_doner_ve_tum_alanlar_listelenir(self):
        fiyat = [("Şampuan", "220.00"), ("Masa Lambası", "100.00")]
        maliyet = [("Şampuan", "220.00"), ("Masa Lambası", "150.00")]
        self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl", fiyat=fiyat, maliyet=maliyet)
        self.assertIn("fiyat.satir[3].onerilen_fiyat_tl", self.oku("zarf.json")["sorunlu_alanlar"])

    def test_bir_kurus_kar_onaylanir(self):
        self.assertEqual(self.calistir(fiyat=[("Şampuan", "220.01")], maliyet=[("Şampuan", "220.00")]), 0)

    def test_md5_uyusmazsa_ajan1e_doner(self):
        self.red_bekle("ajan1", "ajan1_csv.md5", md5="0" * 32)

    def test_maliyet_dosyasi_yoksa_beklemede(self):
        self.beklemede_bekle("Şampuan için geçerli birim maliyet yok", fiyat=[("Şampuan", "250.00")])

    def test_fiyat_yoksa_beklemede(self):
        self.beklemede_bekle("önerilen fiyat girdisi yok", maliyet=[("Şampuan", "220.00")])

    def test_bos_fiyat_dosyasi_onay_uretmez(self):
        self.beklemede_bekle("önerilen fiyat girdisi yok", fiyat=[], maliyet=[("Şampuan", "220.00")])

    def test_bir_urunun_maliyeti_eksikse_kismi_onay_yok(self):
        self.beklemede_bekle("Masa Lambası için geçerli birim maliyet yok",
                             fiyat=[("Şampuan", "250.00"), ("Masa Lambası", "500.00")],
                             maliyet=[("Şampuan", "220.00")])

    def test_gecersiz_maliyet_onay_uretmez(self):
        durumlar = [[("Şampuan", "-1")], [("Şampuan", "NaN")], [("Şampuan", "220.001")],
                    [("Şampuan", "220", "", URETIM)], [("Şampuan", "220", "k", "2026-11-29T17:00:00")],
                    [("Şampuan", "220"), ("Şampuan", "10")]]
        for maliyet in durumlar:
            with self.subTest(maliyet=maliyet):
                self.beklemede_bekle("maliyet", fiyat=[("Şampuan", "250.00")], maliyet=maliyet)

    def test_gecersiz_fiyat_ve_bilinmeyen_urun_ajan2ye_doner(self):
        maliyet = [("Şampuan", "220.00")]
        self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl", fiyat=[("Şampuan", "0")], maliyet=maliyet)
        self.red_bekle("ajan2", "fiyat.satir[2].urun", fiyat=[("Olmayan", "250.00")], maliyet=maliyet)

    def test_denetim_bekliyor_yalniz_maliyet_varsa_kabul_edilir(self):
        self.veri["urunler"][2]["oneri"]["kar_durumu"] = "denetim_bekliyor"
        self.assertEqual(self.calistir(fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")]), 0)
        self.red_bekle("ajan2", "urunler[2].oneri.kar_durumu")

    def test_kaynak_ve_hesap_hatasi_kardan_once_gelir(self):
        girdi = dict(fiyat=[("Şampuan", "200.00")], maliyet=[("Şampuan", "220.00")])
        self.veri["urunler"][0]["ciro"] += 1
        self.red_bekle("ajan2", "urunler[0].ciro", **girdi)
        self.satirlar[0]["para_birimi"] = "USD"
        self.red_bekle("ajan1", "satir[2].para_birimi", **girdi)

    def test_onceki_onay_sonraki_redde_silinir(self):
        girdi = dict(fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")])
        self.assertEqual(self.calistir(**girdi), 0)
        self.red_bekle("ajan1", "ajan1_csv.md5", md5="0" * 32, **girdi)
        self.assertEqual(self.oku("zarf.json")["durum"], "red")

    def test_dogru_girdi_beklemede_kalir_onay_uretmez(self):
        self.assertEqual(self.calistir(), 3)
        self.assertEqual(self.oku("rapor.json")["durum"], "beklemede")
        self.assertIsNone(self.oku("zarf.json"))
        self.assertEqual(len(list((self.tmp / "runs").glob("*-beklemede.json"))), 1)

    def test_isaretlenmemis_bant_disi_satir_medyana_girmez(self):
        self.satirlar[1]["elendi"] = ""  # 1499 TL > 3 x 399 TL
        self.assertEqual(self.calistir(), 3)

    def test_bant_siniri_medyana_dahildir(self):
        self.satirlar[1].update(elendi="", liste_fiyati="1197.00", ham_fiyat_metni="₺1.197,00")
        self.red_bekle("ajan2", "urunler[0].rakip_medyan_fiyati")

    def test_try_disi_para_birimi_ajan1e_doner(self):
        self.satirlar[0]["para_birimi"] = "USD"
        self.red_bekle("ajan1", "satir[2].para_birimi")

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


    def test_veri_topla_urunu_kar_yeterli_olsa_da_beklemede(self):
        self.beklemede_bekle("Masa Lambası için Ajan 2 eylemi veri_topla",
                             fiyat=[("Şampuan", "250.00"), ("Masa Lambası", "1000.00")],
                             maliyet=[("Şampuan", "220.00"), ("Masa Lambası", "1.00")])

    def test_veri_topla_urununde_esik_alti_kar_yine_red(self):
        self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl",
                       fiyat=[("Masa Lambası", "100.00")], maliyet=[("Masa Lambası", "150.00")])

    def test_bozuk_adres_cokmeden_ajan1e_doner(self):
        self.satirlar[0]["urun_url"] = "https://[bozuk"
        self.red_bekle("ajan1", "satir[2].urun_url")

    def test_yanlis_tipte_oneri_alani_cokmeden_ajan2ye_doner(self):
        asil = json.dumps(self.veri)
        for alan in ("eylem", "kar_durumu"):
            for deger in (["x"], {"a": 1}, 5, None):
                with self.subTest(alan=alan, deger=deger):
                    self.veri = json.loads(asil)
                    self.veri["urunler"][0]["oneri"][alan] = deger
                    self.red_bekle("ajan2", f"urunler[0].oneri.{alan}")

    def test_float_a_sigmayan_sayi_cokmeden_ajan2ye_doner(self):
        self.veri["urunler"][0]["satis_adedi"] = 10 ** 400
        self.red_bekle("ajan2", "urunler[0].satis_adedi")


    def test_bulunamayan_girdi_yolu_kullanim_hatasi_ve_eski_sonuc_silinir(self):
        girdi = dict(fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")])
        for secenek in ("--fiyat", "--maliyet", "--canli_kontrol"):
            for yol in (str(self.tmp / "YOK.csv"), str(self.tmp), ""):
                with self.subTest(secenek=secenek, yol=yol):
                    self.assertEqual(self.calistir(**girdi), 0)
                    with self.assertRaises(SystemExit) as hata:
                        self.calistir(**girdi, ek=[secenek, yol])
                    self.assertEqual(hata.exception.code, 1)
                    for ad in ("zarf.json", "nihai.json", "rapor.json"):
                        self.assertIsNone(self.oku(ad))

    def test_fiyati_koru_yalniz_liste_fiyatina_esitse_onaylanir(self):
        maliyet = [("Saklama Kabı Seti", "300.00")]
        for deger in ("639", "639.00"):
            self.assertEqual(self.calistir(fiyat=[("Saklama Kabı Seti", deger)], maliyet=maliyet), 0)
        for deger in ("900.00", "638.99", "639.01"):
            with self.subTest(deger=deger):
                self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl",
                               fiyat=[("Saklama Kabı Seti", deger)], maliyet=maliyet)

    def test_kampanya_yalniz_liste_fiyatindan_dusukse_onaylanir(self):
        maliyet = [("Şampuan", "220.00")]
        self.assertEqual(self.calistir(fiyat=[("Şampuan", "268.99")], maliyet=maliyet), 0)
        for deger in ("269.00", "300.00"):
            with self.subTest(deger=deger):
                self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl",
                               fiyat=[("Şampuan", deger)], maliyet=maliyet)

    def test_eyleme_uymayan_fiyat_maliyet_eksik_olsa_da_red(self):
        self.red_bekle("ajan2", "fiyat.satir[2].onerilen_fiyat_tl", fiyat=[("Şampuan", "300.00")])

    def test_gercek_veride_canli_kontrol_kaydi_yoksa_beklemede(self):
        self.gercek_veri()
        self.beklemede_bekle("Şampuan için geçerli elle canlı fiyat kontrol kaydı yok", referans=None,
                             fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")])

    def test_gercek_veride_gecerli_canli_kontrol_kaydiyla_onay(self):
        simdi = self.gercek_veri()
        self.assertEqual(self.calistir(None, fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")],
                                       canli=[self.sampuan_kontrolu(simdi)]), 0)
        rapor = self.oku("nihai.json")
        self.assertEqual(rapor["yapilmayan_kontroller"], [])
        self.assertIn(a3.CANLI_KAYDI, rapor["gecen_kontroller"])
        self.assertEqual(rapor["urunler"][0]["canli_kontrol"][0]["sayfa_fiyati_tl"], 239.0)

    def test_gecersiz_canli_kontrol_kaydi_onay_uretmez(self):
        simdi = self.gercek_veri()
        durumlar = {
            "baska adres": dict(urun_url="https://www.gratis.com/urun/baska"),
            "bos kaynak": dict(kaynak=""),
            "bozuk fiyat": dict(sayfa_fiyati_tl="239,00"),
            "saat dilimsiz": dict(uretim_zamani=simdi.replace(tzinfo=None).isoformat()),
            "gelecekte": dict(uretim_zamani=(simdi + timedelta(hours=1)).isoformat()),
            "cekimden once": dict(uretim_zamani=(simdi - timedelta(hours=3)).isoformat()),
            "bayat": dict(uretim_zamani=(simdi - timedelta(hours=73)).isoformat()),
        }
        for ad, degisen in durumlar.items():
            with self.subTest(ad):
                self.beklemede_bekle("canlı kontrol dosyasında satır 2 geçersiz", referans=None,
                                     fiyat=[("Şampuan", "250.00")], maliyet=[("Şampuan", "220.00")],
                                     canli=[self.sampuan_kontrolu(simdi, **degisen)])

    def test_bir_urunun_canli_kaydi_eksikse_kismi_onay_yok(self):
        simdi = self.gercek_veri()
        self.beklemede_bekle("Saklama Kabı Seti için geçerli elle canlı fiyat kontrol kaydı yok", referans=None,
                             fiyat=[("Şampuan", "250.00"), ("Saklama Kabı Seti", "639.00")],
                             maliyet=[("Şampuan", "220.00"), ("Saklama Kabı Seti", "300.00")],
                             canli=[self.sampuan_kontrolu(simdi)])

    def test_sayfa_fiyati_uyusmazsa_ajan2_hatasindan_once_ajan1e_doner(self):
        simdi = self.gercek_veri()
        self.veri["urunler"][0]["ciro"] += 1
        self.red_bekle("ajan1", "satir[6].liste_fiyati", referans=None,
                       canli=[self.sampuan_kontrolu(simdi, sayfa_fiyati_tl="249.00")])

    def test_sentetik_veride_uyusmayan_canli_kayit_da_red(self):
        an = datetime.fromisoformat(URETIM)
        self.red_bekle("ajan1", "satir[6].liste_fiyati",
                       canli=[self.sampuan_kontrolu(an, sayfa_fiyati_tl="249.00")])


if __name__ == "__main__":
    unittest.main()
