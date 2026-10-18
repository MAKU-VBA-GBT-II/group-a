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
| pm-rapor | [`skills/pm-rapor/SKILL.md`](skills/pm-rapor/SKILL.md) | Ali Haydar Polat (PM) | Haftalık sprint raporunu (`reports/report-wXX.md`) GitHub'daki Issue, commit ve PR izlerinden derler. | Ajana: "pm-rapor skill'ini kullanarak report-w03.md yaz" · Otomatik: `.github/workflows/haftalik-pm-rapor.yml` teslimden önce taslak PR açar. |
| be-veri | [`skills/be-veri/SKILL.md`](skills/be-veri/SKILL.md) | Hilal Elçin Şahin (BE) | Sipariş verisini (`data/siparisler.csv`) sabit tohumla üretir, şemayı `docs/veri-sozlugu-g1.md`'ye yazar. | Ajana: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret" · Elle: `python src/veri_uret.py` |
| dq-analiz | [`skills/dq-analiz/SKILL.md`](skills/dq-analiz/SKILL.md) | Tuğba Tuana Kaygısız (DQ) | Sipariş verisinden 5 metriği (toplam, ortalama, 2 kırılım, top-3) `src/dq_analiz.py` ile hesaplar; sonuç, yorum ve bulguları `docs/analiz-g1.md`'ye yazar. | Ajana: "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur" · Elle: `python src/dq_analiz.py` |
| dq-test | [`skills/dq-test/SKILL.md`](skills/dq-test/SKILL.md) | Tuğba Tuana Kaygısız (DQ) | Veri kalitesi test senaryolarını (`tests/test-cases.md`) şemaya göre yazar; `src/dq_test.py` ile çalıştırıp sonuçları işler. | Ajana: "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz" · Elle: `python src/dq_test.py` |
| fe-gorsel | [`skills/fe-gorsel/SKILL.md`](skills/fe-gorsel/SKILL.md) | Sema Nur Doğan (FE) | Sipariş verisinden 2 PNG grafik (haftalık ciro zaman serisi + kategori ciro payı kırılımı) `src/fe_gorsel.py` ile üretip `visuals/`'a kaydeder; önce grafik taslaklarını hazırlar. | Ajana: "fe-gorsel skill'ini kullanarak data/siparisler.csv'den visuals/ altındaki iki grafiği üret" · Elle: `python src/fe_gorsel.py` (taslak: `--taslak`) |

> Kural: Roller görevden göreve döner (plan §1.3); skill'ler rolle birlikte el değiştirir. Yeni sahibi skill'i günceller ve bu tablodaki "Sahibi" sütununu değiştirir.

## Ajanlar için çalışma kuralları

1. "GitHub'da yoksa, yapılmamıştır": her iş bir Issue'ya bağlıdır; bitince Issue'ya kanıt yorumu (commit hash + dosya) yazılır.
2. Gerçek kişi verisi asla depoya girmez; tüm veriler simülasyon ürünüdür.
3. Veri üretimi sabit tohumla tekrarlanabilir olmalıdır.
4. Hafta 5'ten itibaren `main`'e yalnızca PR ile girilir; kod/veri PR'ları DQ onayı olmadan merge edilmez.
