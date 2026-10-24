# Sprint Raporu — Hafta 04 (22.10–27.10.2026)

**Şirket:** Sepetix Analitik (Grup A) · **PM:** Ali Haydar Polat · **Görev:** Görev 1 — Kapanış (test, düzeltme, sürüm) + Yan Görev 3 (Duyuru-5)

## Planlanan

| Issue | Başlık | Atanan | Son tarih |
|---|---|---|---|
| #32 | G1-H4 — Görev 1 kapanış kontrol listesi (skill kontrolü, test turu, hata düzeltmeleri, `report-w04.md`, `gorev1-final`) | Ali Haydar Polat (PM) | 27.10.2026 23:59 |
| #27 | G1-veri: `birim_fiyat` / `toplam_tutar` 2 ondalıkla yazılmıyor (bug) | Hilal Elçin Şahin (BE) | 27.10.2026 23:59 |
| #28 | G1-gorsel: `haftalik-ciro.png` ortalaması M4 ile uyuşmuyor (bug) | Sema Nur Doğan (FE) | 27.10.2026 23:59 |
| #29 | G1-gorsel: `haftalik-ciro.png` tarih biçimleri çakışıyor (bug) | Sema Nur Doğan (FE) | 27.10.2026 23:59 |
| #30 | Sentetik veride haftalık ciro oynak — Görev 1 sınırlılığı (enhancement) | Tuğba Tuana Kaygısız (DQ) | 27.10.2026 23:59 |
| #31 | G1-junior — Analizi oku, 3 gözlem yaz | Ebru Türk (Junior) | 27.10.2026 23:59 |
| #38 | G1-H4 junior — Bir test senaryosunu elle kontrol et | Ebru Türk (Junior) | 27.10.2026 23:59 |
| #33–#37 | Yan görev 3 — Grup G skill incelemeleri (be-veri, fe-gorsel, dq-test, pm-rapor, junior-kontrol) | Hilal, Sema, Tuğba, Ali, Ebru | 27.10.2026 23:59 |
| #44–#47, #48 | Hoca geri bildirimleri (#44 rapor zamanlaması, #45 devir yorumu, #46 grafik taslağı, #47 DQ test kaydı düzeni); #48 Tuğba'nın #47 notu için açtığı takip Issue'su | #44: Ali · #45: Hilal · #46: Sema · #47, #48: Tuğba | 27.10.2026 23:59 |
| #53, #54 | Grup B'nin Grup A skill incelemeleri (#53 dq-analiz, #54 fe-gorsel) | #53: Tuğba · #54: Sema | 27.10.2026 23:59 |

## Yapılan

| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|
| #27 | `src/veri_uret.py` `float_format="%.2f"`, `data/siparisler.csv` yeniden üretildi (400 satır, tohum 42) — `1f8beb8` (`Fixes #27`); DQ yeniden testi 9/9 (`1868546`, PR #40) | ✅ Kapandı |
| #28, #29 | `src/fe_gorsel.py` — `c9e31b1`; `visuals/haftalik-ciro.png` (ortalama 77.860 TL, "19.01.2026 haftası") — `4e0012f` (`Fixes #28, Fixes #29`); DQ doğruladı | ✅ Kapandı |
| #14 (analiz onayı) | "Analiz nihai veri üzerinde doğrulandı — onaylıyorum" yorumu; M1–M5 54/54 satır `docs/analiz-g1.md` ile aynı (21.10) | ✅ |
| #16 / test turu | `tests/test-log.md` 21.10 ve 22.10 satırları; `tests/test-cases.md` TC-09…TC-12 (12/12 geçti) — `1868546`, `46f5c49`, PR #40, #43 | ✅ |
| #30 | `docs/analiz-g1.md` "Sınırlılıklar" bölümü — `5539020`; be-veri skill'ine bilinen sınırlılıklar — `27f18cd`, PR #42 | 🟡 Açık (kapatma Görev 2 takibi için bırakıldı) |
| #31, #38 | `reports/junior/ebru-g1-gozlem.md` — `82b7ba7`; TC-03 elle kontrol, `tests/test-log.md` — `2aa4429` | ✅ Kapandı |
| Skill kontrolü (#32) | `skills/be-veri` (`fd1d807`, `b49e659`, `ca0fc25`, PR #41, #42); `skills/fe-gorsel` (`2129cb5`, `1aad2be`); `skills/dq-analiz` + `skills/dq-test` (`1868546`, `fff7fdd`, PR #40, `46f5c49` PR #43); `skills/pm-rapor` (`449406b`, PR #49) | ✅ |
| Yan görev 3 | #33 (Hilal), #34 (Sema), #35 (Tuğba), #36 (Ali), #37 (Ebru) kapandı; Grup G'de açılan Issue'lar: group-g#27 (Hilal), group-g#18 (Sema), group-g#19 (Tuğba), group-g#17 (Ali), group-g#20 (Ebru) | ✅ |
| Grup B'nin Grup A'ya incelemesi | #39 (Sude Çukurtaş, Grup B) kapandı; pm-rapor güncellemesi — `449406b` (PR #49) | ✅ |
| Hoca geri bildirimleri | #44, #45, #46, #47, #48 kapandı; #45 için be-veri skill'inde devir adımı netleştirildi — `a2eaa95` (PR #55, 24.10); test-log Görev 2 bölümü — `6b4eb9e` | ✅ Kapandı |
| Grup B incelemeleri (#53, #54) | #53 kapandı: dq-analiz skill'inde kırılım netleştirmesi — `a6a856a` (#53); #54 açık: fe-gorsel skill'ine kurulum komutu eklendi — `026f504`, Ece Naz Aktürk (Grup B) yanıtı var, Issue açık | 🟡 #53 kapandı, #54 açık |
| be-veri kontrol eşitleme (#32) | `veri_uret.py` TC-10…TC-12 ve geri okuma — `36312ae`; skill/sözlük — `c0cc939`, `839776a`, `43f0e01`, `65b8b39`; PR #51, #52; veri değişmedi (`data/siparisler.csv` 401 satır) | ✅ |
| `reports/report-w04.md` | Bu dosya (otomatik taslak, PR bekliyor) | 🟡 PM onayı bekliyor |
| `gorev1-final` release'i | Release kaydı yok | ⏳ Yapılmadı (#32'de "en son" maddesi açık) |

**Doğrulanan dosyalar (main):** `data/siparisler.csv` 401 satır (1 başlık + 400 kayıt); `visuals/haftalik-ciro.png`, `visuals/kategori-ciro-payi.png`; `tests/test-log.md` 22.10 satırlarında 12 geçti / 0 kaldı; `reports/report-w03.md` mevcut.

## Devir teslim zinciri

- **BE → DQ/FE:** "Veri hazır — commit fa3b368" yorumu #14 ve #15'te var (#13 yorumları); #27 düzeltmesi sonrası yeniden üretilen veri için `1f8beb8` kanıtı #27'de. #45 (hocanın "devir yorumunu iş biter bitmez yaz" notu) kapandı; kural be-veri skill'ine işlendi (`a2eaa95`).
- **DQ → FE:** "Analiz hazır — docs/analiz-g1.md, commit 7840e97" yorumu #15'te var; grafik taslakları (`visuals/taslak/`) kod öncesi #15'e eklenmiş.
- **FE → DQ:** #28 ve #29 için DQ doğrulama yorumları var; PR #24 sonrası kontrol `c06e97a`.
- **DQ → BE/FE (hata):** #27 → BE, #28 ve #29 → FE olarak atandı ve `Fixes` ile kapandı.

## Tıkanan / riskler

- **`gorev1-final` release'i henüz oluşturulmadı** (kayıt yok); #32'de açık madde. Son tarih 27.10.2026 23:59.
- **#32 açık:** `report-w04.md` ve release maddeleri işaretlenmedi.
- **#54 açık** (Grup B'nin fe-gorsel incelemesi; Sema yanıtladı, `026f504`); **#30 açık** (kapatma kararı Görev 2 takibi için PM'e bırakıldı).
- **Geçen hafta rapor main'e geç girdi** (#44, bug); bu rapor taslak PR olarak açılır, PM'in son tarihten önce merge etmesi gerekir.

## Kim ne yaptı

| Üye | Rol | Başlıca commit'ler (21–24.10) | Kapattığı Issue |
|---|---|---|---|
| Ali Haydar Polat | PM | `449406b` (PR #49) | #36, #39, #44 (bkz. Issue durumları); #32 açık |
| Hilal Elçin Şahin | BE | `1f8beb8`, `fd1d807`, `078f076`, `27f18cd`, `b49e659`, `9af054b`, `bf5ab06`, `ca0fc25`, `a591a8e`, `36312ae`, `c0cc939`, `839776a`, `43f0e01`, `65b8b39`, `a2eaa95` (PR #41, #42, #51, #52, #55) | #27, #33, #45 |
| Sema Nur Doğan | FE | `c9e31b1`, `4e0012f`, `2129cb5`, `1aad2be`, `026f504` | #28, #29, #34, #46 |
| Tuğba Tuana Kaygısız | DQ | `5539020`, `1868546`, `fff7fdd` (PR #40), `46f5c49`, `6b4eb9e` (PR #43), `a6a856a` | #35, #47, #48, #53 |
| Ebru Türk | Junior | `82b7ba7`, `2aa4429` | #31, #37, #38 |

## Gelecek hafta

- PM: bu taslağı gözden geçirip merge etmek; #32'yi tamamlayıp `gorev1-final` release'ini oluşturmak (tag `gorev1-final`, sürüm notu: ne teslim edildi, kim yaptı).
- Hilal (BE): Görev 2'de devir yorumlarını iş biter bitmez yazmak.
- DQ: Görev 2 senaryolarını `tests/test-cases.md`'ye yazmak, sonuçları `tests/test-log.md` Görev 2 bölümüne işlemek (#47).
- Herkes: group-a'da açılan "Skill incelemesi" Issue'larına (#39 vb.) cevap yazmak; plana göre Görev 2 (Hafta 5) başlangıcı — plan kaynağı: `ders/AGENTS.md`.

<!-- pm-rapor:otomatik -->
_Bu taslak pm-rapor skill'i ile otomatik derlendi; PM tarafından gözden geçirilip merge edilir._
