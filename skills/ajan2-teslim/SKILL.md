---
name: ajan2-teslim
description: Ajan 2'nin (analiz) son aşaması. Analiz sonucunu docs/mesaj-bicimi.md'deki Ajan 2 → Ajan 3 JSON biçiminde yazar, onay ya da red zarfını üretir, runs/ajan2 altına çalışma izi bırakır, Ajan 3'e devreder ve Issue'ya kanıt yorumu yazar. Analiz bittikten sonra kullan.
---

# ajan2-teslim: Ajan 3'e devir ve kanıt (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Önceki aşama:** `ajan2-isleme` · **Alıcı:** Ajan 3 (Sema, denetim, #116)

## Çıktılar (`src/ajan2_analiz.py` → `calistir()`)

| Dosya | İçerik |
|---|---|
| `--cikti` (varsayılan `data/ajan2-cikti.json`) | `surum`, `veri_turu`, `para_birimi`, `uretim_zamani`, `siparis_donemi`, `urunler`, `iliskiler`. Yalnız onayda yazılır. |
| `--zarf` (varsayılan `data/ajan2-zarf.json`) | Onayda `durum = onay`, `hedef_ajan = ajan3`, `sorunlu_alanlar = []`. Redde `hedef_ajan = ajan1` ve hatalı alan yolları. |
| `runs/ajan2/<zaman>-<onay\|red>.json` | Gerçek araç izi: komut, referans zamanı, girdi ve çıktı MD5'leri, aşama, sonuç ve ürün özeti. |

Çıkış kodları: 0 onay, 2 red, 1 kullanım ya da beklenmeyen hata. Her çalıştırma eski çıktı ve zarfı silerek başlar; hangi yolda hata olursa olsun eski bir `onay` zarfı ortada kalmaz.

## Kurallar

- `veri_turu`: Tüm satırların `arac` değeri `sentetik-fixture` ise `sentetik_test`, değilse `web_ve_sentetik_siparis`.
- `uretim_zamani`: `--referans` verilirse o (yalnız sentetik test girdisi), verilmezse çalıştırma anı.
- Her sayısal alan `kaynaklar` içinde dosya, seçim ve üretim zamanıyla izlenir. Sürümlenmiş ve değişmemiş dosyada üretim zamanı son commit zamanıdır, değilse dosya zamanı.
- Red durumunda çıktı JSON'u yazılmaz ve eski çıktı silinir; hatalı çıktı Ajan 3'e aktarılmaz.
- Çıktı, zarf ve `runs/ajan2/` izi aynı PR'da commit edilir. Kod ya da veri PR'ı DQ onayı olmadan main'e girmez.

## Devir

- **Onay:** #116'ya Ajan 3 için şunlarla yorum yazılır: çıktı ve zarf yolları, commit hash'i, iz dosyası. Ajan 3 kâr ve doğruluk denetimini yapar, gerekirse `ajan1` ya da `ajan2` hedefli red döner.
- **Red:** Zarf #114'e Ajan 1 için yazılır (bkz. `ajan2-alma`).

## Örnek dosyalar (sentetik)

| Durum | Komut | Dosyalar |
|---|---|---|
| Onay | `python src/ajan2_analiz.py --girdi data/ornek-ajan1.csv --referans 2026-11-29T18:00:00+03:00 --cikti data/ajan2-cikti-ornek.json --zarf data/ajan2-zarf-ornek.json` | `data/ajan2-cikti-ornek.json`, `data/ajan2-zarf-ornek.json` |
| Red (72 saat aşıldı) | `python src/ajan2_analiz.py --girdi data/ornek-ajan1.csv --referans 2026-12-01T12:00:00+03:00 --cikti data/ajan2-cikti-red-ornek.json --zarf data/ajan2-zarf-red-ornek.json` | `data/ajan2-zarf-red-ornek.json` |

Onay örneğindeki sayılar ve kaynaklar `data/ornek-ajan2.json` ile birebir aynıdır; yalnız `oneri.gerekce` metni farklıdır (`tests/test_ajan2_analiz.py`).

## Kanıt yorumu (Issue #115)

Merge'den sonra yazılır:

`Üretim: ajan2-{alma,isleme,teslim} skill'leri ile, <araç>, prompt özeti: … · PR #<no> · commit <hash> · dosyalar: … · iz: runs/ajan2/<dosya>`

## Nasıl çalıştırılır

Ajana: "ajan2-teslim skill'ini kullanarak analiz sonucunu Ajan 3'e teslim et ve kanıt yorumunu hazırla."
Test: `python3 -m unittest discover -s tests -p 'test_ajan2_analiz.py'`

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 6. adımından, #115 için Claude (Claude Code) ile yazıldı; Tuğba Tuana Kaygısız'ın incelemesine sunuldu.
