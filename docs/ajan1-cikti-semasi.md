# Ajan 1 çıktı şeması: rakip fiyat tablosu

**Şirket:** Sepetix Analitik (Grup A) · **Görev:** Duyuru-10, Çok Ajanlı Şirket Programı · **Issue:** #96
**Üreten:** Ajan 1, Hilal Elçin Şahin · **Okuyanlar:** Ajan 2, Tuğba Tuana Kaygısız (birleştirme ve analiz) · Ajan 3, Sema Nur Doğan (denetim ve yeniden doğrulama)
**Durum:** 24 Kasım 2026'da Ajan 1, Ajan 2 ve Ajan 3 arasında grupta kararlaştırılan alanlar. Ajanlar arası ortak mesaj biçimi belgesi (Çekirdek, Ali) çıkınca bu tablo o belgenin içine taşınır; alanlar değişmez.

> Yalnız herkese açık ürün ve fiyat bilgisi toplanır. Yorum, kullanıcı adı, bireysel satıcı profili gibi kişisel veriler hiçbir alana yazılmaz (Duyuru-10, web verisi kuralları).

## Dosya

| Özellik | Değer |
|---|---|
| Biçim | UTF-8 CSV, virgül ayraçlı, ilk satır başlık |
| Satır birimi | 1 satır = 1 rakip ürün sayfası (bir ürünümüze birden fazla rakip ürün düşebilir; hepsi ayrı satır) |
| Sütun sayısı | **19**, aşağıdaki sırayla |
| Para | TL; sayı alanlarında yalnız sayı, nokta ondalıklı, tam 2 ondalık (`1299.90`) |
| Zaman | ISO 8601, Türkiye saati (`+03:00`) |
| Silme | Satır silinmez; elenen satır `elendi` alanında gerekçesiyle işaretlenir |

## Alanlar

| # | Alan | Tip / izinli değerler | Zorunlu | Örnek | Kim için, neden |
|---|---|---|---|---|---|
| 1 | `bizim_urun` | Kullanılan ürün listesindeki ad, yazımı birebir (`data/urun-listesi-web.csv`) | evet | `Kablosuz Kulaklık` | Ajan 2 sipariş verisiyle bu alan üzerinden birleştirir |
| 2 | `kategori` | Ürün listesindeki kategori | evet | `Elektronik` | Kategori kırılımı, kural kontrolü |
| 3 | `rakip_urun_adi` | Ürün sayfasındaki başlık, olduğu gibi | evet | (sayfadaki ürün başlığı) | Ajan 3 sayfadaki adla karşılaştırır |
| 4 | `eslesme_yontemi` | `benzer` (şimdilik tek değer; `birebir` sonraki haftalara kaldı) | evet | `benzer` | Ajan 2 |
| 5 | `eslesme_guveni` | `yuksek` / `orta` / `dusuk` | evet | `orta` | `docs/eslesme-tanimlari.md` kural 4 |
| 6 | `birim_miktar` | Metin: miktar ve birim | hayır | `300 ml`, `1 çift`, `20.000 mAh` | Birim fiyat karşılaştırması (Ajan 2) |
| 7 | `ham_fiyat_metni` | Sayfada görünen fiyat metni, olduğu gibi | evet | `₺1.299,90` | Ajan 3 ayrıştırma hatasını yakalar |
| 8 | `liste_fiyati` | Sayı, 2 ondalık | evet | `1499.90` | Kampanya analizi (Ajan 2) |
| 9 | `indirimli_fiyat` | Sayı, 2 ondalık; indirim yoksa boş | hayır | `1299.90` | Kampanya analizi; varsa karşılaştırmada bu kullanılır (eşleşme tanımları kural 7) |
| 10 | `fiyat_turu` | `liste` / `indirimli` / `kampanya` | evet | `indirimli` | Ajan 3: yanlış karşılaştırmayı önler |
| 11 | `kdv_dahil` | `evet` / `hayir` | evet | `evet` | Ajan 2 |
| 12 | `para_birimi` | `TRY` | evet | `TRY` | TL dışı para birimi elenir (kural 7) |
| 13 | `stok_durumu` | `var` / `yok` / `bilinmiyor` | evet | `var` | Stokta olmayanın fiyatı güvenilir sayılmayabilir (Ajan 2, Ajan 3) |
| 14 | `rakip_site` | Sitenin kurumsal adı: `MediaMarkt` / `Gratis` / `D&R` / `Koçtaş` / `IKEA` / `Koton` | evet | `MediaMarkt` | Site bazında karşılaştırma; bireysel satıcı adı yazılmaz |
| 15 | `urun_url` | Ürünün **kendi sayfasının** adresi (liste ya da arama sayfası değil), izleme parametreleri temizlenmiş | evet | `https://www.mediamarkt.com.tr/tr/product/...` | Ajan 3 fiyatı bu sayfadan yeniden doğrular |
| 16 | `bulma_yolu` | Ürünün bulunduğu kategori sayfasının adresi ve sayfa numarası, `<adres> s.<n>` | evet | `https://www.mediamarkt.com.tr/tr/category/...html s.2` | JS'li/sayfalı kaynakta ürünü yeniden bulmak; site içi arama robots.txt ile yasak olduğu için arama ifadesi kullanılmaz |
| 17 | `cekilme_zamani` | ISO 8601 | evet | `2026-11-25T14:05:00+03:00` | Bayat veri kontrolü; her sayının üretim zamanı (Duyuru-10, teslim skill'i) |
| 18 | `arac` | Kullanılan araç | evet | `playwright` | Araç izi; oturum kaydıyla eşleşir |
| 19 | `elendi` | Boş ya da gerekçe: `fiyat bandı dışı` / `çoklu paket` / `ikinci el` / `stok yok` / `TL dışı` | hayır | (boş) | Tuğba'nın isteği: elenen satır silinmez, işaretlenir |

## Ajan 1'in teslimden önce kontrol ettikleri

1. Zorunlu alanların hiçbiri boş değil; 19 sütun bu sırada.
2. `bizim_urun` ve `kategori` kullanılan ürün listesinde var.
3. `urun_url` bir ürün sayfası; arama sayfası (`/search`, `query=`, `q=`) değil.
4. `liste_fiyati` > 0; `indirimli_fiyat` doluysa `liste_fiyati`'ndan küçük ve `fiyat_turu` ≠ `liste`.
5. `ham_fiyat_metni`'nden ayrıştırılan sayı, `indirimli_fiyat` (yoksa `liste_fiyati`) ile aynı.
6. `elendi` gerekçeleri `docs/eslesme-tanimlari.md` kural 2, 5, 6 ve 7'ye göre dolduruldu (ör. karşılaştırma fiyatı < 0,3x veya > 3x liste fiyatımız → `fiyat bandı dışı`).

Bayatlık eşiği (kaç saatten eski `cekilme_zamani`'nın geri gönderileceği) Ajan 2'nin alma skill'inde belirlenir.

## Örnek satır

*Biçimi göstermek içindir, gerçek bir ürün değildir.*

```csv
bizim_urun,kategori,rakip_urun_adi,eslesme_yontemi,eslesme_guveni,birim_miktar,ham_fiyat_metni,liste_fiyati,indirimli_fiyat,fiyat_turu,kdv_dahil,para_birimi,stok_durumu,rakip_site,urun_url,bulma_yolu,cekilme_zamani,arac,elendi
Şampuan,Kozmetik,Örnek Marka Onarıcı Şampuan 400 ml,benzer,yuksek,400 ml,"₺249,90",299.90,249.90,indirimli,evet,TRY,var,Gratis,https://www.gratis.com/sampuan/ornek-marka-onarici-sampuan-400-ml-p-00000000,https://www.gratis.com/sac-bakim/sampuan-c-5030101 s.1,2026-11-25T14:05:00+03:00,playwright,
```

## Değişiklik günlüğü

| Tarih | Değişiklik | Kaynak |
|---|---|---|
| 2026-11-24 | İlk sürüm: 19 alan. Tuğba'nın eklemeleri (site adı, liste/indirimli fiyat ayrımı, KDV, birim/miktar, stok, eşleşme yöntemi, `elendi`) ve Sema'nın eklemeleri (ürün sayfası linki, ham fiyat metni, fiyat türü, bulma yolu, stok) dahil. Güven değerleri eşleşme tanımlarıyla aynı (`yuksek`/`orta`/`dusuk`) | Grup yazışması 24.11, #96, #100 |
