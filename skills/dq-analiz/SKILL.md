---
name: dq-analiz
description: Grup A'nın sipariş verisinden (data/siparisler.csv) metrikleri src/dq_analiz.py ile hesaplar ve sonuçları, yorumları ve bulguları docs/analiz-g1.md'ye yazar. Veri analizi yapılacağı, metrik hesaplanacağı veya analiz raporu yazılacağı zaman kullan.
---

# dq-analiz — Metrik analizi ve bulgular

**Ne yapar:** BE'nin ürettiği veri dosyasından (`data/siparisler.csv`) 5 metriği (1 toplam, 1 ortalama, 2 kırılım, top-3) `src/dq_analiz.py` ile hesaplar; tabloları `docs/analiz-g1.md`'ye aktarır, her metriğin altına 1–2 cümle yorum, sonuna 3 bulgu + 1 eylem önerisi ve sınırlılıklar yazar. Uydurma sayı yazmaz: tablolardaki sayılar betiğin ana çıktısından, yorum/bulgu/sınırlılık cümlelerindeki sayılar `--ek` çıktısından gelir; ikisi de belirtilen veri commit'ine bağlıdır.

## Girdiler

- Veri: `data/siparisler.csv` (BE'nin "Veri hazır" yorumundaki commit)
- Şema: `docs/veri-sozlugu-g1.md`
- Test sonuçları (varsa): `python src/dq_test.py` — veride hata varsa analizden önce BE'ye bildirilir
- İlgili Issue'lar: G1-analiz (#14), G1-veri (#13), G1-gorsel (#15)

## Adımlar

### A) Analizi yaz (Hafta 3)

1. **Veri hazır mı?** #13'te BE'nin "Veri hazır — commit …" yorumunu bul; yoksa dur, analiz yazma.
2. **Güncel veriyi çek:** `git pull`.
3. **Hızlı kalite kontrolü:** `python src/dq_test.py`. Kalan test varsa sonucu #13'e yaz ve BE'yi etiketle; kritik hata (eksik sütun, boş değer, tutarsız `toplam_tutar`) varsa düzeltilene kadar analize geçme.
4. **Metrikleri hesapla:** `python src/dq_analiz.py --ek --cikti analiz-cikti.md`. Çıktının ilk kısmı M1–M5 tablolarıdır; sondaki "Ek istatistikler" bölümü yorumlarda kullanılacak destek sayılarıdır (sipariş tutarı ortalama/medyan/std, kategori başına ortalama adet ve tutar, aylık ciro, haftalık yoğunlaşma, en az ciro getiren ürünler, top-3 ürün fiyat aralığı). `analiz-cikti.md` geçicidir ve `.gitignore`'dadır, commit'lenmez.
5. **`docs/analiz-g1.md`'yi doldur:**
   - Başlıktaki veri satırına commit hash'i, satır sayısını ve tarih aralığını yaz.
   - M1–M5 bölümlerindeki "Sonuç" ve tabloları betik çıktısından birebir aktar.
   - Her metriğin altına 1–2 cümle yorum yaz: sayı ne anlatıyor, beklenenle uyumlu mu? **Yorumda geçen her sayı ya M1–M5 tablolarında ya da "Ek istatistikler" bölümünde birebir bulunmalı**; orada olmayan bir sayıya ihtiyaç varsa önce `src/dq_analiz.py`'ye ekle, sonra yaz.
   - **Bulgular:** veriye dayanan 3 somut gözlem (sayı vererek) + 1 uygulanabilir eylem önerisi.
   - **Sınırlılıklar:** verinin sonuçları sınırlayan özelliklerini sayıyla yaz (örn. haftalık sipariş sayısı az olduğu için haftalık cironun tek siparişlere duyarlılığı, fiyatın üründen değil kategoriden üretilmesi, dalgalanmaların nedensiz olması). Verinin sentetik olduğunu ve gerçek müşteri davranışı iddiası taşımadığını belirt (bkz. #30).
   - Başlığa "Veri kalitesi" satırını (`dq_test.py` sonucu, tarih) yaz; "Taslak" uyarı kutusu varsa kaldır.
6. **Commit at:** `G1-analiz: analiz-g1.md tamamlandı (#14)`
7. **Devir teslim (notlandırılır):** #15'e yaz: "Analiz hazır — docs/analiz-g1.md, commit <hash>. 5 metrik (2 kırılım + top-N) + bulgular. FE görselleştirebilir."
8. **#14'e kanıt yorumu yaz** (commit hash + dosyalar) ve Issue'yu kapat. Yorumun son satırı: `Üretim: dq-analiz skill'i ile, <araç>`.

### B) Nihai veriyle doğrula ve onayla (Hafta 4)

1. BE'nin son veri commit'ini bul: `git log -1 --format=%h -- data/siparisler.csv`. `docs/analiz-g1.md`'deki veri commit'iyle aynı değilse aşağıdaki adımları yeni dosyayla yap.
2. **Şema uyumu:** `python src/dq_test.py` → tüm testler geçmeli (çıkış kodu 0). Kalan test varsa uyumsuzlukları (senaryo + örnek satır) listeleyip #14'e yaz, BE'ye ata; onay verme.
3. **Metrik uyumu:** `python src/dq_analiz.py --ek --cikti analiz-cikti.md` çıktısındaki tablo satırlarını `docs/analiz-g1.md` ile karşılaştır. Fark varsa tabloları, yorumları ve başlıktaki veri commit'ini güncelle; yoksa yalnızca başlıktaki commit/tarih satırını güncelle.
4. Sonucu `tests/test-log.md`'ye tarihli satır olarak ekle (bkz. dq-test, B4).
5. **Kapanış yorumu (#14):** *"Analiz nihai veri üzerinde doğrulandı — onaylıyorum."* + veri commit'i + `dq_test.py` sonucu (ör. 12/12) + `Üretim: dq-analiz skill'i ile, <araç>`.

## Metrik tanım notları

- **Hafta:** pazartesi başlar (`resample("W-MON", label="left", closed="left")`); tablo ilk haftanın pazartesisini gösterir.
- **Kısmi haftalar:** veri 2026-01-01 (perşembe) başlayıp 2026-09-30 (çarşamba) bittiği için ilk ve son hafta 7 gün değildir. Bu iki hafta **en yüksek/en düşük** seçimine katılmaz ama **haftalık ortalamaya** (40 hafta) katılır; FE grafiğindeki ortalama çizgisi de aynı tanımı kullanır (#28). Tanımı değiştirirsen FE'ye haber ver.
- **Para biçimi:** çıktıda Türkçe biçim (`1.234.567,89 TL`, `%38,1`); CSV'de nokta ondalık.

## Ne zaman üretmez (reddeder)

- Veri gerçek kişi/müşteri bilgisi içeriyorsa veya gerçek veriyle analiz istenirse (AGENTS.md kural 2) — durur, PM'e bildirir.
- #13'te BE'nin "Veri hazır" yorumu yoksa veya `dq_test.py`'de kritik test (TC-01…TC-08, TC-10…TC-12) kalıyorsa — analiz yazmaz, sorunu #13'e yazar.
- İstenen sayı betik çıktısında yoksa — tahmin etmez; önce betiğe ekler.

## Örnek giriş → çıkış

**Giriş:** "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur." (veri commit `1f8beb8`)

**Çıkış (`docs/analiz-g1.md`'den kısaltılmış):**

```markdown
**Kullanılan veri:** `data/siparisler.csv` · commit `1f8beb8` · 400 satır · tarih aralığı 2026-01-01 – 2026-09-30

### M1 — Toplam ciro

**3.114.411,51 TL** (400 sipariş)

**Yorum:** … sipariş başına ortalama tutar 7.786 TL. Ancak medyan sipariş tutarı 4.031 TL …
```

Aynı veri commit'iyle betik her çalıştırmada aynı sayıları verir; tabloların `docs/analiz-g1.md` ile birebir aynı olması beklenir.

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
- **Yazar:** `docs/analiz-g1.md` (Hafta 4'te ayrıca `tests/test-log.md`'ye bir satır)
- **Çalıştırır:** `src/dq_analiz.py`, `src/dq_test.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (bu depoda Claude Code kullanıldı): "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur."

Elle: depo kökünde `python src/dq_analiz.py` (farklı dosya için `python src/dq_analiz.py yol/dosya.csv`; yorum sayıları için `--ek`; çıktıyı dosyaya yazmak için `--cikti dosya.md`). Gereken: Python 3 + pandas (`pip install pandas`).

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **İlk üretim (#14):** Claude'a bu skill'in adımları ve #14 Issue'su verildi; `src/dq_analiz.py`, bu skill ve `docs/analiz-g1.md` Claude ile üretildi (commit `b8e50a0`, `7840e97`; commit'lerde `Co-Authored-By: Claude` izi var).
- **Prompt:** "dq-analiz skill'ini kullanarak data/siparisler.csv'yi analiz et ve docs/analiz-g1.md'yi doldur."
- **Sonraki güncellemeler:** Sınırlılıklar bölümü (#30, `5539020`) ve nihai veriyle yeniden doğrulama (#27 sonrası, `1f8beb8`) Claude ile yapıldı.
- **Güncelleme (Hafta 4):** `--ek` ek istatistikleri, Hafta 4 doğrulama adımları, metrik tanım notları, örnek ve reddetme koşulları eklendi; M4 yorumundaki "en yüksek haftalar" düzeltildi (16 Mart değil 20 Temmuz) — Claude ile.
- **Ajan izi olmayan commit'ler:** `5539020` da Claude ile üretildi; dosyalar Tuana'nın hesabından yüklendiği için bu commit'lerde `Co-Authored-By` satırı yok.
- **Kural (Görev 2'den itibaren):** Commit'i ajan atar veya mesajın sonuna `Co-Authored-By:` satırı eklenir; kapanan Issue'ya "Üretim: dq-analiz skill'i ile, Claude" satırı yazılır.
