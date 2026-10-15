# AGENTS.md — Sepetix Analitik (Grup A) skill envanteri

Bu dosya, depodaki yapay zekâ ajanı skill'lerinin envanteridir. Ajan araçları (Claude Code, Codex vb.) bu dosyayı otomatik okur. Her üye kendi skill'ini eklediğinde bu tabloya bir satır ekler.

## Depo bağlamı

- **Şirket:** Sepetix Analitik — Grup A · **Sektör:** E-ticaret
- **Teknoloji:** Python · pandas · matplotlib (görselleştirme: PNG)
- **Dönem planı:** [ders/AGENTS.md](https://github.com/MAKU-VBA-GBT-II/ders/blob/main/AGENTS.md)
- **Klasörler:** `src/` kod · `data/` veri · `visuals/` grafikler · `docs/` sözlük ve analiz · `tests/` test senaryoları ve kayıtları · `reports/` sprint raporları · `skills/` ajan skill'leri

## Skill envanteri

| Skill | Yol | Sahibi (rol) | Ne işe yarar | Nasıl kullanılır |
|---|---|---|---|---|
| pm-rapor | [`skills/pm-rapor/SKILL.md`](skills/pm-rapor/SKILL.md) | Ali Haydar Polat (PM) | Haftalık sprint raporunu (`reports/report-wXX.md`) GitHub'daki Issue, commit ve PR izlerinden derler. | Ajana: "pm-rapor skill'ini kullanarak report-w03.md yaz" |
| be-veri | `skills/be-veri/SKILL.md` | BE | Sipariş verisini sabit tohumla üretir, şemayı yazar. | _BE ekleyecek_ |
| dq-analiz | `skills/dq-analiz/SKILL.md` | DQ | Metrikleri hesaplar, bulguları `docs/analiz-g1.md`'ye yazar. | _DQ ekleyecek_ |
| fe-gorsel | `skills/fe-gorsel/SKILL.md` | FE | Zaman serisi ve kırılım grafiklerini PNG olarak üretir. | _FE ekleyecek_ |
| dq-test | `skills/dq-test/SKILL.md` | DQ | Veri kalitesi test senaryolarını yazar ve çalıştırır. | _DQ ekleyecek_ |

> Kural: Roller görevden göreve döner (plan §1.3); skill'ler rolle birlikte el değiştirir. Yeni sahibi skill'i günceller ve bu tablodaki "Sahibi" sütununu değiştirir.

## Ajanlar için çalışma kuralları

1. "GitHub'da yoksa, yapılmamıştır": her iş bir Issue'ya bağlıdır; bitince Issue'ya kanıt yorumu (commit hash + dosya) yazılır.
2. Gerçek kişi verisi asla depoya girmez; tüm veriler simülasyon ürünüdür.
3. Veri üretimi sabit tohumla tekrarlanabilir olmalıdır.
4. Hafta 5'ten itibaren `main`'e yalnızca PR ile girilir; kod/veri PR'ları DQ onayı olmadan merge edilmez.
