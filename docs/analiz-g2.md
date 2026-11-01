# Analiz — Görev 2 Mini Ürün (Sipariş simülasyonu)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Sema Nur Doğan · **Issue:** #62
**Veri:** `data/siparisler-g2.csv` · commit **`f9dfca7`** (PR #66) · 8.208 satır · 2026-01-05 … 2026-07-05 (26 tam hafta) · MD5 `1b7f765e40e9b9897c82566a6442b45f` · varsayılan parametreler (`tohum=42`)
**Metrik tanımları:** `docs/veri-sozlugu.md` → Metrikler (#60) · **Betik:** `python src/dq_analiz_g2.py --ek` · **Skill:** [`skills/dq-analiz/SKILL.md`](../skills/dq-analiz/SKILL.md)
**Veri kalitesi:** PR #66 incelemesinde sözlüğün 1–11. kalite kuralları bağımsız kontrolle geçti; tam test turu `tests/test-log.md`'de (#64).

> Para metrikleri yalnızca `durum == "Teslim Edildi"` siparişlerden hesaplanır (7.383 sipariş); iade ve iptaller M6'da ayrıca izlenir. Tüm veriler simülasyon ürünüdür.

## Metrikler

### M1 — Toplam net ciro

**11.973.617,93 TL** (7.383 teslim edilen sipariş; tüm siparişler 8.208)

26 haftada teslim edilen siparişlerden elde edilen net gelir budur; iade ve iptal edilen 825 siparişin tutarı dahil değildir. Görev 1'deki 400 siparişlik veriye göre hacim yaklaşık 20 kat büyüktür; bu, haftalık metriklerin tek tek siparişlere duyarlılığını azaltır (#30).

### M2 — Ortalama sepet tutarı

| Ölçü | Değer |
|---|---|
| Ortalama sepet (M1 / teslim edilen sipariş) | 1.621,78 TL |
| Medyan sepet | 728,95 TL |

Ortalama, medyanın yaklaşık 2,2 katıdır: siparişlerin yarısı 729 TL'nin altındayken az sayıdaki yüksek tutarlı sipariş (en yüksek 18.062,25 TL) ortalamayı yukarı çeker. Bu yüzden "tipik sipariş" için medyan, gelir planlaması için ortalama daha anlamlıdır.

### M3 — Haftalık net ciro trendi (zaman kırılımı)

| Hafta başı | Teslim edilen sipariş | Net ciro | Kampanya |
|---|---|---|---|
| 2026-01-05 | 281 | 491.470,92 TL |  |
| 2026-01-12 | 270 | 418.027,03 TL |  |
| 2026-01-19 | 271 | 413.547,99 TL |  |
| 2026-01-26 | 263 | 475.502,42 TL |  |
| 2026-02-02 | 270 | 437.917,18 TL |  |
| 2026-02-09 | 273 | 430.011,50 TL |  |
| 2026-02-16 | 277 | 503.517,69 TL |  |
| 2026-02-23 | 272 | 462.535,97 TL |  |
| 2026-03-02 | 269 | 464.491,23 TL |  |
| 2026-03-09 | 416 | 521.655,16 TL | ✓ |
| 2026-03-16 | 267 | 354.938,80 TL |  |
| 2026-03-23 | 267 | 462.934,92 TL |  |
| 2026-03-30 | 276 | 433.947,77 TL |  |
| 2026-04-06 | 280 | 440.877,68 TL |  |
| 2026-04-13 | 283 | 460.216,29 TL |  |
| 2026-04-20 | 275 | 441.626,69 TL |  |
| 2026-04-27 | 272 | 399.875,59 TL |  |
| 2026-05-04 | 279 | 424.139,56 TL |  |
| 2026-05-11 | 409 | 693.031,67 TL | ✓ |
| 2026-05-18 | 274 | 428.560,99 TL |  |
| 2026-05-25 | 269 | 480.792,03 TL |  |
| 2026-06-01 | 276 | 484.300,71 TL |  |
| 2026-06-08 | 275 | 440.044,51 TL |  |
| 2026-06-15 | 273 | 420.979,26 TL |  |
| 2026-06-22 | 271 | 490.307,47 TL |  |
| 2026-06-29 | 275 | 498.366,90 TL |  |

Haftalık ortalama **460.523,77 TL**; en yüksek hafta 2026-05-11 (693.031,67 TL, kampanya), en düşük hafta 2026-03-16 (354.938,80 TL, ilk kampanyanın ertesi haftası). Kampanya dışındaki 24 haftanın 23'ünde ciro 399–504 bin TL bandında kalıyor (tek istisna 2026-03-16); değişim katsayısı %13,0 (Görev 1'de 17–156 bin TL arası dalgalanma vardı, #30).

### M4 — Kanal bazlı net ciro ve payı (kategorik kırılım)

| Kanal | Teslim edilen sipariş | Net ciro | Pay |
|---|---|---|---|
| Web | 3.244 | 5.300.953,08 TL | %44,3 |
| Mobil | 3.046 | 4.962.757,70 TL | %41,4 |
| Pazaryeri | 1.093 | 1.709.907,15 TL | %14,3 |

Web ve Mobil birlikte cironun %85,7'sini getiriyor ve aralarındaki fark yalnızca 2,9 puan; Pazaryeri %14,3 ile üçüncü sırada. Kanal payları sipariş sayısı paylarına çok yakın, yani kanallar arasında sepet büyüklüğü farkı yok.

### M5 — Ciroda ilk 5 ürün (top-N)

| Sıra | Ürün | Liste fiyatı | Teslim edilen sipariş | Net ciro | Pay |
|---|---|---|---|---|---|
| 1 | Akıllı Saat | 3.499 TL | 304 | 2.055.616,19 TL | %17,2 |
| 2 | Kahve Makinesi | 2.999 TL | 298 | 1.742.230,23 TL | %14,6 |
| 3 | Mont | 2.299 TL | 273 | 1.139.387,83 TL | %9,5 |
| 4 | Spor Ayakkabı | 1.899 TL | 306 | 1.115.093,41 TL | %9,3 |
| 5 | Halı | 1.799 TL | 285 | 1.004.833,46 TL | %8,4 |

İlk 5 ürün cironun **%58,9**'unu oluşturuyor. Bu ürünler liste fiyatı en yüksek 5 üründür: sipariş sayıları diğer ürünlerle aynı düzeyde (248–326), ciro sırası liste fiyatı sırasıyla birebir aynı (Spearman 1,00). Yorum için bkz. Sınırlılıklar.

### M6 (ek) — İade + iptal oranı

Genel **%10,1** (825 / 8.208) · İade %6,1 · İptal %4,0

| Kategori | Sipariş | İade + iptal | Oran |
|---|---|---|---|
| Ev & Yaşam | 1.692 | 177 | %10,5 |
| Elektronik | 1.684 | 172 | %10,2 |
| Giyim | 1.640 | 166 | %10,1 |
| Kitap | 1.594 | 156 | %9,8 |
| Kozmetik | 1.598 | 154 | %9,6 |

Kategoriler arasında fark 1 puanın altında; oranlar sözlükteki %10 (iade %6 + iptal %4) varsayımıyla tutarlı.

## Bulgular

1. **Kampanyalar siparişi aynı oranda artırıyor ama ciroyu aynı oranda artırmıyor.** İki kampanya haftasında da teslim edilen sipariş ~%50 arttı (416 ve 409; normal hafta ~270), ama net ciro ilk kampanyada normal hafta ortalamasının (448.288,80 TL) yalnızca **%16,4**, ikincisinde **%54,6** üstüne çıktı. Kampanyalı siparişlerde ortalama indirim %19,9; sipariş başına net tutar 1.472,35 TL, kampanyasız 1.640,58 TL. İki kampanyada toplam 298.308,00 TL indirim verildi.
2. **İlk kampanyanın ertesi haftası dönemin en düşük haftası.** 2026-03-16 haftası 354.938,80 TL ile normal ortalamanın %20,8 altında; ikinci kampanyanın ertesi haftası ise yalnızca %4,4 altında. Simülasyonda kampanya sonrası düşüş modellenmediği için bu fark rastlantısal sepet dağılımından geliyor; yine de bir haftalık ciro tek başına kampanya başarısını ölçmek için yeterli değil.
3. **Gelir hafta sonu ve yüksek tutarlı siparişlerde yoğunlaşıyor.** Hafta sonu günlük ortalama net ciro 79.151,80 TL, hafta içinden (60.444,03 TL) %31 yüksek. Siparişlerin %7,7'si 5.000 TL'nin üstünde ve ilk 5 ürün cironun %58,9'unu getiriyor; medyan sepet (729 TL) ortalamanın yarısından az.

**Eylem önerisi:** Kampanya etkisini "sipariş sayısı" değil **"kampanya haftası net cirosu + sipariş başına net tutar"** ile ölçelim ve indirimi kontrollü deneyelim: simülasyonun bir sonraki sürümünde indirim oranlarını parametre yapıp (ör. üst sınır %15) aynı tohumla mevcut kurguyla karşılaştıralım; kampanyayı hafta sonunu kapsayacak biçimde tutalım. Karar için en az iki kampanya haftası ve ertesi haftalar birlikte izlenmeli.

## Sınırlılıklar

- **M5 en pahalı ürünleri gösteriyor:** Ürünler şema gereği eşit olasılıkla seçildiği için "ciroda ilk 5 ürün" gerçek bir talep tercihini değil, liste fiyatı sıralamasını yansıtıyor (Spearman 1,00). Bu metrik ancak ürün seçimi ağırlıklı yapılırsa anlam kazanır (BE skill'i → Bilinen sınırlılıklar; PM notu #62).
- **Yeni / tekrar müşteri ayrımı anlamlı değil:** 1.500 kişilik havuzdan 8.208 sipariş rastgele çekildiği için siparişlerin %81,8'i "tekrar" görünüyor; haftalık tekrar payı ilk hafta %10,9'dan son hafta %99,3'e çıkıyor. Bu bir sadakat eğilimi değil, havuzun dolmasının sonucu; yeni ve tekrar müşterinin ortalama sepeti de yakın (1.704,51 TL / 1.603,44 TL). Bu nedenle gözlem olarak kullanılmadı (PM önerisi #62).
- **Kampanya etkisi kısmen rastlantısal:** İndirim oranı her kampanyalı siparişte rastgele seçiliyor ve haftalık ciro büyük sepetlere duyarlı; iki kampanya arasındaki fark (+%16,4 / +%54,6) aynı kurgunun rastlantısal sonucudur.
- **Durum (iade/iptal) ürün, kanal ve tutardan bağımsız** üretiliyor; M6'daki kategori farkları gerçek bir iade davranışı göstermez.
- Veriler sentetiktir; gözlemler nedensellik veya gerçek müşteri davranışı iddiası taşımaz.

## Yeniden üretme

```bash
pip install pandas
python src/dq_analiz_g2.py --ek
```

Veri değişirse (`python src/simulasyon.py` farklı parametrelerle) bu dosyadaki tablolar ve yorumlardaki sayılar betiğin yeni çıktısından güncellenir; başlıktaki veri commit'i de değişir.
