---
name: ajan1-teslim
description: Ajan 1'in (toplama) son aşaması. 19 sütunlu rakip fiyat tablosunu ortak sözleşmeye göre kontrol eder, tazelik kapısından geçirir, dosyaya yazar ve Ajan 2 ile Ajan 3'e devreder. İşleme bittikten sonra kullan.
---

# ajan1-teslim: Kontrol, tazelik kapısı ve devir (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114 · **Önceki:** `ajan1-isleme` · **Alıcılar:** Ajan 2 (Tuğba, #115), Ajan 3 (Sema, #116)

## 1. Ajan 2 ve Ajan 3'ün kapılarıyla aynı kontroller
Ajan 2'nin `ajan2-alma` ve Ajan 3'ün `ajan3-alma` skill'lerinde dosyayı reddettiren her kural, göndermeden önce burada da kontrol edilir (sözleşme: `docs/mesaj-bicimi.md`, `docs/ajan1-cikti-semasi.md`):
1. Dosyada en az bir satır var; 19 sütun, şemadaki sırayla; zorunlu alanlar dolu.
2. Her sütunda yalnızca izinli değerler var (`eslesme_yontemi = benzer`, `eslesme_guveni`, `fiyat_turu`, `kdv_dahil`, `para_birimi = TRY`, `stok_durumu`, `rakip_site`).
3. `bizim_urun` ve `kategori` web fiyatlı ürün listesinde birebir aynı çift olarak var.
4. Fiyatlar sonlu, pozitif, nokta ondalıklı ve tam iki haneli (`1299.90`); `indirimli_fiyat` doluysa liste fiyatından küçük ve `fiyat_turu` ≠ `liste`.
5. `ham_fiyat_metni`'nden okunan sayı karşılaştırma fiyatıyla aynı.
6. `urun_url` https, arama sayfası değil ve `rakip_site`'nin kendi alan adında (Gratis → gratis.com, IKEA → ikea.com.tr).
7. `bulma_yolu` biçimi: `<https adresi> s.<sayfa no>`.
8. `elendi` yalnızca izinli gerekçelerden.
9. `cekilme_zamani` `+03:00` saat dilimiyle yazılmış ve gelecek tarihli değil.
10. `arac` gerçek aracı gösteriyor (`playwright`); `sentetik-fixture` yalnız test verisinde kullanılır.

Bir kontrol düşerse dosya gönderilmez; hangi satırın, hangi kontrolden düştüğü rapora yazılır.

Kod olarak: Ajan 2'nin `src/ajan2_analiz.py` içindeki `alma()` fonksiyonu main'e girince, Ajan 1 göndermeden önce kendi dosyasını o fonksiyondan geçirir. Böylece iki kapının kuralları hiçbir zaman ayrışmaz.

## 2. Tazelik kapısı
- Her satırın `cekilme_zamani` değerine bakılır.
- **24 saati geçen satır varsa teslim durur** (ilk karar 48 saatti; 28 Kasım'da 24 saate indirildi, bkz. karar kaydı). O ürünler `ajan1-alma` ile yeniden toplanır.
- Yeniden toplama **bir kez** denenir. Yine başarısız olursa dosya gönderilmez ve kullanıcıya bildirilir. *(Neden bir kez: site kapalıyken ya da sayfa değişmişken kapı sürekli yeniden toplamayı tetikler; kod sonsuz döngüye girer ve siteye durmadan istek atar.)*
- Ajan 2 ve Ajan 3 de 72 saat kontrolü yapar (Ajan 3 kendi denetim anına göre). Aradaki 48 saat, Ajan 2 ve Ajan 3'ün birlikte kullandığı işleme payıdır.

## 3. Çıktılar
| Dosya | İçerik |
|---|---|
| `data/ajan1-cikti.csv` (öneri: Claude · onay: Hilal) | 19 sütunlu rakip fiyat tablosu |
| `runs/ajan1/<zaman>.json` | Çalışma raporu: açılan sayfalar, okunan ürün sayıları, robots.txt kontrolü, başarısız kategoriler, fiyat değişimi ve kampanya notları, tazelik kapısı sonucu |

Her fiyatın kaynağı `urun_url`, üretim zamanı `cekilme_zamani` alanında taşınır (sözleşme gereği).

Çalışma raporu, açılan her sayfanın adresini ve zamanını tuttuğu için Çekirdeğin oturum kaydını Ajan 1 tarafında tamamlar (Çekirdek kaydı genel görevlerde açılan sayfaları yazmıyor, #118).

## 4. Devir
- Tablo ve çalışma raporu **hem Ajan 2'ye hem Ajan 3'e** gider. Ajan 3, fiyatları sayfadan yeniden doğrularken raporu okuyarak kampanyanın bitmesinden kaynaklanan farkı hata sanmaz.
- #115 ve #116'ya yorum yazılır: dosya yolları, dosyanın MD5'i, commit, çekilme zamanı ve 72 saatlik sürenin ne zaman dolacağı (Ajan 2 ve Ajan 3 için).
- Ajan 2'den **ya da Ajan 3'ten** red zarfı gelirse, zarftaki satır listesine göre yalnızca o ürünler yeniden toplanır.

## Karar kaydı (28 Kasım 2026)

- **Tazelik kapısı (Hilal):** Bayat veri yalnızca uyarıyla geçiştirilmez. Veriyle hiçbir işlem yapılmadan önce akış durur ve veri güncellenmeden devam edilmez (PR #117 incelemesi).
- **Ajan 3'e ham tablo (Hilal):** Denetçi yalnızca Ajan 2'nin özetine değil, Ajan 1'in ham verisine de bakabilmeli (PR #117 incelemesi).
- **Ajan 2 ve 3'ün kapılarıyla eşleşme (Hilal):** Ajan 2'nin ya da Ajan 3'ün reddedeceği bir sorun Ajan 1'de yakalanmazsa zincir başa döner; bu yüzden teslim kontrolleri, Tuğba'nın ve (isteğim üzerine) Sema'nın skill'leri incelenerek onların alma kontrolleriyle birebir eşlendi. TL dışı satırın bütün dosyayı reddettirmesi, iş büyüdüğünde Ajan 2 ile yeniden konuşulacak.
- **Tazelik eşiği 24 saat (Hilal):** Tuğba ve Sema'ya kalan 24 saatin yeterli olup olmadığını sorguladım ve her ajana ayrı 24 saat (24-24-24) verilmesini önerdim. 48 saatlik eşikte ikisi toplam 24 saati paylaşıyordu. İlk adım olarak kendi eşiğimiz 24 saate indirildi; böylece ikisine toplam 48 saat kalıyor ve başka kimsenin kodu değişmiyor. Tam kademeli düzen (Ajan 2 için 48, Ajan 3 için 72 saat), denemelerde ihtiyaç doğarsa gruba önerilecek.
- *Claude'un katkısı:* Dur noktasının veri Ajan 1'den çıkmadan önce kurulmasını önerdi. Kapının kilitlenmesini önlemek için yeniden toplamanın bir kez denenmesini ekledi. Kuralların Ajan 2'nin kontrol fonksiyonuyla ortak tutulmasını; Ajan 3'ün de 72 saat kontrolü yaptığı için devirde iki ajanın süresinin yazılmasını; raporun ve dosya MD5'inin Ajan 3'e de iletilmesini önerdi. Kademeli düzenle sadece kendi eşiğimizi düşürmek arasındaki farkı çıkardı.
