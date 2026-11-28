# Yeni görev: öneri ve roller — Sepetix Analitik (Grup A)

**Şirket:** Sepetix Analitik · **Sektör:** E-ticaret · **Görev:** Duyuru-10, Çok Ajanlı Şirket Programı
**Teslim:** 26 Kasım 2026 Perşembe 13:00 · **PM:** Ali Haydar Polat

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
| 1 | Elektronik (+ Kahve Makinesi) | MediaMarkt | https://www.mediamarkt.com.tr | Ürün adı, güncel/liste fiyatı, stok | **Hayır** (25 Kasım düzeltmesi). Düz istekte ham HTML'de 12 ürün kartı, ürün bağlantıları ve fiyatlar var; `?page=2` düz istekle farklı 12 ürün döndürüyor. 24 Kasım'daki "ham HTML'de kart yok" notu yanlıştı (bkz. **Tarayıcı testi**) | Ürün sayfaları ve `page=` serbest; `/search.html`, `query=`, `sort=`, `filter=` yasak | Otomatik erişim yasağı yok; site materyali yalnız şahsi kullanım içindir, ticari/genel amaçlı çoğaltma yazılı izne tabidir. Akademik, ticari olmayan, düşük hacimli fiyat toplama | **Seçildi** |
| 2 | Kozmetik | Gratis | https://www.gratis.com | Ürün adı, fiyat, indirim, miktar (ml/g) | Hayır (fiyat liste sayfasında) | Ürün sayfaları serbest; `/search` ve `query=` yasak | Otomatik erişimi açıkça yasaklayan madde yok; siteyi başkalarının kullanımını zorlaştıracak biçimde kullanmak yasak | **Seçildi** |
| 3 | Kitap | D&R | https://www.dr.com.tr | Kitap adı, fiyat, indirim, stok | Hayır | Ürün sayfaları serbest, ürün site haritası var; arama yasak | Ayrı kullanım koşulları sayfası yok, ama [üyelik sözleşmesi](https://www.dr.com.tr/uyelik-sozlesmesi) üye olmayan **ziyaretçiler için de bağlayıcı** olduğunu söylüyor ve platform içeriğini izlemek, kopyalamak veya çoğaltmak amacıyla herhangi bir yöntem kullanmayı yasaklıyor. Açık bot yasağı yok | **Seçildi, gri alan** (Koton ile aynı tür madde; aşağıdaki nota bakınız) |
| 4 | Ev & Yaşam | Koçtaş | https://www.koctas.com.tr | Ürün adı, fiyat, indirim, satıcı (kurumsal) | Hayır | Ürün sayfaları serbest (bazı varyantlar hariç); arama yasak | Site kullanım koşulları sayfası yok; "Tüm Politikalarımız" listesinde otomatik erişimle ilgili metin yok | **Seçildi** |
| 5 | Giyim | Koton | https://www.koton.com | Ürün adı, fiyat, indirim | Hayır | Ürün sayfaları serbest; `search_text=` yasak | Altbilgide bağlantı yok; üyelik sözleşmesi sunucuları otomatik programlarla yüklemeyi yasaklıyor, site içeriğinin izinsiz kullanımını ve kopyalanmasını sınırlıyor. Açık bot yasağı yok | **Seçildi, gri alan** (aşağıdaki nota bakınız) |
| 6 | Ev & Yaşam (Masa Lambası) | IKEA | https://www.ikea.com.tr | Ürün adı, fiyat | **Evet.** Kategori sayfasının ham HTML'inde ürün listesi yok (ör. Battaniyeler: tarayıcıda ilk yüklemede 26, sonuna kadar kaydırınca 65 ürün; ham HTML'de yalnız 3–4 vitrin ürünü); liste sayfa açıldıktan sonra JavaScript ile ayrı bir servisten (`frontendapi.ikea.com.tr`) yükleniyor, kaydırdıkça devamı geliyor (Masa Lambaları: sonuna kadar kaydırınca 94 ürün, ham HTML'de 3–4). 25 Kasım'da tarayıcıda doğrulandı | `/kategori/` ve `/urun/` serbest, kategori ve ürün site haritası var; `/arama/` ve `/_ws/` yasak. `frontendapi.ikea.com.tr` için `robots.txt` yok (404) | Ayrı kullanım koşulları sayfası yok; [üyelik sözleşmesi](https://www.ikea.com.tr/uyelik-sozlesmesi) site materyalinin önceden izin alınmadan ve kaynak gösterilmeden kopyalanmasını ve çoğaltılmasını yasaklıyor; otomatik erişim, robot veya kazıma yasağı yok. Otomatik erişim yasağı yok, ama izin şartı yalnız kaynak göstermekle karşılanmayabilir | **Seçildi, gri alan** (tarayıcı gerektiren kaynak; aşağıdaki nota bakınız) |

**Elenen adaylar**

| Kaynak | Neden |
|---|---|
| lcw.com | Kullanım koşulları otomatik program, örümcek, robot ve veri madenciliğini yazılı izin olmadan yasaklıyor |
| decathlon.com.tr | `robots.txt` uygun, ama üyelik sözleşmesi yazılı izin olmadan robot, crawler, veri madenciliği ve "screen scraping" kullanımını yasaklıyor |
| defacto.com.tr | `robots.txt` ürün sayfalarını (`/Product/`) yasaklıyor |
| mavi.com | Koton ile aynı sözleşme şablonu; Koton tercih edildi |
| kitapyurdu.com | 24 Kasım'da `robots.txt` isteği reddedildi; kitap kaynağı olarak D&R tercih edildi |
| migros.com.tr | Tarayıcı gerektiren tek aday (ham HTML'de ürün ve fiyat yok), `robots.txt` kategori sayfalarına izin veriyor; ama kullanım koşulları "page-scrape", "robot", "spider" ve diğer otomatik programları açıkça yasaklıyor (25 Kasım kontrolü) |
| n11.com, teknosa.com, boyner.com.tr, colins.com.tr | `robots.txt` dosyasına erişilemedi |
| vatanbilgisayar.com, akakce.com | Sayfalama/arama yasak (22 Kasım kontrolü) |
| englishhome.com | `*.html*` kuralı ürün sayfalarını engelleyebilir; belirsiz |
| trendyol.com, hepsiburada.com | Ürün sayfaları `robots.txt` ile serbest, ama kullanım şartları okunmadı; yedek |

**Hocaya not (giyim):** Giyim kategorisinde incelenen sitelerin hiçbiri tamamen temiz çıkmadı: LC Waikiki ve Decathlon otomatik erişimi açıkça yasaklıyor, Koton ve Mavi yalnız sunucuyu aşırı yüklemeyi yasaklıyor. Koton'u düşük hacim, istekler arasında bekleme ve yalnız fiyat bilgisiyle kullanmayı öneriyoruz; uygun görmezseniz giyim ürünlerini rakip verisiz bırakıp diğer dört kategoriyle ilerleriz.

**Hocaya not (kitap):** D&R da Koton ile aynı durumda: açık bot yasağı yok, ama ziyaretçiyi de bağlayan üyelik sözleşmesi içeriği izlemek ve kopyalamak için yöntem kullanmayı yasaklıyor. Kitapyurdu'nun `robots.txt` dosyasına erişilemediği için temiz bir yedek yok. Aynı koşulları (düşük hacim, bekleme, yalnız ad ve fiyat) uyguluyoruz; uygun görmezseniz kitap ürünlerini rakip verisiz bırakırız.

**Hocaya not (IKEA):** Tarayıcı gerektiren kaynağımız IKEA. Otomatik erişimi, robotu ya da kazımayı yasaklayan bir madde yok; üyelik sözleşmesi ise site materyalinin "önceden izin alınmadan ve kaynak gösterilmeden" kopyalanmasını yasaklıyor. Kaynak göstermek bu şartı tek başına karşılamayabileceği için Koton ve D&R gibi gri alan sayıyoruz ve aynı koşulları uyguluyoruz (düşük hacim, bekleme, yalnız ad ve fiyat, kaynak gösterilerek). Uygun görmezseniz Masa Lambası Koçtaş verisine döner ve tarayıcı gerektiren kaynak olarak başka bir site ararız.

**Tarayıcı testi (25 Kasım):** Her sitenin kategori sayfası Chrome'da açıldı, aynı adres JavaScript çalıştırılmadan düz istekle (`fetch`) yeniden çekildi ve ham HTML'de ürün adı, ürün bağlantısı ve fiyat arandı.

| Site | Ham HTML'de ürün ve fiyat | Tarayıcı gerekir mi? |
|---|---|---|
| MediaMarkt | Var: 12 ürün kartı, bağlantılar ve fiyatlar; `?page=2` farklı 12 ürün | Hayır |
| Gratis | Var: fiyatlar ham metinde | Hayır |
| Koton | Var: ürün adları ve fiyatlar gömülü veride, kartlar JavaScript ile çiziliyor | Hayır (gömülü veri okunabilir) |
| Koçtaş | Var: ürün adları ve fiyatlar ham HTML'de | Hayır |
| D&R | Var: ürün bağlantıları ve fiyatlar ham metinde | Hayır |
| IKEA | Yok: ham HTML'de yalnız 3–4 vitrin ürünü; liste JavaScript ile ayrı servisten yükleniyor, kaydırdıkça devam ediyor | **Evet** |
| Migros (elendi) | Yok: yalnız uygulama kabuğu; tarayıcıda ürün ve fiyat görünüyor | **Evet** |

Sonuç: ilk beş kaynak düz istekle okunabiliyor; **IKEA tarayıcı gerektiriyor** (Migros da gerektiriyor ama kullanım koşulları nedeniyle elendi). Ajan 1 bütün kaynaklarda fiyatı sayfada görünen haliyle okumak için tarayıcıyla (Playwright) çalışacak; IKEA'da sayfayı kaydırarak listenin tamamını yükleyecek. IKEA, Koçtaş'ta ayrı karşılığı bulunmayan Masa Lambası için kaynak olarak eklendi. Battaniye için kullanılmıyor: IKEA Battaniyeler kategorisindeki 65 ürünün çoğunun adında "battaniye" geçmiyor (örtü vb.), eşleşme kuralı ayrıca gerekirdi; Battaniye Koçtaş'tan. Masa Lambası 25 Kasım'da IKEA'dan tarayıcıyla yeniden tarandı (`docs/fiyat-taramasi.md`: n 52, medyan 1.699 TL; Koçtaş'ın çocuk lambalarında medyan 936 TL'ydi).

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

### ACP araç erişimi ve bağımsız doğrulama (28 Kasım 2026)

- Ebru'nun deneme ortamı Windows; Python 3.15.0 kurulu. Node.js/`npx` ve Claude CLI yok; WSL komutu var ancak Linux dağıtımı kurulu değil. Bu nedenle `claude auth status` çalıştırılamadı; bu ortamda etkin bir Claude Code oturumu doğrulanmadı.
- Abonelik tablosuna göre Ebru'nun Claude aboneliği yok. Mevcut Claude Code Pro onay/red kayıtları Ali'nin 27 Kasım oturumlarından; bunlar Ebru'nun hesabı veya bağımsız tekrarı değildir.
- Windows'ta `python -m unittest discover -s tests -p 'test_acp_cekirdek.py' -v` denemesi 11 testte `FAILED (errors=20)` verdi. `select.select` pipe üzerinde `WinError 10038`, süreç temizliğindeki `os.killpg` eksikliği ise `AttributeError` oluşturdu. Mock izin testleri karar adımına ulaşmadı; gerçek ajan denemesi yapılmadı.
- Kurulum ve gerçek “Bir kez izin ver / Bir kez reddet” doğrulaması için macOS/Linux, Python 3.10+, Node.js 22+ ve kullanmaya yetkili, Claude Code'da oturum açmış bir hesap gerekiyor. Bu denemede önkoşullar sağlanmadığı için doğrulama engelli; oturum belirteci veya kimlik bilgisi paylaşılmamalı. Windows'ta ayrıca çekirdeğin pipe ve süreç yönetimi uyumluluğu çözülmeden test başarılı sayılmamalı.

## 6. Roller

| Ad Soyad | Rol | GitHub |
|---|---|---|
| Ali Haydar Polat | Çekirdek ve Arayüz (PM) | @plt0051ct-rgb |
| Ebru Türk | Çekirdek ve Arayüz — destek (junior) | @ebruturk |
| Hilal Elçin Şahin | Ajan 1 — Toplama | @hilalelcin-stack |
| Tuğba Tuana Kaygısız | Ajan 2 — Analiz | @tugbatuanakaygisiz-web |
| Sema Nur Doğan | Ajan 3 — Denetim | @semadogaan |

## 7. Teslim kontrol listesi

- [x] Senaryo ve üç ajanın birer cümlelik tanımı yazılı
- [x] Web kaynakları listelenmiş; en az biri tarayıcı gerektiriyor (IKEA); robots.txt ve kullanım şartları kontrol edilmiş
- [x] Simülasyon web kaynaklarıyla eşleşen alanlar üretiyor ve dışarıdan liste veya aralık alabiliyor
- [x] Örnek veri ve güncel veri sözlüğü repoda
- [x] Rol listesi ve abonelikler Issue'da, @eofdred etiketli (#109)

---

Üretim: Bu taslak Claude ile hazırlandı. Prompt özeti: "Duyuru-10'a göre docs/oneri.md taslağı yaz: senaryo, 3 ajan tanımı, web kaynakları (robots.txt kontrolüyle), simülasyon genişletme planı, abonelikler, roller."
