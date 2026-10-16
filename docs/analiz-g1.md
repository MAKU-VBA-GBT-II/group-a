# Analiz — Görev 1 (Sipariş verisi)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Tuğba Tuana Kaygısız · **Issue:** #14
**Veri:** `data/siparisler.csv` · **Şema:** `docs/veri-sozlugu-g1.md` · **Hesaplama:** `python src/dq_analiz.py`

> ⏳ **Taslak.** Bu dosyada şimdilik yalnızca metrik tanımları ve formüller var. Sayılar, yorumlar ve bulgular BE'nin "Veri hazır" yorumundan sonra (#13) `src/dq_analiz.py` çıktısıyla doldurulacak.

**Kullanılan veri:** `data/siparisler.csv` · commit `_____` · ___ satır · tarih aralığı ____ – ____

## Metrikler

| # | Metrik | Formül | Neyi ölçer |
|---|---|---|---|
| M1 | Toplam ciro | `Σ toplam_tutar` | Dönem boyunca elde edilen toplam satış geliri (TL) |
| M2 | Sipariş başına ortalama adet | `Σ adet / sipariş sayısı` | Müşterinin bir siparişte ortalama kaç ürün aldığı (sepet büyüklüğü) |
| M3 | Kategori bazlı ciro *(kırılım 1)* | kategoriye göre `Σ toplam_tutar`; pay = kategori cirosu / toplam ciro | Gelirin kategorilere dağılımı; hangi kategorinin işi taşıdığı |
| M4 | Haftalık ciro trendi *(kırılım 2)* | haftaya (pazartesi başlangıçlı) göre `Σ toplam_tutar` | Gelirin zaman içindeki değişimi; yükselen/düşen dönemler |
| M5 | Top-3 ürün | ürüne göre `Σ toplam_tutar`, büyükten küçüğe ilk 3; pay = ürün cirosu / toplam ciro | Ciroya en çok katkı veren ürünler ve gelirin ne kadar yoğunlaştığı |

### M1 — Toplam ciro

_Sonuç:_ ___

_Yorum:_ ___

### M2 — Sipariş başına ortalama adet

_Sonuç:_ ___

_Yorum:_ ___

### M3 — Kategori bazlı ciro

_Tablo `src/dq_analiz.py` çıktısından aktarılacak._

_Yorum:_ ___

### M4 — Haftalık ciro trendi

_Tablo `src/dq_analiz.py` çıktısından aktarılacak. İlk/son hafta kısmiyse en yüksek/en düşük hesabına katılmaz._

_Yorum:_ ___

### M5 — Ciroya en çok katkı veren 3 ürün

_Tablo `src/dq_analiz.py` çıktısından aktarılacak._

_Yorum:_ ___

## Bulgular

1. ___
2. ___
3. ___

**Eylem önerisi:** ___
