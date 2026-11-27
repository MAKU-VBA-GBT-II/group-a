---
name: ajan2-isleme
description: Ajan 2'nin (analiz) ikinci aşaması. Kontrolden geçen rakip satırlarını web fiyatlı sentetik siparişlerle birleştirir; ürün başına rakip medyanı, fiyat farkı, satış adedi, ciro, ürünler arası Pearson ilişkisi ve kural tabanlı kampanya önerisi üretir. Rakip tablosu alındıktan sonra analiz için ya da liste fiyatı değiştiğinde kullan.
---

# ajan2-isleme: Rakip fiyatı × sipariş analizi (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Önceki aşama:** `ajan2-alma` · **Sonraki:** `ajan2-teslim`

Uydurma sayı yazılmaz. Her sayı bir dosyadan ya da betik hesabından gelir ve `kaynaklar` alanında izlenir.

## Girdiler

| Girdi | Dosya |
|---|---|
| Kontrol edilmiş rakip satırları | `ajan2-alma` çıktısı |
| Eşleşme ve eleme kuralları | `docs/eslesme-tanimlari.md` |
| Web fiyatlı ürün listesi | `data/urun-listesi-web.csv` (`kategori,urun,liste_fiyati`) |
| Web fiyatlı sentetik siparişler | `data/siparisler-web.csv` (8.208 satır, MD5 `628b4351…`) |

## Hesaplar (`src/ajan2_analiz.py` → `isleme()`)

1. **Ürün kümesi:** Ajan 1 tablosunda geçen ürünler, tabloda ilk görüldükleri sırayla. Rakip satırı olmayan ürün çıktıya girmez.
2. **Eleme (satır silinmez).** Bir satır şu durumlarda medyana girmez:
   - Ajan 1'in `elendi` gerekçesi varsa.
   - **Saklama Kabı Seti istisnası:** Bu üründe `çoklu paket` gerekçesi yok sayılır, çünkü ürün zaten bir set (eşleşme kuralı 5). Tekli kap Ajan 1'de elenir.
   - Karşılaştırma fiyatı (varsa `indirimli_fiyat`, yoksa `liste_fiyati`) liste fiyatımızın 0,3 katından düşük ya da 3 katından yüksekse: `fiyat bandı dışı`. Ajan 1 işaretlemediyse Ajan 2 yakalar.
   - `stok_durumu = yok` ise `stok yok`. `bilinmiyor` medyana girer.
   - `kdv_dahil = hayir` ise `KDV temeli karşılaştırılamaz`. Kaynaklı KDV oranı olmadan dönüşüm yapılmaz.
   - Medyandan çıkan her satır `elenen_rakip_sayisi`'na sayılır ve kaynak kaydının `secim` alanında gerekçesiyle görünür. Ajan 1'in işaretlemediği KDV satırlarının hangi sayaca yazılacağı PR #117'de soruldu; cevap farklı gelirse yalnız `SAYILMAYAN_SAYAC` sabiti değişir.
   - Makul aralık (0,4x–2,5x; Kitap 0,5x–2x) ve `eslesme_guveni` Ajan 1'in işaretidir. Ajan 2 değiştirmez; `dusuk` güvenli satırlar da medyana girer.
3. **Rakip medyanı:** Medyana giren fiyatların medyanı. Çift sayıda gözlemde ortadaki ikisinin ortalaması alınır, gözlem yoksa `null`.
4. **Fiyat farkı:** `100 × (bizim − medyan) / medyan`. Pozitif değer bizim fiyatın yüksek olduğunu gösterir. Medyan yoksa `null`.
5. **Satış:** Sipariş dönemindeki `Teslim Edildi` satırlarının `adet` ve `toplam_tutar` toplamı; iade ve iptal hariç. Dönem verilmezse verinin ilk ve son günü kullanılır (`--baslangic`, `--bitis`).
6. **İlişki:** Fiyat farkı tanımlı ürünler üzerinden fark–adet ve fark–ciro Pearson katsayıları. İkiden az ürün ya da sıfır varyans varsa `null`. Ara hesap yuvarlanmaz. JSON'da para, medyan ve yüzde iki, korelasyon altı ondalığa yuvarlanır (eşit yarıda çifte).
7. **Öneri (kural tabanlı):**
   - Medyan yok → `veri_topla`.
   - **Masa Lambası** → her durumda `veri_topla`. Gerekçeye karar 5 sınırlaması yazılır: liste fiyatı 399 TL, 1.197 TL üst bant, yanlı örneklem.
   - Fark %10'dan büyük → `kampanya_test_et`. Diğer durumlarda → `fiyati_koru`. %10 eşiği Ajan 2'nin kararıdır (`KAMPANYA_ESIGI`); değişirse bu skill ve testler birlikte güncellenir.
   - Maliyet verisi olmadığından `kar_durumu = maliyet_eksik`. Kâr iddiası ya da otomatik onay verilmez; kâr kararı Ajan 3'ündür.

## Sipariş verisi ve liste fiyatı değişikliği

- Web fiyatlı veri şu komutla üretilir. MD5'i `docs/veri-sozlugu.md` ile karşılaştırılır:
  `python src/simulasyon.py --urun_listesi data/urun-listesi-web.csv --cikti data/siparisler-web.csv`
  Varsayılan dosya `data/siparisler-g2.csv` (MD5 `1b7f765e…`) değiştirilmez.
- Bir ürünün liste fiyatı değişirse dört şey birlikte güncellenir: `data/urun-listesi-web.csv`, `docs/eslesme-tanimlari.md`'deki TL bantları, `data/siparisler-web.csv` ve MD5. Ajan 3 (Sema) testleri yeniden koşar ve `tests/test-log.md`'ye yazar. Masa Lambası'nın 399 TL'si karar 5 gereği bu teslimde değişmez.

## Bilinen sınırlamalar

- Sipariş verisi simülasyondur. Pearson ilişkisi simülasyon kurgusundan gelir; nedensellik ya da gerçek satış etkisi çıkarılmaz.
- Spor Ayakkabı ve Kahve Makinesi eski liste fiyatında (`docs/eslesme-tanimlari.md`).
- Eşleşme yalnız `benzer`. `birebir` eşleşme ve kozmetikte ml başı fiyat sonraki haftalara kaldı.

## Ne zaman üretmez

- Alma reddettiyse analiz yapılmaz.
- İstenen sayı bir dosyada ya da betik hesabında yoksa tahmin edilmez.
- Elenmiş satırları silme isteği reddedilir; satırlar işaretli kalır.

## Nasıl çalıştırılır

Ajana: "ajan2-isleme skill'ini kullanarak alınan rakip tablosunu siparişlerle birleştir ve öneri üret."
Elle: `python src/ajan2_analiz.py --girdi data/<ajan1-tablosu>.csv`

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 2.–5. adımlarından, #115 için Claude (Claude Code) ile yazıldı; Tuğba Tuana Kaygısız'ın incelemesine sunuldu.
