---
name: ajan3-teslim
description: Ajan 3'ün (denetim) son aşaması. Denetim sonucunu nihai rapor ve onay zarfı, red zarfı ya da beklemede ara raporu olarak yazar, çalışma izi bırakır ve Issue kanıt yorumunu hazırlar. Doğrulama bittikten sonra kullan.
---

# ajan3-teslim: sonuç ve kanıt (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Önceki:** `ajan3-isleme`

## Sonuçlar

| Sonuç | Çıkış | Yazılan |
|---|---|---|
| Onay | 0 | `--nihai_rapor` (ürün başına fiyat, maliyet, kâr, eşik, kaynak, karar, gerekçe) ve `--cikis_zarf`: `durum = onay`, `hedef_ajan = null` |
| Red | 2 | `--cikis_zarf`: `durum = red`, `hedef_ajan = ajan1` veya `ajan2`, gerekçe, alan yolları |
| Beklemede | 3 | `--rapor`: bekleme nedeni ve yapılmayan kontroller. **Zarf yazılmaz.** |
| Kullanım hatası (verilen dosya bulunamadı dahil) | 1 | Hiçbir sonuç; eski rapor ve zarf silinmiş olur (argümanlar ayrıştırılabildiyse) |

Her onay, red ve beklemede çalıştırması `runs/ajan3/` altına komut, referans zamanı ve MD5'li iz bırakır.

Gerçek veride onay için `--canli_kontrol <dosya>` gerekir (`ajan3-isleme`); rapor kaydı ürün altında taşır. Kayıt yoksa (sentetik örnekler) rapor `yapilmayan_kontroller` altında canlı fiyat doğrulamasını yazar.

## Çalıştırma (sentetik örnekler)

Onay:

```
python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv --ajan1_md5 7ae26d1c10de56d617b95e241ec6639b --fiyat data/ajan3-fiyat-ornek.csv --maliyet data/ajan3-maliyet-ornek.csv --referans 2026-11-29T18:00:00+03:00 --nihai_rapor data/ajan3-nihai-rapor-ornek.json --cikis_zarf data/ajan3-zarf-onay-ornek.json
```

Beklemede (maliyet verilmedi):

```
python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv --ajan1_md5 7ae26d1c10de56d617b95e241ec6639b --fiyat data/ajan3-fiyat-ornek.csv --referans 2026-11-29T18:00:00+03:00 --rapor data/ajan3-ara-rapor-ornek.json --cikis_zarf data/ajan3-zarf-ornek.json
```

Red (72 saat aşıldı, `ajan1`):

```
python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv --ajan1_md5 7ae26d1c10de56d617b95e241ec6639b --referans 2026-12-01T12:00:00+03:00 --rapor data/ajan3-ara-rapor-red-ornek.json --cikis_zarf data/ajan3-zarf-red-ornek.json
```

Test: `python3 -m unittest discover -s tests -p 'test_ajan3_denetim.py'`

## Kanıt yorumu (Issue #116)

`Üretim: ajan3-{alma,isleme,teslim}, <araç>, prompt özeti · PR #<no> · commit <hash> · dosyalar · iz: runs/ajan3/<dosya>`

## Üretim kaydı

27 Kasım 2026: Claude ile yazıldı ve Claude'un bulut ortamında sentetik veriyle çalıştırıldı. Prompt özeti: Ajan 3'ün maliyetten bağımsız ilk sürümünü hazırla (#116): üç skill, denetim kodu ve testleri, sentetik red ve ara rapor örnekleri; onay sonucu üretme. Sema Nur Doğan'ın incelemesi bekliyor.

28 Kasım 2026: Claude ile onay yolu eklendi ve Claude'un bulut ortamında sentetik veriyle çalıştırıldı. Prompt özeti: PR #117 sözleşmesine göre Ajan 3'e CSV MD5 kontrolü, önerilen fiyat ve maliyet girdisi, kâr eşiği, nihai rapor ve onay zarfı ekle; testleri ve örnek çıktıları güncelle. Sema Nur Doğan'ın incelemesi bekliyor.

28 Kasım 2026: Sema Nur Doğan cb37495'i kendi oturumunda çalıştırdı. Ardından kodu Claude okudu; bozuk girdide çökme ve `veri_topla` ürününe onay düzeltildi, Claude'un bulut ortamında sentetik veriyle test edildi. Prompt özeti: Ajan 3 kodunu ve skill'lerini incele, bulunan hataları düzelt ve testlerini ekle. Sema Nur Doğan ayrıca kod incelemesi yapmadı; düzeltilmiş sürümü henüz çalıştırmadı.

28 Kasım 2026: #120'deki inceleme ve PM kararı Claude ile uygulandı, Claude'un bulut ortamında sentetik veriyle test edildi. Prompt özeti: bulunamayan fiyat/maliyet yolunu kullanım hatası yap; önerilen fiyatı Ajan 2 eylemiyle karşılaştır; gerçek veride elle canlı fiyat kontrol kaydı yoksa beklemede bırak; testlerini ve skill metinlerini güncelle. Sema Nur Doğan ayrıca kod incelemesi yapmadı; bu sürümü henüz çalıştırmadı.

28 Kasım 2026: #123 karar 9 kontrolü Claude ile eklendi, Claude'un bulut ortamında sentetik veriyle test edildi. Prompt özeti: alma aşamasında aynı `bizim_urun` altında tekrar eden `urun_url` satırını Ajan 1'e gerekçeli red yap, farklı ürünümüzde aynı adresi kabul et, testlerini ve skill maddesini ekle.

28 Kasım 2026: canlı kontrol için kampanya notu Claude ile eklendi, Claude'un bulut ortamında sentetik veriyle test edildi. Prompt özeti: canlı kontrolde fiyatı uyuşmayan `kampanya` satırının red gerekçesine kampanyanın bitmiş olabileceğini ve yeniden toplama gerektiğini ekle; skill'e koşulsuz fiyat kuralını yaz, testini ekle.
