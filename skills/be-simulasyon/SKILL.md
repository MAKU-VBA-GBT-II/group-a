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
- **Satır sayısı rastgele değildir**, sözlükteki formülle günden güne hesaplanır: `gun_adet = floor(gunluk_siparis × gun_k + 0.5)`, `gun_k` hafta sonunda `× hafta_sonu_katsayisi`, kampanya gününde `× kampanya_katsayisi`. Varsayılanla **N = 8.208**.
- `toplam_tutar` **hesaplanır**: `round(adet × birim_fiyat × (1 − indirim_orani), 2)`.
- `birim_fiyat` ürünün liste fiyatından en fazla ±%5 sapar (#30 çözümü). Sınırın yuvarlamayla aşılmaması için fiyat **kuruş cinsinden tamsayı** çekilir: `[liste × 95, liste × 105]` kuruş, uçlar dahil, sonra 100'e bölünür.

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
| (çıktı yolu) | `data/siparisler-g2.csv` | `--cikti data/deneme.csv` |

Deneme çalıştırmaları (`gun_sayisi=10` vb.) için **`--cikti` ile `data/` dışında** bir dosya verilir (ör. `/tmp/deneme-10gun.csv`); böylece deneme dosyası yanlışlıkla commit'lenemez. `data/siparisler-g2.csv` yalnızca varsayılanlarla üretilir.

Geçersiz parametrede (aralık dışı, yanlış tip, bozuk tarih, BAŞ > SON) betik çökmez, parametrenin adını ve izinli aralığı söyleyen bir `ValueError` verir ve dosya yazmaz — bu Hafta 6'da `fix/error-handling` dalında eklenir.

## Üretim sırası (bayt bayt aynı dosya için)

1. Günler `baslangic_tarihi`'nden itibaren sırayla gezilir, her günün sipariş adedi formülle hesaplanır; `siparis_tarihi` ve `kampanya` bu sırayla açılır (dosya zaten tarihe göre sıralı çıkar).
2. Tüm rastgele değerler tek `rng = numpy.random.default_rng(tohum)` nesnesinden **bu sırayla** ve tüm N satır için çekilir:
   `urun` (25 ürün, eşit olasılık; `kategori` üründen gelir) → `birim_fiyat` (kuruş) → `adet` → `kanal` → `sehir` → `odeme_tipi` → `durum` → `musteri_id` → `indirim_orani`.
   Ağırlıklar sözlükteki **Ağırlıklı alanlar** tablosundandır. `indirim_orani` her satır için çekilir, kampanya dışı satırlarda `0.00` yapılır.
3. `toplam_tutar` hesaplanır, `siparis_id` 1…N verilir.

Sıra veya çağrı değişirse kurallara uyan ama farklı bir dosya çıkar; MD5 değişir.

**Dikkat:** Her alan tüm N satır için tek seferde çekildiğinden, N'yi değiştiren **her** parametre (`gun_sayisi`, `gunluk_siparis`, katsayılar, `kampanya_donemleri`, `baslangic_tarihi`) dosyanın **tamamını** değiştirir. Ör. `gun_sayisi=10` dosyasının ilk satırları, varsayılan dosyanın ilk satırlarıyla aynı **değildir**. `tohum` ve `musteri_sayisi` N'yi değiştirmez ama onlar da farklı bir dosya üretir.

## Adımlar

1. **Şemayı oku:** `docs/veri-sozlugu.md` ve G2-veri Issue'sundaki DQ'nun "Şema yayımlandı" devir yorumu. Devir yorumu yoksa **üretime başlama**. Belirsiz bir yer varsa Issue'ya yaz, DQ ile netleştir; şemayı tek taraflı değiştirme.
2. **Betiği yalnızca gerekirse yaz/güncelle:** `src/simulasyon.py` varsa ve şema değişmediyse yeniden yazma, 3. adıma geç. Sabitler (`SUTUNLAR`, `KATEGORI_URUN`, ağırlıklar, parametre varsayılanları) dosyanın başındadır; gömülü sihirli sayı bırakma.
3. **Üret:** Depo kökünde `python src/simulasyon.py`.
4. **Kendi kontrolünü yap.** Betik sözlüğün **Veri kalitesi kuralları 1–11**'i yazmadan önce kendisi kontrol eder (`kontrol()` ile, `assert` değil; `python -O` ile de atlanmaz), biri kalırsa `ValueError` verir ve dosya yazılmaz; yazdıktan sonra dosyayı diskten geri okuyup aynı metin mi diye bakar. Elle yapılacaklar:
   - **Kural 12 (tekrarlanabilirlik):** betiği ikinci kez çalıştır, konsoldaki `MD5` aynı mı?
   - **Parametre davranışı:** sözlükteki satır sayısı tablosu — `--gun_sayisi 10` → 424, `--gun_sayisi 7` → 304, `--gun_sayisi 10 --gunluk_siparis 10` → 106 (deneme dosyası `data/` dışına, `--cikti` ile).
5. **Commit at** (`feature/veri` dalında; `main`'e doğrudan commit yok). Mesajda şema bulunur: satır sayısı + sütun listesi. Biçim: `G2-veri: <ne değişti> (#61)`.
6. **PR aç:** başlık `G2 parametreli simülasyon`, açıklamada `Closes #61`, kendi kontrol sonuçları ve üretim satırı; Reviewers: DQ. DQ yorumlarına PR üzerinden cevap ver, düzeltmeleri aynı dala push et; DQ **Approve** verdikten sonra merge'ü PR sahibi yapar.
7. **Devir yorumu merge'ün hemen ardından:** veriyi kullanan her Issue'ya (G2-analiz #62, G2-gorsel #63) ayrı ayrı şablonla yorum yaz; G2-veri Issue'suna kanıt yorumu (commit hash + dosya + satır sayısı + tohum + MD5). Her kapanış yorumunun ve PR açıklamasının sonunda üretim satırı olur.

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
| Ürünün kendine özgü fiyatı yok | `birim_fiyat` = liste fiyatı ±%5 (kuruş tamsayısıyla, sınır aşılamaz) |
| Dalgalanmaların nedeni yok | Hafta sonu `× 1,3` ve kampanya `× 1,5` + indirim; parametreli |

## Bilinen sınırlılıklar ve açıklar

- **Ürünler eşit sıklıkta satılır** (şema gereği). Bu yüzden "ciroda ilk 5 ürün" (M5) en çok satanları değil, liste fiyatı en yüksek ürünleri gösterir (Akıllı Saat, Kahve Makinesi, Mont, Spor Ayakkabı, Halı). Analizde bu not edilmelidir. Ürün bazlı satış ağırlığı istenirse önce DQ sözlüğe ekler.
- **Haftalık ciro oynaklığı** (değişim katsayısı) toplamda %13,0, kampanyasız haftalarda %7,9. Kalan oynaklık büyük ölçüde fiyat karmasından (99 – 3.499 TL) gelir; kampanya haftalarındaki sıçrama bilerek modellenmiştir.
- **Geçersiz parametre henüz `ValueError` vermiyor** (Hafta 6, `fix/error-handling`): BAŞ > SON olan bir kampanya dönemi **hata vermeden** kampanyasız dosya yazar; `gun_sayisi=0` anlamsız bir `TypeError` ile, negatif `gunluk_siparis` NumPy hatasıyla çöker; `musteri_sayisi=10000` iç kontrolde yanıltıcı bir mesajla durur. Bu düzeltilene kadar parametreler sözlükteki izinli aralıkta verilmelidir.

## Şema değişirse

Doğru olan `docs/veri-sozlugu.md`'dir. DQ sözlüğü güncellediğinde: `src/simulasyon.py` sabitleri ve iç kontrolleri → bu skill'in örnek çıktısı ve MD5'i birlikte güncellenir; veri yeniden üretilip yeni devir yorumu yazılır.

## Kullanılan dosyalar

- **Okur:** `docs/veri-sozlugu.md`, `tests/test-cases.md`
- **Yazar:** `data/siparisler-g2.csv`
- **Çalıştırır:** `src/simulasyon.py`
- **Bağımlılıklar:** Python 3.10+, numpy, pandas (`pip install numpy pandas`); ağ erişimi gerekmez.
- **Test edilen sürümler:** Python 3.13, numpy 2.5.3, pandas 3.0.5 → MD5 `1b7f765e…`. MD5 farklı çıkarsa önce sürümlere bak; NumPy rastgele sayı akışının sürümler arasında aynı kalacağını garanti etmez.

## Nasıl çalıştırılır

- Ajana: "be-simulasyon skill'ini kullanarak data/siparisler-g2.csv'yi üret."
- Elle: depo kökünde `python src/simulasyon.py` (yardım: `--help`).

## Üretim kaydı

- **Skill (#61, `bf7b4d7`):** Skill Claude (Claude Code) ile yazıldı ve Görev 2 kuralı gereği betikten **önce** ayrı commit olarak eklendi. Prompt özeti: "Görev 2'de BE oldum; Sema'nın docs/veri-sozlugu.md şemasına birebir parametreli simülasyonu feature/veri dalında yaz, #30 sınırlılıklarına da bak." Not: bu ilk commit'teki örnek çıktı (ilk satırlar, MD5) betiğin deneme çalıştırmasından alınmıştı; betik ve veri bir sonraki commit'te geldi.
- **Betik ve veri (#61, #30, `2159a98`):** `src/simulasyon.py` ve `data/siparisler-g2.csv` bu skill ile, Claude (Claude Code) kullanılarak üretildi. Kalite kuralları 1–11 betik içinde, kural 12 ve satır sayısı senaryoları elle doğrulandı.
- **Skill düzeltmesi (#61):** Öz inceleme sonrası: N'yi değiştiren parametrelerin tüm dosyayı değiştirdiği düzeltildi (önceki "akış kaymaz" cümlesi yanlıştı), Görev 1 verisine dokunmama ret durumu, deneme dosyalarının `data/` dışına yazılması, bilinen sınırlılıklar/açıklar bölümü ve commit hash'leri eklendi. Betik ve veri değişmedi. Claude (Claude Code) ile.
