# Sprint Raporu — Hafta 03 (15.10–20.10.2026)

**Şirket:** Sepetix Analitik (Grup A) · **PM:** Ali Haydar Polat · **Görev:** Görev 1 — Sektörde Mini Veri Hattı (1. hafta)

## Planlanan

| Issue | Başlık | Atanan | Son tarih |
|---|---|---|---|
| #13 | G1-veri — Sektör verisini üret | Hilal Elçin Şahin (BE) | 20.10.2026 23:59 |
| #14 | G1-analiz — Metrikleri hesapla ve bulguları yaz | Tuğba Tuana Kaygısız (DQ) | 20.10.2026 23:59 |
| #15 | G1-gorsel — 2 grafik üret | Sema Nur Doğan (FE) | 20.10.2026 23:59 |
| #16 | G1-test — Veri kalitesi testleri | Tuğba Tuana Kaygısız (DQ) | 20.10.2026 23:59 |
| — | Kök `AGENTS.md` skill envanteri + `skills/pm-rapor` + bu rapor | Ali Haydar Polat (PM) | 20.10.2026 23:59 |

## Yapılan

| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|
| #13 | `data/siparisler.csv` (400 satır, 9 alan, tohum 42), `docs/veri-sozlugu-g1.md`, `src/veri_uret.py` — `fa3b368`; `skills/be-veri/SKILL.md` — `3b34e4b`; PR #22 | ✅ Kapandı |
| #14 | `docs/analiz-g1.md` gerçek veriyle dolduruldu — `7840e97`; `src/dq_analiz.py` + `skills/dq-analiz/SKILL.md` — `b8e50a0`; PR #20, #23 | ✅ Kapandı |
| #15 | Taslaklar Issue'ya eklendi; `visuals/haftalik-ciro.png` + `visuals/kategori-ciro-payi.png` — `ec72adc`; `src/fe_gorsel.py` — `3a226f3`; `skills/fe-gorsel/SKILL.md` — `3ac5d0b`; PR #24 | ✅ Kapandı |
| #16 | `tests/test-cases.md` (8 senaryo; ilk sürüm `29c306e`, şema güncellemesi `9c9b658`), `src/dq_test.py` — `95c3e0a`; `skills/dq-test/SKILL.md` — `943b75d`; test sonuçları 8/8 geçti (`7840e97`), PR #24 sonrası kontrol `c06e97a` (PR #25) | ✅ Kapandı |
| PM | `AGENTS.md` — `f607083`; `skills/pm-rapor/SKILL.md` — `fe0e701`; rapor otomasyonu `.github/workflows/haftalik-pm-rapor.yml` — PR #17 (`ce520e3`); Actions PR izni hocadan istendi (#18, kapandı) | ✅ |

**Öne çıkan sonuçlar (`docs/analiz-g1.md`):** Kategori bazlı ciro payı: Elektronik %38,1 · Ev & Yaşam %34,3 · Giyim %15,8 · Kozmetik %9,2 · Kitap %2,6. Ciroya en çok katkı veren 3 ürün: Saklama Kabı Seti, Kablosuz Kulaklık, Powerbank (birlikte %30,8).

## Devir teslim zinciri

- **BE ↔ DQ (şema):** Hilal alan önerisini #13'te paylaştı; Tuğba `urun` alanını, biçim kurallarını ve TC-08'i (`toplam_tutar = adet × birim_fiyat`) istedi; şema 9 alan / 400 satır / 2026-01-01–2026-09-30 olarak kesinleşti (#13 yorumları).
- **BE → DQ/FE:** "Veri hazır" devir teslim yorumu #14 ve #15'e yazıldı (commit `fa3b368`).
- **DQ → FE:** "Analiz hazır — docs/analiz-g1.md, commit 7840e97" yorumu #15'e yazıldı; grafik önerileri (M3, M4, M5) eklendi.
- **FE → DQ (test):** Sema'nın PR #24'ü sonrası Tuğba kontrolü test-log'a işledi (`c06e97a`, PR #25).

## Tıkanan / riskler

- **Bu raporun kendisi geç kaldı.** Rapor otomasyonu en yeni duyuruyu (Duyuru-4, son tarih satırı içermiyor) okuduğu için teslim tarihini bulamadı ve 15.10'daki taslağı güncellemedi; rapor 21.10'da elle güncellendi (geç teslim). Düzeltme: otomasyon artık son tarih içeren en yeni duyuruyu kullanacak.
- "Veri hazır" yorumu ilk başta yalnızca #13'te vardı; Tuğba'nın hatırlatmasıyla #14 ve #15'e de yazıldı.
- Yan görev 1 (Duyuru-2, son tarih 14.10): kesif-ali (`8a070ff`, 15.10), kesif-hilal (`16eacf8`), kesif-tugba (`43a5a6c`) geç teslim; kesif-sema 21.10'da eklendi (`34871c5`); Ebru'nun keşif raporu kayıt yok.

## Kim ne yaptı

| Üye | Rol | Başlıca commit'ler | Kapattığı Issue |
|---|---|---|---|
| Ali Haydar Polat | PM | `f607083`, `fe0e701`, `8a070ff`, PR #17 | #13–#16 açıldı ve takip edildi; #18 |
| Hilal Elçin Şahin | BE | `fa3b368`, `3b34e4b`, `16eacf8` | #13 |
| Sema Nur Doğan | FE | `3a226f3`, `ec72adc`, `3ac5d0b`, `8d2cd1f` | #15 |
| Tuğba Tuana Kaygısız | DQ | `29c306e`, `95c3e0a`, `943b75d`, `9c9b658`, `b8e50a0`, `7840e97`, `c06e97a` | #14, #16 |
| Ebru Türk | Junior | H2 ısınma: `prova-ebru.csv` (`99ed64f`) | #12 |

## Gelecek hafta (Hafta 4 — plana göre)

- DQ: tüm test senaryolarını nihai veride çalıştırıp `tests/test-log.md`'ye tarihli işlemek; en az 2 `bug` Issue'su açıp ilgili kişiye atamak.
- BE + FE: atanan hataları `Fixes #n` ile düzeltmek.
- DQ (analiz): analizin nihai veriyle uyumunu #14'te onaylamak.
- PM: tüm G1 Issue'larının kanıtla kapandığını doğrulamak, `reports/report-w04.md` ve **gorev1-final** release'i.
- 22.10 derste Yan görev 2: herkes keşfettiği repoyu sözlü sunar (Duyuru-4).

_Bu rapor skills/pm-rapor skill'i ile derlendi ve PM tarafından gözden geçirildi._
