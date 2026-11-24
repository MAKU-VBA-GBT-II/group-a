# Veri Sözlüğü — Görev 2 Mini Ürün (`data/siparisler-g2.csv`)

**Şirket:** Sepetix Analitik (Grup A) · **Sektör:** E-ticaret · **Rol:** DQ · **Issue:** #60
**Üretecek betik:** `src/` altında BE simülasyonu (#61, `skills/be-simulasyon/SKILL.md`) · **Skill:** [`skills/dq-sozluk/SKILL.md`](../skills/dq-sozluk/SKILL.md)
**Okuyanlar:** BE (#61) · FE (#63) · DQ analiz (#62) · DQ test (#64)

> Tüm veriler simülasyon ürünüdür; gerçek kişi ya da işletme verisi içermez (ders kuralı §3.1). Müşteriler yalnızca sentetik kimlikle (`M0001`) temsil edilir.

## Dosya özeti

| Özellik | Değer |
|---|---|
| Dosya | `data/siparisler-g2.csv` |
| Satır birimi | 1 satır = 1 sipariş |
| Satır sayısı | Parametrelerden **hesaplanır** (bkz. Satır sayısı); varsayılanla **8.208** |
| Sütun sayısı | **14** |
| Ayraç / ondalık | virgül (`,`) / nokta (`.`) |
| Kodlama / satır sonu | UTF-8 / `\n` |
| Tarih biçimi | `YYYY-MM-DD` |
| Para | TL; dosyada yalnızca sayı, **her zaman tam 2 ondalık** (`1299.00`) — Görev 1 #27 kuralı |
| Sıralama | `siparis_tarihi` artan; `siparis_id` 1…N ardışık |
| Tekrarlanabilirlik | Aynı parametreler + aynı `tohum` → birebir aynı dosya |

## Simülasyon parametreleri

Parametreler betiğin başında sabit olarak **ve** komut satırından değiştirilebilir olmalıdır (#61).

| Parametre | Tip | Varsayılan | İzinli aralık | Etkisi |
|---|---|---|---|---|
| `gun_sayisi` | int | `182` (26 hafta) | 1 – 366 | Simüle edilen gün sayısı → satır sayısı |
| `gunluk_siparis` | int | `40` | 1 – 500 | Normal bir hafta içi gündeki sipariş sayısı → satır sayısı |
| `hafta_sonu_katsayisi` | float | `1.3` | 0.1 – 5.0 | Cumartesi/Pazar günlük sipariş çarpanı |
| `kampanya_katsayisi` | float | `1.5` | 1.0 – 5.0 | Kampanya günlerinde sipariş çarpanı |
| `kampanya_donemleri` | tarih aralıkları listesi | `2026-03-09:2026-03-15`, `2026-05-11:2026-05-17` | her aralık `BAŞ:SON`, BAŞ ≤ SON | Kampanya günleri (`kampanya = 1`, indirim uygulanır) |
| `baslangic_tarihi` | tarih | `2026-01-05` (Pazartesi) | geçerli `YYYY-MM-DD` | İlk günün tarihi |
| `musteri_sayisi` | int | `1500` | 1 – 9999 | `musteri_id` havuzunun büyüklüğü |
| `tohum` | int | `42` | ≥ 0 | Rastgelelik tohumu |
| `urun_agirliklari` *(isteğe bağlı, Görev 3)* | ürün sayısı kadar sayı (virgülle ayrılmış) | boş (= ürünler eşit olasılık) | tam olarak ürün listesindeki ürün sayısı kadar değer (varsayılan listede **25**), sıra ürün listesinin sırası (varsayılanda aşağıdaki **Ürün sırası**); her değer sonlu ve ≥ 0; en az biri > 0 | Yalnızca `urun` dağılımını (dolayısıyla `kategori` ve ciro karmasını) değiştirir; satır sayısını değiştirmez. Boşken eski üretim aynen çalışır (MD5 `1b7f765e…`); verilince `rng` akışı değiştiği için dosyanın tamamı farklı çıkar |
| `urun_listesi` *(isteğe bağlı, Duyuru-10)* | CSV dosya yolu | boş (= betikteki 25 ürün, aşağıdaki tablo) | var olan UTF-8 CSV; biçimi aşağıdaki **Ürün listesi dosyası** | Ürün kümesini, kategorilerini ve liste fiyatlarını dışarıdan verir; satır sayısını değiştirmez. Varsayılan 25 ürünle aynı içerikteki `data/urun-listesi-ornek.csv` verilirse dosya varsayılanla **aynı MD5**'i (`1b7f765e…`) verir |
| `fiyat_sapmasi` *(isteğe bağlı, Duyuru-10)* | float | `0.05` | 0 – 0.5 | `birim_fiyat`'ın liste fiyatından en fazla sapma oranı: [liste × (1 − sapma), liste × (1 + sapma)]. Ürün listesi dosyasında ürün başına ayrıca verilebilir; dosyadaki değer bu parametreye üstün gelir. Varsayılanda eski ±%5 kuralıyla birebir aynı (MD5 değişmez) |

**Geçersiz parametre** (aralık dışı, yanlış tip, bozuk tarih, BAŞ > SON; `urun_agirliklari` için ürün sayısından farklı sayıda değer, sayı olmayan değer, negatif / `nan` / `inf` değer veya hepsi 0; `fiyat_sapmasi` 0–0.5 dışında; `urun_listesi` için bulunamayan dosya, UTF-8 olarak okunamayan dosya, eksik zorunlu sütun, boş liste, boş `kategori`/`urun`, iki kez geçen ürün, 0 veya negatif ya da 2'den fazla ondalıklı `liste_fiyati`, 0–0.5 dışında ürün başı `fiyat_sapmasi`): betik çökmez, `ValueError` ile parametrenin adını ve izinli aralığı söyleyen bir mesaj verir; dosya **yazılmaz** (Hafta 6 hata yönetimi).

`urun_agirliklari` ağırlıkları toplamı 1 olacak şekilde normalize edilir: ürün *i*'nin olasılığı `w_i / Σw`'dir (`1,1,2,…` ile `2,2,4,…` aynı dosyayı verir). Eşit ağırlık (`1,1,…,1`) bile varsayılandan **farklı MD5** verir; eşit olasılık için parametre boş bırakılır. Negatif değer komut satırında `--urun_agirliklari=-1,…` (eşittir ile) yazılır, yoksa `argparse` değeri seçenek sanır.

### Ürün listesi dosyası (`--urun_listesi`)

UTF-8 CSV (BOM'lu da okunur), virgül ayraçlı, ilk satır başlık. Sütun sırası önemli değildir; ürünlerin sırası dosyadaki satır sırasıdır (`urun_agirliklari` bu sırayı izler).

| Sütun | Zorunlu | Tip / kural | Örnek |
|---|---|---|---|
| `kategori` | evet | boş olmayan metin | `Elektronik` |
| `urun` | evet | boş olmayan metin; dosyada bir kez geçer | `Kablosuz Kulaklık` |
| `liste_fiyati` | evet | TL, nokta ondalıklı, > 0, en fazla 2 ondalık | `2999` |
| `fiyat_sapmasi` | hayır | 0 – 0.5; boş hücre = `--fiyat_sapmasi` değeri | `0.10` |

Repodaki örnekler: `data/urun-listesi-ornek.csv` (betikteki 25 ürün ve liste fiyatları; varsayılan dosyayı aynen üretir) · `data/urun-listesi-web.csv` (aynı 25 ürün, liste fiyatları Ajan 1'in 24 Kasım web fiyat taramasına göre güncellenmiş; bkz. `docs/fiyat-taramasi.md`, `data/web-fiyat-taramasi.csv`).

**Web fiyatlı örnek veri:** `python src/simulasyon.py --urun_listesi data/urun-listesi-web.csv --cikti data/siparisler-web.csv` → `data/siparisler-web.csv`, **8.208** satır, 14 sütun, MD5 `628b4351250b4065b9669baf233449e7`, `birim_fiyat` 170,12 – 15.743,03 TL; iç kontroller (kural 1–11) geçti.

## Satır sayısı

Satır sayısı rastgele değildir; her gün için hesaplanıp toplanır:

```
gun_k     = 1.0
gun_k    *= hafta_sonu_katsayisi   (gün Cumartesi veya Pazar ise)
gun_k    *= kampanya_katsayisi     (gün bir kampanya dönemi içindeyse)
gun_adet  = max(1, floor(gunluk_siparis × gun_k + 0.5))   # en yakın tamsayı (.5 yukarı), en az 1
N         = Σ gun_adet   (gun_sayisi gün boyunca)
```

| Senaryo | Değişen parametre | Beklenen N | Son tarih |
|---|---|---|---|
| Varsayılan | — | **8.208** | 2026-07-05 |
| Kısa dönem | `gun_sayisi = 10` | **424** | 2026-01-14 |
| Tek hafta | `gun_sayisi = 7` | **304** | 2026-01-11 |
| Kısa ve seyrek | `gun_sayisi = 10`, `gunluk_siparis = 10` | **106** | 2026-01-14 |

`max(1, …)` sayesinde **her gün en az bir sipariş** vardır (ör. `gunluk_siparis = 1`, `hafta_sonu_katsayisi = 0.4` → hafta sonu `floor(0.9) = 0` yerine 1); dosyadaki farklı tarih sayısı = `gun_sayisi`. Varsayılan ve tablodaki senaryolarda en küçük gün 40 sipariş olduğu için bu kural sonuçları değiştirmez.

`tohum`, `urun_agirliklari`, `urun_listesi` ve `fiyat_sapmasi` formülde yoktur: içeriği değiştirir, **satır sayısını değiştirmez** (ör. ağırlıklı varsayılan çalıştırma yine 8.208 satır).

## Alanlar

Sütunlar dosyada **tam olarak bu sırada** bulunur:

| # | Alan | Tip | Aralık / kural | Birim | Örnek | Açıklama |
|---|---|---|---|---|---|---|
| 1 | `siparis_id` | int | 1 … N, benzersiz, 1'den başlar, 1'er artar | – | `1` | Sipariş kimliği |
| 2 | `siparis_tarihi` | tarih | `baslangic_tarihi` … `baslangic_tarihi + gun_sayisi − 1` | – | `2026-01-05` | Sipariş günü; dosya bu alana göre artan |
| 3 | `musteri_id` | metin | `M` + 4 hane, `M0001` … `M{musteri_sayisi}` | – | `M0427` | Sentetik müşteri kimliği; bir müşteri birden çok sipariş verebilir |
| 4 | `kanal` | metin | Web, Mobil, Pazaryeri | – | `Mobil` | Siparişin geldiği kanal |
| 5 | `kategori` | metin | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Kitap | – | `Elektronik` | Ürün kategorisi (Görev 1 ile aynı yazım) |
| 6 | `urun` | metin | 25 ürünlük liste (aşağıda) | – | `Powerbank` | Daima kendi kategorisine aittir |
| 7 | `adet` | int | 1 – 5 | adet | `2` | Sipariş miktarı |
| 8 | `birim_fiyat` | float | ürünün liste fiyatı × [0,95 – 1,05], 2 ondalık | TL | `612.35` | **Ürüne özgü** fiyat (#30) |
| 9 | `indirim_orani` | float | kampanya dışı `0.00`; kampanyada `0.10`, `0.15`, `0.20`, `0.25`, `0.30` | oran | `0.20` | Siparişe uygulanan indirim |
| 10 | `kampanya` | int | `0` veya `1` | – | `1` | Sipariş günü bir kampanya dönemindeyse `1` |
| 11 | `toplam_tutar` | float | `round(adet × birim_fiyat × (1 − indirim_orani), 2)`; > 0 | TL | `979.76` | **Hesaplanır**, rastgele üretilmez |
| 12 | `sehir` | metin | İstanbul, Ankara, İzmir, Antalya, Burdur | – | `Burdur` | Teslimat şehri |
| 13 | `odeme_tipi` | metin | Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme | – | `Kredi Kartı` | Ödeme yöntemi |
| 14 | `durum` | metin | Teslim Edildi, İade, İptal | – | `Teslim Edildi` | Siparişin son durumu |

Örnek satır (başlık + 1 satır):

```
siparis_id,siparis_tarihi,musteri_id,kanal,kategori,urun,adet,birim_fiyat,indirim_orani,kampanya,toplam_tutar,sehir,odeme_tipi,durum
1,2026-01-05,M0427,Mobil,Elektronik,Powerbank,2,612.35,0.20,1,979.76,Burdur,Kredi Kartı,Teslim Edildi
```

*(Örnek satır biçimi göstermek içindir; 2026-01-05 varsayılan kampanya döneminde değildir, gerçek dosyada bu tarihte `kampanya = 0`, `indirim_orani = 0.00` olur.)*

## Geçerli değer listeleri

### `kategori`, `urun` ve liste fiyatı

`birim_fiyat` her siparişte **kendi ürününün liste fiyatından** en fazla ±`fiyat_sapmasi` (varsayılan ±%5) sapar. Aşağıdaki tablo varsayılan (betikteki) ürün listesidir; `--urun_listesi` verilirse ürünler, kategoriler ve liste fiyatları o dosyadan gelir. Ürünler **varsayılanda eşit olasılıkla** (her biri %4) seçilir; `urun_agirliklari` verilirse olasılıklar `w_i / Σw` olur (bkz. **Ağırlıklı alanlar**).

| Kategori | Ürün → liste fiyatı (TL) |
|---|---|
| Elektronik | Kablosuz Kulaklık 1.299 · Bluetooth Hoparlör 899 · Powerbank 599 · Akıllı Saat 3.499 · Klavye 749 |
| Giyim | Tişört 249 · Kot Pantolon 699 · Sweatshirt 549 · Spor Ayakkabı 1.899 · Mont 2.299 |
| Ev & Yaşam | Kahve Makinesi 2.999 · Battaniye 449 · Masa Lambası 399 · Saklama Kabı Seti 299 · Halı 1.799 |
| Kozmetik | Nemlendirici 189 · Şampuan 129 · Parfüm 999 · Güneş Kremi 279 · Ruj 159 |
| Kitap | Roman 149 · Deneme 129 · Ders Kitabı 349 · Çocuk Kitabı 99 · Şiir Kitabı 119 |

Buna göre `birim_fiyat` tüm dosyada **94,05 – 3.673,95 TL** aralığındadır.

**Ürün sırası** (`urun_agirliklari`'ndaki 25 değerin sırası; tabloyu soldan sağa, yukarıdan aşağı okuyun): 1 Kablosuz Kulaklık · 2 Bluetooth Hoparlör · 3 Powerbank · 4 Akıllı Saat · 5 Klavye · 6 Tişört · 7 Kot Pantolon · 8 Sweatshirt · 9 Spor Ayakkabı · 10 Mont · 11 Kahve Makinesi · 12 Battaniye · 13 Masa Lambası · 14 Saklama Kabı Seti · 15 Halı · 16 Nemlendirici · 17 Şampuan · 18 Parfüm · 19 Güneş Kremi · 20 Ruj · 21 Roman · 22 Deneme · 23 Ders Kitabı · 24 Çocuk Kitabı · 25 Şiir Kitabı. Bu sıra `src/simulasyon.py` → `URUNLER` ile birebir aynıdır.

### Ağırlıklı alanlar

| Alan | Değer → olasılık |
|---|---|
| `urun` | Varsayılan: 25 ürün eşit, her biri %4 · `urun_agirliklari` verilirse ürün *i* → `w_i / Σw` |
| `adet` | 1 → %50 · 2 → %25 · 3 → %12 · 4 → %8 · 5 → %5 |
| `kanal` | Web %45 · Mobil %40 · Pazaryeri %15 |
| `sehir` | İstanbul %35 · Ankara %20 · İzmir %20 · Antalya %15 · Burdur %10 |
| `odeme_tipi` | Kredi Kartı %50 · Banka Kartı %25 · Kapıda Ödeme %15 · Havale/EFT %10 |
| `durum` | Teslim Edildi %90 · İade %6 · İptal %4 |
| `indirim_orani` (yalnızca `kampanya = 1`) | 0.10 / 0.15 / 0.20 / 0.25 / 0.30 eşit olasılık |
| `musteri_id` | `M0001` … `M{musteri_sayisi}` eşit olasılık |

## Veri kalitesi kuralları

Her kural bir test senaryosuna dönüşür (`tests/test-cases.md`, #64):

1. **Boş değer yok** — hiçbir alanda `NaN` veya boş metin.
2. **Sütunlar** — adları ve sırası yukarıdaki tabloyla birebir aynı; 14 sütun.
3. **Satır sayısı** — kullanılan parametrelerle formülden hesaplanan N'ye eşit.
4. **`siparis_id`** — 1…N ardışık ve benzersiz; dosya `siparis_tarihi`'ne göre artan.
5. **Tarih aralığı** — tüm tarihler `baslangic_tarihi` … `+ gun_sayisi − 1` içinde; farklı tarih sayısı = `gun_sayisi`.
6. **Kategorik değerler** — `kanal`, `kategori`, `urun` (`kategori` ve `urun` için geçerli liste, kullanılan ürün listesidir), `sehir`, `odeme_tipi`, `durum` yalnızca listelerdeki değerleri alır; yazım birebir. Listedeki her değerin dosyada en az bir kez geçmesi beklenir; **istisna:** `urun_agirliklari`'nda ağırlığı 0 verilen ürün (ve tüm ürünleri 0 olan kategori) dosyada hiç geçmez.
7. **Ürün–kategori** — her `urun` kendi `kategori`sine aittir.
8. **Fiyat** — `birim_fiyat`, kendi ürününün liste fiyatının [1 − sapma, 1 + sapma] aralığında (varsayılan [%95, %105]; kuruş cinsinden, alt sınır yukarı, üst sınır aşağı yuvarlanır).
9. **Sayı biçimi** — `birim_fiyat`, `toplam_tutar` ve `indirim_orani` ham metinde tam 2 ondalık (`^\d+\.\d{2}$`; ör. `0.20`, `0.00`).
10. **Hesaplanan alan** — `toplam_tutar == round(adet × birim_fiyat × (1 − indirim_orani), 2)`.
11. **Kampanya tutarlılığı** — `kampanya = 1` ⇔ tarih bir kampanya dönemi içinde; `kampanya = 0` ⇒ `indirim_orani = 0.00`; `kampanya = 1` ⇒ `indirim_orani ∈ {0.10, …, 0.30}`.
12. **Tekrarlanabilirlik** — aynı parametre ve tohumla iki çalıştırma aynı dosyayı (aynı MD5) üretir.

## #30 sınırlılıklarının çözümü

| Görev 1 sınırlılığı (#30) | Görev 2'deki kural |
|---|---|
| Haftada ~10 sipariş → tek büyük sipariş haftalık ciroyu ikiye katlıyor | Varsayılan ~300+ sipariş/hafta (`gunluk_siparis = 40`); `adet` 1–5 ve %50'si 1 adet |
| Ürünün kendine özgü fiyatı yok (Saklama Kabı Seti 134–3.933 TL) | `birim_fiyat` = ürünün liste fiyatı ± %5 (Saklama Kabı Seti 284,05 – 313,95 TL) |
| Dalgalanmaların nedeni yok | Hafta sonu (`× 1,3`) ve kampanya (`× 1,5` + indirim) dönemleri **parametreli ve nedenli** |

## Metrikler

Para metrikleri yalnızca **teslim edilen** siparişler üzerinden hesaplanır (`durum == "Teslim Edildi"`); iade ve iptaller ayrıca M6'da izlenir.

| Kod | Metrik | Formül (pandas) | Dahil satırlar | Neyi ölçer | Grafik |
|---|---|---|---|---|---|
| M1 | **Toplam net ciro** | `t["toplam_tutar"].sum()` | teslim edilen (`t`) | Dönemde gerçekleşen toplam gelir | — |
| M2 | **Ortalama sepet tutarı** | `t["toplam_tutar"].mean()` (= M1 / teslim edilen sipariş sayısı) | teslim edilen | Sipariş başına ortalama gelir | dağılım grafiğinde dikey çizgi |
| M3 | **Haftalık net ciro trendi** *(zaman kırılımı)* | `t.set_index("siparis_tarihi").resample("W-MON", label="left", closed="left")["toplam_tutar"].sum()` | teslim edilen | Haftadan haftaya gelir; kampanya haftalarının etkisi | zaman serisi |
| M4 | **Kanal bazlı net ciro ve payı** *(kategorik kırılım)* | `t.groupby("kanal")["toplam_tutar"].sum()` ve `/ M1 × 100` | teslim edilen | Gelirin Web / Mobil / Pazaryeri'ne dağılımı | kırılım (çubuk) |
| M5 | **Ciroda ilk 5 ürün** *(top-N)* | `t.groupby("urun")["toplam_tutar"].sum().nlargest(5)` | teslim edilen | Gelire en çok katkı veren ürünler | — |
| M6 *(ek)* | **İade + iptal oranı** | `(df["durum"] != "Teslim Edildi").mean() × 100`, ayrıca `kategori` kırılımı | tüm siparişler | Kaybedilen siparişlerin payı | — |

Hafta tanımı Görev 1 ile aynıdır: Pazartesi başlangıçlı (`W-MON`). Varsayılan başlangıç Pazartesi olduğu için kısmi hafta oluşmaz (26 tam hafta).

## Grafik eşlemesi (FE)

| Grafik (#63) | Metrik | Not |
|---|---|---|
| Zaman serisi | M3 | Kampanya haftaları işaretlenir; ortalama çizgisi M3'ün ortalaması |
| Kategorik kırılım | M4 | Kanal başına net ciro (bin TL) ve pay (%) |
| Dağılım (histogram) | `toplam_tutar` (teslim edilen) | M2 dikey çizgiyle gösterilir |

## Değişiklik günlüğü

| Tarih | Değişiklik | Commit / Issue |
|---|---|---|
| 2026-10-29 | İlk sürüm: 14 alan, 8 parametre, satır sayısı formülü, 12 kalite kuralı, M1–M6 | #60 |
| 2026-10-30 | Kural 9: `indirim_orani` da ham metinde tam 2 ondalık (PR #66 incelemesi) | #64 |
| 2026-11-01 | Satır sayısı: `gun_adet = max(1, …)`; izinli aralıktaki parametrelerle 0 siparişli gün oluşup kural 5'in düşmesi önlendi (PR #72 incelemesi) | #64 |
| 2026-11-22 | 9. parametre `urun_agirliklari` (isteğe bağlı ürün popülerlik ağırlığı): parametre tablosu, geçersiz parametre kuralı, normalize ve MD5 notu, satır sayısına etkisizlik, **Ürün sırası**, `urun` olasılığı (Ağırlıklı alanlar), kural 6 istisnası (ağırlığı 0 olan ürün). Alanlar, tipler, aralıklar ve varsayılan dosya değişmedi | PR #95, #86 |
| 2026-11-24 | Duyuru-10 simülasyon genişletmesi (PR #102): 10. ve 11. parametreler `urun_listesi` ve `fiyat_sapmasi`; **Ürün listesi dosyası** biçimi; `urun_agirliklari` ürün sayısına bağlandı; geçersiz parametre kuralı, satır sayısına etkisizlik, kural 6 ve kural 8 genelleştirildi; web fiyatlı örnek veri `data/siparisler-web.csv`. Varsayılan dosya ve MD5 değişmedi | PR #102, #96 |
