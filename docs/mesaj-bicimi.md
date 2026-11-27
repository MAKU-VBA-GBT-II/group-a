# Sepetix Analitik ortak mesaj sözleşmesi

Sürüm `1` · İnşa Haftası 1 · #112

Örnek CSV ve JSON sentetik test girdileridir. CSV ürün başlıklarındaki `[TEST]` ve `.example` adresleri fixture işaretidir. Bu adreslere istek atılmaz. JSON'da `veri_turu` değeri `sentetik_test` olur. Gerçek rakip girdisiyle yapılan analizde `web_ve_sentetik_siparis` kullanılır. Her iki durumda sipariş verisi simülasyondan gelir.

## Ajan 1 → Ajan 2 · CSV

Dosya UTF-8, virgülle ayrılmış, başlıklı ve satır başına bir rakip ürün kaydıdır. Mevcut [Ajan 1 çıktı şeması](ajan1-cikti-semasi.md) alan sırası, tipler, değer kümeleri ve yayımlama kontrolleri için geçerlidir.

| Sıra | Alan | Tip ve zorunluluk |
|---|---|---|
| 1–3 | `bizim_urun`, `kategori`, `rakip_urun_adi` | Zorunlu metin. İlk ikisi web fiyatlı ürün listesindeki ad ve kategoriyle birebir eşleşir. |
| 4–5 | `eslesme_yontemi`, `eslesme_guveni` | Zorunlu. Sırasıyla `benzer` ve `yuksek\|orta\|dusuk`. |
| 6–7 | `birim_miktar`, `ham_fiyat_metni` | Miktar ve birim içeren isteğe bağlı metin, ardından zorunlu görüntülenen fiyat metni. |
| 8–9 | `liste_fiyati`, `indirimli_fiyat` | Pozitif TRY, nokta ve iki ondalık. Liste zorunlu, indirim isteğe bağlı ve listeden küçük. |
| 10–13 | `fiyat_turu`, `kdv_dahil`, `para_birimi`, `stok_durumu` | Zorunlu. Sırasıyla `liste\|indirimli\|kampanya`, `evet\|hayir`, `TRY`, `var\|yok\|bilinmiyor`. |
| 14–16 | `rakip_site`, `urun_url`, `bulma_yolu` | Zorunlu metin. Kurumsal site adı, doğrudan ürün adresi, kategori adresi ve `s.<n>`. |
| 17–19 | `cekilme_zamani`, `arac`, `elendi` | Zorunlu ISO 8601 zaman damgası (`+03:00`), zorunlu araç metni, isteğe bağlı eleme gerekçesi. |

Her sayının mantıksal `kaynak` ve `uretim_zamani` karşılığı CSV içinde taşınır. Fiyatlar ve sayısal miktar için `kaynak = urun_url`. Sayfa numarası için kaynak `bulma_yolu` içindeki kategori adresidir. Her ikisinde de `uretim_zamani = cekilme_zamani`. Ayrıştırılan fiyatın izi `ham_fiyat_metni` ile korunur, `arac` kaydı toplama oturumuyla eşleştirilir. CSV'ye yeni sütun veya açıklama satırı eklenmez.

Ajan 2, alma anında tek ve saat dilimi içeren bir referans zamanı alır. Testler bu zamanı bağımsız olarak verir. Her satır için `0 ≤ referans_zamani − cekilme_zamani ≤ 72 saat` olmalıdır. Tam 72 saat geçerlidir. Gelecek tarih, bozuk tarih, eksik zorunlu alan veya 72 saati aşan herhangi bir satır tüm girdiyi Ajan 1'e geri gönderir. Örneklerin sabit test referansı `2026-11-29T18:00:00+03:00` değeridir. Üretimde alma anı kullanılır.

Eşleşme, eleme ve birim kuralları [eşleşme tanımlarında](eslesme-tanimlari.md) yer alır. Elenen satırlar CSV'de kalır. Masa Lambası için 399 TL web liste fiyatı ve 1.197 TL üst bant nedeniyle örneklem yanlılığı raporlanır. Saklama Kabı Seti set olduğu için elenmez, tekli kap elenir. KDV temeli karşılaştırılamayan ve stokta olmadığı bilinen satırlar medyana katılmaz ve gerekçeleriyle sayılır. KDV dönüşümü ancak kaynaklı oran varsa yapılabilir. Sentetik örnekte bütün fiyatlar KDV dâhildir.

## Ajan 2 → Ajan 3 · JSON

UTF-8 JSON nesnesi. Aşağıdaki alanların tamamı zorunludur. `null` yalnız belirtilen yerlerde kullanılır. Sayılar sonlu JSON sayılarıdır. Para TRY, yüzdeler yüzde puanı ölçeğindedir (ör. `12.5` = %12,5).

| Üst alan | Tip ve anlamı |
|---|---|
| `surum`, `veri_turu`, `para_birimi` | Metin. Sırasıyla `"1"`, `sentetik_test\|web_ve_sentetik_siparis` ve `TRY`. |
| `uretim_zamani` | ISO 8601, saat dilimli. Ajan 2 hesaplamasının bitişi, fixture'da sabit test saati. Çıktıdaki türetilmiş sayıların üretim zamanı budur. |
| `siparis_donemi` | `baslangic`, `bitis` içeren nesne. ISO tarih, iki uç dâhil. |
| `urunler` | Ürün başına tek kayıt içeren, boş olmayan dizi. Ürün kümesi Ajan 1'den gelir. |
| `iliskiler` | `urun_sayisi` (tam sayı), `pearson_fark_adet`, `pearson_fark_ciro` (sayı veya `null`) ve `kaynaklar` dizisi. |

| Ürün alanı | Tip ve hesaplama |
|---|---|
| `urun`, `kategori` | Metin. Ajan 1 tablosu, web fiyatlı ürün listesi ve sipariş verisiyle birebir. |
| `bizim_liste_fiyati` | Sayı. Birleştirmede kullanılan web fiyatlı ürün listesindeki fiyat. |
| `rakip_medyan_fiyati` | Sayı veya `null`. Elenmeyen satırlarda indirimli fiyat varsa o, yoksa liste fiyatı kullanılır. Çift gözlemde ortadaki iki değerin ortalaması alınır. Gözlem yoksa `null`. |
| `fiyat_farki_yuzde` | Sayı veya `null`. `100 × (bizim_liste_fiyati − rakip_medyan_fiyati) / rakip_medyan_fiyati`. Pozitif değer bizim fiyatın daha yüksek olduğunu gösterir. Medyan yoksa `null`. |
| `kullanilan_rakip_sayisi`, `elenen_rakip_sayisi` | Sıfır veya pozitif tam sayı. Geçerli ve elenen CSV satırlarının ayrı adetleri. Toplamları ürüne ait tüm giriş satırlarıdır. |
| `satis_adedi`, `ciro` | Sırasıyla sıfır veya pozitif tam sayı ve sayı. Dönemdeki `Teslim Edildi` satırlarının `adet` ve `toplam_tutar` toplamı. İade/iptal hariç. Eşleşen teslimat yoksa sıfır. |
| `oneri` | `eylem`, `gerekce`, `kar_durumu` içeren nesne, tamamı metin. Eylem `fiyati_koru\|kampanya_test_et\|veri_topla`. Gerekçe ölçüme ve sınırlamalarına dayanır. Maliyet verisi yoksa `kar_durumu = maliyet_eksik`, otomatik onay veya kâr iddiası verilmez. Doğrulanmış ve kaynaklandırılmış maliyet varsa `denetim_bekliyor`; kâr kararını Ajan 3 verir. |
| `kaynaklar` | Dolu dizi. Her kayıt aşağıdaki kaynak biçimini izler. |

Pearson katsayıları ürün düzeyinde, fiyat farkı tanımlı kayıtlar üzerinden ayrı ayrı fiyat farkı–adet ve fiyat farkı–ciro için hesaplanır. `urun_sayisi` bu gözlemlerin sayısıdır. İkiden az ürün veya sıfır varyans varsa ilgili katsayı `null`. Ara hesaplar yuvarlanmaz. JSON'da para, medyan ve yüzde iki, korelasyon altı ondalığa yuvarlanır (eşit yarıda en yakın çift). Bu ilişki sentetik satış verisine aittir. Nedensellik veya gerçek satış etkisi çıkarılmaz.

### Sayıların kaynağı ve zamanı

Her `kaynaklar` elemanı dört zorunlu alan taşır. `alanlar` (dolu metin dizisi) sayısal çıktı alanlarını, `kaynak` (metin) izlenebilir repo dosyasını, JSON alan yolunu ya da ürün adresini, `secim` (metin) ilgili satır veya hesap filtresini, `uretim_zamani` (saat dilimli ISO 8601) kaynak verinin üretim/çekim anını gösterir.

- Rakip satırı başına bir kaynak kaydı, elenmişse gerekçesiyle. URL ve zaman Ajan 1'den taşınır. Aynı ürün adresi tekrarlanırsa CSV satır numaraları `secim` alanında ayırt edilir.
- Liste fiyatı, sipariş ölçümleri ve ilişkiler için yakındaki `kaynaklar` alanı tam kapsam sağlar. Örnekte sürümlenmiş liste ve sipariş dosyası için kaydedildiği commit'in zamanı kullanıldı. Üretimde dosya üretim anı kaydedilir.
- Kâr için maliyet sağlanırsa denetçiye ayrı izlenebilir maliyet girdisi iletilir. Bu sürümde maliyet veya hedef indirim yüzdesi hesap çıktısının parçası değildir.

## Onay ve red zarfı

| Alan | Tip ve kural |
|---|---|
| `durum` | Zorunlu metin. `onay` veya `red`. |
| `hedef_ajan` | Zorunlu. `ajan1\|ajan2\|ajan3` veya `null`. Ajan 2 reddinde `ajan1`, Ajan 3 reddinde düzeltmeyi yapacak `ajan1` ya da `ajan2`. Başarılı Ajan 2 devrinde `ajan3`, nihai onayda `null`. |
| `gerekce` | Zorunlu, boş olmayan metin. Red durumunda hangi kontrolün düştüğünü açıklamalı. |
| `sorunlu_alanlar` | Zorunlu metin dizisi. Red için en az bir alan yolu. CSV satır yolu `satir[2].cekilme_zamani` (başlık satır 1), JSON örneği `urunler[0].rakip_medyan_fiyati` (dizi sıfır tabanlı). Dosyanın tamamı okunamıyorsa `girdi`. Onayda boş dizi. |

Başarılı aktarımda çıktı dosyası ve onay zarfı ayrı taşınabilir. Red durumunda hatalı çıktı bir sonraki aşamaya aktarılmaz.

```json
{"durum":"red","hedef_ajan":"ajan1","gerekce":"İkinci satırdaki fiyat verisi 72 saatten eski.","sorunlu_alanlar":["satir[2].cekilme_zamani"]}
```

## Test ve üretim kaydı

`python3 -m unittest discover -s tests -p 'test_mesaj_bicimi.py'`

Üretim aracı Codex. Prompt özeti: Duyuru 11'i ve mevcut ajan kurallarını okuyarak 19 sütunu koruyan sözleşmeyi, sentetik CSV/JSON örneklerini ve tekrarlanabilir uyum testlerini hazırla.
