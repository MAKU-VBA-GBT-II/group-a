# Analiz — Görev 1 (Sipariş verisi)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Tuğba Tuana Kaygısız · **Issue:** #14
**Veri:** `data/siparisler.csv` · **Şema:** `docs/veri-sozlugu-g1.md` · **Hesaplama:** `python src/dq_analiz.py`

**Kullanılan veri:** `data/siparisler.csv` · commit `1f8beb8` · 400 satır · tarih aralığı 2026-01-01 – 2026-09-30
**Veri kalitesi:** `python src/dq_test.py` → 12/12 test geçti (2026-10-22; bkz. `tests/test-cases.md`).
**Yorum sayılarının kaynağı:** Yorum, Bulgular ve Sınırlılıklar'daki tüm sayılar `python src/dq_analiz.py --ek` çıktısındaki "Ek istatistikler" bölümünden alındı. İlk analiz `fa3b368` ile yapıldı; `1f8beb8` yalnızca para alanlarının CSV'deki yazımını düzeltti (#27), metrik değerleri değişmedi.

> Not: Veri, BE'nin sabit tohumlu (seed 42) simülasyonudur. Gözlemler bu simülasyonun ürettiği deseni anlatır; gerçek müşteri davranışı iddiası taşımaz.

## Metrikler

| # | Metrik | Formül | Neyi ölçer |
|---|---|---|---|
| M1 | Toplam ciro | `Σ toplam_tutar` | Dönem boyunca elde edilen toplam satış geliri (TL) |
| M2 | Sipariş başına ortalama adet | `Σ adet / sipariş sayısı` | Müşterinin bir siparişte ortalama kaç ürün aldığı (sepet büyüklüğü) |
| M3 | Kategori bazlı ciro *(kırılım 1)* | kategoriye göre `Σ toplam_tutar`; pay = kategori cirosu / toplam ciro | Gelirin kategorilere dağılımı; hangi kategorinin işi taşıdığı |
| M4 | Haftalık ciro trendi *(kırılım 2)* | haftaya (pazartesi başlangıçlı) göre `Σ toplam_tutar` | Gelirin zaman içindeki değişimi; yükselen/düşen dönemler |
| M5 | Top-3 ürün | ürüne göre `Σ toplam_tutar`, büyükten küçüğe ilk 3; pay = ürün cirosu / toplam ciro | Ciroya en çok katkı veren ürünler ve gelirin ne kadar yoğunlaştığı |

### M1 — Toplam ciro

**3.114.411,51 TL** (400 sipariş)

**Yorum:** Dokuz ayda 400 siparişten 3,11 milyon TL ciro elde edilmiş; sipariş başına ortalama tutar 7.786 TL. Ancak medyan sipariş tutarı 4.031 TL, yani ortalamanın yaklaşık yarısı: ciroyu az sayıda yüksek tutarlı sipariş yukarı çekiyor.

### M2 — Sipariş başına ortalama adet

**5,38 adet** (medyan 5, toplam 2151 adet)

**Yorum:** Müşteriler bir siparişte ortalama 5–6 adet ürün alıyor. Kategoriler arasında fark küçük (Giyim 5,01 – Ev & Yaşam 5,69); kategoriler arasındaki ciro farkı adetten değil birim fiyattan geliyor.

### M3 — Kategori bazlı ciro

| Kategori | Sipariş | Ciro | Pay |
|---|---|---|---|
| Elektronik | 81 | 1.185.311,64 TL | %38,1 |
| Ev & Yaşam | 89 | 1.069.400,03 TL | %34,3 |
| Giyim | 72 | 491.308,10 TL | %15,8 |
| Kozmetik | 88 | 287.549,18 TL | %9,2 |
| Kitap | 70 | 80.842,56 TL | %2,6 |

**Yorum:** Elektronik ve Ev & Yaşam birlikte cironun **%72,4**'ünü getiriyor, ama siparişlerin yalnızca %42,5'ini (170/400) oluşturuyor. Kitap ise siparişlerin %17,5'ini (70) almasına rağmen cironun sadece %2,6'sında kalıyor; Kitap'ta ortalama sipariş 1.155 TL, Elektronik'te 14.633 TL.

### M4 — Haftalık ciro trendi

| Hafta başı | Sipariş | Ciro |
|---|---|---|
| 2025-12-29 | 7 | 20.940,49 TL |
| 2026-01-05 | 11 | 78.980,62 TL |
| 2026-01-12 | 13 | 93.334,32 TL |
| 2026-01-19 | 14 | 156.388,00 TL |
| 2026-01-26 | 17 | 90.597,05 TL |
| 2026-02-02 | 8 | 98.586,04 TL |
| 2026-02-09 | 9 | 54.931,52 TL |
| 2026-02-16 | 10 | 61.028,76 TL |
| 2026-02-23 | 14 | 74.098,33 TL |
| 2026-03-02 | 5 | 63.620,98 TL |
| 2026-03-09 | 8 | 17.710,13 TL |
| 2026-03-16 | 12 | 138.162,04 TL |
| 2026-03-23 | 10 | 64.023,03 TL |
| 2026-03-30 | 11 | 76.388,09 TL |
| 2026-04-06 | 7 | 58.628,45 TL |
| 2026-04-13 | 9 | 65.985,28 TL |
| 2026-04-20 | 8 | 63.384,20 TL |
| 2026-04-27 | 10 | 82.627,56 TL |
| 2026-05-04 | 7 | 72.137,48 TL |
| 2026-05-11 | 13 | 85.423,07 TL |
| 2026-05-18 | 7 | 62.003,19 TL |
| 2026-05-25 | 9 | 63.015,92 TL |
| 2026-06-01 | 13 | 82.152,15 TL |
| 2026-06-08 | 13 | 90.955,38 TL |
| 2026-06-15 | 11 | 145.306,12 TL |
| 2026-06-22 | 5 | 42.041,41 TL |
| 2026-06-29 | 4 | 43.289,96 TL |
| 2026-07-06 | 16 | 81.256,72 TL |
| 2026-07-13 | 13 | 100.708,55 TL |
| 2026-07-20 | 15 | 139.595,70 TL |
| 2026-07-27 | 10 | 56.199,76 TL |
| 2026-08-03 | 8 | 63.632,56 TL |
| 2026-08-10 | 9 | 101.974,12 TL |
| 2026-08-17 | 13 | 90.712,91 TL |
| 2026-08-24 | 10 | 60.483,15 TL |
| 2026-08-31 | 11 | 135.777,01 TL |
| 2026-09-07 | 8 | 58.400,37 TL |
| 2026-09-14 | 7 | 66.915,50 TL |
| 2026-09-21 | 9 | 47.053,22 TL |
| 2026-09-28 | 6 | 65.962,37 TL |

Haftalık ortalama: 77.860,29 TL · en yüksek: 2026-01-19 haftası (156.388,00 TL) · en düşük: 2026-03-09 haftası (17.710,13 TL)

Not: 2025-12-29, 2026-09-28 haftaları kısmi (7 günün tamamı veride yok); en yüksek/en düşük hesabına katılmadı.

**Yorum:** Haftalık ciro 17,7 bin TL ile 156,4 bin TL arasında dalgalanıyor; belirgin bir yükseliş ya da düşüş trendi yok. Aylık bazda en güçlü ay Ocak (62 sipariş, 440 bin TL), en zayıf ay Şubat (40 sipariş, 288 bin TL). En yüksek cirolu üç tam haftada (19 Ocak, 15 Haziran, 20 Temmuz) haftanın en büyük 3 siparişi, haftalık cironun %55–59'unu tek başına oluşturuyor; bu siparişlerin çoğu Elektronik ve Ev & Yaşam'dan.

### M5 — Ciroya en çok katkı veren 3 ürün

| Sıra | Ürün | Kategori | Ciro | Pay |
|---|---|---|---|---|
| 1 | Saklama Kabı Seti | Ev & Yaşam | 353.688,15 TL | %11,4 |
| 2 | Kablosuz Kulaklık | Elektronik | 306.092,09 TL | %9,8 |
| 3 | Powerbank | Elektronik | 298.541,52 TL | %9,6 |

Top-3'ün toplam payı: %30,8

**Yorum:** 25 ürünün 3'ü cironun yaklaşık üçte birini (%30,8) getiriyor; üçü de yüksek fiyatlı kategorilerden. En az ciro getiren ürünlerin tamamı Kitap kategorisinde (en düşük: Deneme, 6.033 TL).

## Bulgular

1. **Ciroyu sipariş sayısı değil fiyat belirliyor.** Kategorilerin sipariş sayıları birbirine yakın (70–89), ama ciro payları %2,6 ile %38,1 arasında değişiyor. Ortalama adet her kategoride ~5 olduğundan fark tamamen birim fiyattan geliyor.
2. **Gelir birkaç ürüne yoğunlaşmış.** Top-3 ürün (Saklama Kabı Seti, Kablosuz Kulaklık, Powerbank) cironun %30,8'ini getiriyor; ilk 8 ürünün 7'si Elektronik ya da Ev & Yaşam'dan.
3. **Ciro zamanda dengesiz ama trendsiz.** Haftalık ciro 9 kata varan farklarla (17,7 bin – 156,4 bin TL) dalgalanıyor ve ortalama sipariş (7.786 TL) medyanın (4.031 TL) neredeyse iki katı: haftanın cirosu, o hafta birkaç büyük sipariş gelip gelmemesine bağlı.

**Eylem önerisi:** Stok ve kampanya bütçesi ciro payına göre önceliklendirilmeli: Top-3 ürünün stokta kesintisiz tutulması öncelikli; düşük tutarlı Kitap ve Kozmetik için ise sipariş başına tutarı artıracak paket / "X TL üzeri ücretsiz kargo" kampanyası denenmeli ve etkisi bir sonraki veriyle ölçülmeli.

## Sınırlılıklar

> #30 üzerine eklendi. Görev 1 verisi değiştirilmedi; yukarıdaki metrikler ve bulgular aşağıdaki sınırlarla birlikte okunmalıdır. Bu noktalar Görev 2 simülasyonunda ele alınacak.

1. **Haftalık ciro tek tek büyük siparişlere çok duyarlı (M4).** Haftada ortalama yalnızca 10 sipariş var (en az 4, en çok 17) ve sipariş tutarlarının standart sapması (8.832 TL) ortalamasından (7.786 TL) büyük. Tam haftaların yarısında, haftanın en büyük 3 siparişi haftalık cironun %67,6'sını veya daha fazlasını oluşturuyor. Bu yüzden M4'teki sıçramalar (ör. 19 Ocak, 15 Haziran, 20 Temmuz) bir trend ya da sezon etkisi değil, birkaç büyük siparişin aynı haftaya denk gelmesidir; M4 trendi yorumlanırken bu dikkate alınmalı.
2. **Ürünlerin kendine özgü bir fiyatı yok (M3, M5).** `src/veri_uret.py` birim fiyatı her satırda ürünün değil kategorinin fiyat aralığından rastgele çekiyor. Bu yüzden aynı ürün çok farklı fiyatlarla satılmış görünüyor (Saklama Kabı Seti 134–3.933 TL, Powerbank 387–4.647 TL, Kahve Makinesi 144–3.950 TL). Top-3 ürün sıralaması ürünlerin gerçek fiyat farkından çok bu rastgelelikten etkileniyor olabilir; Saklama Kabı Seti'nin 1. sırada çıkması temkinle yorumlanmalı.
3. **Dalgalanmaların bir nedeni yok.** Simülasyonda hafta içi/hafta sonu, kampanya veya sezon etkisi modellenmedi; zaman içindeki tüm değişim rastgele. Bulgu 3'teki "belirgin trend yok" sonucu verinin üretim biçiminin doğal sonucudur ve gerçek müşteri davranışı hakkında çıkarım için kullanılmamalı.
