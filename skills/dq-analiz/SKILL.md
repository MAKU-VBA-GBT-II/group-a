---
name: dq-analiz
description: Grup A'nın sipariş verisinden (data/siparisler.csv) metrikleri src/dq_analiz.py ile hesaplar ve sonuçları, yorumları ve bulguları docs/analiz-g1.md'ye yazar. Veri analizi yapılacağı, metrik hesaplanacağı veya analiz raporu yazılacağı zaman kullan.
---

# dq-analiz — Metrik analizi ve bulgular

**Ne yapar:** BE'nin ürettiği veri dosyasından (`data/siparisler.csv`) 5 metriği (1 toplam, 1 ortalama, 2 kırılım, top-3) `src/dq_analiz.py` ile hesaplar; tabloları `docs/analiz-g1.md`'ye aktarır, her metriğin altına 1–2 cümle yorum, sonuna 3 bulgu + 1 eylem önerisi yazar. Uydurma sayı yazmaz; her sayı betik çıktısından ve belirtilen veri commit'inden gelir.

## Girdiler

- Veri: `data/siparisler.csv` (BE'nin "Veri hazır" yorumundaki commit)
- Şema: `docs/veri-sozlugu-g1.md`
- Test sonuçları (varsa): `python src/dq_test.py` — veride hata varsa analizden önce BE'ye bildirilir
- İlgili Issue'lar: G1-analiz (#14), G1-veri (#13), G1-gorsel (#15)

## Adımlar

1. **Veri hazır mı?** #13'te BE'nin "Veri hazır — commit …" yorumunu bul; yoksa dur, analiz yazma.
2. **Güncel veriyi çek:** `git pull`.
3. **Hızlı kalite kontrolü:** `python src/dq_test.py`. Kalan test varsa sonucu #13'e yaz ve BE'yi etiketle; kritik hata (eksik sütun, boş değer, tutarsız `toplam_tutar`) varsa düzeltilene kadar analize geçme.
4. **Metrikleri hesapla:** `python src/dq_analiz.py --cikti analiz-cikti.md` (çıktı dosyası geçicidir, commit'lenmez).
5. **`docs/analiz-g1.md`'yi doldur:**
   - Başlıktaki veri satırına commit hash'i, satır sayısını ve tarih aralığını yaz.
   - M1–M5 bölümlerindeki "Sonuç" ve tabloları betik çıktısından birebir aktar.
   - Her metriğin altına 1–2 cümle yorum yaz: sayı ne anlatıyor, beklenenle uyumlu mu?
   - **Bulgular:** veriye dayanan 3 somut gözlem (sayı vererek) + 1 uygulanabilir eylem önerisi.
   - **Sınırlılıklar:** verinin sonuçları sınırlayan özelliklerini sayıyla yaz (örn. haftalık sipariş sayısı az olduğu için haftalık cironun tek siparişlere duyarlılığı, fiyatın üründen değil kategoriden üretilmesi, dalgalanmaların nedensiz olması). Verinin sentetik olduğunu ve gerçek müşteri davranışı iddiası taşımadığını belirt (bkz. #30).
   - "Taslak" uyarı kutusunu kaldır.
6. **Commit at:** `G1-analiz: analiz-g1.md tamamlandı (#14)`
7. **Devir teslim (notlandırılır):** #15'e yaz: "Analiz hazır — docs/analiz-g1.md, commit <hash>. 5 metrik (2 kırılım + top-N) + bulgular. FE görselleştirebilir."
8. **#14'e kanıt yorumu yaz** (commit hash + dosyalar) ve Issue'yu kapat.

## Metrik formülleri

| # | Metrik | Formül |
|---|---|---|
| M1 | Toplam ciro | `Σ toplam_tutar` |
| M2 | Sipariş başına ortalama adet | `Σ adet / sipariş sayısı` |
| M3 | Kategori bazlı ciro | kategoriye göre `Σ toplam_tutar` (+ pay %) |
| M4 | Haftalık ciro trendi | pazartesi başlangıçlı haftaya göre `Σ toplam_tutar` |
| M5 | Top-3 ürün | ürüne göre `Σ toplam_tutar`, ilk 3 (+ pay %) |

## Kullanılan dosyalar

- **Okur:** `data/siparisler.csv`, `docs/veri-sozlugu-g1.md`
- **Yazar:** `docs/analiz-g1.md`
- **Çalıştırır:** `src/dq_analiz.py`, `src/dq_test.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (bu depoda Claude Code kullanıldı): "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur."

Elle: depo kökünde `python src/dq_analiz.py` (farklı dosya için `python src/dq_analiz.py yol/dosya.csv`; çıktıyı dosyaya yazmak için `--cikti dosya.md`).

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **İlk üretim (#14):** Claude'a bu skill'in adımları ve #14 Issue'su verildi; `src/dq_analiz.py`, bu skill ve `docs/analiz-g1.md` Claude ile üretildi (commit `b8e50a0`, `7840e97`; commit'lerde `Co-Authored-By: Claude` izi var).
- **Prompt:** "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur."
- **Sonraki güncellemeler:** Sınırlılıklar bölümü (#30, `5539020`) ve nihai veriyle yeniden doğrulama (#27 sonrası, `1f8beb8`) Claude ile yapıldı.
- **Ajan izi olmayan commit'ler:** `5539020` da Claude ile üretildi; dosyalar Tuana'nın hesabından yüklendiği için bu commit'lerde `Co-Authored-By` satırı yok.
- **Kural (Görev 2'den itibaren):** Commit'i ajan atar veya mesajın sonuna `Co-Authored-By:` satırı eklenir; kapanan Issue'ya "Üretim: dq-analiz skill'i ile, Claude" satırı yazılır.
