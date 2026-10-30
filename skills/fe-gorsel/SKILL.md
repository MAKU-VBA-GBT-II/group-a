---
name: fe-gorsel
description: Grup A'nın Görev 2 sipariş verisinden (data/siparisler-g2.csv) src/fe_gorsel.py ile 3 PNG grafik (zaman serisi + kanal kırılımı + dağılım) üretip visuals/ klasörüne kaydeder. Grafik, görselleştirme veya grafik güncellemesi istendiğinde kullan.
---

# fe-gorsel — Görev 2 grafik seti

**Amaç:** FE rolü, DQ'nun şemasına (`docs/veri-sozlugu.md`) ve metrik tanımlarına (`docs/analiz-g2.md`) dayanarak BE'nin ürettiği veriden üç grafiği üretir; her grafik, analiz belgesindeki sayılarla birebir tutarlı ve tek başına okunabilir olur.

| Dosya | Tür | Metrik | Ne gösterir |
|---|---|---|---|
| `visuals/haftalik-net-ciro.png` | Zaman serisi (çizgi + nokta) | M3 — haftalık net ciro | Pazartesi başlangıçlı haftalara göre Σ `toplam_tutar` (bin TL); 26 tam hafta, ortalama çizgisi, iki kampanya haftası işaretli |
| `visuals/kanal-ciro-payi.png` | Kategorik kırılım (yatay çubuk) | M4 — kanal bazlı net ciro | Web / Mobil / Pazaryeri için Σ `toplam_tutar` (bin TL) ve toplam içindeki pay (%); büyükten küçüğe |
| `visuals/siparis-tutari-dagilimi.png` | Dağılım (histogram) | `toplam_tutar` + M2 | Sipariş tutarlarının yayılımı; M2 (ortalama sepet) dikey kesikli çizgiyle |

## Çıktı formatı kuralları

Bunlar `#63`'ün kabul kriterleriyle birebir örtüşür; biri sağlanmazsa teslim eksiktir.

1. **Filtre:** Para metrikleri **yalnızca** `durum == "Teslim Edildi"` satırlarından hesaplanır. İade ve iptal ciroya girmez.
2. **Her grafikte:** başlık, x ekseni etiketi, y ekseni etiketi, birim (bin TL / TL / sipariş sayısı) ve metrik kodu bulunur.
3. **Türkçe karakter:** ş, ğ, İ, ı, ö, ü, ç bozulmadan basılır (`DejaVu Sans`). Kutu veya soru işareti çıkarsa grafik kabul edilmez.
4. **Sayılar:** Grafikteki her sayı veriden hesaplanır, elle yazılmaz; `docs/analiz-g2.md` ile birebir aynı olmalıdır.
5. **Biçim:** Para ekseni bin TL, Türkçe binlik ayırıcı (`1.185`); yüzdeler virgüllü (`%44,3`).
6. **Dosya adları** yukarıdaki tablodaki gibi sabittir; değişirse `AGENTS.md`, `docs/analiz-g2.md` ve rapordaki bağlantılar da güncellenir.
7. **Tekrarlanabilirlik:** Aynı veri dosyası → birebir aynı PNG. Rastgelelik yok.
8. **Hafta tanımı** DQ'nun betiğiyle aynıdır: `resample("W-MON", label="left", closed="left")`. DQ tanımı değiştirirse betik de güncellenir.

## Girdiler

- Veri: `data/siparisler-g2.csv` (BE'nin "Veri hazır" yorumundaki commit)
- Şema: `docs/veri-sozlugu.md` — alanlar, değer listeleri, M1–M6 tanımları, "Grafik eşlemesi (FE)" bölümü
- Metrik sonuçları: `docs/analiz-g2.md` (DQ'nun "Analiz hazır" yorumu)
- İlgili Issue'lar: G2-gorsel (#63), G2-sem (#60), G2-veri (#61), G2-analiz (#62)

## Adımlar

1. **Önce taslak (zorunlu, kod yazmadan):** Üç grafiğin mockup'ı **kağıtta ya da bir çizim aracında** hazırlanır ve `#63`'e yüklenir; DQ'nun kısa görüşü alınır. Betikle taslak üretmek bu adımın yerine geçmez (hocanın #46 notu). **Taslak Issue'ya eklenip DQ görüşü alınmadan koda geçme.**
2. **Devir teslimleri kontrol et:** BE'nin "Veri hazır" (#63) ve DQ'nun "Analiz hazır" (#63) yorumları var mı? Yoksa dur ve sor. Veri yorumu olmadan iskelet yazılabilir, ama son grafikler analiz yorumu olmadan üretilmez.
3. **Güncel veriyi çek ve ortamı hazırla:** `git pull`; bağımlılıklar kurulu değilse `pip install -r requirements.txt`.
4. **Grafikleri üret:** depo kökünde `python src/fe_gorsel.py`. Çıktı: yukarıdaki üç PNG.
5. **Kendi kontrolünü yap:**
   - Üç PNG'yi aç: başlık, iki eksen etiketi, birim ve metrik kodu görünüyor mu? Türkçe karakterler bozuk mu?
   - Kırılımdaki paylar `docs/analiz-g2.md` M4 tablosundaki paylarla birebir aynı mı?
   - Zaman serisindeki ortalama çizgisi M3'teki haftalık ortalamayla aynı mı? Kampanya haftaları (9–15 Mart, 11–17 Mayıs) işaretli mi?
   - Histogramdaki dikey çizgi M2 ile aynı mı ve dağılımın tepesinin **sağında** mı? (Sağa çarpık dağılımda ortalama, en sık görülen değerden büyüktür.)
   - Betiği ikinci kez çalıştır; PNG'ler değişmemeli (`md5sum visuals/*.png`).
6. **Commit at:** `feature/gorsel` dalında; `main`'e doğrudan commit yok.
7. **PR aç (Hafta 6):** başlık `G2 grafik seti`, açıklamaya `Closes #63` + prompt özeti; **Reviewers: DQ**. DQ'nun yorumlarına PR üzerinden cevap ver, düzeltmeleri aynı dala commit'le, onay sonrası merge düğmesine PR sahibi basar.
8. **Kanıt yorumu yaz (#63):** commit hash + üç dosya adı + hangi metrikleri gösterdikleri + "Üretim: fe-gorsel skill'i ile, \<araç\>". Ardından Issue'yu kapat ve panoda Done'a taşı.

## Reddetme durumları

Aşağıdaki isteklerde üretim **yapılmaz**; sebebi yazılıp ilgili role yönlendirilir.

- **Gerçek kişisel veri.** Grafiğe gerçek müşteri adı, e-posta, telefon, adres, TC kimlik numarası veya başka gerçek kişi verisi eklenmesi istenirse reddedilir. Bu depodaki tüm veri simülasyon ürünüdür; müşteriler yalnızca sentetik kimlikle (`M0001`) temsil edilir (ders kuralı §3.1, şema notu). Gerçek veri getirilmesi önerilse de kabul edilmez.
- **Veriden hesaplanmayan sayı.** "Şu rakamı biraz yukarı yaz", "grafikte daha iyi görünsün" türü istekler reddedilir. Grafikteki her sayı `data/siparisler-g2.csv`'den hesaplanır.
- **Analizle çelişen sayı.** `docs/analiz-g2.md` ile tutmayan bir değer grafiğe yazılmaz. Fark varsa önce DQ'ya sorulur; kaynak düzelmeden grafik üretilmez.
- **Filtreyi bozma.** İade ve iptal satırlarını ciroya dahil eden bir "toplam" istenirse reddedilir; şema para metriklerini `durum == "Teslim Edildi"` ile sınırlar. İade/iptal ayrı bir metriktir (M6).
- **Veri dosyasını değiştirme.** FE veriyi üretmez ve düzeltmez. `data/` altındaki dosyada sorun görülürse BE'ye (#61) `bug` Issue'su açılır.
- **Taslaksız üretim.** Taslak `#63`'e eklenmeden ve DQ görüşü alınmadan grafik kodu yazılmaz (#46).

## Örnek giriş / çıkış

**Giriş (ajana verilen talimat):**

```
fe-gorsel skill'ini kullanarak data/siparisler-g2.csv'den visuals/ altındaki
üç grafiği üret ve docs/analiz-g2.md ile karşılaştırarak kontrol et.
```

**Çıkış (konsol):**

```
Okunan: data/siparisler-g2.csv — 8208 satır, 14 sütun
Filtre: durum == "Teslim Edildi" → 7383 satır
Yazıldı: visuals/haftalik-net-ciro.png        (M3, 26 hafta)
Yazıldı: visuals/kanal-ciro-payi.png          (M4, 3 kanal)
Yazıldı: visuals/siparis-tutari-dagilimi.png  (M2 çizgisiyle)
```

Üretilen dosyalar: üç PNG (`visuals/`). Her biri 150 DPI, başlık + iki eksen etiketi + birim + metrik kodu taşır; aynı veriyle ikinci çalıştırmada MD5'leri değişmez.

**Reddetme örneği:**

```
Giriş:  "Grafiğe müşterilerin gerçek adlarını da ekle."
Çıkış:  Üretim yapılmadı. Bu depodaki veri simülasyondur ve gerçek kişi
        verisi içermez (ders kuralı §3.1); musteri_id sentetik bir kimliktir.
        Kanal, kategori veya şehir kırılımı istersen üretebilirim.
```

## Tasarım kuralları

- Renkler betiğin başındaki sabitlerde (`RENK_ANA`, `RENK_VURGU`, `RENK_GRI`); grafik içinde sihirli değer kullanma.
- Sütun adları betiğin başında sabit olarak tutulur (`SUTUN_TARIH`, `SUTUN_TUTAR`, `SUTUN_KANAL`, `SUTUN_DURUM`); şema değişirse tek yerden güncellenir.
- Kampanya haftaları şema parametrelerinden (`kampanya_donemleri`) okunur, tarih elle yazılmaz.
- Dosya adları sabitlerde (`ZAMAN_SERISI`, `KIRILIM`, `DAGILIM`).
- **Hata yönetimi:** veri dosyası yoksa, beklenen sütunlar eksikse veya filtre sonrası satır kalmazsa betik çökmez; `ValueError` ile neyin eksik olduğunu söyleyen bir mesaj verir ve PNG yazmaz.

## Kullanılan dosyalar

- **Okur:** `data/siparisler-g2.csv`, `docs/veri-sozlugu.md`, `docs/analiz-g2.md` (kontrol için)
- **Yazar:** `visuals/haftalik-net-ciro.png`, `visuals/kanal-ciro-payi.png`, `visuals/siparis-tutari-dagilimi.png`
- **Çalıştırır:** `src/fe_gorsel.py`
- **Bağımlılıklar:** Python 3, pandas, matplotlib. Kurulum: `pip install -r requirements.txt`. Ağ erişimi gerekmez.

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.):

- Üretim: "fe-gorsel skill'ini kullanarak data/siparisler-g2.csv'den visuals/ altındaki üç grafiği üret ve kontrol et."
- Değişiklik: "fe-gorsel skill'ini kullanarak kırılım grafiğini şehir bazlı ciroya çevir."

Elle çalıştırma (depo kökünde):

```bash
pip install -r requirements.txt   # ilk kez çalıştırırken
python src/fe_gorsel.py           # grafikler → visuals/
python src/fe_gorsel.py --help    # dosya yolu ve çıktı klasörü seçenekleri
```

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (yapay zekâ ajanı).
- **Görev 1 (#15, Sema Nur Doğan):** `src/fe_gorsel.py`, skill ve iki grafik Claude ile üretildi; #28/#29 düzeltmeleri aynı skill'le yapıldı (c9e31b1, 4e0012f).
- **Görev 2 devralma (#63, Hilal Elçin Şahin):** Skill, `docs/veri-sozlugu.md`'deki "Grafik eşlemesi (FE)" bölümü ve #63 kabul kriterleri okutularak üç grafiğe göre güncellendi; reddetme durumları ve örnek giriş/çıkış çifti Görev 2 kuralı (ders planı md.399) gereği eklendi.
- **Taslak (#63):** Üç grafiğin taslağı kağıda elle çizilip Issue'ya yüklendi, DQ görüşü alındıktan sonra koda geçildi (#46).
- **Kural:** Commit'i ajan atar veya mesajın sonuna `Co-Authored-By:` satırı eklenir; kapanan Issue'ya ve PR açıklamasına "Üretim: fe-gorsel skill'i ile, \<araç\> — prompt özeti: …" satırı yazılır.
