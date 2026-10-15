# Test Senaryoları — Görev 1 (Veri Kalitesi)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Tuğba Tuana Kaygısız · **Issue:** #16
**Test edilen dosya:** `data/siparisler.csv` · **Referans şema:** `docs/veri-sozlugu-g1.md`
**Çalıştırma:** `python src/dq_test.py` (Hafta 4'te çalıştırılacak; sonuçlar `tests/test-log.md`'ye yazılacak)

> Not: Beklenen sonuçlar, BE ile kesinleştirilen şemaya göredir (#13). Şemada değişiklik olursa bu dosyadaki "Beklenen sonuç" hücreleri güncellenir.

## Referans şema (özet)

| # | Alan | Tip | Geçerli aralık / değerler | Birim |
|---|---|---|---|---|
| 1 | `siparis_id` | int | ≥ 1, benzersiz | – |
| 2 | `tarih` | tarih (`YYYY-MM-DD`) | 2026-09-01 – 2026-09-30 | – |
| 3 | `kategori` | metin | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Kitap | – |
| 4 | `urun` | metin | boş olmayan ürün adı | – |
| 5 | `adet` | int | 1 – 10 | adet |
| 6 | `birim_fiyat` | float | 20 – 5000 | TL |
| 7 | `sehir` | metin | İstanbul, Ankara, İzmir, Burdur, Antalya | – |

Hedef satır sayısı: **≥ 100** (başlık satırı hariç).

## Senaryolar

| ID | Senaryo | Adımlar | Girdi | Beklenen sonuç | Gerçekleşen sonuç | Geçti/Kaldı |
|---|---|---|---|---|---|---|
| TC-01 | Veri dosyası var mı, boş değil mi? | 1) `data/siparisler.csv` yolunu kontrol et. 2) Dosya boyutunun 0'dan büyük olduğunu doğrula. 3) Dosyayı pandas ile oku. | `data/siparisler.csv` | Dosya mevcut, boyutu > 0 bayt, pandas hatasız okuyor ve en az 1 veri satırı var. | | |
| TC-02 | Satır sayısı şemadaki hedefi karşılıyor mu? | 1) Dosyayı oku. 2) Başlık hariç satır sayısını say (`len(df)`). 3) Şemadaki hedefle karşılaştır. | `data/siparisler.csv`, şemadaki satır hedefi | Satır sayısı ≥ 100 ve `docs/veri-sozlugu-g1.md`'de yazan sayıya eşit. | | |
| TC-03 | Sütun adları ve sırası şemayla aynı mı? | 1) `df.columns` listesini al. 2) Şemadaki sırayla birebir karşılaştır (ad + sıra). | Başlık satırı; şema alan listesi | Sütunlar tam olarak: `siparis_id, tarih, kategori, urun, adet, birim_fiyat, sehir` (7 sütun, bu sırayla; fazla/eksik yok). | | |
| TC-04 | Tipler, aralıklar ve birimler doğru mu? | 1) `siparis_id`, `adet` tam sayı mı? 2) `birim_fiyat` sayısal mı? 3) `tarih` `YYYY-MM-DD` olarak ayrıştırılıyor mu? 4) Değerler şemadaki aralıklarda mı? 5) Fiyatta para birimi simgesi/metin yok mu (birim = TL, sayı olarak)? | Tüm sayısal ve tarih alanları | `adet` 1–10, `birim_fiyat` 20–5000, `tarih` 2026-09-01 ile 2026-09-30 arasında; aralık dışı / ayrıştırılamayan değer sayısı = 0. | | |
| TC-05 | Ana kategorik alanda yalnızca şemadaki değerler mi var? | 1) `kategori` sütununun benzersiz değerlerini al. 2) Şemadaki izinli küme ile farkını hesapla. 3) Farklı değer sayısını kontrol et. | `kategori` sütunu | Şema dışı değer yok (fark kümesi boş); en az 4 farklı kategori var; büyük/küçük harf ve boşluk tutarsızlığı yok. | | |
| TC-06 | Eksik (boş) değer var mı? | 1) Her sütun için `isna().sum()` hesapla. 2) Boş metin (`""`) değerlerini de say. | Tüm sütunlar | Hiçbir sütunda boş/eksik değer yok (toplam = 0). | | |
| TC-07 | Sipariş kimliği benzersiz mi? | 1) `siparis_id` tekrarlarını say (`duplicated().sum()`). 2) Tamamen aynı satır var mı kontrol et. | `siparis_id` sütunu | Tekrarlanan `siparis_id` = 0; birebir tekrar eden satır = 0. | | |

## Özet (Hafta 4'te doldurulacak)

| Toplam senaryo | Geçti | Kaldı | Test tarihi | Test edilen commit |
|---|---|---|---|---|
| 7 | | | | |
