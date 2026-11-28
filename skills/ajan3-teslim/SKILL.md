---
name: ajan3-teslim
description: Ajan 3'ün (denetim) son aşaması. Denetim sonucunu red zarfı ya da beklemede ara raporu olarak yazar, çalışma izi bırakır ve Issue kanıt yorumunu hazırlar. Doğrulama bittikten sonra kullan.
---

# ajan3-teslim: sonuç ve kanıt (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Önceki:** `ajan3-isleme`

## Sonuçlar

| Sonuç | Çıkış | Yazılan |
|---|---|---|
| Red | 2 | `--cikis_zarf`: `durum = red`, `hedef_ajan = ajan1` veya `ajan2`, gerekçe, alan yolları |
| Beklemede | 3 | `--rapor`: kontrolleri geçen ürünler ve yapılmayan kontroller. **Zarf yazılmaz.** |
| Kullanım hatası | 1 | Hiçbir sonuç; eski rapor ve zarf silinmiş olur (argümanlar ayrıştırılabildiyse) |

Her red ve beklemede çalıştırması `runs/ajan3/` altına komut, referans zamanı ve MD5'li iz bırakır.

**Nihai onay bu sürümde üretilmez.** Kâr denetimi eklenmeden `durum = onay` yazılmaz.

## Çalıştırma (sentetik örnekler)

```
python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv --referans 2026-11-29T18:00:00+03:00 --rapor data/ajan3-ara-rapor-ornek.json --cikis_zarf data/ajan3-zarf-ornek.json
python src/ajan3_denetim.py --girdi data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json --ajan1 data/ornek-ajan1.csv --referans 2026-12-01T12:00:00+03:00 --rapor data/ajan3-ara-rapor-red-ornek.json --cikis_zarf data/ajan3-zarf-red-ornek.json
```

İlki beklemede (ara rapor), ikincisi 72 saat aşıldığı için `ajan1` redidir.
Test: `python3 -m unittest discover -s tests -p 'test_ajan3_denetim.py'`

## Kanıt yorumu (Issue #116)

`Üretim: ajan3-{alma,isleme,teslim}, <araç>, prompt özeti · PR #<no> · commit <hash> · dosyalar · iz: runs/ajan3/<dosya>`

## Üretim kaydı

27 Kasım 2026: Claude ile yazıldı ve Claude'un bulut ortamında sentetik veriyle çalıştırıldı. Prompt özeti: Ajan 3'ün maliyetten bağımsız ilk sürümünü hazırla (#116): üç skill, denetim kodu ve testleri, sentetik red ve ara rapor örnekleri; onay sonucu üretme. Sema Nur Doğan'ın incelemesi bekliyor.
