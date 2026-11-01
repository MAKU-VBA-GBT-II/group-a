# Kullanım Kılavuzu — Sepetix Analitik Mini Ürün (Görev 2)

> **Durum:** başlangıç sürümü (Hafta 6, #64). Kurulum ve 1 kullanım senaryosu yazıldı; analiz ve grafik adımları ilgili PR'lar merge edildikçe eklenecek.
> Ürünün amacı ve kapsamı: `docs/requirements.md` · Alanlar, parametreler, kurallar: `docs/veri-sozlugu.md`

## 1. Ürün ne yapar?

Sentetik e-ticaret sipariş verisi üretir (`src/simulasyon.py`), veriyi veri sözlüğüne göre sınar (`src/dq_test_g2.py`), metrikleri hesaplar (`src/dq_analiz_g2.py`) ve grafikleri çizer (`src/fe_gorsel.py`). Gerçek kişisel veri kullanılmaz; aynı parametre ve tohumla her çalıştırma birebir aynı dosyayı verir.

## 2. Kurulum

**Gerekenler:** Python 3.10 veya üstü (3.13 ile denendi), `pandas`, `numpy`, `matplotlib`, Git.

```bash
git clone https://github.com/MAKU-VBA-GBT-II/group-a.git
cd group-a
python -m pip install pandas numpy matplotlib
```

Kurulumu doğrulamak için:

```bash
python --version                  # Python 3.10+
python src/simulasyon.py --help   # parametre listesi görünmeli
```

> Tüm komutlar **depo kökünde** (`group-a/`) çalıştırılır; betikler `data/`, `docs/` gibi yolları buna göre arar.
> Windows'ta `python` yerine `py` gerekebilir.

## 3. Senaryo 1 — Veriyi üret ve kalitesini kontrol et

**Amaç:** varsayılan parametrelerle 26 haftalık sipariş dosyasını üretmek ve veri sözlüğündeki kurallara uyduğunu görmek.

**Adım 1 — Veriyi üret**

```bash
python src/simulasyon.py
```

Betik `data/siparisler-g2.csv` dosyasını yazar ve bir özet basar: kullanılan parametreler, satır/sütun sayısı, tarih aralığı, net ciro ve dosyanın MD5 özeti.

**Adım 2 — Kalite testlerini koş**

```bash
python src/dq_test_g2.py --grup A B
```

A ve B grupları (G2-TC-01…15) dosyanın yapısını ve içeriğini sınar: sütunlar, satır sayısı, tipler, aralıklar, boş değer, tarih sırası, ürün–kategori eşleşmesi, fiyat ve formüller.

**Beklenen sonuç**

![Senaryo 1 terminal çıktısı](img/kullanim-senaryo-1.png)

*Şekil 1 — Senaryo 1, `main` (`fe41763`) üzerinde, 2026-11-01.*

| Kontrol | Beklenen değer |
|---|---|
| Satır · Sütun | 8208 · 14 |
| Tarih aralığı | 2026-01-05 … 2026-07-05 (182 gün) |
| Net ciro (M1) | 11.973.617,93 TL |
| MD5 | `1b7f765e40e9b9897c82566a6442b45f` |
| Test özeti | `15/15 geçti`, çıkış kodu 0 |

MD5 aynıysa dosya depodaki sürümle birebir aynıdır (veri sözlüğü kural 12: tekrar üretilebilirlik).

**Sık karşılaşılan durumlar**

- `ModuleNotFoundError: No module named 'pandas'` → Kurulum adımındaki `pip install` komutunu çalıştırın.
- `FileNotFoundError: data/siparisler-g2.csv` → Komutu depo kökünde çalıştırdığınızdan emin olun.
- Test özeti `x/15` ve bazı satırlar `❌ Kaldı` → Kalan senaryonun "Gerçekleşen" sütunu sorunu söyler; `tests/test-cases.md`'deki aynı ID'ye bakın ve bir bug Issue'su açın.
- A/B testleri **varsayılan** parametrelerle üretilmiş dosyayı bekler (ör. satır sayısı 8.208). Farklı parametreyle ürettiğiniz dosyada `--dosya` ile koşarsanız G2-TC-03, 08 ve 15 kalabilir; bu bir hata değildir.

## 4. Parametreler (özet)

| Parametre | Varsayılan | Örnek |
|---|---|---|
| `--gun_sayisi` | 182 | `--gun_sayisi 10` → 424 satır |
| `--gunluk_siparis` | 40 | hafta içi günlük sipariş |
| `--hafta_sonu_katsayisi` | 1.3 | hafta sonu çarpanı |
| `--kampanya_katsayisi` | 1.5 | kampanya haftası çarpanı |
| `--kampanya_donemleri` | `2026-03-09:2026-03-15,2026-05-11:2026-05-17` | `BAŞ:SON` biçiminde, virgülle ayrılır |
| `--baslangic_tarihi` | 2026-01-05 | `YYYY-AA-GG` |
| `--musteri_sayisi` | 1500 | müşteri havuzu |
| `--tohum` | 42 | farklı tohum → farklı ama geçerli dosya |
| `--cikti` | `data/siparisler-g2.csv` | başka dosyaya yazmak için |

İzinli aralıklar ve satır sayısı formülü: `docs/veri-sozlugu.md` → Parametreler. Geçersiz parametre davranışı PR #72 ile düzeltiliyor (#76, #77).

## 5. Sonraki bölümler (eklenecek)

- Senaryo 2 — Analizi çalıştır: `python src/dq_analiz_g2.py` → `docs/analiz-g2.md` (PR #75 merge edilince)
- Senaryo 3 — Grafikleri üret: `python src/fe_gorsel.py` → `visuals/` (FE PR'ı merge edilince)
- Senaryo 4 — Kendi parametrelerinle veri üret ve hata mesajlarını oku (PR #72 merge edilince)

---
Üretim: dq-test skill'i ile, Claude — prompt özeti: "Merge edilmiş ürün üzerinde test turunu koş, sonuçları tests/test-log.md'ye tarihli yaz, docs/user-manual.md'ye kurulum ve ekran görüntülü 1 senaryo ile başla."
