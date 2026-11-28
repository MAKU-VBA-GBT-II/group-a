"""Ajan 1'i çalıştırır: kartları alır, işler, tabloyu ve çalışma raporunu yazar.

Kullanım (repo kökünden):  python -m src.ajan1.calistir
Yalnız bazı ürünleri yeniden toplamak için:  python -m src.ajan1.calistir --urun Ruj --urun Şampuan
Çıktılar: data/ajan1-cikti.csv ve runs/ajan1/<zaman>.json
Teslim kontrolleri (ajan1-teslim §1) ayrı adımda: python -m src.ajan1.teslim
"""
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

from . import gratis, ikea, ortak

SITELER = [gratis, ikea]   # yeni site: ajan1-kaynak-ekleme

CIKTI = ortak.KOK / "data" / "ajan1-cikti.csv"
RAPOR_KLASORU = ortak.KOK / "runs" / "ajan1"


def isle(urun, kat_adi, kartlar, tanim, liste_fiyatlari, rozetler, site, modul=gratis, onceki=None):
    """ajan1-isleme: fiyat okuma, eşleştirme, eleme, tekrar ayıklama, rapor notları."""
    kategori, liste = liste_fiyatlari[urun]
    t = tanim[urun]
    satirlar, gorulen = [], set()
    rapor = {"okunan_kart": len(kartlar), "haric": Counter(), "kararsiz": [],
             "kosullu_fiyat": Counter(), "kosullu_ornek": [], "bilinmeyen_fiyat_etiketi": [],
             "rozet": Counter(), "taninmayan_rozet": [], "fiyat_okunamadi": [], "stokta_yok_fiyatsiz": [],
             "ustu_cizili_dogrulanamadi": [], "tekrar": 0, "elendi": Counter(),
             "kampanya_bitisleri": []}
    for k in kartlar:
        if not k.get("url") or not k.get("ad"):
            continue
        url = (k["url"] if k["url"].startswith("http") else modul.ALAN + k["url"]).split("?")[0]
        if url in gorulen:
            rapor["tekrar"] += 1
            continue
        gorulen.add(url)

        karar, ayrinti = ortak.eslestir(k["ad"], t, kat_adi)
        if karar == "haric":
            rapor["haric"][ayrinti] += 1
            continue
        if karar == "kararsiz":
            rapor["kararsiz"].append({"ad": k["ad"], "url": url})
            continue

        stokta_yok = any(re.search(r"tükendi|stokta yok|gelince haber ver", s, re.I) for s in k["satirlar"])
        f = modul.kart_fiyatlari(k["satirlar"], k["ad"], k.get("ustu_cizili", ()))
        if f is None:
            # Gratis stokta olmayan ürünün fiyatını göstermiyor, yerine "Gelince Haber Ver"
            # yazıyor (28 Kasım, 4 güneş ürünü). Fiyatsız satır yazılamaz; ayrı sayılır.
            rapor["stokta_yok_fiyatsiz" if stokta_yok else "fiyat_okunamadi"].append(url)
            continue
        for etiket, metin in f["kosullu"]:
            rapor["kosullu_fiyat"][etiket] += 1
            if len(rapor["kosullu_ornek"]) < 3:
                rapor["kosullu_ornek"].append({"ad": k["ad"], "etiket": etiket, "fiyat": metin,
                                               "karsilastirma": f["ham"]})
        for etiket, metin in f["bilinmeyen"]:
            rapor["bilinmeyen_fiyat_etiketi"].append({"ad": k["ad"], "etiket": etiket, "fiyat": metin})
        if not f["ustu_cizili_dogrulandi"]:
            rapor["ustu_cizili_dogrulanamadi"].append(url)

        kampanya = bool(f.get("kampanya_bitis"))
        if f.get("kampanya_bitis"):
            # Kampanyanın bitişi kategori sayfasında görünüyorsa rapora yazılır (ajan1-isleme §5):
            # Ajan 3 fiyatı yeniden doğrularken kampanyanın bitmesinden doğan farkı hata sanmaz.
            rapor["kampanya_bitisleri"].append({"ad": k["ad"], "url": url, "bitis": f["kampanya_bitis"],
                                                "liste": f["liste"], "indirimli": f["indirimli"]})
        for r in k.get("rozet", []):
            bilgi = rozetler.get((site, r))
            if bilgi is None:
                rapor["taninmayan_rozet"].append({"rozet_id": r, "ornek_urun": url})
                continue
            rapor["rozet"][bilgi["yazi"]] += 1
            kampanya = kampanya or bilgi["fiyati_etkiler"] == "evet"

        karsilastirma = f["indirimli"] or f["liste"]
        stok = "yok" if stokta_yok else "var"
        elendi = ortak.eleme_gerekcesi(urun, k["ad"], karsilastirma, liste, stok)
        if elendi:
            rapor["elendi"][elendi] += 1
        fiyat_turu = "liste" if not f["indirimli"] else ("kampanya" if kampanya else "indirimli")
        satirlar.append({
            "bizim_urun": urun, "kategori": kategori, "rakip_urun_adi": k["ad"],
            "eslesme_yontemi": "benzer",
            "eslesme_guveni": ortak.guven(ayrinti, ortak.birim_uyumlu(t["birim"], k["ad"]),
                                          karsilastirma, t["makul"]),
            "birim_miktar": ortak.birim_miktar(k["ad"]),
            "ham_fiyat_metni": f["ham"],
            "liste_fiyati": ortak.iki_ondalik(f["liste"]),
            "indirimli_fiyat": ortak.iki_ondalik(f["indirimli"]),
            "fiyat_turu": fiyat_turu, "kdv_dahil": "evet", "para_birimi": "TRY",
            "stok_durumu": stok, "rakip_site": site, "urun_url": url,
            "bulma_yolu": k["bulma_yolu"], "cekilme_zamani": k["cekilme_zamani"],
            "arac": "playwright", "elendi": elendi,
        })

    # Fiyat değişimi notu (ajan1-isleme §5): indirimli ve normal ürünlerin medyanı
    karsi = lambda s: float(s["indirimli_fiyat"] or s["liste_fiyati"])
    indirimli = [karsi(s) for s in satirlar if s["indirimli_fiyat"]]
    normal = [karsi(s) for s in satirlar if not s["indirimli_fiyat"]]
    rapor["satir"] = len(satirlar)
    rapor["medyan_indirimli"] = statistics.median(indirimli) if indirimli else None
    rapor["medyan_normal"] = statistics.median(normal) if normal else None
    rapor["liste_fiyatimiz"] = liste
    gecerli = [karsi(s) for s in satirlar if not s["elendi"]]
    if gecerli and abs(statistics.median(gecerli) - liste) / liste > 0.5:
        rapor["uyari"] = "medyan liste fiyatımızdan %50'den fazla sapıyor"
    rapor["fiyat_degisimi"] = fiyat_degisimi(urun, site, satirlar, onceki or {})
    return satirlar, {k: (dict(v) if isinstance(v, Counter) else v) for k, v in rapor.items()}


DEGISIM_ESIGI = 0.05   # liste fiyatı medyanında %5'ten küçük fark "aynı" sayılır


def onceki_tarama(yol=ortak.KOK / "data" / "web-fiyat-taramasi.csv"):
    """Önceki web fiyat taraması (24–25 Kasım, PR #103/#107): (ürün, site) -> satır."""
    import csv
    try:
        with open(yol, encoding="utf-8") as f:
            return {(r["urun"], r["site"]): r for r in csv.DictReader(f)}
    except OSError:
        return {}


def fiyat_degisimi(urun, site, satirlar, onceki):
    """ajan1-isleme §5: fiyat değişiminin nedeni, sayfadaki etikete ve önceki taramaya göre.

    Karşılaştırma ürün düzeyindedir: bugünkü satırların liste fiyatı medyanı, önceki
    taramanın medyanıyla. Önceki tarama kategori sayfasının ilk ürünleriyle yapıldığı için
    (n sütunu) bugünkü örneklemle birebir aynı değildir; bu not rapora da yazılır.
    """
    if not satirlar:
        return None
    eski = onceki.get((urun, site))
    kampanyali = sum(1 for s in satirlar if s["indirimli_fiyat"])
    liste_medyan = statistics.median(float(s["liste_fiyati"]) for s in satirlar)
    not_ = {"kampanyali_ya_da_indirimli": kampanyali, "normal": len(satirlar) - kampanyali,
            "liste_fiyati_medyani": liste_medyan}
    if not eski or not eski.get("medyan"):
        not_["neden"] = "Önceki taramada bu ürün ve site yok; karşılaştırılamadı."
        return not_
    eski_medyan = float(eski["medyan"])
    oran = (liste_medyan - eski_medyan) / eski_medyan
    not_.update({"onceki_medyan": eski_medyan, "onceki_n": int(float(eski["n"])),
                 "degisim_yuzde": round(oran * 100, 1),
                 "kaynak": "data/web-fiyat-taramasi.csv (önceki tarama ilk sayfa ürünleriyle yapıldı)"})
    if abs(oran) < DEGISIM_ESIGI:
        not_["neden"] = (f"Kampanyalı fiyat (liste fiyatı medyanı {liste_medyan:.2f} TL); normal fiyat değişmedi."
                         if kampanyali else "Liste fiyatı önceki taramayla aynı düzeyde.")
    elif oran < 0:
        not_["neden"] = f"Liste fiyatı düştü ({eski_medyan:.2f} → {liste_medyan:.2f} TL); kalıcı olabilir."
    else:
        not_["neden"] = f"Liste fiyatı yükseldi ({eski_medyan:.2f} → {liste_medyan:.2f} TL)."
    return not_


def secenekler(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Ajan 1: rakip fiyatlarını toplar (skills/ajan1-*)")
    p.add_argument("--urun", action="append", metavar="ÜRÜN",
                   help="Yalnız bu ürünü yeniden topla (birden çok kez verilebilir). Tablodaki diğer "
                        "ürünlerin satırları olduğu gibi kalır. Tazelik kapısı ve red zarfı için (ajan1-teslim).")
    return p.parse_args(argv)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows konsolunda Türkçe harfler
    arg = secenekler(argv)
    from playwright.sync_api import sync_playwright

    tanim = ortak.eslesme_tanimlari()
    liste_fiyatlari = ortak.web_liste_fiyatlari()
    rozetler = ortak.rozet_sozlugu()
    onceki = onceki_tarama()
    sadece = set(arg.urun or [])
    bilinen = {u for m in SITELER for u in m.KATEGORILER}
    if sadece - bilinen:
        print(f"Bilinmeyen ürün: {', '.join(sorted(sadece - bilinen))}. Bilinenler: {', '.join(sorted(bilinen))}")
        return 1
    baslangic = ortak.simdi()
    rapor = {"baslangic": baslangic, "site": {}, "kategori": {}, "basarisiz": []}
    if sadece:
        rapor["kismi_toplama"] = sorted(sadece)
    tum_satirlar = []

    # Ne olursa olsun o ana kadar okunanlar yazılır (28 Kasım: Ruj'daki zaman aşımı
    # ilk dört kategorinin verisini de kaybettirmişti).
    try:
        with sync_playwright() as p:
            tarayici = p.chromium.launch(headless=True)
            baglam = tarayici.new_context(locale="tr-TR")
            sayfa = baglam.new_page()

            for modul in SITELER:
                if sadece and not sadece & set(modul.KATEGORILER):
                    continue
                robots_metni = baglam.request.get(f"{modul.ALAN}/robots.txt").text()
                robots = ortak.Robots(robots_metni)
                bekleyici = ortak.Bekleyici(robots.crawl_delay)
                rapor["site"][modul.SITE] = {"robots_okundu": ortak.simdi(), "crawl_delay": robots.crawl_delay}

                urunler = [u for u in modul.KATEGORILER if not sadece or u in sadece]
                for i, urun in enumerate(urunler):
                    iz = []
                    try:
                        kat_adi, kartlar = modul.kategori_oku(sayfa, urun, robots, bekleyici, iz)
                    except ortak.SiteBirakildi as e:
                        rapor["basarisiz"].append({"site": modul.SITE, "urun": urun, "gerekce": f"site bırakıldı ({e})"})
                        for kalan in urunler[i + 1:]:
                            rapor["basarisiz"].append({"site": modul.SITE, "urun": kalan, "gerekce": "denenmedi: site bırakıldı"})
                        rapor["kategori"][f"{modul.SITE}/{urun}"] = {"iz": iz}
                        break   # bu site bırakılır, sıradaki siteye geçilir
                    except Exception as e:
                        rapor["basarisiz"].append({"site": modul.SITE, "urun": urun, "gerekce": f"beklenmeyen hata: {str(e).splitlines()[0][:200]}"})
                        rapor["kategori"][f"{modul.SITE}/{urun}"] = {"iz": iz}
                        continue
                    if not kartlar:
                        rapor["basarisiz"].append({"site": modul.SITE, "urun": urun, "gerekce": (iz[-1] if iz else {}).get("sonuc", "ürün okunamadı")})
                        rapor["kategori"][f"{modul.SITE}/{urun}"] = {"iz": iz}
                        continue
                    satirlar, notlar = isle(urun, kat_adi, kartlar, tanim, liste_fiyatlari, rozetler, modul.SITE, modul, onceki)
                    tum_satirlar.extend(satirlar)
                    rapor["kategori"][f"{modul.SITE}/{urun}"] = {"site_kategorisi": kat_adi, "iz": iz, **notlar}
                    print(f"{modul.SITE} / {urun}: {len(kartlar)} kart, {len(satirlar)} satır")
            tarayici.close()
    except Exception as e:
        rapor["basarisiz"].append({"urun": "-", "gerekce": f"çalışma yarıda kaldı: {str(e).splitlines()[0][:200]}"})

    rapor["bitis"] = ortak.simdi()
    if sadece:
        # Kısmi toplama: diğer ürünlerin satırları tablodan olduğu gibi alınır.
        import csv
        eski = []
        if CIKTI.exists():
            with open(CIKTI, encoding="utf-8", newline="") as f:
                # Toplanamayan ürünün eski satırları silinmez: veri sessizce kaybolmasın,
                # bayatsa tazelik kapısı yakalar.
                toplanan = {k.split("/", 1)[1] for k, v in rapor["kategori"].items() if "site_kategorisi" in v}
                eski = [r for r in csv.DictReader(f) if r["bizim_urun"] not in toplanan]
        rapor["korunan_satir"] = len(eski)
        tum_satirlar = eski + tum_satirlar
    ortak.tablo_yaz(tum_satirlar, CIKTI)
    RAPOR_KLASORU.mkdir(parents=True, exist_ok=True)
    rapor_yolu = RAPOR_KLASORU / (baslangic.replace(":", "-") + ".json")
    rapor_yolu.write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Tablo: {CIKTI}\nRapor: {rapor_yolu}")
    if rapor["basarisiz"]:
        print("BAŞARISIZ KATEGORİLER:", rapor["basarisiz"])
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
