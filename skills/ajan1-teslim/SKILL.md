---
name: ajan1-teslim
description: Ajan 1'in (toplama) son aşaması. 19 sütunlu rakip fiyat tablosunu ortak sözleşmeye göre kontrol eder, tazelik kapısından geçirir, dosyaya yazar ve Ajan 2 ile Ajan 3'e devreder. İşleme bittikten sonra kullan.
---

# ajan1-teslim: Kontrol, tazelik kapısı ve devir (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114 · **Önceki:** `ajan1-isleme` · **Alıcılar:** Ajan 2 (Tuğba, #115), Ajan 3 (Sema, #116)

## 1. Sözleşme kontrolü (`docs/mesaj-bicimi.md`, `docs/ajan1-cikti-semasi.md`)
Göndermeden önce:
1. 19 sütun, şemadaki sırayla; zorunlu alanların hiçbiri boş değil.
2. `bizim_urun` ve `kategori` web fiyatlı ürün listesinde var.
3. `urun_url` bir ürün sayfası; arama sayfası değil.
4. `liste_fiyati` > 0; `indirimli_fiyat` doluysa liste fiyatından küçük ve `fiyat_turu` ≠ `liste`.
5. `ham_fiyat_metni`'nden okunan sayı, karşılaştırma fiyatıyla aynı.
6. `elendi` gerekçeleri yalnızca izin verilen değerlerden.

Bir kontrol düşerse dosya gönderilmez; hangi satırın, hangi kontrolden düştüğü rapora yazılır.

## 2. Tazelik kapısı
- Her satırın `cekilme_zamani` değerine bakılır.
- **48 saati geçen satır varsa teslim durur** (öneri: Claude · onay: Hilal). O ürünler `ajan1-alma` ile yeniden toplanır.
- Yeniden toplama **bir kez** denenir. Yine başarısız olursa dosya gönderilmez ve kullanıcıya bildirilir. *(Neden bir kez: site kapalıyken ya da sayfa değişmişken kapı sürekli yeniden toplamayı tetikler; kod sonsuz döngüye girer ve siteye durmadan istek atar.)*
- Ajan 2'nin 72 saat kontrolü ikinci güvenlik katmanı olarak kalır; aradaki 24 saat Ajan 2'nin işleme payıdır.

## 3. Çıktılar
| Dosya | İçerik |
|---|---|
| `data/ajan1-cikti.csv` (öneri: Claude · onay: Hilal) | 19 sütunlu rakip fiyat tablosu |
| `runs/ajan1/<zaman>.json` | Çalışma raporu: açılan sayfalar, okunan ürün sayıları, robots.txt kontrolü, başarısız kategoriler, fiyat değişimi notları, tazelik kapısı sonucu |

Her fiyatın kaynağı `urun_url`, üretim zamanı `cekilme_zamani` alanında taşınır (sözleşme gereği).

## 4. Devir
- Tablo **hem Ajan 2'ye hem Ajan 3'e** gider.
- #115 ve #116'ya yorum yazılır: dosya yolları, commit, çekilme zamanı ve 72 saatlik sürenin ne zaman dolacağı.
- Ajan 2'den red zarfı gelirse, zarftaki satır listesine göre yalnızca o ürünler yeniden toplanır.

## Karar kaydı (28 Kasım 2026)

- **Tazelik kapısı (Hilal):** Bayat veri yalnızca uyarıyla geçiştirilmez. Veriyle hiçbir işlem yapılmadan önce akış durur ve veri güncellenmeden devam edilmez (PR #117 incelemesi).
- **Ajan 3'e ham tablo (Hilal):** Denetçi yalnızca Ajan 2'nin özetine değil, Ajan 1'in ham verisine de bakabilmeli (PR #117 incelemesi).
- *Claude'un katkısı:* Dur noktasının veri Ajan 1'den çıkmadan önce kurulmasını önerdi. 48 saatlik eşiği önerdi; böylece Ajan 2'ye 24 saatlik işleme payı kalıyor. Kapının kilitlenmesini önlemek için yeniden toplamanın bir kez denenmesini ekledi.
