---
name: be-veri
description: Grup A'nın sipariş veri setini (data/siparisler.csv) sabit tohumla üretir ve şemayı docs/veri-sozlugu-g1.md dosyasına yazar. Veri seti üretilecek, yeniden üretilecek veya şema güncellenecek zaman kullan.
---

# be-veri — Sipariş verisi üretimi

**Ne yapar:** `src/veri_uret.py` betiğiyle sabit tohumlu, tekrarlanabilir sentetik sipariş verisi üretir (`data/siparisler.csv`) ve bu verinin şemasını `docs/veri-sozlugu-g1.md` dosyasına yazar. Üretilen ana dosya **temizdir**: eksik değer, aralık dışı değer veya tutarsız kategori adı içermez. Kirli (hatalı) kopyaları DQ kendi tarafında üretir; bu skill kirli veri üretmez.

Gerçek kişi verisi asla kullanılmaz — tüm değerler simülasyon ürünüdür (AGENTS.md kural 2).

## Girdiler

- Anlaşılan şema (aşağıdaki **Şema** bölümü). `docs/veri-sozlugu-g1.md` ve `src/veri_uret.py` içindeki sabitler bununla birebir aynı tutulur; biri değişirse üçü birlikte güncellenir (bkz. **Şema değişirse**).
- DQ test senaryoları: `tests/test-cases.md` (üretim bunları geçecek şekilde yapılır)
- İlgili Issue: G1-veri (#13), devir teslim: G1-analiz (#14) ve G1-gorsel (#15), para alanlarının 2 ondalık biçimi (#27), veri sınırlılıkları (#30)

## Şema

Sütunlar **tam olarak bu sırada**, 9 sütun, fazla/eksik yok:

| # | Alan | Tip | Geçerli aralık / değerler | Birim |
|---|---|---|---|---|
| 1 | `siparis_id` | int | 1'den başlar, 1'er artar, benzersiz | – |
| 2 | `siparis_tarihi` | tarih (`YYYY-MM-DD`) | 2026-01-01 – 2026-09-30 | – |
| 3 | `kategori` | metin | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Kitap | – |
| 4 | `urun` | metin | kategorisine ait ürün adı (her kategoride 5 ürün) | – |
| 5 | `adet` | int | 1 – 10 | adet |
| 6 | `birim_fiyat` | float | 50.00 – 5000.00, 2 ondalık | TL |
| 7 | `toplam_tutar` | float | `adet × birim_fiyat`, 2 ondalığa yuvarlı (50 – 50000) | TL |
| 8 | `sehir` | metin | İstanbul, Ankara, İzmir, Burdur, Antalya | – |
| 9 | `odeme_tipi` | metin | Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme | – |

- **Satır sayısı:** 400 (başlık hariç, tam olarak)
- **Tohum (seed):** 42
- **Biçim:** virgül ayraçlı, nokta ondalıklı, UTF-8, satır sonu `\n`; para alanları dosyada **tam 2 ondalıkla** yazılır (`1667.40`, `1667.4` değil)
- **Boş değer:** hiçbir alanda yok

### Ürün listesi

| Kategori | Ürünler |
|---|---|
| Elektronik | Kablosuz Kulaklık, Bluetooth Hoparlör, Powerbank, Akıllı Saat, Klavye |
| Giyim | Tişört, Kot Pantolon, Sweatshirt, Spor Ayakkabı, Mont |
| Ev & Yaşam | Kahve Makinesi, Battaniye, Masa Lambası, Saklama Kabı Seti, Halı |
| Kozmetik | Nemlendirici, Şampuan, Parfüm, Güneş Kremi, Ruj |
| Kitap | Roman, Deneme, Ders Kitabı, Çocuk Kitabı, Şiir Kitabı |

### Üretim kuralları

1. **Kategori adları birebir aynı yazılır.** `Ev & Yaşam` her satırda tam olarak böyledir — büyük/küçük harf, boşluk veya `&` farkı olmaz.
2. **`urun` daima kendi kategorisinden seçilir.** Kategoriler arası karışma olmaz.
3. **`birim_fiyat` kategoriye göre makul aralıkta üretilir:** Elektronik 300–5000, Giyim 100–2500, Ev & Yaşam 80–4000, Kozmetik 50–1200, Kitap 50–400 TL (aynı tablo `docs/veri-sozlugu-g1.md` → Geçerli değer listeleri; betikte `KATEGORI_URUN`). Hepsi şemadaki 50–5000 sınırları içinde kalır.
4. **`toplam_tutar` hesaplanır, rastgele üretilmez:** `round(adet * birim_fiyat, 2)`. DQ bunu TC-08'de test eder.
5. **Fiyatlarda biçimlendirme yok, ama her zaman 2 ondalık var:** binlik ayırıcı yok, "TL" yazısı yok, sadece sayı (`1249.90`). `round(x, 2)` bunu tek başına sağlamaz: pandas dosyaya yazarken sondaki sıfırı düşürür (`1667.40` → `1667.4`). Bu yüzden CSV `float_format="%.2f"` ile yazılır. DQ bunu TC-09'da test eder (#27).
6. **Her kategori, her şehir ve her ödeme tipi en az bir kez geçer**; dağılım tamamen düzgün olmak zorunda değil.
7. **Tohum sabittir:** `numpy.random.default_rng(42)`; başka rastgele kaynak kullanılmaz. Betik iki kez çalıştırıldığında **birebir aynı** dosya üretilmelidir.

### Dağılımlar ve üretim sırası

Tüm rastgele değerler tek bir `rng = numpy.random.default_rng(42)` nesnesinden, **bu sırayla** çekilir. Sıra değişirse kurallara uyan ama farklı bir dosya çıkar; bayt bayt aynı dosya için sıra korunur.

1. `kategori`, `sehir`, `odeme_tipi`: her listenin tamamı bir kez eklenir (her değer en az bir kez geçsin), kalan satırlar listeden eşit olasılıkla seçilir; ardından üç dizi sırayla karıştırılır.
2. Her satır için `urun`: kendi kategorisinin 5 ürününden eşit olasılıkla; `birim_fiyat`: kategorinin fiyat aralığında düzgün dağılımla, 2 ondalığa yuvarlanır.
3. `adet`: 1–10 arasında eşit olasılıklı tam sayı; `toplam_tutar = round(adet * birim_fiyat, 2)`.
4. `siparis_tarihi`: 2026-01-01 – 2026-09-30 arasındaki günlerden eşit olasılıkla.
5. Satırlar tarihe göre (kararlı sıralama, `mergesort`) dizilir; `siparis_id` bu sırayla 1'den 400'e verilir.

## Adımlar

1. **Şemayı doğrula:** Yukarıdaki şemayı `tests/test-cases.md`'deki referans şema ile karşılaştır. Fark varsa DQ ile netleştir; şemayı tek taraflı değiştirme.
2. **`src/veri_uret.py` betiğini yaz/güncelle:** Şema sabitlerini (`SUTUNLAR`, `KATEGORI_URUN`, `SEHIRLER`, `ODEME_TIPLERI`, `SEED`, `SATIR_SAYISI`) dosyanın başında sabit olarak tanımla — gömülü sihirli sayı bırakma.
3. **Üret:** Depo kökünde `python src/veri_uret.py` çalıştır. Çıktı: `data/siparisler.csv`.
4. **Kendi kontrolünü yap** (DQ'ya göndermeden önce). Her madde DQ'nun bir test senaryosunun aynasıdır (`tests/test-cases.md`, TC-01…TC-12):
   - Satır sayısı tam 400 mü? (TC-02)
   - Sütun adları ve sırası şemayla birebir mi? (TC-03)
   - `adet` 1–10, `birim_fiyat` 50–5000, `siparis_tarihi` 2026-01-01 – 2026-09-30 aralığında mı; tarih `YYYY-MM-DD` olarak ayrıştırılıyor mu? (TC-04)
   - `set(df.kategori)` tam olarak şemadaki 5 kategori mi? (TC-05)
   - `df.isna().sum().sum() == 0` ve boş metin (`""`) yok mu? (TC-06)
   - `df.siparis_id.duplicated().sum() == 0` ve birebir tekrar eden satır yok mu? (TC-07)
   - `(df.toplam_tutar - (df.adet * df.birim_fiyat).round(2)).abs()` hiçbir satırda 0.01'den büyük değil mi? (TC-08)
   - Dosya **ham metin olarak** okununca (`pd.read_csv(..., dtype=str)`) `birim_fiyat` ve `toplam_tutar` her satırda tam 2 ondalık mı (`^\d+\.\d{2}$`)? Sayıya çevirerek bakılırsa bu hata görünmez. (TC-09)
   - `set(df.sehir)` ve `set(df.odeme_tipi)` tam olarak şemadaki değer listeleri mi? (TC-10)
   - Her satırdaki `urun`, o satırın `kategori`sinin 5 ürününden biri mi? (TC-11)
   - `siparis_id` tam olarak 1, 2, …, 400 mü ve dosya `siparis_tarihi`ne göre artan sıralı mı? (TC-12)
   - Yazılan dosya diskten geri okununca doğrulanan metinle bayt bayt aynı mı? (TC-01)
   - Betiği ikinci kez çalıştırıp dosyanın değişmediğini doğrula (tekrarlanabilirlik).

   `src/veri_uret.py` bu kontrollerin hepsini kendisi yapar: dosyayı yazmadan önce `dogrula` ve `metni_dogrula`, yazdıktan sonra geri okuma. Biri kalırsa `ValueError` verir; yazmadan önceki kontrollerden biri kalırsa dosya hiç yazılmaz. Geri okuma (TC-01) ise dosya yazıldıktan sonra çalışır: bu kontrol kalırsa diskte bozuk bir dosya kalmış olabilir; o dosya kullanılmaz, silinir ve betik yeniden çalıştırılır. Kontroller `assert` ile değil `kontrol()` ile yazılır, böylece `python -O` ile çalıştırılsa bile atlanmaz. DQ yeni bir test senaryosu eklerse aynası buraya ve betiğe de eklenir.
5. **Şemayı yaz:** `docs/veri-sozlugu-g1.md` dosyasını yukarıdaki **Şema** bölümünden üret. Şu dördü mutlaka yazılı olsun: geçerli `sehir` ve `odeme_tipi` listesi, `siparis_id` benzersiz ve 1'den başlıyor, hiçbir alanda boş değer yok, kullanılan tohum değeri (42) ve satır sayısı (400).
6. **Commit at:** `G1-veri: siparisler.csv, veri-sozlugu-g1.md ve be-veri skill'i eklendi (#13)`. Bir hata Issue'sunu düzeltiyorsan mesaja `Fixes #<numara>` ekle; Issue otomatik kapanır.
7. **Issue'ya kanıt yorumu yaz:** commit hash + üretilen dosyalar + satır sayısı + tohum. Ardından **hem G1-analiz (#14, DQ) hem G1-gorsel (#15, FE)** Issue'suna aşağıdaki devir teslim yorumunu yaz; bu yorum DQ ve FE'nin başlama iznidir. Hata düzeltmesinde Issue otomatik kapansa bile ne düzeldiğini yazan bir kanıt yorumu bırak. Her kapanış yorumunun sonuna şu satırı ekle: `Üretim: be-veri skill'i ile, <araç>` (örn. Claude).

### Devir teslim yorumu şablonu

> Veri hazır — commit `<hash>`. Dosya: `data/siparisler.csv` (400 satır, tohum 42). Şema: `docs/veri-sozlugu-g1.md`.

## Şema değişirse

Şema her değiştiğinde **üç dosya birlikte** güncellenir, yoksa testler kalır:

1. Bu skill'in **Şema** bölümü
2. `src/veri_uret.py` içindeki sabitler
3. `docs/veri-sozlugu-g1.md`

Ardından DQ'ya haber ver — `tests/test-cases.md` ve `src/dq_test.py` içindeki şema sabitleri de güncellenmeli.

## Bilinen sınırlılıklar (#30)

Veri, Görev 1'in hattını sınamak için üretilmiş basit bir simülasyondur; analiz ve grafikler yorumlanırken şunlar dikkate alınır:

- **Haftada ortalama ~10 sipariş var**; tek bir büyük sipariş o haftanın cirosunu belirgin biçimde değiştirebilir, haftalık ciro bu yüzden oynaktır.
- **Ürünlerin kendine özgü fiyatı yok:** fiyat, ürünün kategorisinin aralığından çekilir (ör. aynı Powerbank 387 TL de 4.647 TL de olabilir). Ürün bazlı Top-3 sıralaması temkinle yorumlanmalı.
- **Dalgalanmaların nedeni yok:** tarihler aralık içinde düzgün dağılımla seçilir; hafta sonu, kampanya ve sezon etkisi modellenmedi.

Görev 1 verisi bilerek değiştirilmedi (analiz, testler ve grafikler bu veriye dayanıyor); bu maddeler Görev 2 simülasyonunda ele alınacak.

## Kapsam dışı

- **Görev 3 veri değişimi** (`exchange/output.csv`, Grup B'ye giden sipariş akışı) bu skill'in işi değildir. Gönderilecek alanlar Görev 3'te iki şirketin DQ'larının yazacağı `docs/veri-sozlesmesi.md` ile belirlenir; lojistik için gereken ek alanlar (ör. ağırlık, ilçe, teslim tarihi) orada kararlaştırılır ve bu skill o zaman güncellenir.

## Ne zaman üretmez

- **Gerçek kişi verisi istenirse** (ad-soyad, TC no, telefon, adres, gerçek müşteri kaydı): üretmez, nedenini söyler ve aynı alanın sentetik karşılığını önerir.
- **Şema DQ ile netleşmeden** alan eklemek, silmek veya aralık değiştirmek istenirse: önce DQ'ya sorar (Adım 1); şemayı tek taraflı değiştirmez.

## Örnek çıktı

`python src/veri_uret.py` sonrası `data/siparisler.csv` dosyasının ilk satırları:

```csv
siparis_id,siparis_tarihi,kategori,urun,adet,birim_fiyat,toplam_tutar,sehir,odeme_tipi
1,2026-01-01,Kitap,Şiir Kitabı,5,333.48,1667.40,Burdur,Kapıda Ödeme
2,2026-01-01,Ev & Yaşam,Battaniye,1,2661.24,2661.24,İzmir,Banka Kartı
3,2026-01-02,Kozmetik,Güneş Kremi,2,1194.05,2388.10,Ankara,Kredi Kartı
```

## Kullanılan dosyalar

- **Okur:** `tests/test-cases.md`
- **Yazar:** `data/siparisler.csv`, `docs/veri-sozlugu-g1.md`
- **Çalıştırır:** `src/veri_uret.py`
- **Bağımlılıklar:** Python 3.10+, pandas (1.5+), numpy. Kurulum: `pip install pandas numpy`. Betik yalnızca bunları kullanır; ağ erişimi gerekmez.

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.):

- Üretim: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret."
- Şema değişikliği: "be-veri skill'ini kullanarak şemaya `kargo_ucreti` alanını ekle ve veriyi yeniden üret."

Elle çalıştırma: önce bağımlılıkları kur (`pip install pandas numpy`), sonra depo kökünde `python src/veri_uret.py`. Aynı tohumla her çalıştırmada aynı dosya üretilir.

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **İlk üretim (#13):** Bu skill, `src/veri_uret.py`, `docs/veri-sozlugu-g1.md` ve `data/siparisler.csv` Claude ile üretildi (3b34e4b, fa3b368; commit'lerde `Co-Authored-By: Claude` izi var). Prompt: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret."
- **Düzeltme (#27):** DQ'nun önerdiği `float_format="%.2f"` düzeltmesi Claude ile uygulandı, veri yeniden üretildi (1f8beb8, `Fixes #27`). Değerler değişmedi, yalnızca yazım biçimi düzeldi. Bu commit'te `Co-Authored-By` satırı yok; ajan izi #27'deki kanıt yorumunda.
- **Skill güncellemesi (#32):** #27'de öğrenilen kural skill'e işlendi, betiğe yazmadan önce ham metin kontrolü eklendi. Claude ile yapıldı (Claude in Chrome); çıktı dosyası bayt bayt aynı kaldı.
- **Skill güncellemesi (#30, #32):** Devir teslim şablonu (#14 + #15), tam kategori fiyat tablosu, "Dağılımlar ve üretim sırası", "Bilinen sınırlılıklar" ve "Kapsam dışı" bölümleri eklendi; kişi adı yerine rol yazıldı. Betikte `assert` kontrolleri `kontrol()` ile `ValueError`'a çevrildi (`python -O` ile de çalışır). Çıktı dosyası bayt bayt aynı, `dq_test.py` 9/9. Claude ile yapıldı (Claude in Chrome).
- **Skill ve betik güncellemesi (#32):** DQ'nun eklediği TC-10…TC-12 için betiğe ürün–kategori (TC-11) ve ardışık id + tarih sırası (TC-12) kontrolleri eklendi, şehir/ödeme kontrolü TC-10 olarak etiketlendi; dosya yazıldıktan sonra diskten geri okunup doğrulanıyor (TC-01). Skill'deki kontrol listesi betikle eşitlendi (aralık kontrolleri dahil, her madde bir TC'ye bağlı), bağımlılıklar yazıldı. Çıktı dosyası bayt bayt aynı (md5 `e64f4def…`, `python` ve `python -O`), `dq_test.py` 12/12. Claude ile yapıldı (Claude in Chrome).
