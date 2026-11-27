---
name: ajan2-alma
description: Ajan 2'nin (analiz) ilk aşaması. Ajan 1'in 19 sütunlu rakip fiyat CSV'sini docs/mesaj-bicimi.md sözleşmesine göre kontrol eder; eksik, bozuk, gelecek tarihli ya da 72 saatten eski girdiyi gerekçeli red zarfıyla Ajan 1'e geri gönderir. Ajan 1'den yeni rakip tablosu geldiğinde kullan.
---

# ajan2-alma: Rakip fiyat tablosunu alma ve kontrol (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Sözleşme:** `docs/mesaj-bicimi.md` (#112) · **Ajan 1 Issue'su:** #114 · **Sonraki aşama:** `ajan2-isleme`

## Girdiler

| Girdi | Dosya |
|---|---|
| Ajan 1 rakip tablosu (19 sütun) | Ajan 1 teslimi (`data/` altında); test için `data/ornek-ajan1.csv` |
| Alan tanımları | `docs/ajan1-cikti-semasi.md`, `docs/mesaj-bicimi.md` |
| Web fiyatlı ürün listesi | `data/urun-listesi-web.csv` |
| Referans zamanı | Alma anı (Türkiye saati). `--referans` yalnız tüm satırları `sentetik-fixture` olan test girdisinde kabul edilir; gerçek veride bayatlık kontrolü aşılamaz. |

## Kontroller (`src/ajan2_analiz.py` → `alma()`)

Elenmiş (`elendi` dolu) satırlar da bütün kontrollerden geçer; elenmiş olmak bozuk veriyi kabul ettirmez.

1. **Dosya:** UTF-8 okunabilir, başlık 19 sütun ve sözleşme sırasında, en az bir satır var. Değilse `sorunlu_alanlar = ["girdi"]`.
2. **Zorunlu alanlar dolu.** İsteğe bağlı olanlar: `birim_miktar`, `indirimli_fiyat`, `elendi`.
3. **Değer kümeleri:** `eslesme_yontemi = benzer`; `eslesme_guveni` `yuksek|orta|dusuk`; `fiyat_turu` `liste|indirimli|kampanya`; `kdv_dahil` `evet|hayir`; `para_birimi = TRY`; `stok_durumu` `var|yok|bilinmiyor`; `rakip_site` kurumsal ad listesinde (MediaMarkt, Gratis, D&R, Koçtaş, IKEA, Koton).
   - Sözleşmede `para_birimi` yalnız `TRY` olabilir. TL dışı satır elenerek değil, red ile döner.
4. **Ürün:** `bizim_urun` ve `kategori`, ürün listesinde birebir aynı çift olarak var.
5. **Fiyat:** `liste_fiyati` ve `indirimli_fiyat` sonlu (`NaN`, `Infinity` değil), pozitif, nokta ve tam iki ondalık. `indirimli_fiyat` doluysa listeden küçük ve `fiyat_turu ≠ liste`.
6. **Fiyat izi:** `ham_fiyat_metni`'nden ayrıştırılan sayı karşılaştırma fiyatına eşit (varsa `indirimli_fiyat`, yoksa `liste_fiyati`). Örnek: `₺1.299,90` → `1299.90`.
7. **Adresler:** `urun_url` bir `https` ürün sayfası; arama sayfası (`/search`, `q=`, `query=`) değil ve alan adı `rakip_site` ile uyumlu (ör. IKEA → `*.ikea.*`, D&R → `*.dr.*`). `bulma_yolu` `<https adresi> s.<n>` biçiminde.
8. **Eleme gerekçesi:** `elendi` boş ya da şu değerlerden biri: `fiyat bandı dışı`, `çoklu paket`, `ikinci el`, `stok yok`, `TL dışı`.
9. **72 saat kuralı:** Her satırda `0 ≤ referans − cekilme_zamani ≤ 72 saat` ve saat dilimi `+03:00` olmalı. Tam 72 saat geçerli; gelecek tarih, saat dilimsiz ya da bozuk tarih geçersiz.

Tek bir satır bile düşerse **girdinin tamamı** reddedilir. Red zarfında `durum = red` ve `hedef_ajan = ajan1` yazar; her hatalı alan `satir[<n>].<alan>` yoluyla listelenir (başlık satır 1). Red durumunda analiz yapılmaz, varsa eski çıktı dosyası silinir ve betik 2 koduyla çıkar.

## Kişisel veri (elle kontrol)

Betik kişisel veriyi otomatik tanımaz. Ajan, çalıştırmadan önce `rakip_urun_adi`, `urun_url` ve `rakip_site` alanlarına göz atar. Yorum, kullanıcı adı ya da bireysel satıcı adı görürse durur, Ajan 1'e (#114) ve PM'e bildirir.

## Red sonrası

1. `data/ajan2-zarf.json`'daki red zarfını, hangi kontrolün düştüğüyle birlikte #114'e yorum olarak yaz.
2. Ajan 1'in düzeltilmiş teslimini bekle. "Yine de analiz et" isteğini reddet.

## Nasıl çalıştırılır

Ajana: "ajan2-alma skill'ini kullanarak Ajan 1'in tablosunu kontrol et."

Elle çalıştırmada betik üç aşamayı sırayla koşar; alma reddederse sonraki aşamalar çalışmaz:

```
python src/ajan2_analiz.py --girdi data/<ajan1-tablosu>.csv
```

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 1. adımından, #115 için Claude (Claude Code) ile ayrıldı ve sözleşmenin tüm alma kontrolleriyle tamamlandı; Tuğba Tuana Kaygısız'ın incelemesine sunuldu.
