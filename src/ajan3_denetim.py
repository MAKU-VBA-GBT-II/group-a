#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sepetix Analitik (Grup A) — Ajan 3 (denetim). Issue: #116. Sözleşme: docs/mesaj-bicimi.md (PR #117).

Ajan 2'nin JSON çıktısını ve onay zarfını, Ajan 1'in rakip CSV'si ve MD5'iyle birlikte alır;
kaynakları, fiyat izini, 72 saat kuralını ve bütün sayıları ham dosyalardan bağımsız
olarak yeniden hesaplar (ajan2_analiz modülü kullanılmaz). Önerilen fiyat ve birim
maliyet verilirse fiyatın Ajan 2 eylemiyle uyumunu ve kâr eşiğini (birim kâr 0 TL'nin
üstünde) denetler.

    alma    → skills/ajan3-alma/SKILL.md
    isleme  → skills/ajan3-isleme/SKILL.md
    teslim  → skills/ajan3-teslim/SKILL.md

Kod sayfalara istek atmaz. Canlı fiyat kontrolü elle yapılır ve --canli_kontrol dosyasıyla
verilir; gerçek veride bu kayıt yoksa onay çıkmaz (beklemede). Kaydı olmayan sentetik
çalıştırmada raporda "yapılmayan" olarak yazılır.

Örnek (depo kökünde, sentetik veri):
    python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json \
        --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv \
        --ajan1_md5 7ae26d1c10de56d617b95e241ec6639b \
        --fiyat data/ajan3-fiyat-ornek.csv --maliyet data/ajan3-maliyet-ornek.csv \
        --referans 2026-11-29T18:00:00+03:00

Çıkış kodları: 0 onay, 2 red, 3 kontroller geçti ama fiyat, maliyet ya da canlı kontrol
kaydı eksik (beklemede), 1 kullanım (verilen dosya bulunamadı dahil) ya da beklenmeyen hata.
Yalnız standart kütüphane kullanılır.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

KOK = Path(__file__).resolve().parents[1]
TR = timezone(timedelta(hours=3))
BAYATLIK = timedelta(hours=72)
SENTETIK_ARAC = "sentetik-fixture"
SITE_ALAN_ADI = {"MediaMarkt": "mediamarkt.com.tr", "Gratis": "gratis.com", "D&R": "dr.com.tr",
                 "Koçtaş": "koctas.com.tr", "IKEA": "ikea.com.tr", "Koton": "koton.com"}
SET_ISTISNASI = {"Saklama Kabı Seti"}
CSV_ALANLARI = ("bizim_urun kategori ham_fiyat_metni liste_fiyati indirimli_fiyat kdv_dahil "
                "stok_durumu rakip_site urun_url cekilme_zamani arac elendi para_birimi").split()
UST_ALANLAR = ("surum veri_turu para_birimi uretim_zamani siparis_donemi urunler iliskiler").split()
URUN_ALANLARI = ("urun kategori bizim_liste_fiyati rakip_medyan_fiyati fiyat_farki_yuzde "
                 "kullanilan_rakip_sayisi elenen_rakip_sayisi satis_adedi ciro oneri kaynaklar").split()
EYLEMLER = {"fiyati_koru", "kampanya_test_et", "veri_topla"}
PARA = re.compile(r"[0-9]+(\.[0-9]{1,2})?")
KAR_ESIGI = Decimal(0)  # birim kâr kesin olarak bu değerin üstünde olmalı
GECEN_KONTROLLER = ["Ajan 1 CSV özeti (MD5)", "72 saat", "fiyat izi", "ürün adresi alan adı",
                    "Ajan 2 zarfı", "sayıların bağımsız yeniden hesabı", "kaynak kayıtları"]
CANLI = "sayfadan canlı fiyat doğrulaması"
CANLI_KAYDI = "elle canlı fiyat kontrol kaydı"
CANLI_ALANLARI = ["urun", "urun_url", "sayfa_fiyati_tl", "kaynak", "uretim_zamani"]


class Red(Exception):
    """Denetim düştü: düzeltmeyi yapacak ajana gerekçeli red."""

    def __init__(self, hedef, sorunlar):
        self.hedef = hedef
        self.alanlar = list(dict.fromkeys(alan for alan, _ in sorunlar))
        nedenler = list(dict.fromkeys(neden for _, neden in sorunlar))
        self.gerekce = f"{len(self.alanlar)} alanda denetim düştü: " + "; ".join(nedenler[:5]) + "."
        super().__init__(self.gerekce)


def yuvarla(deger, basamak=2):
    return float(Decimal(str(deger)).quantize(Decimal(1).scaleb(-basamak), ROUND_HALF_EVEN))


def fiyat(metin):
    """Pozitif, sonlu Decimal; değilse None."""
    try:
        deger = Decimal(metin)
    except (InvalidOperation, TypeError):
        return None
    return deger if deger.is_finite() and deger > 0 else None


def ham_fiyat(metin):
    """'₺1.299,90' → Decimal('1299.90')."""
    sayi = "".join(c for c in metin if c in "0123456789.,").replace(".", "").replace(",", ".")
    return fiyat(sayi)


def zaman(metin):
    """Saat dilimli ISO 8601; değilse None."""
    try:
        deger = datetime.fromisoformat(metin)
    except (ValueError, TypeError):
        return None
    return deger if deger.utcoffset() is not None else None


def csv_oku(yol):
    with Path(yol).open(encoding="utf-8", newline="") as dosya:
        return list(csv.DictReader(dosya))


def _sonlu_degil(sabit):
    raise ValueError(f"JSON içinde sonlu olmayan sayı: {sabit}")


def json_oku(yol):
    return json.loads(Path(yol).read_text(encoding="utf-8"), parse_constant=_sonlu_degil)


def alan_adi_uyumlu(satir):
    alan = SITE_ALAN_ADI.get(satir["rakip_site"])
    try:
        adres = urlparse(satir["urun_url"])
        host = (adres.hostname or "").lower()
    except ValueError:  # ör. kapanmayan köşeli ayraç
        return False
    if alan is None or adres.scheme != "https":
        return False
    izinli = [alan]
    if satir["arac"] == SENTETIK_ARAC:
        izinli.append(alan.split(".")[0] + ".example")
    return any(host == a or host.endswith("." + a) for a in izinli)


# ---------------------------------------------------------------- 1. alma

def canli_kontrol_oku(yol, satirlar, katalog_yolu, referans):
    """Elle yapılan canlı fiyat kontrolü: (ürün → geçerli kayıtlar, eksikler, uyuşmazlıklar).

    Geçerli kayıt, ürünün medyana giren bir satırının adresini gösterir; çekimden sonra ve
    son 72 saat içinde yapılmıştır.
    """
    if yol is None:
        return {}, [], []
    try:
        kayit_satirlari = csv_oku(yol)
    except (OSError, UnicodeDecodeError, csv.Error):
        return {}, ["canlı kontrol dosyası okunamıyor"], []
    if any(k.get(a) is None for k in kayit_satirlari for a in CANLI_ALANLARI):
        return {}, ["canlı kontrol dosyasında zorunlu sütun eksik"], []
    katalog = {s["urun"]: s for s in csv_oku(katalog_yolu)}
    kayitlar, eksikler, uyusmazliklar = {}, [], []
    for no, k in enumerate(kayit_satirlari, 2):
        ad, adres, metin = k["urun"].strip(), k["urun_url"].strip(), k["sayfa_fiyati_tl"].strip()
        eslesen = [(n, s) for n, s in enumerate(satirlar, 2)
                   if ad in katalog and s["bizim_urun"] == ad and s["urun_url"] == adres
                   and medyana_girer(s, Decimal(katalog[ad]["liste_fiyati"]))]
        deger = fiyat(metin) if PARA.fullmatch(metin) else None
        an = zaman(k["uretim_zamani"])
        if (not eslesen or deger is None or not k["kaynak"].strip() or an is None
                or not timedelta(0) <= referans - an <= BAYATLIK
                or any(an < zaman(s["cekilme_zamani"]) for _, s in eslesen)):
            eksikler.append(f"canlı kontrol dosyasında satır {no} geçersiz")
            continue
        for n, s in eslesen:
            alan = "indirimli_fiyat" if s["indirimli_fiyat"] else "liste_fiyati"
            if deger != Decimal(s[alan]):
                uyusmazliklar.append((f"satir[{n}].{alan}",
                                      f"{ad}: elle canlı kontrolde sayfa {deger} TL, tabloda {s[alan]} TL"))
        kayitlar.setdefault(ad, []).append({
            "urun_url": adres, "sayfa_fiyati_tl": float(deger), "kaynak": k["kaynak"].strip(),
            "uretim_zamani": k["uretim_zamani"]})
    return kayitlar, eksikler, uyusmazliklar


def alma(girdi, zarf_yolu, ajan1_yolu, ajan1_md5, referans, canli_yolu, katalog_yolu):
    """Ajan 1 tablosu ve Ajan 2 teslimi denetlenebilir mi? Değilse Red."""
    try:
        ham = Path(ajan1_yolu).read_bytes()
        satirlar = list(csv.DictReader(io.StringIO(ham.decode("utf-8"), newline="")))
    except (OSError, UnicodeDecodeError, csv.Error):
        raise Red("ajan1", [("girdi", "Ajan 1 tablosu okunamıyor")])
    if not satirlar or any(satir.get(a) is None for satir in satirlar for a in CSV_ALANLARI):
        raise Red("ajan1", [("girdi", "Ajan 1 tablosu boş ya da zorunlu sütun eksik")])

    sorunlar = []
    if hashlib.md5(ham).hexdigest() != ajan1_md5:
        sorunlar.append(("ajan1_csv.md5", "Ajan 1 CSV'sinin MD5'i devirde bildirilenle uyuşmuyor"))
    if any(s["arac"] != SENTETIK_ARAC for s in satirlar) and not Path(ajan1_yolu).resolve().is_relative_to(KOK):
        sorunlar.append(("ajan1_csv.yol", "gerçek veride Ajan 1 CSV'si repo içinde olmalı"))
    for no, satir in enumerate(satirlar, 2):
        cekilme = zaman(satir["cekilme_zamani"])
        if cekilme is None or not timedelta(0) <= referans - cekilme <= BAYATLIK:
            sorunlar.append((f"satir[{no}].cekilme_zamani", "çekilme zamanı bozuk, gelecekte ya da 72 saatten eski"))
        liste = fiyat(satir["liste_fiyati"])
        indirimli = fiyat(satir["indirimli_fiyat"]) if satir["indirimli_fiyat"] else None
        if liste is None:
            sorunlar.append((f"satir[{no}].liste_fiyati", "geçersiz liste fiyatı"))
        if satir["indirimli_fiyat"] and (indirimli is None or (liste and indirimli >= liste)):
            sorunlar.append((f"satir[{no}].indirimli_fiyat", "geçersiz indirimli fiyat"))
        gorunen = indirimli if satir["indirimli_fiyat"] else liste
        if gorunen is not None and ham_fiyat(satir["ham_fiyat_metni"]) != gorunen:
            sorunlar.append((f"satir[{no}].ham_fiyat_metni", "fiyat, sayfadaki ham metinle uyuşmuyor"))
        if satir["para_birimi"] != "TRY":
            sorunlar.append((f"satir[{no}].para_birimi", "para birimi TRY değil"))
        if not alan_adi_uyumlu(satir):
            sorunlar.append((f"satir[{no}].urun_url", "ürün adresi https değil ya da alan adı rakip siteye ait değil"))
    if sorunlar:
        raise Red("ajan1", sorunlar)
    # Sayfayla uyuşmayan fiyat kaynak hatasıdır; Ajan 2 kontrollerinden önce gelir.
    canli, canli_eksik, uyusmazliklar = canli_kontrol_oku(canli_yolu, satirlar, katalog_yolu, referans)
    if uyusmazliklar:
        raise Red("ajan1", uyusmazliklar)

    try:
        zarf2 = json_oku(zarf_yolu)
        if zarf2["durum"] != "onay" or zarf2["hedef_ajan"] != "ajan3":
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError):
        raise Red("ajan2", [("girdi", "Ajan 2 onay zarfı yok, okunamıyor ya da Ajan 3'e devir içermiyor")])
    try:
        veri = json_oku(girdi)
    except (OSError, ValueError):
        raise Red("ajan2", [("girdi", "Ajan 2 çıktısı okunamıyor ya da sonlu olmayan sayı içeriyor")])

    if not isinstance(veri, dict):
        raise Red("ajan2", [("girdi", "Ajan 2 çıktısı JSON nesnesi değil")])
    sorunlar = [(a, "zorunlu üst alan eksik") for a in UST_ALANLAR if a not in veri]
    if sorunlar:
        raise Red("ajan2", sorunlar)
    if veri["surum"] != "1":
        sorunlar.append(("surum", "sözleşme sürümü 1 değil"))
    if veri["para_birimi"] != "TRY":
        sorunlar.append(("para_birimi", "para birimi TRY değil"))
    beklenen_tur = ("sentetik_test" if all(s["arac"] == SENTETIK_ARAC for s in satirlar)
                    else "web_ve_sentetik_siparis")
    if veri["veri_turu"] != beklenen_tur:
        sorunlar.append(("veri_turu", "veri türü Ajan 1 tablosundaki araç kaydıyla uyuşmuyor"))
    if zaman(veri["uretim_zamani"]) is None:
        sorunlar.append(("uretim_zamani", "üretim zamanı saat dilimli ISO 8601 değil"))
    try:
        donem = veri["siparis_donemi"]
        if date.fromisoformat(donem["baslangic"]) > date.fromisoformat(donem["bitis"]):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        sorunlar.append(("siparis_donemi", "sipariş dönemi eksik, bozuk ya da ters"))
    urunler = veri["urunler"]
    if not isinstance(urunler, list) or not urunler:
        sorunlar.append(("urunler", "ürün listesi boş ya da dizi değil"))
    else:
        for i, urun in enumerate(urunler):
            if not isinstance(urun, dict):
                sorunlar.append((f"urunler[{i}]", "ürün kaydı nesne değil"))
                continue
            sorunlar += [(f"urunler[{i}].{a}", "zorunlu ürün alanı eksik") for a in URUN_ALANLARI if a not in urun]
    if not isinstance(veri["iliskiler"], dict):
        sorunlar.append(("iliskiler", "ilişki nesnesi yok"))
    if sorunlar:
        raise Red("ajan2", sorunlar)
    return satirlar, veri, canli, canli_eksik


# ---------------------------------------------------------------- 2. işleme

def medyana_girer(satir, bizim_fiyat):
    gerekce = satir["elendi"].strip()
    if gerekce == "çoklu paket" and satir["bizim_urun"] in SET_ISTISNASI:
        gerekce = ""
    # eşleşme kuralı 2: işaretlenmemiş olsa da bant dışı fiyat medyana girmez
    karsilastirma = Decimal(satir["indirimli_fiyat"] or satir["liste_fiyati"])
    bantta = bizim_fiyat * Decimal("0.3") <= karsilastirma <= bizim_fiyat * 3
    return not gerekce and bantta and satir["stok_durumu"] != "yok" and satir["kdv_dahil"] == "evet"


def ayni(bulunan, beklenen):
    """Sayı karşılaştırması: bool ve metin kabul edilmez."""
    if beklenen is None:
        return bulunan is None
    if isinstance(bulunan, bool) or not isinstance(bulunan, (int, float)):
        return False
    try:
        return math.isclose(bulunan, beklenen, rel_tol=0, abs_tol=1e-9)
    except OverflowError:  # float'a sığmayan tam sayı
        return False


def isleme(satirlar, veri, katalog_yolu, siparis_yolu, maliyetli=frozenset()):
    """Her sayıyı ham dosyalardan yeniden hesaplar. Fark varsa Red.

    maliyetli: geçerli birim maliyeti verilmiş ürünler.
    """
    katalog = {s["urun"]: s for s in csv_oku(katalog_yolu)}
    siparisler = csv_oku(siparis_yolu)
    eksik = [(f"satir[{no}].bizim_urun", "ürün web fiyatlı listede yok")
             for no, s in enumerate(satirlar, 2) if s["bizim_urun"] not in katalog]
    if eksik:
        raise Red("ajan1", eksik)

    baslangic = date.fromisoformat(veri["siparis_donemi"]["baslangic"])
    bitis = date.fromisoformat(veri["siparis_donemi"]["bitis"])
    sorunlar, ozet, farklar, adetler, cirolar = [], [], [], [], []
    adlar = [u["urun"] for u in veri["urunler"]]
    if sorted(adlar, key=str) != sorted({s["bizim_urun"] for s in satirlar}):
        raise Red("ajan2", [("urunler", "ürün kümesi Ajan 1 tablosuyla birebir değil")])

    for i, urun in enumerate(veri["urunler"]):
        ad, yol = urun["urun"], f"urunler[{i}]"
        kendi = [(no, s) for no, s in enumerate(satirlar, 2) if s["bizim_urun"] == ad]
        liste = Decimal(katalog[ad]["liste_fiyati"])
        gecerli = [Decimal(s["indirimli_fiyat"] or s["liste_fiyati"]) for _, s in kendi
                   if medyana_girer(s, liste)]
        medyan = statistics.median(gecerli) if gecerli else None
        fark = 100 * (liste - medyan) / medyan if medyan else None
        satis = [s for s in siparisler if s["urun"] == ad and s["durum"] == "Teslim Edildi"
                 and baslangic <= date.fromisoformat(s["siparis_tarihi"]) <= bitis]
        adet = sum(int(s["adet"]) for s in satis)
        ciro = sum((Decimal(s["toplam_tutar"]) for s in satis), Decimal(0))
        beklenen = {
            "bizim_liste_fiyati": yuvarla(liste),
            "rakip_medyan_fiyati": yuvarla(medyan) if medyan is not None else None,
            "fiyat_farki_yuzde": yuvarla(fark) if fark is not None else None,
            "kullanilan_rakip_sayisi": len(gecerli),
            "elenen_rakip_sayisi": len(kendi) - len(gecerli),
            "satis_adedi": adet,
            "ciro": yuvarla(ciro),
        }
        for alan, deger in beklenen.items():
            if not ayni(urun[alan], deger):
                sorunlar.append((f"{yol}.{alan}", f"{ad} {alan}: çıktıda {urun[alan]}, yeniden hesapta {deger}"))
        if urun["kategori"] != katalog[ad]["kategori"]:
            sorunlar.append((f"{yol}.kategori", f"{ad}: kategori ürün listesiyle uyuşmuyor"))

        kaynaklar = [k for k in urun["kaynaklar"] if isinstance(k, dict)] \
            if isinstance(urun["kaynaklar"], list) else []
        for no, s in kendi:
            if not any(k.get("kaynak") == s["urun_url"] and k.get("uretim_zamani") == s["cekilme_zamani"]
                       and f"satır {no};" in str(k.get("secim", "")) for k in kaynaklar):
                sorunlar.append((f"{yol}.kaynaklar", f"{ad}: CSV satır {no} için adres ve zamanı uyan kaynak yok"))
        for dosya in (Path(katalog_yolu).name, Path(siparis_yolu).name):
            if not any(str(k.get("kaynak", "")).endswith(dosya) and zaman(k.get("uretim_zamani"))
                       for k in kaynaklar):
                sorunlar.append((f"{yol}.kaynaklar", f"{ad}: {dosya} için zamanlı kaynak kaydı yok"))

        oneri = urun["oneri"] if isinstance(urun["oneri"], dict) else {}
        eylem, kar_durumu = oneri.get("eylem"), oneri.get("kar_durumu")
        if not isinstance(eylem, str) or eylem not in EYLEMLER or (medyan is None and eylem != "veri_topla"):
            sorunlar.append((f"{yol}.oneri.eylem", f"{ad}: eylem sözleşmeye uymuyor"))
        if not str(oneri.get("gerekce", "")).strip():
            sorunlar.append((f"{yol}.oneri.gerekce", f"{ad}: öneri gerekçesi boş"))
        izinli = {"maliyet_eksik", "denetim_bekliyor"} if ad in maliyetli else {"maliyet_eksik"}
        if not isinstance(kar_durumu, str) or kar_durumu not in izinli:
            sorunlar.append((f"{yol}.oneri.kar_durumu",
                             f"{ad}: kar_durumu {' ya da '.join(sorted(izinli))} olmalı"))
        ozet.append({"urun": ad, "eylem": oneri.get("eylem"), "sayilar": beklenen})
        if fark is not None:
            farklar.append(float(fark))
            adetler.append(adet)
            cirolar.append(float(ciro))

    beklenen = {"urun_sayisi": len(farklar), "pearson_fark_adet": pearson(farklar, adetler),
                "pearson_fark_ciro": pearson(farklar, cirolar)}
    for alan, deger in beklenen.items():
        if not ayni(veri["iliskiler"].get(alan, "yok"), deger):
            sorunlar.append((f"iliskiler.{alan}", f"{alan} yeniden hesapla uyuşmuyor"))
    if not veri["iliskiler"].get("kaynaklar"):
        sorunlar.append(("iliskiler.kaynaklar", "ilişki için kaynak kaydı yok"))
    if sorunlar:
        raise Red("ajan2", sorunlar)
    return ozet, beklenen


def pearson(x, y):
    if len(x) < 2:
        return None
    try:
        return yuvarla(statistics.correlation(x, y), 6)
    except statistics.StatisticsError:
        return None


def girdi_tablosu(yol, onek, deger_alani, sifir_olur):
    """Fiyat ya da maliyet CSV'si: (ürün → kayıt, sorunlar). Dosya yoksa kayıt None."""
    if not yol or not Path(yol).is_file():
        return None, []
    alanlar = ["urun", deger_alani, "kaynak", "uretim_zamani"]
    try:
        satirlar = csv_oku(yol)
    except (OSError, UnicodeDecodeError, csv.Error):
        return {}, [(onek, f"{onek} dosyası okunamıyor")]
    if any(s.get(a) is None for s in satirlar for a in alanlar):
        return {}, [(onek, f"{onek} dosyasında zorunlu sütun eksik")]
    kayitlar, sorunlar, gorulen = {}, [], set()
    for no, s in enumerate(satirlar, 2):
        ad, metin = s["urun"].strip(), s[deger_alani].strip()
        hatalar = []
        if not ad or ad in gorulen:
            hatalar.append(("urun", f"{onek} dosyasında ürün boş ya da tekrarlı"))
            kayitlar.pop(ad, None)  # hangi satırın geçerli olduğu belirsiz
        gorulen.add(ad)
        deger = Decimal(metin) if PARA.fullmatch(metin) else None
        if deger is None or (deger == 0 and not sifir_olur):
            hatalar.append((deger_alani, f"{onek} değeri geçerli bir TL tutarı değil"))
        if not s["kaynak"].strip():
            hatalar.append(("kaynak", f"{onek} kaynağı boş"))
        if zaman(s["uretim_zamani"]) is None:
            hatalar.append(("uretim_zamani", f"{onek} üretim zamanı saat dilimli ISO 8601 değil"))
        sorunlar += [(f"{onek}.satir[{no}].{alan}", neden) for alan, neden in hatalar]
        if not hatalar:
            kayitlar[ad] = {"satir": no, "deger": deger, "kaynak": s["kaynak"].strip(),
                            "uretim_zamani": s["uretim_zamani"]}
    return kayitlar, sorunlar


def kar_denetimi(oneriler, fiyatlar, fiyat_sorunlari, maliyetler, maliyet_sorunlari):
    """(onaylanan kalemler, eksikler). oneriler: ürün → (Ajan 2 eylemi, web liste fiyatı).

    Geçersiz öneri, eylemle uyumsuz fiyat ya da eşik altı kâr → Red ajan2. fiyati_koru liste
    fiyatına eşit, kampanya_test_et liste fiyatından düşük olmalı. veri_topla ürünü kâr
    yeterli olsa da onaylanmaz.
    """
    sorunlar = list(fiyat_sorunlari)
    kalemler, eksikler = [], []
    maliyetler = maliyetler or {}
    for ad, f in (fiyatlar or {}).items():
        if ad not in oneriler:
            sorunlar.append((f"fiyat.satir[{f['satir']}].urun", f"{ad}: fiyat önerilen ürün denetlenen veride yok"))
            continue
        eylem, liste = oneriler[ad]
        alan = f"fiyat.satir[{f['satir']}].onerilen_fiyat_tl"
        uyumsuz = ((eylem == "fiyati_koru" and f["deger"] != liste)
                   or (eylem == "kampanya_test_et" and f["deger"] >= liste))
        if uyumsuz:
            kosul = "liste fiyatına eşit" if eylem == "fiyati_koru" else "liste fiyatından düşük"
            sorunlar.append((alan, f"{ad}: Ajan 2 eylemi {eylem}, önerilen fiyat {f['deger']} TL "
                                   f"{kosul} olmalı (liste {liste:.2f} TL)"))
        if ad not in maliyetler:
            eksikler.append(f"{ad} için geçerli birim maliyet yok")
            continue
        m = maliyetler[ad]
        kar = f["deger"] - m["deger"]
        if kar <= KAR_ESIGI:
            sorunlar.append((alan,
                             f"{ad}: {f['deger']} − {m['deger']} = {kar} TL, birim kâr {KAR_ESIGI} TL'nin üstünde değil"))
            continue
        if uyumsuz:
            continue
        if eylem == "veri_topla":
            eksikler.append(f"{ad} için Ajan 2 eylemi veri_topla (veri yetersiz)")
            continue
        kalemler.append({
            "urun": ad, "onerilen_fiyat_tl": float(f["deger"]), "birim_maliyet_tl": float(m["deger"]),
            "birim_kar_tl": float(kar), "esik_tl": float(KAR_ESIGI),
            "kaynak": f["kaynak"], "fiyat_uretim_zamani": f["uretim_zamani"],
            "maliyet_kaynagi": m["kaynak"], "maliyet_uretim_zamani": m["uretim_zamani"],
            "karar": "onay", "gerekce": f"{f['deger']} − {m['deger']} = {kar} TL; birim kâr eşiğin üstünde.",
        })
    if sorunlar:
        raise Red("ajan2", sorunlar)
    if not fiyatlar:
        eksikler.insert(0, "önerilen fiyat girdisi yok")
    eksikler += list(dict.fromkeys(neden for _, neden in maliyet_sorunlari))
    return kalemler, eksikler


# ---------------------------------------------------------------- 3. teslim

def goreli(yol):
    yol = Path(yol).resolve()
    try:
        return yol.relative_to(KOK).as_posix()
    except ValueError:
        return yol.as_posix()


def md5(yol):
    return hashlib.md5(Path(yol).read_bytes()).hexdigest()


def yaz_json(yol, veri):
    Path(yol).parent.mkdir(parents=True, exist_ok=True)
    Path(yol).write_text(json.dumps(veri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def calistir(arg, referans, argv):
    girdiler = (arg.girdi, arg.zarf, arg.ajan1, arg.urun_listesi, arg.siparisler, arg.fiyat, arg.maliyet,
                arg.canli_kontrol)
    iz = {
        "arac": "src/ajan3_denetim.py",
        "komut": " ".join(["python", "src/ajan3_denetim.py"] + list(argv)),
        "baslangic": datetime.now(TR).isoformat(timespec="seconds"),
        "referans_zamani": referans.isoformat(),
        "girdiler": {goreli(p): md5(p) for p in girdiler if p and Path(p).is_file()},
    }
    try:
        satirlar, veri, canli, canli_eksik = alma(arg.girdi, arg.zarf, arg.ajan1, arg.ajan1_md5, referans,
                                                  arg.canli_kontrol, arg.urun_listesi)
        fiyatlar, fiyat_sorunlari = girdi_tablosu(arg.fiyat, "fiyat", "onerilen_fiyat_tl", False)
        maliyetler, maliyet_sorunlari = girdi_tablosu(arg.maliyet, "maliyet", "birim_maliyet_tl", True)
        urunler, iliskiler = isleme(satirlar, veri, arg.urun_listesi, arg.siparisler, set(maliyetler or {}))
        oneriler = {u["urun"]: (u["eylem"], Decimal(str(u["sayilar"]["bizim_liste_fiyati"]))) for u in urunler}
        kalemler, eksikler = kar_denetimi(oneriler, fiyatlar, fiyat_sorunlari, maliyetler, maliyet_sorunlari)
        if veri["veri_turu"] != "sentetik_test":  # gerçek veride elle kontrol kaydı olmadan onay yok
            eksikler += [f"{k['urun']} için geçerli {CANLI_KAYDI} yok" for k in kalemler if k["urun"] not in canli]
        eksikler += canli_eksik
    except Red as red:
        yaz_json(arg.cikis_zarf, {"durum": "red", "hedef_ajan": red.hedef, "gerekce": red.gerekce,
                                  "sorunlu_alanlar": red.alanlar})
        durum, kod, ciktilar = "red", 2, [arg.cikis_zarf]
        print(f"RED → {red.hedef}: {red.gerekce}")
    else:
        ortak = {"veri_turu": veri["veri_turu"], "denetim_zamani": referans.isoformat(),
                 "ajan1_csv": {"yol": goreli(arg.ajan1), "md5": arg.ajan1_md5}}
        if eksikler:
            yaz_json(arg.rapor, {
                "durum": "beklemede",
                "bekleme_nedeni": "; ".join(eksikler) + ". Onay verilmedi.",
                **ortak,
                "gecen_kontroller": GECEN_KONTROLLER,
                "yapilmayan_kontroller": ["kâr eşiği (bütün kapsam için)", CANLI],
                "urunler": urunler,
                "iliskiler": iliskiler,
            })
            durum, kod, ciktilar = "beklemede", 3, [arg.rapor]
            print(f"BEKLEMEDE: veri kontrolleri geçti, onay yok: {'; '.join(eksikler)}.")
        else:
            canli_tam = all(k["urun"] in canli for k in kalemler)
            for k in kalemler:
                if k["urun"] in canli:
                    k["canli_kontrol"] = canli[k["urun"]]
            zarf = {"durum": "onay", "hedef_ajan": None,
                    "gerekce": f"Raporda listelenen {len(kalemler)} ürün kaynak, hesap ve kâr kontrollerini geçti.",
                    "sorunlu_alanlar": []}
            yaz_json(arg.nihai_rapor, {
                "durum": "onay",
                **ortak,
                "fiyat_dosyasi": goreli(arg.fiyat),
                "maliyet_dosyasi": goreli(arg.maliyet),
                **({"canli_kontrol_dosyasi": goreli(arg.canli_kontrol)} if arg.canli_kontrol else {}),
                "gecen_kontroller": GECEN_KONTROLLER + ["kâr eşiği"] + ([CANLI_KAYDI] if canli_tam else []),
                "yapilmayan_kontroller": [] if canli_tam else [CANLI],
                "urunler": kalemler,
                "zarf": zarf,
            })
            yaz_json(arg.cikis_zarf, zarf)
            durum, kod, ciktilar = "onay", 0, [arg.nihai_rapor, arg.cikis_zarf]
            not_canli = ("Elle canlı fiyat kontrol kaydı denetlendi; kod sayfaya istek atmadı." if canli_tam
                         else "Canlı fiyat doğrulaması bu kodda yapılmadı.")
            print(f"ONAY: {', '.join(k['urun'] for k in kalemler)}. {not_canli}")
    iz.update(sonuc=durum, cikis_kodu=kod, cikti={goreli(c): md5(c) for c in ciktilar},
              bitis=datetime.now(TR).isoformat(timespec="seconds"))
    yaz_json(Path(arg.iz_klasoru) / f"{datetime.now(TR):%Y%m%d-%H%M%S}-{durum}.json", iz)
    return kod


class Ayristirici(argparse.ArgumentParser):
    def error(self, message):
        """Kullanım hataları 1 ile çıkar; 2 yalnız red demektir."""
        self.print_usage(sys.stderr)
        self.exit(1, f"Hata: {message}\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    p = Ayristirici(description="Ajan 3 denetimi: kaynak, hesap ve kâr eşiği")
    p.add_argument("--girdi", required=True, help="Ajan 2'nin JSON çıktısı")
    p.add_argument("--zarf", required=True, help="Ajan 2'nin onay zarfı")
    p.add_argument("--ajan1", required=True, help="Ajan 2'nin kullandığı Ajan 1 CSV'si")
    p.add_argument("--ajan1_md5", required=True, help="Devirde bildirilen Ajan 1 CSV MD5'i (küçük harf)")
    p.add_argument("--fiyat", help="CSV: urun,onerilen_fiyat_tl,kaynak,uretim_zamani")
    p.add_argument("--maliyet", help="CSV: urun,birim_maliyet_tl,kaynak,uretim_zamani")
    p.add_argument("--canli_kontrol", help="CSV: " + ",".join(CANLI_ALANLARI) + " (gerçek veride onay için)")
    p.add_argument("--urun_listesi", default=str(KOK / "data/urun-listesi-web.csv"))
    p.add_argument("--siparisler", default=str(KOK / "data/siparisler-web.csv"))
    p.add_argument("--referans", help="Yalnız sentetik test girdisi için sabit denetim zamanı")
    p.add_argument("--rapor", default=str(KOK / "data/ajan3-ara-rapor.json"))
    p.add_argument("--nihai_rapor", default=str(KOK / "data/ajan3-nihai-rapor.json"))
    p.add_argument("--cikis_zarf", default=str(KOK / "data/ajan3-zarf.json"))
    p.add_argument("--iz_klasoru", default=str(KOK / "runs/ajan3"))
    arg = p.parse_args(argv)
    girdiler = {Path(g).resolve() for g in (arg.girdi, arg.zarf, arg.ajan1, arg.urun_listesi,
                                             arg.siparisler, arg.fiyat, arg.maliyet, arg.canli_kontrol) if g}
    ciktilar = (arg.rapor, arg.nihai_rapor, arg.cikis_zarf)
    if girdiler & {Path(c).resolve() for c in ciktilar}:
        p.error("çıktı yolu bir girdi dosyasıyla aynı olamaz")
    if len({Path(c).resolve() for c in ciktilar}) != len(ciktilar):
        p.error("çıktı yolları birbirinden farklı olmalı")
    # Önceki sonuç, bu çalıştırma hata verse bile geçerliymiş gibi kalmaz.
    for eski in ciktilar:
        Path(eski).unlink(missing_ok=True)
    for secenek in ("fiyat", "maliyet", "canli_kontrol"):
        yol = getattr(arg, secenek)
        if yol is not None and not Path(yol).is_file():
            p.error(f"--{secenek} ile verilen dosya bulunamadı: {yol}")
    referans = datetime.now(TR).replace(microsecond=0)
    if arg.referans:
        referans = zaman(arg.referans)
        if referans is None:
            p.error("--referans saat dilimli ISO 8601 olmalı")
        try:
            gercek = any(s.get("arac") != SENTETIK_ARAC for s in csv_oku(arg.ajan1))
        except (OSError, UnicodeDecodeError, csv.Error):
            gercek = False  # okunamayan tablo alma aşamasında gerekçeli red alır
        if gercek:
            p.error("--referans yalnız sentetik test girdisinde kullanılır")
    return calistir(arg, referans, argv)


if __name__ == "__main__":
    sys.exit(main())
