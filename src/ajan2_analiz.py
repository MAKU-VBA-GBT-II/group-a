#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — Ajan 2 (analiz): rakip fiyatı × sentetik sipariş analizi

Ajan 1'in 19 sütunlu rakip fiyat CSV'sini alır, `docs/mesaj-bicimi.md` sözleşmesine
göre kontrol eder, web fiyatlı sentetik siparişlerle birleştirir, ürün başına rakip
medyanı, fiyat farkı, satış adedi ve ciroyu, ürünler arası Pearson ilişkisini
hesaplar, kampanya önerisi üretir ve Ajan 3'e JSON + onay zarfı olarak teslim eder.

Üç aşama, üç skill:
    alma    → skills/ajan2-alma/SKILL.md     (kontrol, 72 saat, gerekçeli red)
    isleme  → skills/ajan2-isleme/SKILL.md   (birleştirme, hesap, öneri)
    teslim  → skills/ajan2-teslim/SKILL.md   (JSON, zarf, çalışma izi)

Kullanım (depo kökünde):
    python src/ajan2_analiz.py --girdi data/ornek-ajan1.csv \
        --referans 2026-11-29T18:00:00+03:00 \
        --cikti data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json
    python src/ajan2_analiz.py --help

`--referans` verilmezse alma anı (şimdiki Türkiye saati) kullanılır.
Çıkış kodları: 0 onay, 2 red (Ajan 1'e geri gönderildi), 1 beklenmeyen hata.
Yalnız Python standart kütüphanesi kullanılır. Issue: #115.
"""

import argparse
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import parse_qs, urlparse

KOK = Path(__file__).resolve().parents[1]
TR = timezone(timedelta(hours=3))

ALANLAR = (
    "bizim_urun kategori rakip_urun_adi eslesme_yontemi eslesme_guveni "
    "birim_miktar ham_fiyat_metni liste_fiyati indirimli_fiyat fiyat_turu "
    "kdv_dahil para_birimi stok_durumu rakip_site urun_url bulma_yolu "
    "cekilme_zamani arac elendi"
).split()
ISTEGE_BAGLI = {"birim_miktar", "indirimli_fiyat", "elendi"}
DEGER_KUMELERI = {
    "eslesme_yontemi": {"benzer"},
    "eslesme_guveni": {"yuksek", "orta", "dusuk"},
    "fiyat_turu": {"liste", "indirimli", "kampanya"},
    "kdv_dahil": {"evet", "hayir"},
    "para_birimi": {"TRY"},
    "stok_durumu": {"var", "yok", "bilinmiyor"},
    "rakip_site": {"MediaMarkt", "Gratis", "D&R", "Koçtaş", "IKEA", "Koton"},
}
BAYATLIK = timedelta(hours=72)
# rakip_site → ürün adresinin alan adında bulunması gereken etiket
SITE_ALAN_ADI = {"MediaMarkt": "mediamarkt", "Gratis": "gratis", "D&R": "dr", "Koçtaş": "koctas",
                 "IKEA": "ikea", "Koton": "koton"}
ELENDI_GEREKCELERI = {"fiyat bandı dışı", "çoklu paket", "ikinci el", "stok yok", "TL dışı"}
BULMA_YOLU = re.compile(r"^https://\S+ s\.[1-9]\d*$")
SENTETIK_ARAC = "sentetik-fixture"

# Bilinen sınırlamalar ve istisnalar (docs/eslesme-tanimlari.md, karar 5 ve kural 5)
SINIRLI_URUNLER = {
    "Masa Lambası": "Liste fiyatı 399 TL'de bırakıldı (karar 5); 1.197 TL üst bandı "
                    "pahalı rakipleri eler, örneklem yanlıdır.",
}
SET_ISTISNASI = {"Saklama Kabı Seti"}  # set olması elenme gerekçesi değildir

# Elendi alanı boş olsa da medyana katılmayan satırlar (docs/mesaj-bicimi.md).
# Hangi sayaca yazılacağı PR #117 incelemesinde soruldu; cevap gelene kadar
# "elenen" tarafında sayılır. Cevaba göre yalnız bu sabit değişir.
SAYILMAYAN_SAYAC = "elenen"

KAMPANYA_ESIGI = Decimal("10")  # bizim fiyat rakip medyanından %10'dan fazla yüksekse


class Red(Exception):
    """Girdi sözleşmeye uymuyor: Ajan 1'e gerekçeli red."""

    def __init__(self, gerekce, alanlar):
        super().__init__(gerekce)
        self.gerekce = gerekce
        self.alanlar = alanlar


def yuvarla(deger, basamak):
    """Eşit yarıda en yakın çifte yuvarlar, JSON için float döner."""
    return float(Decimal(str(deger)).quantize(Decimal(1).scaleb(-basamak), ROUND_HALF_EVEN))


def goreli(yol):
    yol = Path(yol).resolve()
    try:
        return yol.relative_to(KOK).as_posix()
    except ValueError:
        return yol.as_posix()


def dosya_zamani(yol):
    """Sürümlenmiş ve değişmemiş dosyada son commit zamanı, yoksa dosya zamanı."""
    yol = Path(yol).resolve()
    try:
        degisik = subprocess.run(["git", "status", "--porcelain", "--", str(yol)], cwd=KOK,
                                 capture_output=True, text=True, check=True).stdout.strip()
        zaman = subprocess.run(["git", "log", "-1", "--format=%cI", "--", str(yol)], cwd=KOK,
                               capture_output=True, text=True, check=True).stdout.strip()
        if zaman and not degisik:
            return zaman
    except (OSError, subprocess.CalledProcessError):
        pass
    return datetime.fromtimestamp(yol.stat().st_mtime, TR).isoformat(timespec="seconds")


def md5(yol):
    return hashlib.md5(Path(yol).read_bytes()).hexdigest()


def csv_oku(yol):
    with Path(yol).open(encoding="utf-8", newline="") as dosya:
        okuyucu = csv.DictReader(dosya)
        return okuyucu.fieldnames, list(okuyucu)


# ---------------------------------------------------------------- 1. alma

def alma(girdi, katalog_yolu, referans):
    """Ajan 1 CSV'sini kontrol eder. Uymazsa Red, uyarsa satırları döner."""
    try:
        baslik, satirlar = csv_oku(girdi)
    except (OSError, UnicodeDecodeError, csv.Error) as hata:
        raise Red(f"Girdi okunamadı: {hata}", ["girdi"]) from hata
    if baslik != ALANLAR:
        raise Red("Başlık 19 sütunlu sözleşme sırasıyla eşleşmiyor.", ["girdi"])
    if not satirlar:
        raise Red("Girdide hiç rakip satırı yok.", ["girdi"])
    katalog = {s["urun"]: s for s in csv_oku(katalog_yolu)[1]}

    sorunlar = []
    for no, satir in enumerate(satirlar, 2):
        yol = f"satir[{no}]"
        if None in satir or any(v is None for v in satir.values()):
            sorunlar.append(f"{yol}")
            continue
        for alan in ALANLAR:
            if alan not in ISTEGE_BAGLI and not satir[alan].strip():
                sorunlar.append(f"{yol}.{alan}")
        for alan, izinli in DEGER_KUMELERI.items():
            if satir[alan] and satir[alan] not in izinli:
                sorunlar.append(f"{yol}.{alan}")
        urun = katalog.get(satir["bizim_urun"])
        if satir["bizim_urun"] and (urun is None or urun["kategori"] != satir["kategori"]):
            sorunlar.append(f"{yol}.bizim_urun")
        liste = _fiyat(satir["liste_fiyati"])
        if satir["liste_fiyati"] and liste is None:
            sorunlar.append(f"{yol}.liste_fiyati")
        if satir["indirimli_fiyat"]:
            indirim = _fiyat(satir["indirimli_fiyat"])
            if indirim is None or (liste is not None and indirim >= liste) or satir["fiyat_turu"] == "liste":
                sorunlar.append(f"{yol}.indirimli_fiyat")
        if satir["elendi"].strip() and satir["elendi"].strip() not in ELENDI_GEREKCELERI:
            sorunlar.append(f"{yol}.elendi")
        if satir["urun_url"] and (not _urun_sayfasi(satir["urun_url"])
                                  or not _site_uyumlu(satir["urun_url"], satir["rakip_site"])):
            sorunlar.append(f"{yol}.urun_url")
        if satir["bulma_yolu"] and not BULMA_YOLU.match(satir["bulma_yolu"]):
            sorunlar.append(f"{yol}.bulma_yolu")
        karsilastirma = _fiyat(satir["indirimli_fiyat"]) if satir["indirimli_fiyat"] else liste
        if satir["ham_fiyat_metni"] and karsilastirma is not None \
                and _ham_fiyat(satir["ham_fiyat_metni"]) != karsilastirma:
            sorunlar.append(f"{yol}.ham_fiyat_metni")
        if satir["cekilme_zamani"]:
            try:
                zaman = datetime.fromisoformat(satir["cekilme_zamani"])
                if zaman.utcoffset() != timedelta(hours=3):
                    raise ValueError("saat dilimi +03:00 değil")
                if not timedelta() <= referans - zaman <= BAYATLIK:
                    raise ValueError("72 saatten eski ya da gelecekte")
            except (TypeError, ValueError):
                sorunlar.append(f"{yol}.cekilme_zamani")

    if sorunlar:
        bayat = [a for a in sorunlar if a.endswith(".cekilme_zamani")]
        if bayat and len(bayat) == len(sorunlar):
            gerekce = (f"{len(bayat)} satırda çekilme zamanı geçersiz, gelecekte ya da "
                       f"referans zamanından ({referans.isoformat()}) 72 saatten eski.")
        else:
            gerekce = f"{len(sorunlar)} alan sözleşmeye uymuyor (eksik, bozuk ya da izinli değer dışı)."
        raise Red(gerekce, sorunlar)
    return satirlar, katalog


def _urun_sayfasi(adres):
    """Doğrudan ürün sayfası mı? Arama sayfası (/search, q=, query=) kabul edilmez."""
    parca = urlparse(adres)
    sorgu = parse_qs(parca.query)
    return (parca.scheme == "https" and bool(parca.hostname) and "/search" not in parca.path.lower()
            and "q" not in sorgu and "query" not in sorgu)


def _site_uyumlu(adres, site):
    """Ürün adresinin alan adı rakip_site ile uyumlu mu? (ör. IKEA → *.ikea.*)"""
    etiket = SITE_ALAN_ADI.get(site)
    host = (urlparse(adres).hostname or "").lower()
    return etiket is None or etiket in host.split(".")


def _ham_fiyat(metin):
    """'₺1.299,90' → Decimal('1299.90'). Ayrıştırılamazsa None."""
    sayi = re.sub(r"[^\d.,]", "", metin).replace(".", "").replace(",", ".")
    try:
        deger = Decimal(sayi)
    except InvalidOperation:
        return None
    return deger if deger.is_finite() else None


def _fiyat(metin):
    try:
        deger = Decimal(metin)
    except (InvalidOperation, TypeError):
        return None
    if not deger.is_finite() or deger <= 0 or deger.as_tuple().exponent != -2:
        return None
    return deger


# ---------------------------------------------------------------- 2. işleme

def eleme_gerekcesi(satir, bizim_fiyat):
    """Satır medyana girmiyorsa gerekçesini, giriyorsa None döner."""
    gerekce = satir["elendi"].strip()
    if gerekce == "çoklu paket" and satir["bizim_urun"] in SET_ISTISNASI:
        gerekce = ""  # Saklama Kabı Seti istisnası: set elenmez
    if gerekce:
        return gerekce
    fiyat = Decimal(satir["indirimli_fiyat"] or satir["liste_fiyati"])
    if fiyat < bizim_fiyat * Decimal("0.3") or fiyat > bizim_fiyat * 3:
        return "fiyat bandı dışı"
    if satir["stok_durumu"] == "yok":
        return "stok yok"
    if satir["kdv_dahil"] != "evet":
        return "KDV temeli karşılaştırılamaz"
    return None


def sayilmayan(gerekce, satir):
    """Ajan 1'in işaretlemediği, Ajan 2'nin medyandan çıkardığı stok/KDV satırı mı?"""
    return not satir["elendi"].strip() and gerekce in {"stok yok", "KDV temeli karşılaştırılamaz"}


def isleme(satirlar, katalog, siparis_yolu, girdi_yolu, katalog_yolu, uretim_zamani, donem=None):
    _, siparisler = csv_oku(siparis_yolu)
    tarihler = [date.fromisoformat(s["siparis_tarihi"]) for s in siparisler]
    baslangic, bitis = donem or (min(tarihler), max(tarihler))
    girdi_adi, katalog_adi, siparis_adi = goreli(girdi_yolu), goreli(katalog_yolu), goreli(siparis_yolu)
    katalog_zamani, siparis_zamani = dosya_zamani(katalog_yolu), dosya_zamani(siparis_yolu)

    urunler, farklar, adetler, cirolar = [], [], [], []
    for ad in dict.fromkeys(s["bizim_urun"] for s in satirlar):
        bizim = Decimal(katalog[ad]["liste_fiyati"])
        gecerli, elenen, ek_kullanilan, kaynaklar = [], 0, 0, [
            {"alanlar": ["bizim_liste_fiyati", "fiyat_farki_yuzde"], "kaynak": katalog_adi,
             "secim": f"urun={ad}; liste_fiyati", "uretim_zamani": katalog_zamani},
            {"alanlar": ["satis_adedi", "ciro"], "kaynak": siparis_adi,
             "secim": f"urun={ad}; durum=Teslim Edildi; siparis_donemi dâhil",
             "uretim_zamani": siparis_zamani},
        ]
        for no, satir in enumerate(satirlar, 2):
            if satir["bizim_urun"] != ad:
                continue
            gerekce = eleme_gerekcesi(satir, bizim)
            sayaclar = ["kullanilan_rakip_sayisi", "elenen_rakip_sayisi"]
            if gerekce is None:
                alan = "indirimli_fiyat" if satir["indirimli_fiyat"] else "liste_fiyati"
                gecerli.append(Decimal(satir[alan]))
                secim, alanlar = f"{girdi_adi} satır {no}; {alan}", \
                    ["rakip_medyan_fiyati", "fiyat_farki_yuzde"] + sayaclar
            else:
                if sayilmayan(gerekce, satir) and SAYILMAYAN_SAYAC == "kullanilan":
                    ek_kullanilan += 1
                else:
                    elenen += 1
                secim, alanlar = f"{girdi_adi} satır {no}; elendi: {gerekce}", list(sayaclar)
            kaynaklar.append({"alanlar": alanlar, "kaynak": satir["urun_url"], "secim": secim,
                              "uretim_zamani": satir["cekilme_zamani"]})

        medyan = statistics.median(gecerli) if gecerli else None
        fark = 100 * (bizim - medyan) / medyan if medyan else None
        satis = [s for s in siparisler if s["urun"] == ad and s["durum"] == "Teslim Edildi"
                 and baslangic <= date.fromisoformat(s["siparis_tarihi"]) <= bitis]
        adet = sum(int(s["adet"]) for s in satis)
        ciro = sum((Decimal(s["toplam_tutar"]) for s in satis), Decimal(0))
        kullanilan = len(gecerli) + ek_kullanilan
        if not gecerli:
            # medyan null: nedeni elenen satırlardır, kapsamı onların kaynak kaydı taşır
            for kayit in kaynaklar[2:]:
                kayit["alanlar"] = ["rakip_medyan_fiyati", "fiyat_farki_yuzde"] + kayit["alanlar"]

        urunler.append({
            "urun": ad,
            "kategori": katalog[ad]["kategori"],
            "bizim_liste_fiyati": yuvarla(bizim, 2),
            "rakip_medyan_fiyati": yuvarla(medyan, 2) if medyan is not None else None,
            "fiyat_farki_yuzde": yuvarla(fark, 2) if fark is not None else None,
            "kullanilan_rakip_sayisi": kullanilan,
            "elenen_rakip_sayisi": elenen,
            "satis_adedi": adet,
            "ciro": yuvarla(ciro, 2),
            "oneri": oneri(ad, fark, kullanilan, elenen),
            "kaynaklar": kaynaklar,
        })
        if fark is not None:
            farklar.append(float(fark))
            adetler.append(adet)
            cirolar.append(float(ciro))

    iliskiler = {
        "urun_sayisi": len(farklar),
        "pearson_fark_adet": _pearson(farklar, adetler),
        "pearson_fark_ciro": _pearson(farklar, cirolar),
        "kaynaklar": [{
            "alanlar": ["urun_sayisi", "pearson_fark_adet", "pearson_fark_ciro"],
            "kaynak": "$.urunler",
            "secim": "Fiyat farkı tanımlı ürünler; yuvarlama öncesi değerler ve ürünlerin kaynak kayıtları",
            "uretim_zamani": uretim_zamani,
        }],
    }
    return urunler, iliskiler, (baslangic, bitis)


def _pearson(x, y):
    if len(x) < 2:
        return None
    try:
        return yuvarla(statistics.correlation(x, y), 6)
    except statistics.StatisticsError:  # sıfır varyans
        return None


def oneri(ad, fark, kullanilan, elenen):
    """Kural tabanlı öneri. Maliyet verisi yok: kâr iddiası yapılmaz."""
    if fark is None:
        eylem = "veri_topla"
        gerekce = f"Karşılaştırılabilir rakip fiyatı yok ({elenen} satır elendi). Fiyat kararı için veri gerekir."
    elif ad in SINIRLI_URUNLER:
        eylem = "veri_topla"
        gerekce = (f"{SINIRLI_URUNLER[ad]} {kullanilan} rakip kullanıldı, {elenen} elendi; "
                   f"fark %{yuvarla(fark, 2)} ihtiyatla okunmalı.")
    elif fark > KAMPANYA_ESIGI:
        eylem = "kampanya_test_et"
        gerekce = (f"Liste fiyatımız rakip medyanından %{yuvarla(fark, 2)} yüksek ({kullanilan} rakip). "
                   "Maliyet ve kâr eşiği doğrulanırsa kontrollü bir kampanya testi planlanabilir.")
    else:
        eylem = "fiyati_koru"
        gerekce = (f"Liste fiyatımız rakip medyanına göre %{yuvarla(fark, 2)} ({kullanilan} rakip); "
                   "kampanya eşiğinin (%10) altında. Maliyet doğrulanınca yeniden değerlendirilir.")
    return {"eylem": eylem, "gerekce": gerekce, "kar_durumu": "maliyet_eksik"}


# ---------------------------------------------------------------- 3. teslim

def zarf(durum, hedef, gerekce, alanlar):
    return {"durum": durum, "hedef_ajan": hedef, "gerekce": gerekce, "sorunlu_alanlar": alanlar}


def yaz_json(yol, veri):
    Path(yol).parent.mkdir(parents=True, exist_ok=True)
    Path(yol).write_text(json.dumps(veri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def calistir(arg, argv=None):
    referans = datetime.fromisoformat(arg.referans) if arg.referans else datetime.now(TR).replace(microsecond=0)
    if referans.utcoffset() is None:
        raise SystemExit("Hata: --referans saat dilimi içermeli (ör. +03:00)")
    # Her çalıştırma temiz başlar: hata hangi yolda olursa olsun eski çıktı ve
    # zarf Ajan 3'e onaylıymış gibi kalmaz.
    for eski in (arg.cikti, arg.zarf):
        Path(eski).unlink(missing_ok=True)
    if arg.referans and not _hepsi_sentetik(arg.girdi):
        raise SystemExit("Hata: --referans yalnız tüm satırları sentetik-fixture olan test girdisinde "
                         "kullanılır; gerçek veride alma anı kullanılmalı.")
    iz = {
        "arac": "src/ajan2_analiz.py",
        "komut": " ".join(["python", "src/ajan2_analiz.py"] + (sys.argv[1:] if argv is None else list(argv))),
        "baslangic": datetime.now(TR).isoformat(timespec="seconds"),
        "referans_zamani": referans.isoformat(),
        "girdiler": {goreli(p): md5(p) for p in (arg.girdi, arg.urun_listesi, arg.siparisler) if Path(p).exists()},
    }
    try:
        satirlar, katalog = alma(arg.girdi, arg.urun_listesi, referans)
    except Red as red:
        sonuc = zarf("red", "ajan1", red.gerekce, red.alanlar)
        yaz_json(arg.zarf, sonuc)
        Path(arg.cikti).unlink(missing_ok=True)  # eski çıktı Ajan 3'e aktarılmasın
        iz.update(asama="alma", sonuc=sonuc, cikti={goreli(arg.zarf): md5(arg.zarf)})
        _iz_yaz(arg.iz_klasoru, iz)
        print(f"RED → ajan1: {red.gerekce} ({', '.join(red.alanlar[:5])})")
        return 2

    sentetik = all(s["arac"] == SENTETIK_ARAC for s in satirlar)  # --referans varsa hep True
    uretim = referans if arg.referans else datetime.now(TR).replace(microsecond=0)
    donem = (date.fromisoformat(arg.baslangic), date.fromisoformat(arg.bitis)) if arg.baslangic and arg.bitis else None
    urunler, iliskiler, (bas, bit) = isleme(satirlar, katalog, arg.siparisler, arg.girdi,
                                            arg.urun_listesi, uretim.isoformat(), donem)
    cikti = {
        "surum": "1",
        "veri_turu": "sentetik_test" if sentetik else "web_ve_sentetik_siparis",
        "para_birimi": "TRY",
        "uretim_zamani": uretim.isoformat(),
        "siparis_donemi": {"baslangic": bas.isoformat(), "bitis": bit.isoformat()},
        "urunler": urunler,
        "iliskiler": iliskiler,
    }
    yaz_json(arg.cikti, cikti)
    sonuc = zarf("onay", "ajan3",
                 f"{len(satirlar)} rakip satırı alındı, {len(urunler)} ürün analiz edildi; çıktı {goreli(arg.cikti)}.",
                 [])
    yaz_json(arg.zarf, sonuc)
    iz.update(asama="teslim", sonuc=sonuc,
              ozet={u["urun"]: {"fark": u["fiyat_farki_yuzde"], "eylem": u["oneri"]["eylem"]} for u in urunler},
              cikti={goreli(p): md5(p) for p in (arg.cikti, arg.zarf)})
    _iz_yaz(arg.iz_klasoru, iz)
    print(f"ONAY → ajan3: {len(urunler)} ürün, çıktı {goreli(arg.cikti)}")
    return 0


def _hepsi_sentetik(girdi):
    try:
        _, satirlar = csv_oku(girdi)
    except (OSError, UnicodeDecodeError, csv.Error):
        return True  # okunamayan girdi alma aşamasında gerekçeli red alır
    return all(s.get("arac") == SENTETIK_ARAC for s in satirlar)


def _iz_yaz(klasor, iz):
    iz["bitis"] = datetime.now(TR).isoformat(timespec="seconds")
    ad = datetime.now(TR).strftime("%Y%m%d-%H%M%S") + f"-{iz['sonuc']['durum']}.json"
    yaz_json(Path(klasor) / ad, iz)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--girdi", required=True, help="Ajan 1'in 19 sütunlu rakip CSV'si")
    p.add_argument("--urun_listesi", default=str(KOK / "data/urun-listesi-web.csv"))
    p.add_argument("--siparisler", default=str(KOK / "data/siparisler-web.csv"))
    p.add_argument("--referans", help="Alma anı (ISO 8601, saat dilimli). Verilmezse şimdi.")
    p.add_argument("--baslangic", help="Sipariş dönemi başlangıcı (YYYY-AA-GG); verilmezse verinin ilk günü")
    p.add_argument("--bitis", help="Sipariş dönemi bitişi (YYYY-AA-GG); verilmezse verinin son günü")
    p.add_argument("--cikti", default=str(KOK / "data/ajan2-cikti.json"))
    p.add_argument("--zarf", default=str(KOK / "data/ajan2-zarf.json"))
    p.add_argument("--iz_klasoru", default=str(KOK / "runs/ajan2"))
    arg = p.parse_args(argv)
    if bool(arg.baslangic) != bool(arg.bitis):
        p.error("--baslangic ve --bitis birlikte verilmeli")
    if arg.baslangic:
        try:
            bas, bit = date.fromisoformat(arg.baslangic), date.fromisoformat(arg.bitis)
        except ValueError:
            p.error("--baslangic ve --bitis YYYY-AA-GG biçiminde olmalı")
        if bas > bit:
            p.error("--baslangic, --bitis'ten sonra olamaz")
    return calistir(arg, argv)


if __name__ == "__main__":
    sys.exit(main())
