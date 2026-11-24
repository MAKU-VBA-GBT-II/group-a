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

Kontrol tarihi: 24 Kasım 2026 (Hilal, Ajan 1). Her aday için `robots.txt` dosyası ve kullanım şartları / üyelik sözleşmesi okundu. İncelenen sitelerin hepsinde **arama sayfaları `robots.txt` ile yasak, ürün sayfaları serbest**; bu yüzden Ajan 1 ürünlere site içi aramayla değil, kategori sayfaları ve site haritaları üzerinden ulaşır. İstekler arasına bekleme konur, yalnız ürün adı ve fiyat bilgisi toplanır; yorum, kullanıcı adı ve bireysel satıcı profili gibi kişisel veriler toplanmaz.

| # | Kategori | Kaynak | Adres | Vereceği veri | Tarayıcı gerekir mi? | robots.txt sonucu | Kullanım şartları | Karar |
|---|---|---|---|---|---|---|---|---|
| 1 | Elektronik (+ Kahve Makinesi) | MediaMarkt | https://www.mediamarkt.com.tr | Ürün adı, güncel/liste fiyatı, stok | **Evet.** Ürün kartları JavaScript ile çiziliyor (ham HTML'de kart yok, veri gömülü JSON'da); sonraki ürünler "12 ürün daha göster" düğmesiyle yükleniyor, adres `?page=2` oluyor. Tarayıcıda doğrulandı | Ürün sayfaları ve `page=` serbest; `/search.html`, `query=`, `sort=`, `filter=` yasak | Otomatik erişim yasağı yok; site materyali yalnız şahsi kullanım içindir, ticari/genel amaçlı çoğaltma yazılı izne tabidir. Akademik, ticari olmayan, düşük hacimli fiyat toplama | **Seçildi** (tarayıcı gerektiren kaynak) |
| 2 | Kozmetik | Gratis | https://www.gratis.com | Ürün adı, fiyat, indirim, miktar (ml/g) | Hayır (fiyat liste sayfasında) | Ürün sayfaları serbest; `/search` ve `query=` yasak | Otomatik erişimi açıkça yasaklayan madde yok; siteyi başkalarının kullanımını zorlaştıracak biçimde kullanmak yasak | **Seçildi** |
| 3 | Kitap | D&R | https://www.dr.com.tr | Kitap adı, fiyat, indirim, stok | Hayır | Ürün sayfaları serbest, ürün site haritası var; arama yasak | Genel kullanım koşulları sayfası yok (altbilgide yalnız üyelik ve aydınlatma metinleri) | **Seçildi** |
| 4 | Ev & Yaşam | Koçtaş | https://www.koctas.com.tr | Ürün adı, fiyat, indirim, satıcı (kurumsal) | Hayır | Ürün sayfaları serbest (bazı varyantlar hariç); arama yasak | Site kullanım koşulları sayfası yok; "Tüm Politikalarımız" listesinde otomatik erişimle ilgili metin yok | **Seçildi** |
| 5 | Giyim | Koton | https://www.koton.com | Ürün adı, fiyat, indirim | Hayır | Ürün sayfaları serbest; `search_text=` yasak | Altbilgide bağlantı yok; üyelik sözleşmesi sunucuları otomatik programlarla yüklemeyi yasaklıyor, site içeriğinin izinsiz kullanımını ve kopyalanmasını sınırlıyor. Açık bot yasağı yok | **Seçildi, gri alan** (aşağıdaki nota bakınız) |

**Elenen adaylar**

| Kaynak | Neden |
|---|---|
| lcw.com | Kullanım koşulları otomatik program, örümcek, robot ve veri madenciliğini yazılı izin olmadan yasaklıyor |
| decathlon.com.tr | `robots.txt` uygun, ama üyelik sözleşmesi yazılı izin olmadan robot, crawler, veri madenciliği ve "screen scraping" kullanımını yasaklıyor |
| defacto.com.tr | `robots.txt` ürün sayfalarını (`/Product/`) yasaklıyor |
| mavi.com | Koton ile aynı sözleşme şablonu; Koton tercih edildi |
| kitapyurdu.com | 24 Kasım'da `robots.txt` isteği reddedildi; kitap kaynağı olarak D&R tercih edildi |
| n11.com, teknosa.com, boyner.com.tr, colins.com.tr | `robots.txt` dosyasına erişilemedi |
| vatanbilgisayar.com, akakce.com | Sayfalama/arama yasak (22 Kasım kontrolü) |
| englishhome.com | `*.html*` kuralı ürün sayfalarını engelleyebilir; belirsiz |
| trendyol.com, hepsiburada.com | Ürün sayfaları `robots.txt` ile serbest, ama kullanım şartları okunmadı; yedek |

**Hocaya not (giyim):** Giyim kategorisinde incelenen sitelerin hiçbiri tamamen temiz çıkmadı: LC Waikiki ve Decathlon otomatik erişimi açıkça yasaklıyor, Koton ve Mavi yalnız sunucuyu aşırı yüklemeyi yasaklıyor. Koton'u düşük hacim, istekler arasında bekleme ve yalnız fiyat bilgisiyle kullanmayı öneriyoruz; uygun görmezseniz giyim ürünlerini rakip verisiz bırakıp diğer dört kategoriyle ilerleriz.

**İlk fiyat taraması:** 25 ürünün bu sitelerdeki kategori sayfalarından alınan fiyat örnekleri [`docs/fiyat-taramasi.md`](fiyat-taramasi.md) (veri: `data/web-fiyat-taramasi.csv`). 25 ürünün hepsinde web medyanı bugünkü liste fiyatımızın üstünde, 17'sinde 2 katından fazla; simülasyon liste fiyatları bu tabloya göre güncellenecek (bölüm 4).

## 4. Simülasyonun genişletilmesi (plan)

Mevcut yapı: `src/simulasyon.py`, `data/siparisler-g2.csv`, `docs/veri-sozlugu.md`. PR #95 (`--urun_agirliklari`) birleşti ve temel alınacak.

- **Yapıldı (Tuğba, PR #102):** Dışarıdan ürün listesi: `--urun_listesi <csv>` (`kategori,urun,liste_fiyati[,fiyat_sapmasi]`). Verilmezse bugünkü 25 ürün ve varsayılan MD5 (`1b7f765e…`) değişmez. Örnek: `data/urun-listesi-ornek.csv`.
- **Yapıldı (Tuğba, PR #102):** Fiyat aralığı: `--fiyat_sapmasi` (0–0.5, vars. 0.05) ve listede ürün başına `fiyat_sapmasi` sütunu.
- **Yapıldı (Tuğba, PR #102):** Web fiyatlı liste `data/urun-listesi-web.csv` (`onerilen_liste_tl`; Spor Ayakkabı, Masa Lambası ve Kahve Makinesi eski fiyatta, gerekçe `docs/eslesme-tanimlari.md`) ve bununla üretilen örnek veri `data/siparisler-web.csv`.
- Ürün adları, Ajan 1'in eşleştirdiği web ürünleriyle uyuşacak; eşleşme tanımları `docs/eslesme-tanimlari.md` (PR #100). Liste fiyatları için önerilen yeni değerler `data/web-fiyat-taramasi.csv` → `onerilen_liste_tl` sütununda (Hilal, 24 Kasım).
- Örnek veri `data/` altına, yeni parametreler `docs/veri-sozlugu.md` Simülasyon parametreleri tablosuna ve değişiklik günlüğüne yazılacak (Hilal, DQ).
- Yeni parametreler (`--urun_listesi`, `--fiyat_sapmasi`) için test kuralları: `tests/test-cases.md` G2-TC-26…34, koşucu `src/dq_test_g2.py` (36/36), sonuç `tests/test-log.md` (Sema, DQ).

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
