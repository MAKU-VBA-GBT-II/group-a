---
name: ajan3-isleme
description: Ajan 3'ün (denetim) ikinci aşaması. Ajan 2 çıktısındaki bütün sayıları ham dosyalardan bağımsız olarak yeniden hesaplar, kaynak kayıtlarını denetler ve önerilen fiyat ile maliyet verilmişse eylem uyumunu ve kâr eşiğini uygular. ajan3-alma geçtikten sonra kullan.
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
| Eylem `fiyati_koru` ve fiyat web liste fiyatına eşit değil | Red → `ajan2` |
| Eylem `kampanya_test_et` ve fiyat web liste fiyatından düşük değil | Red → `ajan2` |
| Gerçek veride onaylanacak ürün için geçerli canlı kontrol kaydı 3 farklı rakip sayfasından (medyana giren sayfa azsa hepsinden) az | Beklemede |
| Fiyat dosyası yok/boş, ürünün maliyeti yok ya da maliyet dosyasında geçersiz satır | Beklemede |
| Listedeki bir ürünün Ajan 2 eylemi `veri_topla` (ör. Masa Lambası), kâr eşiğin üstünde olsa da | Beklemede |
| Listedeki bütün ürünler geçti | Onay (yalnız listelenen ürünler); kalan ürünler nihai raporda `karara_baglanmayan_urunler` altında ve zarf gerekçesinde |

Tutar biçimi: nokta ondalık, en çok iki hane. Ürün fiyat ve maliyet dosyasında tek satır. Zaman saat dilimli ISO 8601.

Fiyat ve maliyet kayıtlarının yaşı kodla denetlenmiyor (bilinen sınırlama): **gerçek veride elle bakılır**; eski kayıtla onay komutu çalıştırılmaz.

## Canlı fiyat doğrulaması (kontrol elle, kayıt kodda denetlenir)

Gerçek Ajan 1 verisinde onay komutundan **önce**: denetlenen her ürün için medyana giren en az 3 farklı rakip satırının (3'ten azsa hepsinin) `urun_url` adresini tarayıcıda aç ve görünen fiyatı `runs/ajan3/` altında bir CSV'ye yaz: `urun,urun_url,sayfa_fiyati_tl,kaynak,uretim_zamani` (`uretim_zamani` = kontrol anı; `kaynak` = kontrolün nasıl yapıldığı). Dosyayı `--canli_kontrol` ile ver. Sayfayı açmadan kayıt yazılmaz.

- Geçerli kayıt: adres eşleşiyor, kontrol çekimden sonra ve son 72 saat içinde.
- Sayfada iki fiyat varsa koşulsuz (herkesin ödediği) fiyat yazılır; kart ya da üyelik fiyatı yazılmaz.
- Sayfa fiyatı CSV'den farklıysa red → `ajan1`. Satır `kampanya` ise gerekçe, kampanyanın bitmiş olabileceğini ve Ajan 1'in yeniden toplaması gerektiğini de yazar; bitiş tarihleri Ajan 1 raporundaki `kampanya_bitisleri` listesindedir.
- Onaylanacak bir ürünün geçerli kayıtlı sayfa sayısı bunun altındaysa ya da dosyada geçersiz satır varsa beklemede. Aynı sayfa bir kez sayılır.

Kod sayfaya istek atmaz; kaydın doğruluğu kontrolü yapanın sorumluluğundadır. Sentetik `.example` adreslerine istek atılmaz.

Kampanya eşiği gibi Ajan 2'nin öneri kuralları yeniden denetlenmiyor.
