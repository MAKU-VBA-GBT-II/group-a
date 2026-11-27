---
name: ajan2-isleme
description: Ajan 2'nin (analiz) ikinci aşaması. Kontrolden geçen rakip satırlarını web fiyatlı sentetik siparişlerle birleştirir; ürün başına rakip medyanı, fiyat farkı, satış adedi, ciro, ürünler arası Pearson ilişkisi ve kural tabanlı kampanya önerisi üretir. Rakip tablosu alındıktan sonra analiz için kullan.
---

# ajan2-isleme: Rakip fiyatı × sipariş analizi (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Önceki aşama:** `ajan2-alma` · **Sonraki:** `ajan2-teslim`

Uydurma sayı yazılmaz: her sayı bir dosyadan ya da betik hesabından gelir ve `kaynaklar` alanında izlenir.

## Girdiler

| Girdi | Dosya |
|---|---|
| Kontrol edilmiş rakip satırları | `ajan2-alma` çıktısı |
| Eşleşme ve eleme kuralları | `docs/eslesme-tanimlari.md` |
| Web fiyatlı ürün listesi | `data/urun-listesi-web.csv` |
| Web fiyatlı sentetik siparişler | `data/siparisler-web.csv` (MD5 `628b4351…`, `src/simulasyon.py --urun_listesi data/urun-listesi-web.csv --cikti data/siparisler-web.csv`) |

## Hesaplar (`src/ajan2_analiz.py` → `isleme()`)

1. **Eleme (satır silinmez):** Ajan 1'in `elendi` gerekçesi korunur. Ajan 2 ayrıca karşılaştırma fiyatı (varsa `indirimli_fiyat`, yoksa `liste_fiyati`) < 0,3x veya > 3x liste fiyatımız ise `fiyat bandı dışı`, `stok_durumu = yok` ise `stok yok`, `kdv_dahil ≠ evet` ise `KDV temeli karşılaştırılamaz` sayar.
   - **Saklama Kabı Seti istisnası:** `çoklu paket` gerekçesi bu üründe yok sayılır (set olması elenme sebebi değildir; tekli kap Ajan 1'de elenir).
   - Stok/KDV nedeniyle Ajan 2'nin çıkardığı satırların hangi sayaca yazılacağı PR #117'de soruldu. Cevaba kadar `elenen_rakip_sayisi`'na sayılır (`SAYILMAYAN_SAYAC` sabiti).
2. **Rakip medyanı:** Elenmeyen satırların karşılaştırma fiyatlarının medyanı; çift gözlemde ortadaki ikisinin ortalaması; gözlem yoksa `null`.
3. **Fiyat farkı:** `100 × (bizim − medyan) / medyan`. Pozitif = bizim fiyat yüksek.
4. **Satış:** Sipariş dönemindeki `Teslim Edildi` satırlarının `adet` ve `toplam_tutar` toplamı (iade/iptal hariç).
5. **İlişki:** Fiyat farkı tanımlı ürünler üzerinden fark–adet ve fark–ciro Pearson katsayıları; ikiden az ürün ya da sıfır varyansta `null`. Ara hesap yuvarlanmaz; JSON'da para/yüzde 2, korelasyon 6 ondalık (eşit yarıda çifte).
6. **Öneri (kural tabanlı):**
   - Medyan yok → `veri_topla`.
   - **Masa Lambası** (karar 5, 399 TL liste fiyatı, 1.197 TL üst bant, yanlı örneklem) → her durumda `veri_topla`, gerekçede sınırlama yazılır.
   - Fark > %10 → `kampanya_test_et`; diğer durumlar → `fiyati_koru`.
   - Maliyet verisi olmadığı için `kar_durumu = maliyet_eksik`; kâr iddiası ya da otomatik onay verilmez.

## Bilinen sınırlamalar

- Sipariş verisi simülasyondur; Pearson ilişkisi simülasyon kurgusundan gelir, nedensellik ya da gerçek satış etkisi çıkarılmaz.
- Spor Ayakkabı ve Kahve Makinesi eski liste fiyatında (`docs/eslesme-tanimlari.md`).
- Eşleşme yalnız `benzer`; `birebir` ve ml başı fiyat sonraki haftalara.

## Nasıl çalıştırılır

Ajana: "ajan2-isleme skill'ini kullanarak alınan rakip tablosunu siparişlerle birleştir ve öneri üret."
Elle: `python src/ajan2_analiz.py --girdi <ajan1.csv>` (`--baslangic/--bitis` ile sipariş dönemi daraltılabilir).

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 2.–5. adımlarından, #115 için Claude (Claude Code) ile yazıldı; Tuğba Tuana Kaygısız'ın incelemesine sunuldu.
