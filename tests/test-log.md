# Test Kaydı — Veri Kalitesi

Her test çalıştırması bu dosyaya bir satır olarak eklenir (bkz. `skills/dq-test/SKILL.md`, adım B4).

| Tarih | Test edilen dosya | Veri commit'i | Komut | Geçti | Kaldı | Not |
|---|---|---|---|---|---|---|
| 2026-10-17 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 0 | İlk çalıştırma; BE verisi (#13) şemaya tam uyuyor. Ayrıntılar `tests/test-cases.md`. |
| 2026-10-18 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 0 | PR #24 (G1-gorsel) birleştikten sonra `main` (`7278b05`) üzerinde DQ kontrolü; grafiklerdeki kategori payları ve en yüksek hafta `docs/analiz-g1.md` ile uyuşuyor (#15). |
| 2026-10-21 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 1 | Hafta 4 test turu, `main` (`ec7db3c`) üzerinde. TC-01…TC-08 geçti; yeni eklenen TC-09 (para alanları 2 ondalık) kaldı: 128 satır → bug #27 (@hilalelcin-stack). Grafik–analiz kontrolünde 2 hata: #28 (ortalama M4 ile uyuşmuyor), #29 (tarih biçimi) → @semadogaan. Analiz (M1–M5) nihai veriyle yeniden hesaplandı, `docs/analiz-g1.md` ile birebir tutarlı (#14). |
