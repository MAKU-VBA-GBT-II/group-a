# Test Senaryoları — Görev 1 (Veri Kalitesi)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Tuğba Tuana Kaygısız · **Issue:** #16
**Test edilen dosya:** `data/siparisler.csv` · **Referans şema:** `docs/veri-sozlugu-g1.md`
**Çalıştırma:** `python src/dq_test.py` (sonuçlar aşağıda; çalıştırma kaydı `tests/test-log.md`)
**Son çalıştırma:** 2026-10-22 · TC-10…TC-12 eklendikten sonra (veri `1f8beb8`) · 12/12 geçti.

> Not: Beklenen sonuçlar, BE ile kesinleştirilen şemaya göredir (#13). Şemada değişiklik olursa bu dosyadaki "Beklenen sonuç" hücreleri güncellenir.

## Referans şema (özet)

#13'te BE ile kesinleştirildi; ayrıntılar `docs/veri-sozlugu-g1.md`'de (tohum 42).

| # | Alan | Tip | Geçerli aralık / değerler | Birim |
|---|---|---|---|---|
| 1 | `siparis_id` | int | 1 – 400, benzersiz, 1'er artar; dosya tarihe göre sıralı | – |
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
| TC-01 | Veri dosyası var mı, boş değil mi? | 1) `data/siparisler.csv` yolunu kontrol et. 2) Dosya boyutunun 0'dan büyük olduğunu doğrula. 3) Dosyayı pandas ile oku. | `data/siparisler.csv` | Dosya mevcut, boyutu > 0 bayt, pandas hatasız okuyor ve en az 1 veri satırı var. | 29.726 bayt, 400 veri satırı; pandas hatasız okudu. | ✅ Geçti |
| TC-02 | Satır sayısı şemadaki hedefi karşılıyor mu? | 1) Dosyayı oku. 2) Başlık hariç satır sayısını say (`len(df)`). 3) Şemadaki hedefle karşılaştır. | `data/siparisler.csv`, şemadaki satır hedefi | Satır sayısı ≥ 100 ve `docs/veri-sozlugu-g1.md`'de yazan sayıya (400) eşit. | 400 satır (hedef ≥ 100 ve şemadaki 400 ile eşit). | ✅ Geçti |
| TC-03 | Sütun adları ve sırası şemayla aynı mı? | 1) `df.columns` listesini al. 2) Şemadaki sırayla birebir karşılaştır (ad + sıra). | Başlık satırı; şema alan listesi | Sütunlar tam olarak: `siparis_id, siparis_tarihi, kategori, urun, adet, birim_fiyat, toplam_tutar, sehir, odeme_tipi` (9 sütun, bu sırayla; fazla/eksik yok). | 9 sütun, şemadaki ad ve sırayla birebir aynı. | ✅ Geçti |
| TC-04 | Tipler, aralıklar ve birimler doğru mu? | 1) `siparis_id`, `adet` tam sayı mı? 2) `birim_fiyat`, `toplam_tutar` sayısal mı? 3) `siparis_tarihi` `YYYY-MM-DD` olarak ayrıştırılıyor mu? 4) Değerler şemadaki aralıklarda mı? 5) Fiyatta para birimi simgesi/metin yok mu (birim = TL, sayı olarak)? | Tüm sayısal ve tarih alanları | `adet` 1–10, `birim_fiyat` 50–5000, `toplam_tutar` 50–50000, `siparis_tarihi` 2026-01-01 ile 2026-09-30 arasında; aralık dışı / ayrıştırılamayan değer sayısı = 0. | Tüm tip ve aralıklar doğru; aralık dışı / ayrıştırılamayan değer = 0. | ✅ Geçti |
| TC-05 | Ana kategorik alanda yalnızca şemadaki değerler mi var? | 1) `kategori` sütununun benzersiz değerlerini al. 2) Şemadaki izinli küme ile farkını hesapla. 3) Farklı değer sayısını kontrol et. | `kategori` sütunu | Şema dışı değer yok (fark kümesi boş); en az 4 farklı kategori var; büyük/küçük harf ve boşluk tutarsızlığı yok. | 5 farklı kategori; şema dışı değer yok. | ✅ Geçti |
| TC-06 | Eksik (boş) değer var mı? | 1) Her sütun için `isna().sum()` hesapla. 2) Boş metin (`""`) değerlerini de say. | Tüm sütunlar | Hiçbir sütunda boş/eksik değer yok (toplam = 0). | Toplam eksik değer = 0. | ✅ Geçti |
| TC-07 | Sipariş kimliği benzersiz mi? | 1) `siparis_id` tekrarlarını say (`duplicated().sum()`). 2) Tamamen aynı satır var mı kontrol et. | `siparis_id` sütunu | Tekrarlanan `siparis_id` = 0; birebir tekrar eden satır = 0. | Tekrarlanan `siparis_id` = 0, tekrarlanan satır = 0. | ✅ Geçti |
| TC-08 | `toplam_tutar` tutarlı mı? | 1) Her satır için `adet × birim_fiyat` hesapla. 2) `toplam_tutar` ile farkını al. | `adet`, `birim_fiyat`, `toplam_tutar` sütunları | Farkı 0,01 TL'den büyük olan satır sayısı = 0. | `adet × birim_fiyat` ile uyuşmayan satır = 0. | ✅ Geçti |
| TC-09 | Para alanları dosyada tam 2 ondalıkla mı yazılmış? | 1) Dosyayı metin olarak oku (`dtype=str`). 2) `birim_fiyat` ve `toplam_tutar` değerlerini `^\d+\.\d{2}$` desenine göre kontrol et. 3) Desene uymayan satırları say. | `birim_fiyat`, `toplam_tutar` sütunları (ham metin) | Veri sözlüğündeki "2 ondalık" biçimine uymayan satır sayısı = 0 (ör. `1667.40`, `1667.4` değil). | Biçim dışı satır = 0 (ör. 1. satır `1667.40`). İlk turda (2026-10-21) 128 satır kalmıştı → #27; BE düzeltti (`1f8beb8`), 2026-10-22'de yeniden test edildi. | ✅ Geçti |
| TC-10 | `sehir` ve `odeme_tipi` yalnızca şemadaki değerleri mi içeriyor? | 1) `sehir` değerlerini izinli 5 şehirle karşılaştır. 2) `odeme_tipi` değerlerini izinli 4 ödeme tipiyle karşılaştır. 3) İkisinden birinde şema dışı değer olan satırları say. | `sehir`, `odeme_tipi` sütunları | Şema dışı değerli satır sayısı = 0. | Şema dışı değerli satır = 0. | ✅ Geçti |
| TC-11 | Ürünler sözlükteki listeden mi ve kendi kategorisinde mi? | 1) Her satır için `urun` değerinin, o satırın `kategori`sine ait 5 üründen biri olup olmadığına bak. 2) Uymayan satırları say. | `kategori`, `urun` sütunları | Listede olmayan ya da başka kategoriye ait ürün içeren satır sayısı = 0 (ör. `Kozmetik` + `Roman` hatadır). | Uyuşmayan satır = 0. | ✅ Geçti |
| TC-12 | Kimlikler ardışık ve dosya tarihe göre sıralı mı? | 1) `siparis_id` listesinin `1, 2, …, N` ile birebir aynı olduğunu kontrol et. 2) `siparis_tarihi`nin artan sıralı olduğunu kontrol et. | `siparis_id`, `siparis_tarihi` sütunları | `siparis_id` 1…400 ardışık (atlama yok) ve tarih artan sıralı. | `siparis_id` 1…400 ardışık; tarih artan sıralı. | ✅ Geçti |

## Özet

| Toplam senaryo | Geçti | Kaldı | Test tarihi | Test edilen commit |
|---|---|---|---|---|
| 8 | 8 | 0 | 2026-10-17 | `fa3b368` (`data/siparisler.csv`) |
| 9 | 8 | 1 (TC-09 → #27) | 2026-10-21 | `main` @ `ec7db3c` (veri `fa3b368`) |
| 9 | 9 | 0 | 2026-10-22 | `main` @ `1aad2be` (veri `1f8beb8`, #27 düzeltmesi) |
| 12 | 12 | 0 | 2026-10-22 | veri `1f8beb8` — TC-10…TC-12 eklendi (şehir/ödeme, ürün–kategori, id/sıra) |
