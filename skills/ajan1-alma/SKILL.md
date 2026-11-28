---
name: ajan1-alma
description: Ajan 1'in (toplama) ilk aşaması. Rakip sitelerin kategori sayfalarını kurallara uyarak açar, sayfanın gerçekten yüklendiğini kontrol eder ve ham ürün kartlarını ajan1-isleme'ye verir. Rakip fiyatı toplanacağı zaman kullan.
---

# ajan1-alma: Rakip sayfalarını kurallara uyarak alma (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114 · **Sonraki aşama:** `ajan1-isleme`

## Kaynaklar (İnşa Haftası 1)

| Ürün | Site | Kategori sayfası | Tarayıcı |
|---|---|---|---|
| Masa Lambası | IKEA | Masa Lambaları | Gerekli: liste JavaScript ile 24'er yükleniyor (`?page=N`); sayfa adım adım kaydırılır, her yeni yüklemede bekleme kuralı uygulanır |
| Nemlendirici | Gratis | Yüz Nemlendirici Gece Kremleri | Gerekmez (ürünler ham HTML'de); sayfalar `?page=N` ile gezilir |
| Şampuan | Gratis | Şampuanlar | Gerekmez |
| Parfüm | Gratis | Parfüm | Gerekmez |
| Güneş Kremi | Gratis | Güneş Ürünleri | Gerekmez |
| Ruj | Gratis | Ruj | Gerekmez |

Kod bütün siteleri aynı Playwright tarayıcısıyla açar (`arac = playwright`); "Gerekmez", ürünlerin JavaScript olmadan da sayfada olduğu anlamına gelir.

Kaynak seçimi ve robots.txt / kullanım şartları kontrolü: `docs/oneri.md` §3. Diğer siteler sonraki haftalarda `ajan1-kaynak-ekleme` ile eklenir.

## Erişim kuralları

1. **Yalnızca kategori ve ürün sayfaları.** Arama sayfaları (`/search`, `/arama/`, `q=`, `query=`) robots.txt ile yasak; açılmaz.
2. **Bekleme, şu sırayla:**
   - robots.txt'de `Crawl-delay` varsa ona uyulur (28 Kasım kontrolünde Gratis ve IKEA'da yok).
   - Site 429 (çok fazla istek) dönerse sitenin istediği kadar beklenir; ikinci 429'da o site bırakılır.
   - Sayfa hiç cevap vermezse (zaman aşımı, bağlantı hatası) site "yavaşla" diyor sayılır: **30 saniye** beklenip bir kez daha denenir; ikinci zaman aşımında o site bırakılır, sıradaki siteye geçilir. *(28 Kasım: Gratis Ruj sayfasında zaman aşımı alındı.)*
   - Sunucu hatası (5xx) bir kez daha denenir.
   - Site bir şey söylemiyorsa istekler arasında **3–5 saniye rastgele** beklenir.
3. **Sınır:** Kategori başına en fazla **100 ürün** (öneri: Claude · onay: Hilal). Sınıra ulaşılırsa durulur ve kayda yazılır.
4. **Kişisel veri yok:** Yalnızca ürün adı, fiyat, miktar, stok ve sayfa adresi alınır. Yorum, kullanıcı adı ve satıcı profili alınmaz.
5. **robots.txt her çalıştırmada kontrol edilir.** Her sayfa açılmadan önce adresin sitenin robots.txt dosyasında hâlâ serbest olduğuna bakılır; yasaklanmışsa açılmaz ve kayda yazılır. *(24 Kasım'daki elle kontrol o günün durumunu gösterir; siteler kurallarını değiştirebilir.)*

## Girdi kontrolü (sayfa gerçekten geldi mi?)

Bir kategori sayfası şu durumlarda **başarısız** sayılır ve o kategori boş tabloyla geçilmez:
- Sayfa açılmadı ya da hata döndü.
- Sayfada hiç ürün kartı bulunamadı (site tasarımı değişmiş olabilir).
- IKEA'da kaydırma bitti ama ürün sayısı ham HTML'deki 3–4 üründen fazla değil. Bu kontrol, Playwright'ın sayfayı gerçekten kaydırıp JavaScript ile yüklenen listeyi aldığını doğrular.

Başarısız kategori `runs/ajan1/` kaydına gerekçesiyle yazılır ve kullanıcıya bildirilir. **Sessizce boş veri üretilmez.** Çalışma yarıda kalsa da o ana kadar okunan kategoriler tabloya ve rapora yazılır; bir kategorinin hatası diğerlerinin verisini kaybettirmez.

## İz

Açılan her sayfanın adresi, zamanı, robots.txt kontrolünün sonucu ve kaç ürün okunduğu `runs/ajan1/` altındaki çalışma kaydına yazılır.

## Karar kaydı (28 Kasım 2026)

- **Kaynak kapsamı (Hilal):** Yalnızca IKEA ile başlamak elendi. Masa Lambası satırlarının çoğu 3 kat kuralıyla elenecek; bu, Ajan 2 ve 3'ün elinde kanıt olarak çok az veri bırakır ve çıkarım yapmalarını zorlaştırır.
- **Gratis seçimi (Hilal):** Gratis fiyatları listemize yakın. İşleyişi önce bu "cevabı bilinen" veriyle görmek; hataları erken fark etmeyi, analiz kısmını revize etmeyi ve Playwright/Python tarafında gerekli güncellemeleri zor kaynaklardan önce yapmayı sağlar.
- **Bekleme süresi (Hilal):** Sürenin bizim değil sitenin belirlemesi gerektiğini sorguladım. Kural buna göre kuruldu: önce `Crawl-delay`, sonra 429, en son bizim varsayılanımız.
- **Rastgele aralık (Hilal):** Sabit 4 saniye yerine 3–5 saniye arası rastgele bekleme. Yavaş başlanır; istendiği gibi gitmezse daha da yavaşlanır.
- **Uyarlanabilir bekleme (Hilal, sonraki haftalar):** Bekleme süresinin sabit bir sayıya değil, sitenin ne kadar rahat çalıştığına göre ayarlanmasını önerdim. İlk başta bunu rastgele aralığın sağlayacağını düşünmüştüm; Claude rastgele beklemenin siteye uyum sağlamadığını düzeltti. Fikir böylece "uyarlanabilir bekleme" olarak netleşti: site rahatsa bekleme kısalır, yükleniyorsa uzar.
- **Kontrollerin zenginleştirilmesi (Hilal):** Skill'lerin tekdüze kaldığını fark edip zenginleştirilmesini istedim. Claude'un önerdiği beş kontrolden robots.txt'nin her çalıştırmada kontrolünü (bu skill), önceki taramayla karşılaştırmayı ve tekrar ayıklamayı (`ajan1-isleme`) bu hafta için seçtim.
- **Zaman aşımı da bir işarettir (Hilal):** Bekleme süresini sitenin belirlemesi gerektiği fikrinden yola çıkarak sayfanın hiç cevap vermemesinin de sitenin "yavaşla" demesi olduğunu söyledim; Claude ilk başta bunu gerekli görmemişti; 28 Kasım'daki Ruj zaman aşımında gerekli olduğu ortaya çıktı ve kural eklendi.
- *Claude'un katkısı:* Rastgele beklemenin hız kazandırmadığını, gerekçenin isteklerin düzenli görünmemesi olduğunu belirtti. Uyarlanabilir beklemede "düşük hacim" sözünü korumak için alt sınırın 3 saniyede sabit kalmasını önerdi. Sayfanın gerçekten yüklendiğini doğrulayan girdi kontrolünü ekledi.
