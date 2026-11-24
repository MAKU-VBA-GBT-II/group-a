# Yeni görev: öneri ve roller — Sepetix Analitik (Grup A)

**Şirket:** Sepetix Analitik · **Sektör:** E-ticaret · **Görev:** Duyuru-10, Çok Ajanlı Şirket Programı
**Teslim:** 26 Kasım 2026 Perşembe 13:00 · **PM:** Ali Haydar Polat

> TASLAK (24 Kasım 2026). `[TODO]` ile işaretli yerler ekip tarafından doldurulacak; doldurulmadan teslim edilmez.

## 1. Senaryo

Hocanın e-ticaret örneğini alıyoruz: **rakiplere göre fiyat ve kampanya stratejisi**.

Kullanıcı programa "rakiplere göre fiyat ve kampanya stratejisi çıkar" işini verir. Program işi üç ajana sırayla dağıtır: Ajan 1 rakip fiyatlarını toplar, Ajan 2 bunları sipariş verimizle birleştirip öneri üretir, Ajan 3 önerileri denetleyip son çıktıyı hazırlar.

## 2. Ajanlar (birer cümle)

| Rol | Tanım |
|---|---|
| **Çekirdek ve Arayüz** | Ajanları ACP üzerinden başlatır, aralarında mesaj taşır, kullanılacak aracı (Vibe / Claude Code / Codex) ayardan seçtirir, ilerleme ve izin ekranını gösterir, oturum kayıtlarını tutar. |
| **Ajan 1 — Toplama** | Açık web kaynaklarından rakip ürün fiyatlarını toplar ve ürünleri bizim ürünlerle eşleştirir. |
| **Ajan 2 — Analiz** | Rakip fiyatlarını sentetik sipariş verisiyle birleştirir, fiyat farkı ile satış ilişkisini hesaplar ve fiyat/kampanya önerileri üretir. |
| **Ajan 3 — Denetim** | Önerileri kâr eşiğine göre süzer, örnek rakip fiyatlarını siteye yeniden girip doğrular, gerekirse işi gerekçesiyle geri gönderir ve son çıktıyı hazırlar. |

## 3. Web kaynakları

Kontrol tarihi: 22 Kasım 2026. `robots.txt` sonuçları sitelerin dosyalarının o gün okunmasıyla yazıldı. **Kullanım şartları henüz okunmadı**; her aday için `[TODO]`.

| # | Kaynak | Adres | Vereceği veri | Tarayıcı gerekir mi? | robots.txt sonucu | Kullanım şartları | Karar |
|---|---|---|---|---|---|---|---|
| 1 | Kitapyurdu | https://www.kitapyurdu.com | Kitap adı ve fiyatı (listeleme/arama sayfaları) | Hayır: fiyat ham HTML'de | Yalnızca `/admin/`, `/system/`, `/image/`, `/img/`, `/download/` yasak; arama ve listeleme serbest | `[TODO]` | Aday (yalnız Kitap kategorisi) |
| 2 | Vatan Bilgisayar | https://www.vatanbilgisayar.com | Elektronik fiyatları | — | `/arama/*` ve `?page=` yasak | — | Elendi (sayfalama ve arama yasak) |
| 3 | n11 | https://www.n11.com | Çok kategorili fiyat | — | Çok sayıda filtre parametresi, `/rest/`, `getProduct*` yasak | — | Elendi (riskli) |
| 4 | Akakçe | https://www.akakce.com | Fiyat karşılaştırma | — | `?sayfa=`, `/yorum*`, `/siparis/*` yasak | — | Elendi (sayfalama yasak) |
| 5 | webscraper.io test siteleri | https://webscraper.io/test-sites | Eğitim amaçlı ürün/fiyat | Evet (load-more, scroll, pagination) | `/test-sites/pagination/`, `/load-more/`, `/scroll/` yasak | `[TODO]` (şartlar sayfası bulunamadı) | Kullanılamaz |

**Açık sorunlar**
- `[TODO — Hilal]` JavaScript ile yüklenen veya sayfalamalı en az bir kaynak bulunmalı (duyuru şartı). Şu an uygun kaynak yok.
- `[TODO — Hilal]` Kitapyurdu yalnızca Kitap kategorisini kapsıyor. Elektronik, Giyim, Ev & Yaşam, Kozmetik için kaynak gerekiyor; ya da simülasyonun ürün listesi kaynağı olan kategorilere daraltılacak.
- `[TODO — Hilal]` Seçilen her kaynak için kullanım şartları okunup sonuç tabloya yazılacak; istekler arasına bekleme konacak; kişisel veri (yorum, isim, profil) çekilmeyecek.

## 4. Simülasyonun genişletilmesi (plan)

Mevcut yapı: `src/simulasyon.py`, `data/siparisler-g2.csv`, `docs/veri-sozlugu.md`. PR #95 (`--urun_agirliklari`) birleşti ve temel alınacak.

- `[TODO — Tuğba]` Dışarıdan ürün listesi alma: ürün adı, kategori ve liste fiyatı içeren bir dosya (örn. `--urun_listesi`). Verilmezse bugünkü 25 ürün ve varsayılan MD5 değişmez.
- `[TODO — Tuğba]` Fiyat aralığı parametresi: ürün başına liste fiyatı sapması dışarıdan verilebilsin.
- Ürün adları, Ajan 1'in eşleştirdiği web ürünleriyle uyuşacak; eşleştirme listesi Hilal'den gelecek.
- Örnek veri `data/` altına, yeni parametreler `docs/veri-sozlugu.md` Simülasyon parametreleri tablosuna ve değişiklik günlüğüne yazılacak (Hilal, DQ).
- `[TODO — Sema]` Yeni parametreler için test kuralları.

## 5. Abonelikler

| Ad Soyad | Abonelik |
|---|---|
| Ali Haydar Polat | Claude Pro, ChatGPT |
| Hilal Elçin Şahin | Claude Pro |
| Sema Nur Doğan | Claude Pro |
| Tuğba Tuana Kaygısız | Claude Pro |
| Ebru Türk | Aboneliği yok |

Program herhangi bir API anahtarı içermeyecek; araç seçimi ayardan yapılacak, böylece hocanın kendi aboneliğiyle çalışabilecek.

## 6. Roller

| Ad Soyad | Rol | GitHub |
|---|---|---|
| Ali Haydar Polat | Çekirdek ve Arayüz (PM) | @plt0051ct-rgb |
| Ebru Türk | Çekirdek ve Arayüz — destek (junior) | @ebruturk |
| Hilal Elçin Şahin | Ajan 1 — Toplama | @hilalelcin-stack |
| Tuğba Tuana Kaygısız | Ajan 2 — Analiz | @tugbatuanakaygisiz-web |
| Sema Nur Doğan | Ajan 3 — Denetim | @semadogaan |

## 7. Teslim kontrol listesi

- [ ] Senaryo ve üç ajanın birer cümlelik tanımı yazılı
- [ ] Web kaynakları listelenmiş; en az biri tarayıcı gerektiriyor; robots.txt ve kullanım şartları kontrol edilmiş
- [ ] Simülasyon web kaynaklarıyla eşleşen alanlar üretiyor ve dışarıdan liste veya aralık alabiliyor
- [ ] Örnek veri ve güncel veri sözlüğü repoda
- [ ] Rol listesi ve abonelikler Issue'da, @eofdred etiketli

---

Üretim: Bu taslak Claude ile hazırlandı. Prompt özeti: "Duyuru-10'a göre docs/oneri.md taslağı yaz: senaryo, 3 ajan tanımı, web kaynakları (robots.txt kontrolüyle), simülasyon genişletme planı, abonelikler, roller."
