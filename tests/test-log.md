# Test Kaydı — Veri Kalitesi

Her test çalıştırması bu dosyaya bir satır olarak eklenir (bkz. `skills/dq-test/SKILL.md`, adım B4).

| Tarih | Test edilen dosya | Veri commit'i | Komut | Geçti | Kaldı | Not |
|---|---|---|---|---|---|---|
| 2026-10-17 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 0 | İlk çalıştırma; BE verisi (#13) şemaya tam uyuyor. Ayrıntılar `tests/test-cases.md`. |
| 2026-10-18 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 0 | PR #24 (G1-gorsel) birleştikten sonra `main` (`7278b05`) üzerinde DQ kontrolü; grafiklerdeki kategori payları ve en yüksek hafta `docs/analiz-g1.md` ile uyuşuyor (#15). |
| 2026-10-21 | `data/siparisler.csv` | `fa3b368` | `python src/dq_test.py` | 8 | 1 | Hafta 4 test turu, `main` (`ec7db3c`) üzerinde. TC-01…TC-08 geçti; yeni eklenen TC-09 (para alanları 2 ondalık) kaldı: 128 satır → bug #27 (@hilalelcin-stack). Grafik–analiz kontrolünde 2 hata: #28 (ortalama M4 ile uyuşmuyor), #29 (tarih biçimi) → @semadogaan. Analiz (M1–M5) nihai veriyle yeniden hesaplandı, `docs/analiz-g1.md` ile birebir tutarlı (#14). |
| 2026-10-22 | `data/siparisler.csv` | `1f8beb8` | `python src/dq_test.py` | 9 | 0 | #27 düzeltmesi sonrası yeniden test, `main` (`1aad2be`) üzerinde. TC-09 artık geçiyor (biçim dışı satır = 0). `python src/veri_uret.py` yeniden çalıştırıldı, dosya birebir aynı (tohum 42). Analiz (M1–M5) yeni dosyayla yeniden hesaplandı: 51/51 tablo satırı `docs/analiz-g1.md` ile aynı, değerler değişmedi. |
| 2026-10-22 | `data/siparisler.csv` | `1f8beb8` | Elle kontrol (TC-03) | 1 | 0 | Başlıkta 9 sütun var; adlar ve sıra veri sözlüğüyle birebir aynı: `siparis_id, siparis_tarihi, kategori, urun, adet, birim_fiyat, toplam_tutar, sehir, odeme_tipi`. |
