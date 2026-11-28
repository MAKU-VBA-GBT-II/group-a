---
name: ajan3-isleme
description: Ajan 3'ün (denetim) ikinci aşaması. Ajan 2 çıktısındaki bütün sayıları ham dosyalardan bağımsız olarak yeniden hesaplar, kaynak kayıtlarını denetler ve önerilen fiyat ile maliyet verilmişse kâr eşiğini uygular. ajan3-alma geçtikten sonra kullan.
---

# ajan3-isleme: bağımsız doğrulama (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Önceki:** `ajan3-alma` · **Sonraki:** `ajan3-teslim`

## Kontroller (`src/ajan3_denetim.py` → `isleme()`)

`ajan2_analiz` modülü kullanılmaz; hesap `data/urun-listesi-web.csv`, `data/siparisler-web.csv` ve Ajan 1 CSV'sinden yeniden yapılır.

- Ürün kümesi ve kategoriler.
- Liste fiyatı, rakip medyanı, fiyat farkı, kullanılan/elenen sayısı, satış adedi, ciro.
- Pearson fark–adet ve fark–ciro, gözlem sayısı.
- Her CSV satırı için adresi, zamanı ve satır numarası uyan kaynak kaydı; liste ve sipariş dosyası için zamanlı kayıt.
- Eylem izinli değerlerden biri (medyan yoksa yalnız `veri_topla`); gerekçe boş değil.
- `kar_durumu = maliyet_eksik`; `denetim_bekliyor` yalnız o ürün için geçerli maliyet verilmişse kabul edilir.

Medyana girmeyen satır: `elendi` dolu (Saklama Kabı Seti'nde `çoklu paket` hariç), `stok_durumu = yok`, `kdv_dahil ≠ evet` ya da işaretlenmemiş olsa da karşılaştırma fiyatı web liste fiyatının 0,3–3 katı dışında (eşleşme kuralı 2; sınırlar dahil). Hepsi "elenen" sayılır.

## Kâr eşiği (`girdi_tablosu()`, `kar_denetimi()`)

Kaynak ve hesap kontrolleri geçtikten sonra yalnız `--fiyat` dosyasındaki ürünler denetlenir. Birim kâr = önerilen fiyat − birim maliyet; **0 TL'nin üstünde** olmalı. Kampanya cümlesinden indirim yüzdesi türetilmez.

| Durum | Sonuç |
|---|---|
| Kâr ≤ 0, geçersiz fiyat satırı ya da veride olmayan ürün | Red → `ajan2`, bütün alan yolları |
| Fiyat dosyası yok/boş, ürünün maliyeti yok ya da maliyet dosyasında geçersiz satır | Beklemede |
| Listedeki bir ürünün Ajan 2 eylemi `veri_topla` (ör. Masa Lambası), kâr eşiğin üstünde olsa da | Beklemede |
| Listedeki bütün ürünler geçti | Onay (yalnız listelenen ürünler) |

Tutar biçimi: nokta ondalık, en çok iki hane. Ürün her dosyada tek satır. Zaman saat dilimli ISO 8601.

## Canlı fiyat doğrulaması (elle, kodda yok)

Gerçek Ajan 1 verisinde onay komutundan **önce**: denetlenen her ürünün en az bir rakip satırının `urun_url` adresini tarayıcıda aç, görünen fiyatı CSV ile karşılaştır, adres + saat + iki fiyatı `runs/ajan3/` altına yaz. Uyuşmazsa onay komutunu çalıştırma; Ajan 1'e red yaz. Sentetik `.example` adreslerine istek atılmaz.

Kampanya eşiği gibi Ajan 2'nin öneri kuralları yeniden denetlenmiyor.
