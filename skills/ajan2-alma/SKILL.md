---
name: ajan2-alma
description: Ajan 2'nin (analiz) ilk aşaması. Ajan 1'in 19 sütunlu rakip fiyat CSV'sini docs/mesaj-bicimi.md sözleşmesine göre kontrol eder; eksik, bozuk, gelecek tarihli ya da 72 saatten eski girdiyi gerekçeli red zarfıyla Ajan 1'e geri gönderir. Ajan 1'den yeni rakip tablosu geldiğinde kullan.
---

# ajan2-alma: Rakip fiyat tablosunu alma ve kontrol (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Sözleşme:** `docs/mesaj-bicimi.md` (#112) · **Sonraki aşama:** `ajan2-isleme`

## Girdiler

| Girdi | Dosya |
|---|---|
| Ajan 1 rakip tablosu (19 sütun) | Ajan 1 teslimi; test için `data/ornek-ajan1.csv` |
| Alan tanımları | `docs/ajan1-cikti-semasi.md`, `docs/mesaj-bicimi.md` |
| Web fiyatlı ürün listesi | `data/urun-listesi-web.csv` |
| Referans zamanı | Alma anı (Türkiye saati). Test ve tekrar için `--referans` ile sabitlenir. |

## Kontroller (`src/ajan2_analiz.py` → `alma()`)

1. Başlık 19 sütun, sözleşme sırasıyla; en az bir satır var. Değilse `sorunlu_alanlar = ["girdi"]`.
2. Zorunlu alanlar dolu (`birim_miktar`, `indirimli_fiyat`, `elendi` isteğe bağlı).
3. Değer kümeleri: `eslesme_yontemi = benzer`, `eslesme_guveni`, `fiyat_turu`, `kdv_dahil`, `para_birimi = TRY`, `stok_durumu`, `rakip_site` (kurumsal ad listesi).
4. `bizim_urun` ve `kategori` ürün listesinde birebir var.
5. Fiyatlar pozitif, nokta ve iki ondalık. `indirimli_fiyat` doluysa listeden küçük ve `fiyat_turu ≠ liste`.
6. **72 saat kuralı:** her satırda `0 ≤ referans − cekilme_zamani ≤ 72 saat`, saat dilimi `+03:00`. Tam 72 saat geçerli; gelecek tarih ve bozuk tarih geçersiz.

Tek bir satır bile düşerse **girdinin tamamı** reddedilir. Red zarfı (`durum = red`, `hedef_ajan = ajan1`) her hatalı alanı `satir[<n>].<alan>` yoluyla listeler (başlık satır 1). Red durumunda analiz yapılmaz, eski çıktı dosyası silinir.

## Ne zaman üretmez

- Girdide kişisel veri (yorum, kullanıcı adı, bireysel satıcı) görülürse: durur, Ajan 1'e ve PM'e bildirir.
- Red sonrası "yine de analiz et" isteği: reddeder; Ajan 1'in düzeltilmiş teslimi beklenir.

## Nasıl çalıştırılır

Ajana: "ajan2-alma skill'ini kullanarak Ajan 1'in tablosunu kontrol et."
Elle (alma + işleme + teslim tek komutta, red olursa 2 ile çıkar):

```
python src/ajan2_analiz.py --girdi <ajan1.csv>
```

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 1. adımından, #115 için Claude (Claude Code) ile ayrıldı; Tuğba Tuana Kaygısız onayladı.
