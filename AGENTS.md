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
| pm-rapor | [`skills/pm-rapor/SKILL.md`](skills/pm-rapor/SKILL.md) | Ali Haydar Polat (PM) | Haftalık sprint raporunu (`reports/report-wXX.md`) GitHub'daki Issue, commit ve PR izlerinden derler; görev başında Issue taslaklarını (başlık, atanan, son tarih, kabul kriteri) üretir. | Ajana: "pm-rapor skill'ini kullanarak report-w03.md yaz" · Otomatik: `.github/workflows/haftalik-pm-rapor.yml` teslimden önce taslak PR açar. |
| be-veri | [`skills/be-veri/SKILL.md`](skills/be-veri/SKILL.md) | Hilal Elçin Şahin (BE, Görev 1; Görev 2'de yerini `be-simulasyon` aldı) | Sipariş verisini (`data/siparisler.csv`) sabit tohumla üretir, şemayı `docs/veri-sozlugu-g1.md`'ye yazar. | Ajana: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret" · Elle: `python src/veri_uret.py` |
| dq-analiz | [`skills/dq-analiz/SKILL.md`](skills/dq-analiz/SKILL.md) | Tuğba Tuana Kaygısız (DQ, Görev 1) · Sema Nur Doğan (DQ, Görev 2 — #62'de Görev 2'ye güncellenecek) | Sipariş verisinden 5 metriği (toplam, ortalama, 2 kırılım, top-3) `src/dq_analiz.py` ile hesaplar; sonuç, yorum ve bulguları `docs/analiz-g1.md`'ye yazar; Hafta 4'te nihai veriyle doğrulayıp onaylar. | Ajana: "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur" · Elle: `python src/dq_analiz.py` |
| dq-test | [`skills/dq-test/SKILL.md`](skills/dq-test/SKILL.md) | Tuğba Tuana Kaygısız (DQ, Görev 1) · Sema Nur Doğan (DQ, Görev 2) | Test senaryolarını veri sözlüğüne göre `tests/test-cases.md`'ye yazar (Görev 2: 22 senaryo; Görev 1 arşivi `tests/test-cases-g1.md`), sonuçları tarihli olarak `tests/test-log.md`'ye işler, BE/FE PR'larını DQ olarak inceler. | Ajana: "dq-test skill'ini kullanarak docs/veri-sozlugu.md'ye göre Görev 2 için tests/test-cases.md yaz" · PR incelemesi: "dq-test skill'ini kullanarak PR #<no>'yu DQ olarak incele" |
| dq-sozluk | [`skills/dq-sozluk/SKILL.md`](skills/dq-sozluk/SKILL.md) | Sema Nur Doğan (DQ, Görev 2) | Görev 2 veri sözlüğünü (`docs/veri-sozlugu.md`) üretir: alanlar, tipler, aralıklar, parametreler, satır sayısı formülü, kalite kuralları ve 5 metrik (#60). | Ajana: "dq-sozluk skill'ini kullanarak #60'ın kabul kriterlerine göre docs/veri-sozlugu.md yaz" · Değişiklik: "…sözlüğe <alan> ekle; satır sayısı, kurallar ve değişiklik günlüğünü güncelle" |
| fe-gorsel | [`skills/fe-gorsel/SKILL.md`](skills/fe-gorsel/SKILL.md) | Sema Nur Doğan (FE, Görev 1) · Hilal Elçin Şahin (FE, Görev 2 — #63'te 3 grafiğe güncellenecek) | Sipariş verisinden PNG grafikler üretip `visuals/`'a kaydeder (Görev 1: haftalık ciro zaman serisi + kategori ciro payı; Görev 2: zaman serisi + kanal kırılımı + dağılım); grafik taslağı koddan önce Issue'ya eklenir (#46). | Ajana: "fe-gorsel skill'ini kullanarak data/siparisler-g2.csv'den visuals/ altındaki üç grafiği üret" · Elle: `python src/fe_gorsel.py` |
| be-simulasyon | [`skills/be-simulasyon/SKILL.md`](skills/be-simulasyon/SKILL.md) | Tuğba Tuana Kaygısız (BE, Görev 2) | Görev 2 sipariş verisini (`data/siparisler-g2.csv`) `docs/veri-sozlugu.md` şemasına birebir, parametreli ve sabit tohumlu simülasyonla üretir. | Ajana: "be-simulasyon skill'ini kullanarak data/siparisler-g2.csv'yi üret" · Elle: `python src/simulasyon.py` (`--help` ile parametreler) |

> Kural: Roller görevden göreve döner (plan §1.3); skill'ler rolle birlikte el değiştirir. Yeni sahibi skill'i günceller ve bu tablodaki "Sahibi" sütununu değiştirir.

## Ajanlar için çalışma kuralları

1. "GitHub'da yoksa, yapılmamıştır": her iş bir Issue'ya bağlıdır; bitince Issue'ya kanıt yorumu (commit hash + dosya) yazılır.
2. Gerçek kişi verisi asla depoya girmez; tüm veriler simülasyon ürünüdür.
3. Veri üretimi sabit tohumla tekrarlanabilir olmalıdır.
4. Hafta 5'ten itibaren `main`'e yalnızca PR ile girilir; kod/veri PR'ları DQ onayı olmadan merge edilmez.
