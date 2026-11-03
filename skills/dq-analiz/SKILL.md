---
name: dq-analiz
description: Grup A'nın sipariş verisinden veri sözlüğündeki metrikleri betikle hesaplar; sonuçları, yorumları, bulguları ve sınırlılıkları analiz belgesine (Görev 2: docs/analiz-g2.md) yazar ve gereksinim belgesini (docs/requirements.md) hazırlar. Veri analizi yapılacağı, metrik hesaplanacağı veya analiz raporu yazılacağı zaman kullan.
---

# dq-analiz — Metrik analizi, bulgular ve gereksinimler (DQ)

**Amaç:** Veri sözlüğünde tanımlı metrikleri, BE'nin "Veri hazır" dediği commit üzerinde **betikle** hesaplamak; her sayıyı yeniden üretilebilir kılmak ve FE'nin grafiklerine tek doğru kaynak olmak. Uydurma sayı yazmaz: tablolar betiğin ana çıktısından, yorum/bulgu/sınırlılık cümlelerindeki sayılar `--ek` çıktısından gelir.

**Rol:** DQ (analiz) · **Sahibi:** Görev 1'de Tuğba Tuana Kaygısız, Görev 2'de Sema Nur Doğan · **Issue:** G2-analiz (#62)

## Görev 2 bağlamı

| | Görev 2 |
|---|---|
| Veri | `data/siparisler-g2.csv` (BE'nin "Veri hazır" commit'i, #61) |
| Metrik tanımları | `docs/veri-sozlugu.md` → Metrikler: M1 net ciro · M2 ortalama sepet · M3 haftalık ciro (zaman kırılımı) · M4 kanal (kategorik kırılım) · M5 ilk 5 ürün (top-N) · M6 iade+iptal (ek) |
| Betik | `src/dq_analiz_g2.py` (Görev 1: `src/dq_analiz.py`, arşiv) |
| Çıktılar | `docs/analiz-g2.md`, `docs/requirements.md` |

## Adımlar

1. **Veri hazır mı?** G2-analiz Issue'sunda BE'nin "Veri hazır — commit …" yorumunu bul; yoksa dur. Veri commit'ini ve MD5'i not al.
2. **Kalite kontrolü:** Veri sözlüğün kalite kurallarını geçmiyorsa (dq-test) analize geçme; sorunu BE Issue'suna yaz.
3. **Hesapla:** `python src/dq_analiz_g2.py --ek --cikti analiz-cikti-g2.md` (geçici dosya, commit'lenmez). Ana çıktı M1–M6 tabloları; "Ek istatistikler" yorumlar için destek sayılarıdır (sepet dağılımı, kampanya/normal hafta, hafta içi/sonu, ürün sipariş sayıları, yeni/tekrar müşteri).
4. **`docs/analiz-g2.md`'yi yaz** (başlık sırası aşağıda):
   - En üstte veri commit'i, satır sayısı, tarih aralığı, MD5, parametreler.
   - M1–M6 tabloları çıktıdan **birebir**; her metriğin altında 1–2 cümle yorum.
   - **Bulgular:** sayıyla desteklenen 3 gözlem + 1 uygulanabilir eylem önerisi.
   - **Sınırlılıklar:** simülasyon kurgusundan gelen etkiler (ör. eşit olasılıklı ürün seçimi → M5 = en pahalı ürünler; sabit müşteri havuzu → yeni/tekrar ayrımı anlamsız). Sentetik veri uyarısı.
5. **`docs/requirements.md`'yi yaz (1 sayfa):** amaç · yaptıkları (numaralı) · yapmadıkları. Büyük proje önerisinin şablonu olacağı için yalnızca kodda gerçekten olanı yaz.
6. **Dal → PR:** `src/` içerdiği için PR'ı DQ açar, inceleyici **PM** (ders kuralı §3.5); onaydan sonra merge.
7. **Devir:** G2-gorsel Issue'suna *"Analiz hazır — `docs/analiz-g2.md`, commit `<hash>`"* + FE'nin kullanacağı sayılar (M3 ortalaması, M4 payları, M2 ortalama/medyan). Aynı yorum G2-test Issue'suna da yazılır: son ürün testinde grafikler bu sayılara karşı sınanır (grafik–analiz tutarlılığı).
8. **Kanıt + kapanış:** G2-analiz'e commit hash'leri + dosyalar + `Üretim: dq-analiz skill'i ile, <araç> — prompt özeti: …`

## Çıktı formatı kuralları

- `docs/analiz-g2.md` başlıkları: `Metrikler` (M1…M6) → `Bulgular` → `Sınırlılıklar` → `Yeniden üretme`.
- Para Türkçe biçimde (`11.973.617,93 TL`), yüzde `%44,3`; tarih `YYYY-MM-DD`; hafta `W-MON` (pazartesi başlangıçlı).
- Para metrikleri yalnızca `durum == "Teslim Edildi"`; M6 tüm siparişler.
- Yorumdaki her sayı betik çıktısından okunur; çıktıda olmayan bir sayı gerekiyorsa önce betiğe eklenir.

## Örnek giriş → çıkış

**Giriş (ajana):** "dq-analiz skill'ini kullanarak data/siparisler-g2.csv'yi (commit f9dfca7) analiz et; docs/analiz-g2.md ve docs/requirements.md'yi yaz; PM'in yeni/tekrar müşteri ve M5 notlarını değerlendir."

**Çıkış (kısaltılmış):**

| Kanal | Teslim edilen sipariş | Net ciro | Pay |
|---|---|---|---|
| Web | 3.244 | 5.300.953,08 TL | %44,3 |

> Web ve Mobil birlikte cironun %85,7'sini getiriyor ve aralarındaki fark yalnızca 2,9 puan.

## Ne zaman üretmez (reddeder)

- Veride **gerçek kişi/müşteri bilgisi** varsa veya gerçek veriyle analiz istenirse (ders kuralı §3.1) — durur, PM'e bildirir.
- BE'nin "Veri hazır" yorumu yoksa ya da veri kalite kurallarını geçmiyorsa — analiz yazmaz.
- İstenen sayı betik çıktısında yoksa — tahmin etmez; önce betiğe ekler.
- Simülasyon kurgusunun sonucu olan bir örüntüyü (ör. %81,8 "tekrar müşteri") gerçek davranış gibi sunma isteği — sınırlılık olarak yazar.

## Kullanılan dosyalar

- **Okur:** `data/siparisler-g2.csv`, `docs/veri-sozlugu.md`
- **Yazar:** `docs/analiz-g2.md`, `docs/requirements.md`
- **Çalıştırır:** `src/dq_analiz_g2.py` (Python 3 + pandas; `pip install pandas`)

## Nasıl çalıştırılır

Ajana: "dq-analiz skill'ini kullanarak data/siparisler-g2.csv'yi analiz et ve docs/analiz-g2.md'yi yaz."

Elle (depo kökünde):

```bash
pip install pandas
python src/dq_analiz_g2.py            # M1–M6
python src/dq_analiz_g2.py --ek       # + ek istatistikler
python src/dq_analiz_g2.py yol.csv    # başka parametrelerle üretilmiş dosya
```

## Üretim kaydı

**Görev 2 (Sema Nur Doğan, DQ):** Claude ile; önce bu skill Görev 2'ye güncellendi, sonra `src/dq_analiz_g2.py` yazıldı, veri commit `f9dfca7` üzerinde çalıştırıldı ve `docs/analiz-g2.md` + `docs/requirements.md` bu skill'in adımlarıyla yazıldı (#62). PM'in iki önerisi (yeni/tekrar müşteri, M5 sınırlılığı) veride denendi; ikisi de Sınırlılıklar'a yazıldı. Değerlendirme notu üzerine devir adımına G2-test eklendi.

**Görev 1 (Tuğba Tuana Kaygısız, DQ) — arşiv:** `src/dq_analiz.py` ve `docs/analiz-g1.md` (M1–M5, haftalık trend, top-3) Claude (Claude Code) ile üretildi; Hafta 4'te nihai veriyle doğrulandı (#14). Ajan izi olmayan commit'ler skill'in önceki sürümünde listelenmiştir.
