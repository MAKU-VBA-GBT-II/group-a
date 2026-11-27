---
name: ajan2-teslim
description: Ajan 2'nin (analiz) son aşaması. Analiz sonucunu docs/mesaj-bicimi.md'deki Ajan 2 → Ajan 3 JSON biçiminde yazar, onay ya da red zarfını üretir, runs/ajan2 altına çalışma izi bırakır ve Issue'ya kanıt yorumu hazırlar. Analiz bittikten sonra Ajan 3'e devir için kullan.
---

# ajan2-teslim: Ajan 3'e devir ve kanıt (Ajan 2)

**Rol:** Ajan 2 (analiz) · **Sahibi:** Tuğba Tuana Kaygısız · **Issue:** #115 · **Önceki aşama:** `ajan2-isleme` · **Alıcı:** Ajan 3 (Sema, denetim)

## Çıktılar (`src/ajan2_analiz.py` → `calistir()`)

| Dosya | İçerik |
|---|---|
| `--cikti` (varsayılan `data/ajan2-cikti.json`) | `surum`, `veri_turu`, `para_birimi`, `uretim_zamani`, `siparis_donemi`, `urunler`, `iliskiler`. Yalnız onayda yazılır. |
| `--zarf` (varsayılan `data/ajan2-zarf.json`) | Onay: `durum = onay`, `hedef_ajan = ajan3`, `sorunlu_alanlar = []`. Red: `hedef_ajan = ajan1` ve hatalı alan yolları. |
| `runs/ajan2/<zaman>-<onay\|red>.json` | Gerçek araç izi: komut, referans zamanı, girdi ve çıktı MD5'leri, aşama, sonuç, ürün özeti. |

Kurallar:
- `veri_turu`: tüm satırların `arac` değeri `sentetik-fixture` ise `sentetik_test`, değilse `web_ve_sentetik_siparis`.
- `uretim_zamani`: `--referans` verilirse o (tekrarlanabilir test), verilmezse hesaplamanın bitişi.
- Her sayısal alan `kaynaklar` içinde dosya, seçim ve üretim zamanıyla izlenir. Sürümlenmiş ve değişmemiş dosyada üretim zamanı son commit zamanıdır, değilse dosya zamanı.
- Red durumunda çıktı JSON'u yazılmaz ve eski çıktı silinir; hatalı çıktı Ajan 3'e aktarılmaz.

## Örnek dosyalar (sentetik)

- Onay: `data/ajan2-cikti-ornek.json`, `data/ajan2-zarf-ornek.json` (`--referans 2026-11-29T18:00:00+03:00`). Sayılar `data/ornek-ajan2.json` ile birebir aynıdır (`tests/test_ajan2_analiz.py`).
- Red: `data/ajan2-zarf-red-ornek.json` (`--referans 2026-12-01T12:00:00+03:00`, tüm satırlar 72 saatten eski).

## Kanıt yorumu (Issue #115)

`Üretim: ajan2-{alma,isleme,teslim} skill'leri ile, <araç>, prompt özeti: … · PR #<no> · commit <hash> · dosyalar: … · iz: runs/ajan2/<dosya>`

## Nasıl çalıştırılır

Ajana: "ajan2-teslim skill'ini kullanarak analiz sonucunu Ajan 3'e teslim et ve kanıt yorumunu hazırla."
Test: `python3 -m unittest discover -s tests -p 'test_ajan2_analiz.py'`

## Üretim kaydı

27 Kasım 2026: Eski `ajan2-analiz` skill'inin 6. adımından, #115 için Claude (Claude Code) ile yazıldı; Tuğba Tuana Kaygısız'ın incelemesine sunuldu.
