"""Duyuru 11 sözleşmesinin sentetik örnekleri için bağımsız uyum kontrolleri."""
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import statistics
import unittest
from urllib.parse import urlparse

DATA = Path(__file__).resolve().parents[1] / "data"
FIELDS = (
    "bizim_urun kategori rakip_urun_adi eslesme_yontemi eslesme_guveni "
    "birim_miktar ham_fiyat_metni liste_fiyati indirimli_fiyat fiyat_turu "
    "kdv_dahil para_birimi stok_durumu rakip_site urun_url bulma_yolu "
    "cekilme_zamani arac elendi"
).split()
OPTIONAL = {"birim_miktar", "indirimli_fiyat", "elendi"}
REFERENCE = datetime.fromisoformat("2026-11-29T18:00:00+03:00")


def csv_rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def conflicts(rows, reference):
    """Test oracle: sabit veya üretim saatiyle kullanılır."""
    errors = []
    for line, row in enumerate(rows, 2):
        for key in FIELDS:
            if key not in OPTIONAL and not row.get(key):
                errors.append(f"satir[{line}].{key}")
        if row.get("cekilme_zamani"):
            try:
                observed = datetime.fromisoformat(row["cekilme_zamani"])
                if observed.utcoffset() != timedelta(hours=3):
                    raise ValueError
                if not timedelta() <= reference - observed <= timedelta(hours=72):
                    raise ValueError
            except ValueError:
                errors.append(f"satir[{line}].cekilme_zamani")
    return errors


class MesajBicimiTest(unittest.TestCase):
    def setUp(self):
        self.header, self.rivals = csv_rows("ornek-ajan1.csv")
        self.catalog = {row["urun"]: row for row in csv_rows("urun-listesi-web.csv")[1]}
        self.payload = json.loads((DATA / "ornek-ajan2.json").read_text(encoding="utf-8"))

    def test_csv_19_sutun_ve_fiyatlar(self):
        self.assertEqual(self.header, FIELDS)
        self.assertTrue(self.rivals)
        self.assertEqual(conflicts(self.rivals, REFERENCE), [])
        for row in self.rivals:
            self.assertEqual(set(row), set(FIELDS))
            self.assertEqual(row["kategori"], self.catalog[row["bizim_urun"]]["kategori"])
            self.assertTrue(row["rakip_urun_adi"].startswith("[TEST]"))
            self.assertTrue(urlparse(row["urun_url"]).hostname.endswith(".example"))
            self.assertRegex(row["bulma_yolu"], r"^https://[^ ]+ s\.[1-9]\d*$")
            self.assertEqual(row["arac"], "sentetik-fixture")
            self.assertEqual(row["eslesme_yontemi"], "benzer")
            self.assertIn(row["eslesme_guveni"], ("yuksek", "orta", "dusuk"))
            self.assertIn(row["rakip_site"], ("MediaMarkt", "Gratis", "D&R", "Koçtaş", "IKEA", "Koton"))
            self.assertEqual((row["para_birimi"], row["kdv_dahil"], row["stok_durumu"]), ("TRY", "evet", "var"))
            self.assertRegex(row["liste_fiyati"], r"^\d+\.\d{2}$")
            listed = Decimal(row["liste_fiyati"])
            self.assertGreater(listed, 0)
            comparison = listed
            if row["indirimli_fiyat"]:
                self.assertRegex(row["indirimli_fiyat"], r"^\d+\.\d{2}$")
                comparison = Decimal(row["indirimli_fiyat"])
                self.assertGreater(comparison, 0)
                self.assertLess(comparison, listed)
                self.assertIn(row["fiyat_turu"], ("indirimli", "kampanya"))
            else:
                self.assertEqual(row["fiyat_turu"], "liste")
            raw = row["ham_fiyat_metni"].removeprefix("₺").replace(".", "").replace(",", ".")
            self.assertEqual(Decimal(raw), comparison)

    def test_bayatlik_tam_72_saat_ve_kontrollu_referans(self):
        row = self.rivals[0]
        observed = datetime.fromisoformat(row["cekilme_zamani"])
        boundary = observed + timedelta(hours=72)
        self.assertEqual(conflicts([row], boundary), [])
        self.assertEqual(conflicts([row], boundary + timedelta(seconds=1)), ["satir[2].cekilme_zamani"])
        self.assertEqual(conflicts([row], observed - timedelta(seconds=1)), ["satir[2].cekilme_zamani"])

    def test_eksik_alan_ve_bozuk_zaman_red(self):
        for timestamp in ("", "dün", "2026-11-27T15:00:00"):
            bad = {**self.rivals[0], "urun_url": "", "cekilme_zamani": timestamp}
            fields = conflicts([bad], REFERENCE)
            self.assertEqual(set(fields), {"satir[2].urun_url", "satir[2].cekilme_zamani"})

    def assert_sources(self, entries, numeric_fields):
        covered = set()
        for source in entries:
            self.assertEqual(set(source), {"kaynak", "secim", "uretim_zamani", "alanlar"})
            self.assertTrue(source["kaynak"] and source["secim"] and source["alanlar"])
            self.assertIsInstance(source["alanlar"], list)
            self.assertIsNotNone(datetime.fromisoformat(source["uretim_zamani"]).utcoffset())
            covered.update(source["alanlar"])
        self.assertEqual(covered, numeric_fields)

    def test_json_hesaplar_ve_kaynaklar(self):
        payload = self.payload
        self.assertEqual(set(payload), {"surum", "veri_turu", "para_birimi", "uretim_zamani",
                                        "siparis_donemi", "urunler", "iliskiler"})
        self.assertEqual((payload["surum"], payload["veri_turu"], payload["para_birimi"]),
                         ("1", "sentetik_test", "TRY"))
        self.assertEqual(datetime.fromisoformat(payload["uretim_zamani"]), REFERENCE)
        dates = payload["siparis_donemi"]
        self.assertEqual(set(dates), {"baslangic", "bitis"})
        start, end = (date.fromisoformat(dates[key]) for key in ("baslangic", "bitis"))
        self.assertLessEqual(start, end)
        orders = csv_rows("siparisler-web.csv")[1]
        products = payload["urunler"]
        names = [item["urun"] for item in products]
        self.assertCountEqual(names, {row["bizim_urun"] for row in self.rivals})
        gaps, volumes, revenues = [], [], []
        numeric = {"bizim_liste_fiyati", "rakip_medyan_fiyati", "fiyat_farki_yuzde",
                   "kullanilan_rakip_sayisi", "elenen_rakip_sayisi", "satis_adedi", "ciro"}
        for item in products:
            self.assertEqual(set(item), numeric | {"urun", "kategori", "oneri", "kaynaklar"})
            name = item["urun"]
            self.assertEqual(item["kategori"], self.catalog[name]["kategori"])
            own = Decimal(self.catalog[name]["liste_fiyati"])
            rivals = [row for row in self.rivals if row["bizim_urun"] == name]
            eligible = []
            for row in rivals:
                price = Decimal(row["indirimli_fiyat"] or row["liste_fiyati"])
                outside_band = price < own * Decimal("0.3") or price > own * 3
                self.assertEqual(row["elendi"], "fiyat bandı dışı" if outside_band else "")
                if not outside_band:
                    eligible.append(price)
            median = statistics.median(eligible)
            gap = 100 * (own - median) / median
            sales = [row for row in orders if row["urun"] == name and row["durum"] == "Teslim Edildi"
                     and start <= date.fromisoformat(row["siparis_tarihi"]) <= end]
            volume = sum(int(row["adet"]) for row in sales)
            revenue = sum(Decimal(row["toplam_tutar"]) for row in sales)
            expected = dict(bizim_liste_fiyati=float(own), rakip_medyan_fiyati=float(median),
                            fiyat_farki_yuzde=float(round(gap, 2)), kullanilan_rakip_sayisi=len(eligible),
                            elenen_rakip_sayisi=len(rivals)-len(eligible), satis_adedi=volume, ciro=float(revenue))
            for key, value in expected.items():
                self.assertIn(type(item[key]), (int, float))
                self.assertEqual(item[key], value, key)
            for key in ("kullanilan_rakip_sayisi", "elenen_rakip_sayisi", "satis_adedi"):
                self.assertIs(type(item[key]), int)
            self.assert_sources(item["kaynaklar"], numeric)
            rival_sources = {(s["kaynak"], s["uretim_zamani"]) for s in item["kaynaklar"]
                             if s["kaynak"].startswith("https://")}
            self.assertEqual(rival_sources, {(r["urun_url"], r["cekilme_zamani"]) for r in rivals})
            self.assertEqual(set(item["oneri"]), {"eylem", "gerekce", "kar_durumu"})
            self.assertIn(item["oneri"]["eylem"], ("fiyati_koru", "kampanya_test_et", "veri_topla"))
            self.assertTrue(item["oneri"]["gerekce"])
            self.assertEqual(item["oneri"]["kar_durumu"], "maliyet_eksik")
            gaps.append(float(gap))
            volumes.append(volume)
            revenues.append(float(revenue))
        relations = payload["iliskiler"]
        metrics = {"urun_sayisi", "pearson_fark_adet", "pearson_fark_ciro"}
        self.assertEqual(set(relations), metrics | {"kaynaklar"})
        self.assert_sources(relations["kaynaklar"], metrics)
        self.assertEqual(relations["urun_sayisi"], len(gaps))
        self.assertEqual(relations["pearson_fark_adet"], round(statistics.correlation(gaps, volumes), 6))
        self.assertEqual(relations["pearson_fark_ciro"], round(statistics.correlation(gaps, revenues), 6))

    def test_belgedeki_red_zarfi(self):
        document = (DATA.parent / "docs/mesaj-bicimi.md").read_text(encoding="utf-8")
        rejection = json.loads(document.split("```json\n")[1].split("\n```")[0])
        self.assertEqual(set(rejection), {"durum", "hedef_ajan", "gerekce", "sorunlu_alanlar"})
        self.assertEqual((rejection["durum"], rejection["hedef_ajan"]), ("red", "ajan1"))
        self.assertTrue(rejection["gerekce"])
        self.assertEqual(rejection["sorunlu_alanlar"], ["satir[2].cekilme_zamani"])
