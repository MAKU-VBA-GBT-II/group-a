---
name: ajan3-alma
description: Ajan 3'ün (denetim) ilk aşaması. Ajan 2'nin JSON çıktısını, onay zarfını ve Ajan 1'in rakip CSV'sini alıp denetlenebilir olduklarını kontrol eder; bayat veya izlenemeyen girdiyi gerekçeli red ile geri gönderir. Denetime başlarken kullan.
---

# ajan3-alma: girdi kontrolü (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Sonraki aşama:** `ajan3-isleme`

## Girdiler

| Argüman | İçerik |
|---|---|
| `--girdi`, `--zarf` | Ajan 2 JSON'u ve onay zarfı |
| `--ajan1`, `--ajan1_md5` | Ajan 2'nin kullandığı 19 sütunlu CSV'nin yolu ve devirde bildirilen MD5'i (ikisi de zorunlu) |
| `--fiyat` (isteğe bağlı) | `urun,onerilen_fiyat_tl,kaynak,uretim_zamani` |
| `--maliyet` (isteğe bağlı) | `urun,birim_maliyet_tl,kaynak,uretim_zamani` |
| `--canli_kontrol` (gerçek veride onay için) | `urun,urun_url,sayfa_fiyati_tl,kaynak,uretim_zamani`; elle yapılan sayfa kontrolü |

Biçim: `docs/mesaj-bicimi.md`. Fiyat dosyasının sütunları sözleşmede henüz yazmıyor; bu skill'deki biçim geçerlidir. Fiyat ve maliyet aynı birim ve KDV esasında olmalı (kod bunu denetleyemez, dosyayı hazırlayan kontrol eder). Maliyet uydurulmaz; deneme verisinin kaynağı `sentetik_test:...` diye yazılır.

## Kontroller (`src/ajan3_denetim.py` → `alma()`)

1. Ajan 1 tablosu okunur, MD5'i `--ajan1_md5` ile aynıdır, denetimde kullanılan sütunlar vardır; gerçek veride dosya repo içindedir.
2. Her satırda `0 ≤ referans − cekilme_zamani ≤ 72 saat`.
3. Fiyatlar sonlu ve pozitif; indirimli fiyat listeden küçük; `ham_fiyat_metni` karşılaştırma fiyatına eşit; `para_birimi = TRY`.
4. `urun_url` https ve alan adı `rakip_site`'ye ait (sentetik satırda `<ad>.example` kabul).
5. Ajan 2 zarfı `onay` ve `hedef_ajan = ajan3`.
6. `--canli_kontrol` verilmişse geçerli kayıtlardaki sayfa fiyatı CSV'deki karşılaştırma fiyatına eşittir.
7. Ajan 2 JSON'u okunur, `NaN`/`Infinity` içermez, zorunlu alanlar tamdır; `veri_turu` CSV'deki `arac` ile uyumludur.

1–4 ve 6 düşerse red `ajan1`'e, 5 ve 7 düşerse `ajan2`'ye gider. İkisi de hatalıysa önce `ajan1`; Ajan 2 kontrolleri kaynak düzeltilince yapılır.

`--fiyat`, `--maliyet` ya da `--canli_kontrol` ile verilen dosya bulunamazsa bu bir kullanım hatasıdır (çıkış 1), "eksik veri" sayılmaz.

`--referans` yalnız sentetik test girdisinde kullanılır; gerçek veride denetim anı alınır.
