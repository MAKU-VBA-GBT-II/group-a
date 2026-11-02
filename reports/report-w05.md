# Sprint Raporu — Hafta 05 (28.10–05.11.2026)

**Şirket:** Sepetix Analitik (Grup A) · **PM:** Ali Haydar Polat · **Görev:** Görev 2 — Şirket Mini Ürünü (parametreli simülasyon + analiz + 3 grafik) · Duyuru-7 Bölüm 1 (5 Kasım 23:59 bitiş hattı)

## Planlanan

| Issue | Başlık | Atanan | Son tarih |
|---|---|---|---|
| #60 | G2-sem — Veri şeması ve analiz planı | Sema Nur Doğan (DQ, @semadogaan) | 01.11.2026 23:59 |
| #61 | G2-veri — Parametreli simülasyon | Tuğba Tuana Kaygısız (BE, @tugbatuanakaygisiz-web) | 03.11.2026 23:59 |
| #62 | G2-analiz — Metrik hesabı ve bulgular | Sema Nur Doğan (DQ) | 10.11 → Duyuru-7 ile 05.11.2026 23:59 |
| #63 | G2-gorsel — Grafik seti | Hilal Elçin Şahin (FE, @hilalelcin-stack) | 10.11 → 05.11.2026 23:59 |
| #64 | G2-test — Test senaryoları ve PR incelemesi | Sema Nur Doğan (DQ) | 10.11 → 05.11.2026 23:59 |
| #58 | Skill incelemesi: pm-rapor (İpek Özarslan, Grup B) | Ali Haydar Polat (PM, @plt0051ct-rgb) | 05.11.2026 23:59 |
| #73 | Dönem Raporu 1 — üye yanıtları | Ali Haydar Polat (PM) | 04.11.2026 23:59 |
| — | Görev 2 milestone, `pm-rapor` Görev 2 güncellemesi, bu rapor, `gorev2-final` | Ali Haydar Polat (PM) | 05.11.2026 23:59 |

Milestone: **Görev 2 — Mini Ürün** (#60–#64 bağlı). Görev 2 kuralları: `main`'e yalnız PR ile girilir; her teslimat rol skill'iyle üretilir ve PR/Issue'ya prompt özeti yazılır.

## Yapılan

| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|
| #60 | `skills/dq-sozluk/SKILL.md` önce (`eaeafcf`); `docs/veri-sozlugu.md` — 14 alan, 8 parametre, satır sayısı formülü, 12 kalite kuralı, M1–M6 (`47cf7db`) → PR #65 (`9ec0b70`); kural 9 eki PR #67 (`105c913`), `max(1, …)` düzeltmesi PR #74 (`fe41763`); devir yorumları #61, #63 | Tamamlandı |
| #61 | `skills/be-simulasyon/SKILL.md` önce (`bf7b4d7`); `src/simulasyon.py` + `data/siparisler-g2.csv` (8.208 satır, 14 sütun, tohum 42, MD5 `1b7f765e…`) (`2159a98`) → PR #66, DQ'nun 3 satır içi inceleme yorumu + Approve ile merge (`f9dfca7`); "Veri hazır" yorumları #62, #63, #64 | Tamamlandı |
| Hata yönetimi (Hafta 6 işi, erken) | `beab94a` (skill), `350d95c` (geçersiz parametrede `ValueError`, dosya yazılmaz), `a22c867` (`gun_adet = max(1, …)`) → PR #72, DQ incelemesi + Approve ile merge (`e856395`); `Fixes` #76, #77 | Tamamlandı |
| #62 | `skills/dq-analiz/SKILL.md` Görev 2'ye (`cbd9f7e`); `src/dq_analiz_g2.py` (`02b80f1`); `docs/analiz-g2.md` + `docs/requirements.md` (`e425bae`) → PR #75, PM incelemesi (metrikler CSV'den bağımsız hesaplandı, birebir) + Approve, merge `c9015c9`; PM notu düzeltmesi `f1e849a` | Tamamlandı |
| #63 | Elle çizilmiş 3 taslak kod öncesi Issue'ya yüklendi, DQ onayı alındı; `skills/fe-gorsel/SKILL.md` + `requirements.txt` (`99c0902`); iskelet `src/fe_gorsel.py` + 3 PNG (`2469d0c`); son hal `dd5dce9`, `c85a4e0` → PR #79, DQ Approve ile merge (`ffb363e`) | Tamamlandı |
| #64 | `skills/dq-test/SKILL.md` (`4cc1640`); `tests/test-cases.md` 22 senaryo (`c06d2a1`) → PR #68 (`943a06f`); test koşucusu `src/dq_test_g2.py` (`5e5c00b`) + ilk tur (A–C 20/20, D 0/3) → PR #78, PM Approve (`538c217`); bug #76, #77 açıldı; PR #72 sonrası yeniden test 23/23 (`b95a2d7`, PR #80); `docs/user-manual.md` kurulum + Senaryo 1–4 (`6f80c1d`, `3d11cff`, PR #81) | Tamamlandı |
| #76, #77 | `bug` — DQ açtı, BE PR #72 ile düzeltti, DQ yeniden test edip kapattı (`b95a2d7`) | Tamamlandı |
| #58 | İpek'in önerisi (Durum değerleri) `14180b8` → PR #59 (`bb15f99`), `Fixes #58` | Tamamlandı |
| `pm-rapor` Görev 2 | Amaç, Issue taslakları, çıktı formatı, örnek giriş/çıkış, reddetme durumları (`9e07431`); AGENTS.md (`f1ee2e1`) → PR #70 (`65646fc`) | Tamamlandı |
| #73 | Dört üyenin (Sema, Ebru, Tuğba, Hilal) yanıtı Issue yorumlarında | Tamamlandı |
| Milestone | *Görev 2 — Mini Ürün* 5/5 Issue kapalı, milestone kapatıldı (02.11) | Tamamlandı |
| `gorev2-final` | Bu rapor merge edildikten sonra oluşturulacak | Yapılmadı |

**Doğrulanan dosyalar (main):** `data/siparisler-g2.csv` 8.208 satır; `docs/analiz-g2.md` M1 = 11.973.617,93 TL (PM bağımsız hesabıyla aynı); `visuals/` altında 3 PNG; `tests/test-log.md` son tur 23/23.

## Devir teslim zinciri

- **DQ → BE/FE (şema):** "Şema yayımlandı — commit `9ec0b70`" yorumu #61 ve #63'te (29.10).
- **BE → DQ/FE (veri):** "Veri hazır — commit `f9dfca7`" yorumu #62, #63, #64'te (30.10, merge ile aynı gün).
- **DQ → FE (analiz):** "Analiz hazır — `docs/analiz-g2.md`" yorumu #63'te (01.11); grafik değerleri analizle birebir.
- **PR incelemeleri:** PR #66 (DQ, 3 satır içi soru → cevap → Approve), PR #72 (DQ, 1 bulgu → düzeltme → Approve), PR #79 (DQ Approve), PR #75 ve #78 (PM Approve, DQ'nun kendi kod PR'ları).

## Tıkanan / riskler

- **Son tarih öne çekildi:** Duyuru-7 (01.11) Görev 2 bitişini 10.11'den 05.11'e aldı; ekip 01.11'de tüm işleri kapattı.
- **İzinli parametrede iç kontrol hatası:** `--gunluk_siparis 1 --hafta_sonu_katsayisi 0.4` ile 0 siparişli gün oluşuyordu (#76); sözlük (PR #74) ve kod (PR #72) `max(1, …)` ile düzeltildi.
- **PR #70 çakışması:** AGENTS.md'de aynı satır (fe-gorsel) PR #71 ile de güncellenmişti; çakışma `7132a05` ile çözüldü.
- **Junior:** Görev 2'de Ebru için ayrı kart açılmadı; Ebru'nun bu haftaki izi #73 yanıtı. Görev 3'te junior kartı açılacak.
- **Simülasyon sınırlılıkları** (`docs/analiz-g2.md` → Sınırlılıklar): ürünler eşit sıklıkta seçildiği için M5 en pahalı ürünleri gösteriyor; yeni/tekrar müşteri ayrımı havuz etkisi taşıyor.

## Kim ne yaptı

| Üye | Rol | Commit (28.10–02.11, merge hariç) | Kapattığı Issue |
|---|---|---|---|
| Ali Haydar Polat | PM | 3 — `14180b8`, `9e07431`, `f1ee2e1`; milestone + #60–#64 açıldı; PR #75, #78 incelemesi | #58 (PR #59), #73 |
| Hilal Elçin Şahin | FE | 5 — `31fab47`, `99c0902`, `2469d0c`, `dd5dce9`, `c85a4e0` | #63 |
| Sema Nur Doğan | DQ | 21 — örn. `eaeafcf`, `47cf7db`, `c06d2a1`, `02b80f1`, `e425bae`, `5e5c00b`, `b95a2d7` | #60, #62, #64, #76, #77 |
| Tuğba Tuana Kaygısız | BE | 8 — `bf7b4d7`, `2159a98`, `a0af0ae`, `f066065`, `beab94a`, `350d95c`, `edda171`, `a22c867` | #61 |
| Ebru Türk | Junior | kayıt yok (commit); #73 yanıtı | — |

## Gelecek hafta

- PM: `gorev2-final` release'i (bu rapor merge edildikten sonra); `reports/donem-raporu-1.md` (Duyuru-7 Bölüm 2, son tarih 08.11.2026 23:59) + "Dönem Raporu 1 teslim" Issue'su (@eofdred).
- Herkes: Yan Görev 4 — TÜBİTAK 2209-A başvurusu (Duyuru-6, 11.11.2026 17:30), group-a'da kişisel Issue + TYBS ekran görüntüsü.
- Görev 3 (B2B veri değişimi) duyurusu bekleniyor; rol rotasyonu: Hilal DQ, Sema BE, Tuğba FE.

_Bu rapor skills/pm-rapor skill'i ile derlendi ve PM tarafından gözden geçirildi._

Üretim: pm-rapor skill'i ile, Claude — prompt özeti: "pm-rapor skill'ini kullanarak Hafta 05 (28.10–05.11) için report-w05.md yaz; Duyuru-7 bitiş hattını, #60–#64, PR #65–#81 ve commit izlerini kaynak göster."
