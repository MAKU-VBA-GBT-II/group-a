---
name: ajan3-alma
description: Ajan 3'ün (denetim) ilk aşaması. Ajan 2'nin JSON çıktısını, onay zarfını ve Ajan 1'in rakip CSV'sini alıp denetlenebilir olduklarını kontrol eder; bayat veya izlenemeyen girdiyi gerekçeli red ile geri gönderir. Denetime başlarken kullan.
---

# ajan3-alma: girdi kontrolü (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Sonraki aşama:** `ajan3-isleme`

## Girdiler

`--girdi` (Ajan 2 JSON), `--zarf` (Ajan 2 onay zarfı), `--ajan1` (Ajan 2'nin kullandığı 19 sütunlu CSV). Biçim: `docs/mesaj-bicimi.md`.

## Kontroller (`src/ajan3_denetim.py` → `alma()`)

1. Ajan 1 tablosu okunur ve denetimde kullanılan sütunlar vardır.
2. Her satırda `0 ≤ referans − cekilme_zamani ≤ 72 saat`.
3. Fiyatlar sonlu ve pozitif; indirimli fiyat listeden küçük; `ham_fiyat_metni` karşılaştırma fiyatına eşit; `para_birimi = TRY`.
4. `urun_url` https ve alan adı `rakip_site`'ye ait (sentetik satırda `<ad>.example` kabul).
5. Ajan 2 zarfı `onay` ve `hedef_ajan = ajan3`.
6. Ajan 2 JSON'u okunur, `NaN`/`Infinity` içermez, zorunlu alanlar tamdır; `veri_turu` CSV'deki `arac` ile uyumludur.

1–4 düşerse red `ajan1`'e, 5–6 düşerse `ajan2`'ye gider. İkisi de hatalıysa önce `ajan1`.

## Takıma açık sorular (PR #117 incelemesi)

Bu üç kural sözleşmede henüz yazmıyor; cevap gelene kadar yukarıdaki gibi uygulanır: Ajan 3'ün CSV'yi girdi olarak alması, 72 saatin denetimde de geçerli olması, `ajan1` önceliği.

`--referans` yalnız sentetik test girdisinde kullanılır; gerçek veride denetim anı alınır.
