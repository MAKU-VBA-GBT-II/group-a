# Sprint Raporu — Hafta 03 (15.10–20.10.2026)

**Şirket:** Sepetix Analitik (Grup A) · **PM:** Ali Haydar Polat

> Veri kesiti: 16.10.2026 00:24 (Europe/Istanbul) — teslime (20.10.2026 Salı 23:59) kadar durum değişebilir.

## Planlanan
| Issue | Başlık | Atanan | Son tarih |
|---|---|---|---|
| [#13](https://github.com/MAKU-VBA-GBT-II/group-a/issues/13) | G1-veri — Sektör verisini üret | @hilalelcin-stack (BE) | 20.10.2026 23:59 |
| [#14](https://github.com/MAKU-VBA-GBT-II/group-a/issues/14) | G1-analiz — Metrikleri hesapla ve bulguları yaz | @tugbatuanakaygisiz-web (DQ) | 20.10.2026 23:59 |
| [#15](https://github.com/MAKU-VBA-GBT-II/group-a/issues/15) | G1-gorsel — 2 grafik üret | @semadogaan (FE) | 20.10.2026 23:59 |
| [#16](https://github.com/MAKU-VBA-GBT-II/group-a/issues/16) | G1-test — Veri kalitesi testleri | @tugbatuanakaygisiz-web (DQ) | 20.10.2026 23:59 |
| [#12](https://github.com/MAKU-VBA-GBT-II/group-a/issues/12) | H2 ısınma — Ebru Türk (Junior) | @ebruturk | 14.10.2026 23:59 |
| [#18](https://github.com/MAKU-VBA-GBT-II/group-a/issues/18) | Actions ayarı: PR açma izni (hocaya istek) | atanan yok (açan: @plt0051ct-rgb) | kayıt yok |

## Yapılan
| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|
| #16 G1-test | `tests/test-cases.md` — `29c306e` (7 senaryo, kabul kriteri ≥5 sağlandı); `skills/dq-test/SKILL.md` — `943b75d`; `src/dq_test.py` — `95c3e0a`; `AGENTS.md` satırı — `732337d`. Kanıt yorumu mevcut. | Kapalı (15.10) |
| #12 H2 ısınma (Ebru) | `data/prova-ebru.csv` — `99ed64f` | Kapalı (15.10) |
| #18 Actions ayarı | Hoca (@eofdred) yorumuyla ayarı açtığını bildirdi; `workflow_dispatch` ile deneme önerildi. Workflow: `cd818e0` / PR #17 | Kapalı (15.10) |
| PM işleri (Duyuru-3) | `AGENTS.md` — `f607083`; `skills/pm-rapor/SKILL.md` — `fe0e701`; PM workflow'u PR #17 (`cd818e0`, merge `ce520e3`) | Tamamlandı |
| #13 G1-veri | `data/siparisler.csv` ve `docs/veri-sozlugu-g1.md` depoda yok; `skills/be-veri/` yok | Açık — kanıt yok |
| #14 G1-analiz | `docs/analiz-g1.md` depoda yok; `skills/dq-analiz/` yok | Açık — kanıt yok |
| #15 G1-gorsel | `visuals/` boş; taslak/PNG yok; `skills/fe-gorsel/` yok | Açık — kanıt yok |

## Devir teslim zinciri
- BE → DQ/FE: #13, #14 ve #15'te "Veri hazır" yorumu kayıt yok.
- DQ → FE: #15'te "Analiz hazır" yorumu kayıt yok.

## Tıkanan / riskler
- #13 (BE) açık ve yorumsuz; zincirin başı olduğundan #14 ve #15 buna bağlı ("Veri hazır" yorumu başlama izni).
- #16'daki testler `data/siparisler.csv` ve `docs/veri-sozlugu-g1.md` dosyalarına dayanıyor; ikisi de henüz yok. Tuana'nın #16 yorumu şemanın BE ile kesinleştirilmesini bekliyor (cc @hilalelcin-stack) — yanıt kayıt yok.
- #15'te FE taslağı (ekran görüntüsü) kayıt yok; duyuruya göre taslaksız başlamak kural ihlali.
- #14, #15 ve #13 için skill dosyaları (`be-veri`, `dq-analiz`, `fe-gorsel`) yok; `AGENTS.md` satırları "_ekleyecek_" durumunda.
- Son tarih 20.10.2026 23:59; kalan süre kesit anında yaklaşık 4,9 gün.

## Kim ne yaptı
| Üye | Rol | Commit | Kapattığı Issue |
|---|---|---|---|
| Ali Haydar Polat (@plt0051ct-rgb) | PM | 5 (`8a070ff`, `fe0e701`, `f607083`, `cd818e0`, `ce520e3`) | kayıt yok |
| Hilal Elçin Şahin (@hilalelcin-stack) | BE | 0 | kayıt yok |
| Tuğba Tuana Kaygısız (@tugbatuanakaygisiz-web) | DQ | 4 (`943b75d`, `29c306e`, `95c3e0a`, `732337d`) | #16 |
| Sema Nur Doğan (@semadogaan) | FE | 0 | kayıt yok |
| Ebru Türk (@ebruturk) | Junior | 1 (`99ed64f`) | #12 |

Commit sayıları 15.10.2026'dan itibaren `origin/main` üzerindedir.

## Gelecek hafta
- #13: BE `data/siparisler.csv` + şemayı üretip #14 ve #15'e "Veri hazır" yorumunu yazmalı (kaynak: #13 kabul kriteri).
- #14: DQ "Veri hazır" sonrası `docs/analiz-g1.md`'yi yazıp #15'e "Analiz hazır" yorumu bırakmalı.
- #15: FE önce iki grafik taslağını Issue'ya eklemeli, sonra 2 PNG üretmeli.
- #16: Hafta 4'te `python src/dq_test.py` çalıştırılıp "Gerçekleşen sonuç" sütunları doldurulacak (kaynak: #16, `tests/test-cases.md`).
- Skill'ler (`be-veri`, `dq-analiz`, `fe-gorsel`) eklenip `AGENTS.md` tablosu güncellenmeli.

<!-- pm-rapor:otomatik -->
_Bu taslak pm-rapor skill'i ile otomatik derlendi; PM tarafından gözden geçirilip merge edilir._
