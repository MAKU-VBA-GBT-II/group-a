---
name: be-veri
description: Grup A'nın sipariş veri setini (data/siparisler.csv) sabit tohumla üretir ve şemayı docs/veri-sozlugu-g1.md dosyasına yazar. Veri seti üretilecek, yeniden üretilecek veya şema güncellenecek zaman kullan.
---

# be-veri — Sipariş verisi üretimi

**Ne yapar:** `src/veri_uret.py` betiğiyle sabit tohumlu, tekrarlanabilir sentetik sipariş verisi üretir (`data/siparisler.csv`) ve bu verinin şemasını `docs/veri-sozlugu-g1.md` dosyasına yazar. Üretilen ana dosya **temizdir**: eksik değer, aralık dışı değer veya tutarsız kategori adı içermez. Kirli (hatalı) kopyaları DQ kendi tarafında üretir; bu skill kirli veri üretmez.

Gerçek kişi verisi asla kullanılmaz — tüm değerler simülasyon ürünüdür (AGENTS.md kural 2).

## Girdiler

- Anlaşılan şema (aşağıdaki **Şema** bölümü — tek doğru kaynak budur)
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

## Adımlar

1. **Şemayı doğrula:** Yukarıdaki şemayı `tests/test-cases.md`'deki referans şema ile karşılaştır. Fark varsa DQ ile netleştir; şemayı tek taraflı değiştirme.
2. **`src/veri_uret.py` betiğini yaz/güncelle:** Şema sabitlerini (`SUTUNLAR`, `KATEGORI_URUN`, `SEHIRLER`, `ODEME_TIPLERI`, `SEED`, `SATIR_SAYISI`) dosyanın başında sabit olarak tanımla — gömülü sihirli sayı bırakma.
3. **Üret:** Depo kökünde `python src/veri_uret.py` çalıştır. Çıktı: `data/siparisler.csv`.
4. **Kendi kontrolünü yap** (DQ'ya göndermeden önce):
   - Satır sayısı tam 400 mü?
   - Sütun adları ve sırası şemayla birebir mi?
   - `df.isna().sum().sum() == 0` mı?
   - `(df.toplam_tutar - (df.adet * df.birim_fiyat).round(2)).abs().max() == 0` mı?
   - `df.siparis_id.duplicated().sum() == 0` mı?
   - `set(df.kategori)`, `set(df.sehir)` ve `set(df.odeme_tipi)` tam olarak şemadaki değer listeleri mi?
   - Dosya **ham metin olarak** okununca (`pd.read_csv(..., dtype=str)`) `birim_fiyat` ve `toplam_tutar` her satırda tam 2 ondalık mı (`^\d+\.\d{2}$`)? Sayıya çevirerek bakılırsa bu hata görünmez.
   - Betiği ikinci kez çalıştırıp dosyanın değişmediğini doğrula (tekrarlanabilirlik).

   `src/veri_uret.py` bu kontrollerin hepsini dosyayı yazmadan önce kendisi yapar (`dogrula`, `metni_dogrula`); biri kalırsa hata verir ve dosya yazılmaz.
5. **Şemayı yaz:** `docs/veri-sozlugu-g1.md` dosyasını yukarıdaki **Şema** bölümünden üret. Şu dördü mutlaka yazılı olsun: geçerli `sehir` ve `odeme_tipi` listesi, `siparis_id` benzersiz ve 1'den başlıyor, hiçbir alanda boş değer yok, kullanılan tohum değeri (42) ve satır sayısı (400).
6. **Commit at:** `G1-veri: siparisler.csv, veri-sozlugu-g1.md ve be-veri skill'i eklendi (#13)`. Bir hata Issue'sunu düzeltiyorsan mesaja `Fixes #<numara>` ekle; Issue otomatik kapanır.
7. **Issue'ya kanıt yorumu yaz:** commit hash + üretilen dosyalar + satır sayısı + tohum. Ardından **hem G1-analiz (#14, DQ) hem G1-gorsel (#15, FE)** Issue'suna aşağıdaki devir teslim yorumunu yaz; bu yorum DQ ve FE'nin başlama iznidir. Hata düzeltmesinde Issue otomatik kapansa bile ne düzeldiğini yazan bir kanıt yorumu bırak. Her kapanış yorumunun sonuna şu satırı ekle: `Üretim: be-veri skill'i ile, <araç>` (örn. Claude).

## Şema değişirse

Şema her değiştiğinde **üç dosya birlikte** güncellenir, yoksa testler kalır:

1. Bu skill'in **Şema** bölümü
2. `src/veri_uret.py` içindeki sabitler
3. `docs/veri-sozlugu-g1.md`

Ardından DQ'ya haber ver — `tests/test-cases.md` ve `src/dq_test.py` içindeki şema sabitleri de güncellenmeli.

### Devir teslim yorumu şablonu

> Veri hazır — commit `<hash>`. Dosya: `data/siparisler.csv` (400 satır, tohum 42). Şema: `docs/veri-sozlugu-g1.md`.

## Bilinen sınırlılıklar (#30)

Veri, Görev 1'in hattını sınamak için üretilmiş basit bir simülasyondur; analiz ve grafikler yorumlanırken şunlar dikkate alınır:

- **Haftada ortalama ~10 sipariş var**; tek bir büyük sipariş o haftanın cirosunu belirgin biçimde değiştirebilir, haftalık ciro bu yüzden oynaktır.
- **Ürünlerin kendine özgü fiyatı yok:** fiyat, ürünün kategorisinin aralığından çekilir (ör. aynı Powerbank 387 TL de 4.647 TL de olabilir). Ürün bazlı Top-3 sıralaması temkinle yorumlanmalı.
- **Dalgalanmaların nedeni yok:** tarihler aralık içinde düzgün dağılımla seçilir; hafta sonu, kampanya ve sezon etkisi modellenmedi.

Görev 1 verisi bilerek değiştirilmedi (analiz, testler ve grafikler bu veriye dayanıyor); bu maddeler Görev 2 simülasyonunda ele alınacak.

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
- **Çalıştırır:** `src/veri_uret.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.):

- Üretim: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret."
- Şema değişikliği: "be-veri skill'ini kullanarak şemaya `kargo_ucreti` alanını ekle ve veriyi yeniden üret."

Elle çalıştırma: depo kökünde `python src/veri_uret.py`. Aynı tohumla her çalıştırmada aynı dosya üretilir.

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **İlk üretim (#13):** Bu skill, `src/veri_uret.py`, `docs/veri-sozlugu-g1.md` ve `data/siparisler.csv` Claude ile üretildi (3b34e4b, fa3b368; commit'lerde `Co-Authored-By: Claude` izi var). Prompt: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret."
- **Düzeltme (#27):** DQ'nun önerdiği `float_format="%.2f"` düzeltmesi Claude ile uygulandı, veri yeniden üretildi (1f8beb8, `Fixes #27`). Değerler değişmedi, yalnızca yazım biçimi düzeldi. Bu commit'te `Co-Authored-By` satırı yok; ajan izi #27'deki kanıt yorumunda.
- **Skill güncellemesi (#32):** #27'de öğrenilen kural skill'e işlendi, betiğe yazmadan önce ham metin kontrolü eklendi. Claude ile yapıldı (Claude in Chrome); çıktı dosyası bayt bayt aynı kaldı.
- **Skill güncellemesi (#30, #32):** Devir teslim şablonu (#14 + #15), tam kategori fiyat tablosu ve "Bilinen sınırlılıklar" bölümü eklendi; kişi adı yerine rol yazıldı. Yalnızca bu dosya değişti, betik ve veri aynı. Claude ile yapıldı (Claude in Chrome).
