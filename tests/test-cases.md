# Test Senaryoları — Görev 1 (Veri Kalitesi)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Tuğba Tuana Kaygısız · **Issue:** #16
**Test edilen dosya:** `data/siparisler.csv` · **Referans şema:** `docs/veri-sozlugu-g1.md`
**Çalıştırma:** `python src/dq_test.py` (sonuçlar aşağıda; çalıştırma kaydı `tests/test-log.md`)

> Not: Beklenen sonuçlar, BE ile kesinleştirilen şemaya göredir (#13). Şemada değişiklik olursa bu dosyadaki "Beklenen sonuç" hücreleri güncellenir.

## Referans şema (özet)

#13'te BE ile kesinleştirildi; ayrıntılar `docs/veri-sozlugu-g1.md`'de (tohum 42).

| # | Alan | Tip | Geçerli aralık / değerler | Birim |
|---|---|---|---|---|
| 1 | `siparis_id` | int | ≥ 1, benzersiz | – |
| 2 | `siparis_tarihi` | tarih (`YYYY-MM-DD`) | 2026-01-01 – 2026-09-30 | – |
| 3 | `kategori` | metin | Elektronik, Giyim, Kitap, Ev & Yaşam, Kozmetik | – |
| 4 | `urun` | metin | 25 ürün (kategori başına 5; liste veri sözlüğünde) | – |
| 5 | `adet` | int | 1 – 10 | adet |
| 6 | `birim_fiyat` | float (2 ondalık) | 50 – 5000 | TL |
| 7 | `toplam_tutar` | float (2 ondalık) | = `adet × birim_fiyat` (50 – 50000) | TL |
| 8 | `sehir` | metin | İstanbul, Ankara, İzmir, Burdur, Antalya | – |
| 9 | `odeme_tipi` | metin | Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme | – |

Dosya biçimi: virgül ayraçlı, nokta ondalıklı, UTF-8, binlik ayırıcı yok.
Hedef satır sayısı: **400** (başlık satırı hariç; ödevdeki alt sınır ≥ 100).

## Senaryolar

| ID | Senaryo | Adımlar | Girdi | Beklenen sonuç | Gerçekleşen sonuç | Geçti/Kaldı |
|---|---|---|---|---|---|---|
| TC-01 | Veri dosyası var mı, boş değil mi? | 1) `data/siparisler.csv` yolunu kontrol et. 2) Dosya boyutunun 0'dan büyük olduğunu doğrula. 3) Dosyayı pandas ile oku. | `data/siparisler.csv` | Dosya mevcut, boyutu > 0 bayt, pandas hatasız okuyor ve en az 1 veri satırı var. | 29.555 bayt, 400 veri satırı; pandas hatasız okudu. | ✅ Geçti |
| TC-02 | Satır sayısı şemadaki hedefi karşılıyor mu? | 1) Dosyayı oku. 2) Başlık hariç satır sayısını say (`len(df)`). 3) Şemadaki hedefle karşılaştır. | `data/siparisler.csv`, şemadaki satır hedefi | Satır sayısı ≥ 100 ve `docs/veri-sozlugu-g1.md`'de yazan sayıya (400) eşit. | 400 satır (hedef ≥ 100 ve şemadaki 400 ile eşit). | ✅ Geçti |
| TC-03 | Sütun adları ve sırası şemayla aynı mı? | 1) `df.columns` listesini al. 2) Şemadaki sırayla birebir karşılaştır (ad + sıra). | Başlık satırı; şema alan listesi | Sütunlar tam olarak: `siparis_id, siparis_tarihi, kategori, urun, adet, birim_fiyat, toplam_tutar, sehir, odeme_tipi` (9 sütun, bu sırayla; fazla/eksik yok). | 9 sütun, şemadaki ad ve sırayla birebir aynı. | ✅ Geçti |
| TC-04 | Tipler, aralıklar ve birimler doğru mu? | 1) `siparis_id`, `adet` tam sayı mı? 2) `birim_fiyat`, `toplam_tutar` sayısal mı? 3) `siparis_tarihi` `YYYY-MM-DD` olarak ayrıştırılıyor mu? 4) Değerler şemadaki aralıklarda mı? 5) Fiyatta para birimi simgesi/metin yok mu (birim = TL, sayı olarak)? | Tüm sayısal ve tarih alanları | `adet` 1–10, `birim_fiyat` 50–5000, `toplam_tutar` 50–50000, `siparis_tarihi` 2026-01-01 ile 2026-09-30 arasında; aralık dışı / ayrıştırılamayan değer sayısı = 0. | Tüm tip ve aralıklar doğru; aralık dışı / ayrıştırılamayan değer = 0. | ✅ Geçti |
| TC-05 | Ana kategorik alanda yalnızca şemadaki değerler mi var? | 1) `kategori` sütununun benzersiz değerlerini al. 2) Şemadaki izinli küme ile farkını hesapla. 3) Farklı değer sayısını kontrol et. | `kategori` sütunu | Şema dışı değer yok (fark kümesi boş); en az 4 farklı kategori var; büyük/küçük harf ve boşluk tutarsızlığı yok. | 5 farklı kategori; şema dışı değer yok. | ✅ Geçti |
| TC-06 | Eksik (boş) değer var mı? | 1) Her sütun için `isna().sum()` hesapla. 2) Boş metin (`""`) değerlerini de say. | Tüm sütunlar | Hiçbir sütunda boş/eksik değer yok (toplam = 0). | Toplam eksik değer = 0. | ✅ Geçti |
| TC-07 | Sipariş kimliği benzersiz mi? | 1) `siparis_id` tekrarlarını say (`duplicated().sum()`). 2) Tamamen aynı satır var mı kontrol et. | `siparis_id` sütunu | Tekrarlanan `siparis_id` = 0; birebir tekrar eden satır = 0. | Tekrarlanan `siparis_id` = 0, tekrarlanan satır = 0. | ✅ Geçti |
| TC-08 | `toplam_tutar` tutarlı mı? | 1) Her satır için `adet × birim_fiyat` hesapla. 2) `toplam_tutar` ile farkını al. | `adet`, `birim_fiyat`, `toplam_tutar` sütunları | Farkı 0,01 TL'den büyük olan satır sayısı = 0. | `adet × birim_fiyat` ile uyuşmayan satır = 0. | ✅ Geçti |

## Özet

| Toplam senaryo | Geçti | Kaldı | Test tarihi | Test edilen commit |
|---|---|---|---|---|
| 8 | 8 | 0 | 2026-10-17 | `fa3b368` (`data/siparisler.csv`) |
