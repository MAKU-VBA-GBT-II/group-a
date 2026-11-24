---
name: be-simulasyon
description: Grup A'nın Görev 2 sipariş verisini (data/siparisler-g2.csv) DQ'nun şemasına (docs/veri-sozlugu.md) birebir uyan, parametreli ve sabit tohumlu bir simülasyonla üretir. Veri üretilecek, parametreyle yeniden üretilecek veya şema değiştiğinde betik güncellenecek zaman kullan.
---

# be-simulasyon — Görev 2 parametreli sipariş simülasyonu

**Amaç:** DQ'nun yayımladığı `docs/veri-sozlugu.md` şemasına birebir uyan, parametreleri komut satırından değiştirilebilen ve aynı parametre + aynı tohumla bayt bayt aynı dosyayı üreten sentetik sipariş verisini `src/simulasyon.py` ile üretmek.

Gerçek kişi ya da işletme verisi asla kullanılmaz — tüm değerler simülasyon ürünüdür (AGENTS.md kural 2, ders kuralı §3.1). Müşteri yalnızca sentetik kimlikle (`M0001`) temsil edilir.

## Girdiler

- **Şema (tek kaynak):** `docs/veri-sozlugu.md` (DQ, #60). Bu skill şemayı **kopyalamaz**, ona uyar; şema ile betik arasında fark varsa doğru olan sözlüktür.
- DQ test senaryoları: `tests/test-cases.md` (#64; Görev 2 senaryoları yazıldıkça betiğin iç kontrolleri bunların aynası olur)
- İlgili Issue'lar: G2-veri (#61), devir: G2-analiz (#62), G2-gorsel (#63), G2-test (#64); Görev 1 sınırlılıkları (#30); para alanlarının 2 ondalık biçimi (#27)

## Çıktı formatı kuralları

- **Dosya:** `data/siparisler-g2.csv` — 1 satır = 1 sipariş, **14 sütun**, sözlükteki sırayla:
  `siparis_id, siparis_tarihi, musteri_id, kanal, kategori, urun, adet, birim_fiyat, indirim_orani, kampanya, toplam_tutar, sehir, odeme_tipi, durum`
- Virgül ayraçlı, nokta ondalıklı, UTF-8, satır sonu `\n`, indeks sütunu yok.
- `birim_fiyat`, `indirim_orani`, `toplam_tutar` ham metinde **tam 2 ondalık** (`1299.00`, `0.20`): CSV `float_format="%.2f"` ile yazılır (#27).
- Tarih `YYYY-MM-DD`; dosya `siparis_tarihi` artan, `siparis_id` 1…N ardışık.
- **Satır sayısı rastgele değildir**, sözlükteki formülle günden güne hesaplanır: `gun_adet = max(1, floor(gunluk_siparis × gun_k + 0.5))`, `gun_k` hafta sonunda `× hafta_sonu_katsayisi`, kampanya gününde `× kampanya_katsayisi`. `max(1, …)` her günün dosyada en az bir kez geçmesini sağlar (ör. `gunluk_siparis=1`, `hafta_sonu_katsayisi=0.4` → hafta sonu 0 yerine 1 sipariş); yoksa kural 5 izinli parametrelerle bile düşer (PR #72 incelemesi). Varsayılanla **N = 8.208**.
- Kampanya dönemlerinden hiçbiri simülasyon aralığıyla kesişmiyorsa betik hata vermez (sözlük yasaklamıyor) ama konsola `Uyarı: … kesişmiyor; dosyada kampanyalı sipariş yok` yazar.
- `toplam_tutar` **hesaplanır**: `round(adet × birim_fiyat × (1 − indirim_orani), 2)`.
- `birim_fiyat` ürünün liste fiyatından en fazla `fiyat_sapmasi` (varsayılan ±%5) sapar (#30 çözümü). Sınırın yuvarlamayla aşılmaması için fiyat **kuruş cinsinden tamsayı** çekilir: `[⌈liste × (1 − sapma)⌉, ⌊liste × (1 + sapma)⌋]` kuruş, uçlar dahil, tam ondalıkla (`Decimal`) hesaplanır, sonra 100'e bölünür. Varsayılanda bu `[liste × 95, liste × 105]` kuruştur.

## Parametreler

Betiğin başında sabit olarak tanımlıdır **ve** komut satırından değiştirilebilir (`python src/simulasyon.py --help`). Varsayılanlar ve izinli aralıklar sözlükteki tabloyla aynıdır:

| Parametre | Varsayılan | Komut satırı |
|---|---|---|
| `gun_sayisi` | 182 | `--gun_sayisi 10` |
| `gunluk_siparis` | 40 | `--gunluk_siparis 10` |
| `hafta_sonu_katsayisi` | 1.3 | `--hafta_sonu_katsayisi 1.0` |
| `kampanya_katsayisi` | 1.5 | `--kampanya_katsayisi 2.0` |
| `kampanya_donemleri` | `2026-03-09:2026-03-15,2026-05-11:2026-05-17` | `--kampanya_donemleri "2026-02-02:2026-02-08"` |
| `baslangic_tarihi` | 2026-01-05 | `--baslangic_tarihi 2026-02-02` |
| `musteri_sayisi` | 1500 | `--musteri_sayisi 300` |
| `tohum` | 42 | `--tohum 7` |
| `urun_agirliklari` (isteğe bağlı) | boş = 25 ürün eşit olasılık | `--urun_agirliklari "1,1,1,0.3,1,…"` (ürün sayısı kadar) |
| `urun_listesi` (isteğe bağlı, Duyuru-10) | boş = betikteki 25 ürün | `--urun_listesi data/urun-listesi-ornek.csv` |
| `fiyat_sapmasi` (Duyuru-10) | 0.05 (0–0.5) | `--fiyat_sapmasi 0.10` |
| (çıktı yolu) | `data/siparisler-g2.csv` | `--cikti data/deneme.csv` |

Deneme çalıştırmaları (`gun_sayisi=10` vb.) için **`--cikti` ile `data/` dışında** bir dosya verilir (ör. `/tmp/deneme-10gun.csv`); böylece deneme dosyası yanlışlıkla commit'lenemez. `data/siparisler-g2.csv` yalnızca varsayılanlarla üretilir.

### Hata yönetimi (geçersiz parametre)

Parametreler **üretimden önce** `parametreleri_dogrula()` ile sözlükteki aralıklara göre kontrol edilir (aralıklar betiğin başında `PARAMETRE_ARALIKLARI`). Geçersiz bir değerde:

- `ValueError` verilir; mesaj **parametrenin adını, izinli aralığı/biçimi ve verilen değeri** Türkçe söyler.
- Komut satırında betik çökmez (traceback yok): `Hata (ValueError): <mesaj>` yazar, **1** koduyla çıkar. Hata yutulmaz; betik `import` edilip `main()` çağrılırsa `ValueError` olduğu gibi yükselir.
- **Hiçbir dosya yazılmaz** (doğrulama, çıktı klasörü oluşturulmadan önce çalışır).
- Tipler `argparse`'a bırakılmaz: `--gun_sayisi abc` de İngilizce argparse hatası yerine aynı biçimde Türkçe `ValueError` verir.

| Girdi | Mesaj |
|---|---|
| `--gun_sayisi 0` / `-3` | `gun_sayisi 1–366 arasında olmalı, verilen: 0` |
| `--gun_sayisi abc` | `gun_sayisi tamsayı olmalı (1–366 arasında), verilen: 'abc'` |
| `--gunluk_siparis 0` | `gunluk_siparis 1–500 arasında olmalı, verilen: 0` |
| `--musteri_sayisi 10000` | `musteri_sayisi 1–9999 arasında olmalı, verilen: 10000` |
| `--hafta_sonu_katsayisi nan` | `hafta_sonu_katsayisi 0.1–5.0 arasında olmalı, verilen: nan` |
| `--tohum -1` | `tohum 0 veya büyük olmalı, verilen: -1` |
| `--baslangic_tarihi 2026-13-01` | `baslangic_tarihi geçerli bir YYYY-MM-DD tarihi olmalı, verilen: '2026-13-01'` |
| `--kampanya_donemleri 2026-03-09` | `kampanya_donemleri her dönem BAŞ:SON (YYYY-MM-DD:YYYY-MM-DD) biçiminde, dönemler virgülle ayrılmış olmalı, verilen: '2026-03-09'` |
| `--kampanya_donemleri 2026-03-15:2026-03-09` | `kampanya_donemleri içinde başlangıç sondan sonra olamaz, verilen: '2026-03-15:2026-03-09'` |

### Ürün ağırlıkları (isteğe bağlı, Görev 3)

Varsayılanda 25 ürün **eşit olasılıkla** seçilir; bu yüzden M5 (ciroda ilk 5 ürün) en çok satanları değil liste fiyatı en yüksek ürünleri gösterir (bkz. Bilinen sınırlılıklar). `--urun_agirliklari` ile ürünlere satış ağırlığı verilebilir:

- Değer **25 sayı**, virgülle ayrılmış, ürünler `URUNLER` sırasıyla (Elektronik 5 → Giyim 5 → Ev & Yaşam 5 → Kozmetik 5 → Kitap 5). Sayılar toplamı 1 olacak şekilde normalize edilir (`1,1,2` ile `0.25,0.25,0.5` aynıdır).
- **Boş bırakılırsa** (varsayılan) eski `rng.integers` satırı **aynen** çalışır: dosya, MD5 `1b7f765e…` ve tüm testler değişmez.
- Verilirse ürün `rng.choice(25, size=n, p=ağırlıklar)` ile seçilir. Satır sayısı ağırlıktan etkilenmez; ama `rng` akışı değiştiği için **dosyanın tamamı** (fiyat, adet, kanal… dahil) farklı çıkar. Eşit ağırlık (`1,1,…,1`) bile **farklı MD5** verir; bu yüzden eşit olasılık için parametreyi boş bırak.
- Negatif değer `--urun_agirliklari=-1,…` biçiminde (eşittir ile) verilmelidir; yoksa `argparse` değeri seçenek sanır.
- Yeni alan veya değer eklenmez, şema aynıdır; yalnızca `urun` dağılımı değişir. Sözlükteki parametre tablosuna eklenmesi DQ'nun işidir (Hilal'e bildirildi, bkz. PR).

| Girdi | Mesaj |
|---|---|
| `--urun_agirliklari 1,2,3` | `urun_agirliklari 25 sayı içermeli (virgülle ayrılmış), verilen: 3 değer` |
| 25 değerden biri `a` | `urun_agirliklari yalnızca sayı içermeli, verilen: 'a'` |
| 25 değerden biri `-1` veya `nan` | `urun_agirliklari her değer 0 veya büyük bir sayı olmalı, verilen: '-1'` |
| 25 değerin hepsi `0` | `urun_agirliklari toplamı 0'dan büyük olmalı, verilen: hepsi 0` |
| Çok büyük değerler (ör. 25 × `1e308`) | Hata yok: önce en büyük değere bölünüp normalize edilir, toplam taşmaz (PR #95 incelemesi) |

Bu hatalarda da betik çökmez, **1** koduyla çıkar ve dosya yazılmaz.

Sınır değerler geçerlidir (`gun_sayisi=1` ve `366`, `musteri_sayisi=9999`, `tohum=0`); boş `kampanya_donemleri` (`""`) kampanyasız dönem demektir. Sözlüğe yeni bir parametre veya aralık eklenirse `PARAMETRE_ARALIKLARI` ve bu tablo birlikte güncellenir.

### Ürün listesi ve fiyat sapması (isteğe bağlı, Duyuru-10)

Ajan 1'in topladığı rakip fiyatlarıyla uyuşması için ürünler ve liste fiyatları dışarıdan verilebilir (`docs/oneri.md` §4).

- `--urun_listesi <yol>`: UTF-8 CSV (Excel BOM'u kabul edilir), virgül ayraçlı, nokta ondalıklı. Zorunlu sütunlar `kategori,urun,liste_fiyati`; isteğe bağlı `fiyat_sapmasi` (ürün başına; boş hücre = `--fiyat_sapmasi`). `liste_fiyati` TL, > 0, en fazla 2 ondalık. Ürün adı tekil olmalı. Örnek: `data/urun-listesi-ornek.csv` (bugünkü 25 ürün).
- `--fiyat_sapmasi <oran>`: tüm ürünler için varsayılan sapma, 0–0.5 (vars. 0.05). `0` verilirse `birim_fiyat` = liste fiyatı.
- **Boş bırakılırsa** (varsayılan) betikteki 25 ürün kullanılır ve dosya, MD5 `1b7f765e…` değişmez. `data/urun-listesi-ornek.csv` ile çalıştırmak da aynı MD5'i verir (aynı ürünler, aynı sıra).
- Liste verildiğinde `kategori`/`urun` geçerli değerleri, kural 7 (ürün kendi kategorisinde) ve kural 8 (fiyat sınırı) bu listeden kontrol edilir; `urun_agirliklari` ürün sayısı kadar değer almalıdır.
- Şema (14 sütun) değişmez. Sözlükteki parametre tablosuna eklenmesi DQ'nun işidir (`docs/oneri.md` §4).

| Girdi | Mesaj |
|---|---|
| Dosya yok | `urun_listesi dosyası bulunamadı, verilen: 'yok.csv'` |
| `liste_fiyati` sütunu yok | `urun_listesi şu sütunları içermeli: kategori, urun, liste_fiyati; eksik: liste_fiyati` |
| Başlık var, satır yok | `urun_listesi en az 1 ürün içermeli, verilen: '…'` |
| Aynı ürün iki kez | `urun_listesi 3. satır: urun iki kez geçiyor, verilen: 'B'` |
| `liste_fiyati` `-3` / `nan` | `urun_listesi 2. satır: liste_fiyati 0'dan büyük olmalı, verilen: '-3'` |
| `liste_fiyati` `1.234` | `urun_listesi 2. satır: liste_fiyati en fazla 2 ondalık olmalı, verilen: '1.234'` |
| Satırda `fiyat_sapmasi` `0.9` | `urun_listesi 2. satır: fiyat_sapmasi 0.0–0.5 arasında olmalı, verilen: '0.9'` |
| `--fiyat_sapmasi 0.6` | `fiyat_sapmasi 0.0–0.5 arasında olmalı, verilen: 0.6` |
| 3 ürünlük listeyle `--urun_agirliklari 1,2` | `urun_agirliklari 3 sayı içermeli (virgülle ayrılmış), verilen: 2 değer` |

## Üretim sırası (bayt bayt aynı dosya için)

1. Günler `baslangic_tarihi`'nden itibaren sırayla gezilir, her günün sipariş adedi formülle hesaplanır; `siparis_tarihi` ve `kampanya` bu sırayla açılır (dosya zaten tarihe göre sıralı çıkar).
2. Tüm rastgele değerler tek `rng = numpy.random.default_rng(tohum)` nesnesinden **bu sırayla** ve tüm N satır için çekilir:
   `urun` (25 ürün; varsayılanda eşit olasılık `rng.integers`, `--urun_agirliklari` verilmişse `rng.choice(p=…)`; `kategori` üründen gelir) → `birim_fiyat` (kuruş) → `adet` → `kanal` → `sehir` → `odeme_tipi` → `durum` → `musteri_id` → `indirim_orani`.
   Ağırlıklar sözlükteki **Ağırlıklı alanlar** tablosundandır. `indirim_orani` her satır için çekilir, kampanya dışı satırlarda `0.00` yapılır.
3. `toplam_tutar` hesaplanır, `siparis_id` 1…N verilir.

Sıra veya çağrı değişirse kurallara uyan ama farklı bir dosya çıkar; MD5 değişir.

**Dikkat:** Her alan tüm N satır için tek seferde çekildiğinden, N'yi değiştiren **her** parametre (`gun_sayisi`, `gunluk_siparis`, katsayılar, `kampanya_donemleri`, `baslangic_tarihi`) dosyanın **tamamını** değiştirir. Ör. `gun_sayisi=10` dosyasının ilk satırları, varsayılan dosyanın ilk satırlarıyla aynı **değildir**. `tohum` ve `musteri_sayisi` N'yi değiştirmez ama onlar da farklı bir dosya üretir.

## Adımlar

1. **Şemayı oku:** `docs/veri-sozlugu.md` ve G2-veri Issue'sundaki DQ'nun "Şema yayımlandı" devir yorumu. Devir yorumu yoksa **üretime başlama**. Belirsiz bir yer varsa Issue'ya yaz, DQ ile netleştir; şemayı tek taraflı değiştirme.
2. **Betiği yalnızca gerekirse yaz/güncelle:** `src/simulasyon.py` varsa ve şema değişmediyse yeniden yazma, 3. adıma geç. Sabitler (`SUTUNLAR`, `KATEGORI_URUN`, ağırlıklar, parametre varsayılanları) dosyanın başındadır; gömülü sihirli sayı bırakma.
3. **Üret:** Depo kökünde `python src/simulasyon.py`.
4. **Kendi kontrolünü yap.** Parametre hatası varsa betik daha 3. adımda durur (bkz. **Hata yönetimi**). Betik sözlüğün **Veri kalitesi kuralları 1–11**'i yazmadan önce kendisi kontrol eder (`kontrol()` ile, `assert` değil; `python -O` ile de atlanmaz), biri kalırsa `ValueError` verir ve dosya yazılmaz; yazdıktan sonra dosyayı diskten geri okuyup aynı metin mi diye bakar. Elle yapılacaklar:
   - **Kural 12 (tekrarlanabilirlik):** betiği ikinci kez çalıştır, konsoldaki `MD5` aynı mı?
   - **Parametre davranışı:** sözlükteki satır sayısı tablosu — `--gun_sayisi 10` → 424, `--gun_sayisi 7` → 304, `--gun_sayisi 10 --gunluk_siparis 10` → 106 (deneme dosyası `data/` dışına, `--cikti` ile).
5. **Commit at** (`feature/veri` dalında; `main`'e doğrudan commit yok). Mesajda şema bulunur: satır sayısı + sütun listesi. Biçim: `G2-veri: <ne değişti> (#61)`.
6. **PR aç:** başlık `G2 parametreli simülasyon`, açıklamada `Closes #61`, kendi kontrol sonuçları ve üretim satırı; Reviewers: DQ. DQ yorumlarına PR üzerinden cevap ver, düzeltmeleri aynı dala push et; DQ **Approve** verdikten sonra merge'ü PR sahibi yapar.
7. **Devir yorumu merge'ün hemen ardından:** veriyi kullanan her Issue'ya (G2-analiz #62, G2-gorsel #63 **ve G2-test #64**; Görev 1'deki #45 geri bildirimi gereği test Issue'su da listede) ayrı ayrı şablonla yorum yaz; G2-veri Issue'suna kanıt yorumu (commit hash + dosya + satır sayısı + tohum + MD5). Her kapanış yorumunun ve PR açıklamasının sonunda üretim satırı olur.

### Devir yorumu şablonu

> Veri hazır — commit `<hash>`, dosya `data/siparisler-g2.csv` (8.208 satır, 14 sütun, tohum 42, MD5 `<md5>`). Şema: `docs/veri-sozlugu.md`.

### Üretim satırı

> Üretim: be-simulasyon skill'i ile, Claude — prompt özeti: "<ne istendi>"

## Ne zaman üretmez (reddetme durumları)

- **Gerçek kişisel veri istenirse** (ad-soyad, TC kimlik no, telefon, e-posta, açık adres, gerçek müşteri/sipariş kaydı, gerçek bir firmanın satış verisi): üretmez, nedenini söyler, alanın sentetik karşılığını önerir (ör. `musteri_id = M0427`).
- **Şema yayımlanmadan** (G2-veri Issue'sunda DQ'nun devir yorumu yokken) üretim istenirse: başlamaz, DQ'ya sorar.
- **Şemada olmayan bir alan, değer veya aralık** istenirse: tek taraflı eklemez; önce DQ'nun sözlüğü güncellemesini ister.
- **Görev 1 verisini değiştirmek** istenirse (`data/siparisler.csv`, `src/veri_uret.py`, `docs/veri-sozlugu-g1.md`): yapmaz. G1 analizi, testleri ve grafikleri bu dosyalara bağlıdır (#30 kararı); bunlar `be-veri` skill'inin alanıdır. Görev 2 yalnızca `data/siparisler-g2.csv`'ye yazar.
- **`main`'e doğrudan commit** istenirse: yapmaz; dal → PR → inceleme → merge.

## Örnek giriş ve çıkış

**Örnek 1 — üretim**

- **Giriş (prompt):** "be-simulasyon skill'ini kullanarak docs/veri-sozlugu.md şemasına göre data/siparisler-g2.csv'yi varsayılan parametrelerle üret."
- **Çıkış:** `data/siparisler-g2.csv` — 8.208 satır, 14 sütun, 2026-01-05 … 2026-07-05 (182 gün). İlk satırlar:

```csv
siparis_id,siparis_tarihi,musteri_id,kanal,kategori,urun,adet,birim_fiyat,indirim_orani,kampanya,toplam_tutar,sehir,odeme_tipi,durum
1,2026-01-05,M1387,Mobil,Elektronik,Powerbank,2,587.83,0.00,0,1175.66,İstanbul,Kredi Kartı,Teslim Edildi
2,2026-01-05,M0826,Mobil,Kozmetik,Ruj,5,165.48,0.00,0,827.40,İstanbul,Banka Kartı,Teslim Edildi
```

Konsol özeti (kısaltılmış): `Satır: 8208 · Sütun: 14`, `Tarih: 2026-01-05 .. 2026-07-05 · Farklı gün: 182`, `Kampanyalı sipariş: 912 · Teslim edilen: 7383`, `Net ciro (teslim edilen, M1): 11,973,617.93 TL`, `MD5: 1b7f765e40e9b9897c82566a6442b45f`, `Tüm iç kontroller geçti …`.

**Örnek 2 — parametre değişikliği**

- **Giriş:** "gun_sayisi=10 ile dene, ana dosyayı bozma."
- **Çıkış:** `python src/simulasyon.py --gun_sayisi 10 --cikti /tmp/deneme-10gun.csv` → `Satır: 424`, `Tarih: 2026-01-05 .. 2026-01-14`. Deneme dosyası `data/` dışında kalır, commit'lenmez; `data/siparisler-g2.csv` değişmez.

**Örnek 3 — ret**

- **Giriş:** "Müşterilere gerçek ad-soyad ve telefon numarası ekle, daha gerçekçi olsun."
- **Çıkış:** Üretim yapılmaz, dosya değişmez. Yanıt: "Gerçek kişisel veri üretemem (AGENTS.md kural 2). Müşteriler zaten sentetik `musteri_id` (ör. `M0427`) ile temsil ediliyor; başka bir sentetik alan gerekiyorsa önce DQ'nun `docs/veri-sozlugu.md`'ye eklemesi gerekir."

## #30 sınırlılıkları — Görev 2'de nasıl kapandı

| Görev 1 sınırlılığı | Görev 2 simülasyonundaki karşılığı |
|---|---|
| Haftada ~10 sipariş, tek büyük sipariş haftalık ciroyu ikiye katlıyor | Haftada ~284 teslim edilen sipariş; `adet` 1–5 ve %50'si 1 |
| Ürünün kendine özgü fiyatı yok | `birim_fiyat` = liste fiyatı ±`fiyat_sapmasi` (vars. %5; kuruş tamsayısıyla, sınır aşılamaz) |
| Dalgalanmaların nedeni yok | Hafta sonu `× 1,3` ve kampanya `× 1,5` + indirim; parametreli |

## Bilinen sınırlılıklar ve açıklar

- **Ürünler varsayılanda eşit sıklıkta satılır** (şema gereği). Bu yüzden "ciroda ilk 5 ürün" (M5) en çok satanları değil, liste fiyatı en yüksek ürünleri gösterir (Akıllı Saat, Kahve Makinesi, Mont, Spor Ayakkabı, Halı). Analizde bu not edilmelidir. Görev 3'te `--urun_agirliklari` eklendi (bkz. **Ürün ağırlıkları**): ağırlık verilirse M5 değişir; varsayılan dosya ve bu sınırlılık aynen kalır. Sözlüğe ekleme DQ'nun işidir.
- **Haftalık ciro oynaklığı** (değişim katsayısı) toplamda %13,0, kampanyasız haftalarda %7,9. Kalan oynaklık büyük ölçüde fiyat karmasından (99 – 3.499 TL) gelir; kampanya haftalarındaki sıçrama bilerek modellenmiştir.
- ~~Geçersiz parametre `ValueError` vermiyor~~ — Hafta 6'da `fix/error-handling` ile kapandı (bkz. **Hata yönetimi**).
- **Müşteri havuzu rastgele:** `musteri_id` havuzdan eşit olasılıkla çekildiği için siparişlerin çoğu zamanla "tekrar müşteri" görünür (varsayılanda %81,8); bu gerçek bir sadakat göstergesi değildir (DQ'nun #62 ön denemesi).

## Şema değişirse

Doğru olan `docs/veri-sozlugu.md`'dir. DQ sözlüğü güncellediğinde: `src/simulasyon.py` sabitleri ve iç kontrolleri → bu skill'in örnek çıktısı ve MD5'i birlikte güncellenir; veri yeniden üretilip yeni devir yorumu yazılır.

## Kullanılan dosyalar

- **Okur:** `docs/veri-sozlugu.md`, `tests/test-cases.md`
- **Yazar:** `data/siparisler-g2.csv`, `skills/be-simulasyon/uretim-kaydi.md` (skill değişince)
- **Çalıştırır:** `src/simulasyon.py`
- **Bağımlılıklar:** Python 3.10+, numpy, pandas (`pip install numpy pandas`); ağ erişimi gerekmez.
- **Test edilen sürümler:** Python 3.13, numpy 2.5.3, pandas 3.0.5 → MD5 `1b7f765e…`. MD5 farklı çıkarsa önce sürümlere bak; NumPy rastgele sayı akışının sürümler arasında aynı kalacağını garanti etmez.

## Nasıl çalıştırılır

- Ajana: "be-simulasyon skill'ini kullanarak data/siparisler-g2.csv'yi üret."
- Elle: depo kökünde `python src/simulasyon.py` (yardım: `--help`).

## Üretim kaydı

Skill, betik ve veri Claude (Claude Code) ile üretildi; her değişikliğin commit'i ve prompt özeti [`uretim-kaydi.md`](uretim-kaydi.md) dosyasındadır. Bu skill'de bir değişiklik yapınca o dosyaya yeni madde ekle.
