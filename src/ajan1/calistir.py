"""Ajan 1'i çalıştırır: kartları alır, işler, tabloyu ve çalışma raporunu yazar.

Kullanım (repo kökünden):  python -m src.ajan1.calistir
Çıktılar: data/ajan1-cikti.csv ve runs/ajan1/<zaman>.json
Teslim kontrolleri (ajan1-teslim §1) ayrı adımda: python -m src.ajan1.teslim
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from . import gratis, ortak

CIKTI = ortak.KOK / "data" / "ajan1-cikti.csv"
RAPOR_KLASORU = ortak.KOK / "runs" / "ajan1"


def isle(urun, kat_adi, kartlar, tanim, liste_fiyatlari, rozetler, site):
    """ajan1-isleme: fiyat okuma, eşleştirme, eleme, tekrar ayıklama, rapor notları."""
    kategori, liste = liste_fiyatlari[urun]
    t = tanim[urun]
    satirlar, gorulen = [], set()
    rapor = {"okunan_kart": len(kartlar), "haric": Counter(), "kararsiz": [],
             "kosullu_fiyat": Counter(), "kosullu_ornek": [], "bilinmeyen_fiyat_etiketi": [],
             "rozet": Counter(), "taninmayan_rozet": [], "fiyat_okunamadi": [],
             "ustu_cizili_dogrulanamadi": [], "tekrar": 0, "elendi": Counter()}
    for k in kartlar:
        if not k.get("url") or not k.get("ad"):
            continue
        url = (gratis.ALAN + k["url"]).split("?")[0]
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

        f = gratis.kart_fiyatlari(k["satirlar"], k["ad"], k.get("ustu_cizili", ()))
        if f is None:
            rapor["fiyat_okunamadi"].append(url)
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

        kampanya = False
        for r in k.get("rozet", []):
            bilgi = rozetler.get((site, r))
            if bilgi is None:
                rapor["taninmayan_rozet"].append({"rozet_id": r, "ornek_urun": url})
                continue
            rapor["rozet"][bilgi["yazi"]] += 1
            kampanya = kampanya or bilgi["fiyati_etkiler"] == "evet"

        karsilastirma = f["indirimli"] or f["liste"]
        stok = "yok" if any("tükendi" in s.lower() or "stokta yok" in s.lower() for s in k["satirlar"]) else "var"
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
    return satirlar, {k: (dict(v) if isinstance(v, Counter) else v) for k, v in rapor.items()}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows konsolunda Türkçe harfler
    from playwright.sync_api import sync_playwright

    tanim = ortak.eslesme_tanimlari()
    liste_fiyatlari = ortak.web_liste_fiyatlari()
    rozetler = ortak.rozet_sozlugu()
    baslangic = ortak.simdi()
    rapor = {"baslangic": baslangic, "site": {}, "kategori": {}, "basarisiz": []}
    tum_satirlar = []

    # Ne olursa olsun o ana kadar okunanlar yazılır (28 Kasım: Ruj'daki zaman aşımı
    # ilk dört kategorinin verisini de kaybettirmişti).
    try:
        with sync_playwright() as p:
            tarayici = p.chromium.launch(headless=True)
            baglam = tarayici.new_context(locale="tr-TR")
            sayfa = baglam.new_page()

            robots_metni = baglam.request.get(f"{gratis.ALAN}/robots.txt").text()
            robots = ortak.Robots(robots_metni)
            bekleyici = ortak.Bekleyici(robots.crawl_delay)
            rapor["site"][gratis.SITE] = {"robots_okundu": ortak.simdi(), "crawl_delay": robots.crawl_delay}

            urunler = list(gratis.KATEGORILER)
            for i, urun in enumerate(urunler):
                iz = []
                try:
                    kat_adi, kartlar = gratis.kategori_oku(sayfa, urun, robots, bekleyici, iz)
                except ortak.SiteBirakildi as e:
                    rapor["basarisiz"].append({"urun": urun, "gerekce": f"site bırakıldı ({e})"})
                    for kalan in urunler[i + 1:]:
                        rapor["basarisiz"].append({"urun": kalan, "gerekce": "denenmedi: site bırakıldı"})
                    rapor["kategori"][urun] = {"iz": iz}
                    break
                except Exception as e:
                    rapor["basarisiz"].append({"urun": urun, "gerekce": f"beklenmeyen hata: {str(e).splitlines()[0][:200]}"})
                    rapor["kategori"][urun] = {"iz": iz}
                    continue
                if not kartlar:
                    rapor["basarisiz"].append({"urun": urun, "gerekce": (iz[-1] if iz else {}).get("sonuc", "ürün okunamadı")})
                    rapor["kategori"][urun] = {"iz": iz}
                    continue
                satirlar, notlar = isle(urun, kat_adi, kartlar, tanim, liste_fiyatlari, rozetler, gratis.SITE)
                tum_satirlar.extend(satirlar)
                rapor["kategori"][urun] = {"gratis_kategorisi": kat_adi, "iz": iz, **notlar}
                print(f"{urun}: {len(kartlar)} kart, {len(satirlar)} satır")
            tarayici.close()
    except Exception as e:
        rapor["basarisiz"].append({"urun": "-", "gerekce": f"çalışma yarıda kaldı: {str(e).splitlines()[0][:200]}"})

    rapor["bitis"] = ortak.simdi()
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
