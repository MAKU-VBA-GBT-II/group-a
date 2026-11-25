---
name: ajan2-analiz
description: Grup A çok ajanlı programında Ajan 2'nin (analiz) işi. Ajan 1'in rakip fiyat tablosunu alıp kontrol eder, "benzer" eşleşme kurallarını uygular, web fiyatlı sentetik sipariş verisini hazırlar ve fiyat/kampanya analizini Ajan 3'e devreder. Rakip fiyat verisi alınacağı, eşleşme tanımları güncelleneceği veya web fiyatlı veri üretileceği zaman kullan.
---

# ajan2-analiz: Rakip fiyatlarını sipariş verisiyle birleştirme (Ajan 2)

**Amaç:** Ajan 1'in topladığı rakip fiyatlarını, 25 ürünlük sentetik sipariş verimizle aynı ürün adı üzerinden birleştirmek; fiyat farkı ile satış ilişkisini hesaplamak ve fiyat/kampanya önerisi üretmek. Uydurma sayı yazılmaz: her sayı bir dosyadan ya da betik çıktısından gelir.

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #101 · **Ajan 1 şeması:** #96 · **Senaryo:** `docs/oneri.md` (Duyuru-10)

**Durum (25 Kasım 2026):** 1.–4. adımlar tanımlı ve kullanılabilir. 5. adımın (analiz kodu) betiği henüz yok, sonraki duyuruya kaldı; o zaman bu skill güncellenir.

## Girdiler

| Girdi | Dosya | Sahibi |
|---|---|---|
| Rakip fiyat tablosu (19 sütun) | Biçim: `docs/ajan1-cikti-semasi.md` | Ajan 1 (Hilal) |
| Eşleşme tanımları ve eleme kuralları | `docs/eslesme-tanimlari.md` | Ajan 2 |
| Web fiyatlı ürün listesi | `data/urun-listesi-web.csv` (`kategori,urun,liste_fiyati`) | Ajan 2 |
| Web fiyatlı sipariş verisi | `data/siparisler-web.csv` (8.208 satır, MD5 `628b4351…`) | Ajan 2 (`src/simulasyon.py`) |
| Fiyat taraması (medyanlar) | `docs/fiyat-taramasi.md`, `data/web-fiyat-taramasi.csv` | Ajan 1 |

## Adımlar

1. **Alma kontrolü (Ajan 1'den gelen tablo):**
   - 19 sütun, `docs/ajan1-cikti-semasi.md`'deki sırayla; zorunlu alanlar dolu.
   - `bizim_urun` ve `kategori`, `data/urun-listesi-web.csv`'de birebir var.
   - `para_birimi` = `TRY`; `rakip_site` şemadaki kurumsal ad listesinde; satıcı adı ya da kişisel veri yok.
   - **Bayatlık eşiği:** `cekilme_zamani` alma anından **72 saatten** eskiyse tablo Ajan 1'e geri gönderilir.
   - Bir kontrol düşerse tablo alınmaz; sorun #96'ya yazılır.
2. **Eşleşme kurallarını uygula:** `docs/eslesme-tanimlari.md` ortak kuralları 1–7. Karşılaştırma fiyatı, varsa `indirimli_fiyat`, yoksa `liste_fiyati`.
   - Fiyat < 0,3x veya > 3x liste fiyatımız → `elendi = fiyat bandı dışı`.
   - Makul aralık dışı (0,4x–2,5x; Kitap 0,5x–2x) → elenmez, `eslesme_guveni = dusuk`.
   - Çoklu paket → `çoklu paket`, ikinci el → `ikinci el`.
   - **Satır silinmez.** Elenen satırlar analize girmez ama ürün başına sayıları raporlanır.
3. **Sipariş verisi:** Web fiyatlı veri şu komutla üretilir, MD5 `docs/veri-sozlugu.md` ile karşılaştırılır:
   `python src/simulasyon.py --urun_listesi data/urun-listesi-web.csv --cikti data/siparisler-web.csv`
   Varsayılan dosya `data/siparisler-g2.csv` (MD5 `1b7f765e…`) değiştirilmez.
4. **Liste fiyatı değişikliği:** Bir ürünün liste fiyatı değişirse `data/urun-listesi-web.csv`, eşleşme tablosundaki TL bantları, `data/siparisler-web.csv` ve MD5 birlikte güncellenir. Ajan 3 (Sema) testleri yeniden koşar ve `tests/test-log.md`'ye yazar.
5. **Analiz (sonraki duyuru, betik henüz yok):** Ürün başına rakip medyanı ile liste fiyatımız arasındaki fark, bu farkın satış adedi ve ciroyla ilişkisi, fiyat/kampanya önerisi. Çıktı Ajan 3'e devredilir.
6. **Kanıt:** #101'e commit hash ve dosyalarla yorum: `Üretim: ajan2-analiz skill'i ile, <araç>, prompt özeti: …`

## Bilinen sınırlamalar

- **Masa Lambası (karar 5, 25 Kasım):** Liste fiyatı 399 TL, IKEA medyanı 1.699 TL. IKEA satırlarının yaklaşık dörtte üçü otomatik bantta elenir; bu ürünün sonucu ihtiyatla yorumlanır.
- **Spor Ayakkabı, Kahve Makinesi:** Eski liste fiyatında; gerekçe `docs/eslesme-tanimlari.md` → Tablo.
- Eşleşme yalnızca "benzer"; `birebir` eşleşme ve kozmetikte ml başı fiyat sonraki haftalara bırakıldı.
- Sipariş verisi simülasyondur; satış ile fiyat arasındaki ilişki simülasyon kurgusundan gelir, gerçek müşteri davranışı gibi sunulmaz.

## Ne zaman üretmez (reddeder)

- Tabloda gerçek kişi verisi (yorum, kullanıcı adı, bireysel satıcı) varsa: durur, Ajan 1'e ve PM'e bildirir.
- Alma kontrolü düşerse ya da veri bayatsa: analize geçmez.
- İstenen sayı bir dosyada ya da betik çıktısında yoksa: tahmin etmez.
- Elenmiş satırları silme isteği: reddeder, işaretli bırakır.

## Kullanılan dosyalar

- **Okur:** Ajan 1 tablosu, `docs/ajan1-cikti-semasi.md`, `docs/eslesme-tanimlari.md`, `data/urun-listesi-web.csv`, `docs/fiyat-taramasi.md`
- **Yazar:** `docs/eslesme-tanimlari.md`, `data/urun-listesi-web.csv`, `data/siparisler-web.csv`
- **Çalıştırır:** `src/simulasyon.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana: "ajan2-analiz skill'ini kullanarak Ajan 1'in rakip fiyat tablosunu al, kontrol et ve eşleşme kurallarını uygula."

## Üretim kaydı

25 Kasım 2026: Bu skill Claude (Claude Code) ile taslaklandı, Tuğba Tuana Kaygısız gözden geçirip onayladı (#101). Önceki Ajan 2 işleri: eşleşme tanımları PR #100, simülasyon genişletmesi PR #102.
