# Test Senaryoları — Görev 2 (Mini Ürün)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** DQ — Sema Nur Doğan · **Issue:** #64
**Test edilen:** `data/siparisler-g2.csv` ve `src/simulasyon.py` (BE, #61 / PR #66) · **Referans şema:** `docs/veri-sozlugu.md` (#60)
**Skill:** [`skills/dq-test/SKILL.md`](../skills/dq-test/SKILL.md) · Görev 1 senaryoları: [`tests/test-cases-g1.md`](test-cases-g1.md)

> **Kural (#47):** Bu dosya yalnızca senaryoları içerir; "Gerçekleşen" ve "Geçti/Kaldı" sütunları burada **doldurulmaz**. Testler Hafta 6'da koşuldukça sonuçlar `tests/test-log.md` → Görev 2 tablosuna **tarihli** satır olarak (kullanılan parametrelerle birlikte) yazılır.

## Kapsam

- **Varsayılan parametreler:** `gun_sayisi=182` · `gunluk_siparis=40` · `hafta_sonu_katsayisi=1.3` · `kampanya_katsayisi=1.5` · `kampanya_donemleri=2026-03-09:2026-03-15,2026-05-11:2026-05-17` · `baslangic_tarihi=2026-01-05` · `musteri_sayisi=1500` · `tohum=42`
- **Beklenen satır sayıları** sözlükteki formülden hesaplanmıştır (veriden kopyalanmamıştır): `gun_adet = floor(gunluk_siparis × katsayılar + 0.5)`, `N = Σ gun_adet`.
- Parametre ve hata senaryolarında betik **geçici bir dosyaya** çalıştırılır (`--cikti` ile); geçici dosyalar commit'lenmez.
- **Görev 3 eki (PR #95):** isteğe bağlı `urun_agirliklari` parametresi için G2-TC-23…25 eklendi; varsayılanı boştur, yukarıdaki varsayılan dosya değişmez. Beklenen ürün payları sözlükteki `w_i / Σw` formülünden hesaplanır.
- **Görev 3 eki 2 (PR #102):** `urun_listesi` ve `fiyat_sapmasi` parametreleri için G2-TC-26…34 eklendi (varsayılanlar eski davranışı korur). G2-TC-09/10/11 artık fiilen kullanılan ürün listesine (varsayılan 25 ürünlük sözlük tablosu ya da `--urun_listesi` dosyası) ve sapmaya göre koşulur; varsayılan dosyada sonuç değişmez.
- Para metriklerinin hesabı (M1–M6) bu dosyanın değil, `docs/analiz-g2.md`'nin (#62) konusudur.

## Senaryolar

### A — Dosya ve şema

| ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı |
|---|---|---|---|---|---|---|---|
| G2-TC-01 | Dosya özeti | Veri dosyası var, boş değil, UTF-8 okunuyor mu? | 1) Dosya yolunu ve boyutunu kontrol et. 2) UTF-8 ile pandas'a oku. | `data/siparisler-g2.csv` | Dosya var, boyut > 0; pandas hatasız okuyor; Türkçe karakterler bozuk değil (ör. `İstanbul`, `Kapıda Ödeme`) | | |
| G2-TC-02 | Kural 2 | Sütun adları ve sırası şemayla aynı mı? | 1) `df.columns` al. 2) Sözlükteki listeyle ad + sıra karşılaştır. | Başlık satırı | Tam olarak 14 sütun, bu sırayla: `siparis_id, siparis_tarihi, musteri_id, kanal, kategori, urun, adet, birim_fiyat, indirim_orani, kampanya, toplam_tutar, sehir, odeme_tipi, durum` | | |
| G2-TC-03 | Kural 3 · Satır sayısı | Satır sayısı formüldeki değere eşit mi? | 1) Başlık hariç satır say. 2) Varsayılan parametrelerle formülden hesaplanan N ile karşılaştır. | Varsayılan dosya | **8.208** satır | | |
| G2-TC-04 | Alanlar (tip) | Tipler doğru mu? | 1) `siparis_id`, `adet`, `kampanya` tamsayıya; `birim_fiyat`, `indirim_orani`, `toplam_tutar` sayıya; `siparis_tarihi` `%Y-%m-%d` ile tarihe çevrilir. 2) Çevrilemeyen değerleri say. | Tüm sütunlar | Çevrilemeyen değer = 0 | | |
| G2-TC-05 | Alanlar (aralık) | Sayısal alanlar ve `musteri_id` aralıkta mı? | 1) `adet` 1–5; `kampanya` ∈ {0,1}; `indirim_orani` ∈ {0.00, 0.10, 0.15, 0.20, 0.25, 0.30}; `toplam_tutar` > 0. 2) `musteri_id` `^M\d{4}$` ve numarası 1–1500. 3) Aralık dışı satırları say. | `adet`, `kampanya`, `indirim_orani`, `toplam_tutar`, `musteri_id` | Aralık / biçim dışı satır = 0 | | |
| G2-TC-06 | Kural 1 | Boş değer var mı? | 1) Her sütunda `isna().sum()`. 2) Boş metin (`""`) say. | Tüm sütunlar | Toplam boş değer = 0 | | |
| G2-TC-07 | Kural 4 | `siparis_id` ardışık, dosya tarihe göre sıralı mı? | 1) `siparis_id` == `1…N` mi? 2) `siparis_tarihi` artan mı? | `siparis_id`, `siparis_tarihi` | `siparis_id` 1…8.208 ardışık, tekrar = 0; tarih artan | | |
| G2-TC-08 | Kural 5 | Tarih aralığı ve gün sayısı doğru mu? | 1) En küçük / en büyük tarih. 2) Farklı tarih sayısı. | `siparis_tarihi` | En küçük 2026-01-05, en büyük 2026-07-05; farklı tarih = 182 | | |

### B — Değerler ve kurallar

| ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı |
|---|---|---|---|---|---|---|---|
| G2-TC-09 | Kural 6 | Kategorik alanlar yalnızca listedeki değerleri mi alıyor? | 1) `kanal`, `kategori`, `urun`, `sehir`, `odeme_tipi`, `durum` benzersiz değerlerini sözlük listeleriyle karşılaştır. 2) Listedeki her değerin en az bir kez geçtiğine bak. | 6 kategorik sütun | Liste dışı değer = 0; listedeki her değer ≥ 1 kez geçiyor (3 kanal, 5 kategori, 25 ürün, 5 şehir, 4 ödeme, 3 durum) | | |
| G2-TC-10 | Kural 7 | Her ürün kendi kategorisinde mi? | Her satırda `urun`'un sözlükteki kategorisi == `kategori` mi? | `kategori`, `urun` | Uyuşmayan satır = 0 | | |
| G2-TC-11 | Kural 8 · #30 | Fiyat ürünün liste fiyatına bağlı mı? | Her satırda `birim_fiyat` ∈ [liste × 0,95 ; liste × 1,05] mi? (liste: sözlük tablosu) | `urun`, `birim_fiyat` | Aralık dışı satır = 0; tüm dosyada `birim_fiyat` 94,05 – 3.673,95 TL | | |
| G2-TC-12 | Kural 9 | Sayılar ham metinde tam 2 ondalık mı? | 1) Dosyayı `dtype=str` oku. 2) `birim_fiyat`, `toplam_tutar`, `indirim_orani` için `^\d+\.\d{2}$`. | Ham metin | Desene uymayan satır = 0 (ör. `0.20`, `0.00`, `1299.00`) | | |
| G2-TC-13 | Kural 10 | `toplam_tutar` formülle tutarlı mı? | `round(adet × birim_fiyat × (1 − indirim_orani), 2)` hesapla, farkı al. | `adet`, `birim_fiyat`, `indirim_orani`, `toplam_tutar` | Farkı ≥ 0,005 TL olan satır = 0 | | |
| G2-TC-14 | Kural 11 | Kampanya bayrağı ve indirim tutarlı mı? | 1) Tarih bir kampanya dönemindeyse `kampanya == 1` mi? 2) `kampanya == 0` ⇒ `indirim_orani == 0.00`? 3) `kampanya == 1` ⇒ `indirim_orani ∈ {0.10 … 0.30}`? | `siparis_tarihi`, `kampanya`, `indirim_orani` | Üç kontrolde de aykırı satır = 0; kampanya günü = 14 (2 × 7 gün) | | |
| G2-TC-15 | Ağırlıklı alanlar | Dağılımlar sözlükteki ağırlıklara uyuyor mu? | Varsayılan dosyada `adet`, `kanal`, `sehir`, `odeme_tipi`, `durum` oranlarını hesapla. | Varsayılan dosya | Her değerin oranı sözlükteki olasılığın ±3 puan içinde (ör. `durum` Teslim Edildi %87–93) | | |
| G2-TC-16 | Kural 12 | Aynı parametre + tohum aynı dosyayı veriyor mu? | 1) Betiği varsayılanla 2 kez geçici dosyalara çalıştır. 2) MD5'leri ve repodaki dosyanın MD5'ini karşılaştır. | Varsayılan parametreler | Üç MD5 aynı | | |

### C — Parametre davranışı

| ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı |
|---|---|---|---|---|---|---|---|
| G2-TC-17 | Satır sayısı tablosu | `gun_sayisi` satır sayısını formüle göre değiştiriyor mu? | Betiği iki ayrı ayarla geçici dosyaya çalıştır; satır, son tarih ve farklı tarih sayısına bak. | a) `--gun_sayisi 10` · b) `--gun_sayisi 7` | a) **424** satır, son tarih 2026-01-14, 10 farklı tarih · b) **304** satır, son tarih 2026-01-11 | | |
| G2-TC-18 | Satır sayısı tablosu | `gunluk_siparis` satır sayısını değiştiriyor mu? | `--gun_sayisi 10 --gunluk_siparis 10` ile çalıştır. | `gun_sayisi=10`, `gunluk_siparis=10` | **106** satır; hafta içi günlerde 10, hafta sonu günlerinde 13 sipariş | | |
| G2-TC-19 | Parametreler (katsayılar) | Hafta sonu ve kampanya katsayıları ayrı ayrı etkili mi? | Üç ayarla çalıştır, satır say. | a) `--hafta_sonu_katsayisi 1.0` · b) `--kampanya_katsayisi 1.0` · c) `--baslangic_tarihi 2026-03-09 --gun_sayisi 14` | a) **7.560** · b) **7.904** · c) **760** satır (ilk hafta kampanyalı: hafta içi 60, hafta sonu 78; ikinci hafta 40 / 52) | | |
| G2-TC-20 | Parametreler (tohum) | `tohum` yalnızca içeriği değiştiriyor mu? | `--tohum 7` ile çalıştır; satır sayısı ve MD5'i varsayılanla karşılaştır. | `--tohum 7` | Satır sayısı yine **8.208**; MD5 varsayılandan **farklı**; G2-TC-02…14 bu dosyada da geçer | | |
| G2-TC-23 | Parametreler (`urun_agirliklari`) · Ağırlıklı alanlar (`urun`) | Ürün ağırlığı dağılımı değiştiriyor, satır sayısını değiştirmiyor mu? | 1) Ağırlıkla geçici dosyaya çalıştır. 2) Satır say, MD5'i varsayılanla karşılaştır. 3) Ürün paylarını `w_i / Σw` ile karşılaştır. 4) G2-TC-02…14'ü bu dosyada koş. | `--urun_agirliklari 1,1,2,0.5,1,4,3,4,1,1,1,3,2,3,1,4,4,1,3,3,2,2,1,3,1` (Σw = 53) | **8.208** satır; MD5 varsayılandan **farklı**; her ürünün payı `w_i / 53`'ün **±1,5 puan** içinde (ör. Akıllı Saat %0,9, Tişört %7,5); G2-TC-02…14 geçer | | |
| G2-TC-24 | Parametreler (`urun_agirliklari`) · Kural 12 | Boş ağırlık eski davranışı koruyor, ağırlıklar normalize ediliyor mu? | 1) `--urun_agirliklari ""` ile çalıştır, MD5'i repodaki dosyayla karşılaştır. 2) G2-TC-23 ağırlıklarının 2 katıyla çalıştır, MD5'i G2-TC-23 dosyasıyla karşılaştır. | a) `""` · b) G2-TC-23 ağırlıkları × 2 | a) MD5 = `1b7f765e…` (repo) · b) MD5 = G2-TC-23 dosyasının MD5'i | | |
| G2-TC-26 | Parametreler (`urun_listesi`, `fiyat_sapmasi`) · Kural 12 | Örnek liste ve varsayılan sapma, varsayılan dosyayı aynen üretiyor mu? | `--urun_listesi data/urun-listesi-ornek.csv` ile, sonra `--fiyat_sapmasi 0.05` ile geçici dosyaya çalıştır; MD5'leri repodaki dosyayla karşılaştır. | a) `--urun_listesi data/urun-listesi-ornek.csv` · b) `--fiyat_sapmasi 0.05` | İkisinde de MD5 = `1b7f765e…` (repo); varsayılan veri değişmez | | |
| G2-TC-27 | Parametreler (`urun_listesi`) · Kural 6/7/8 · Kural 12 | Web fiyat listesiyle üretilen veri kurallara uyuyor ve tekrarlanabilir mi? | 1) Web listesiyle iki kez çalıştır. 2) Satır, ürün, kategori say; `birim_fiyat` aralığına bak. 3) G2-TC-09/10/11'i listedeki ürünlerle koş. 4) MD5'leri repodaki `data/siparisler-web.csv` ile karşılaştır. | `--urun_listesi data/urun-listesi-web.csv` | **8.208** satır; **25** ürün, **5** kategori; Kural 6/7/8 listeye göre geçer; 2 çalıştırma + repo dosyası aynı MD5 (`628b4351…`); `birim_fiyat` 170,12–15.743,03 | | |
| G2-TC-28 | Parametreler (`urun_listesi`) · Kural 6/7/8 | Küçük özel liste yalnızca kendi ürün ve kategorilerini mi üretiyor? | Geçici 3 ürünlük liste dosyası yaz; çalıştır; satır, ürün, kategori ve fiyat aralığına bak. | Liste: `A,U1,100` · `A,U2,200.50` · `B,U3,300` | **8.208** satır; yalnızca U1/U2/U3 ve A/B; Kural 6/7/8 listeye göre geçer; `birim_fiyat` **95,00–315,00** | | |
| G2-TC-29 | Parametreler (`fiyat_sapmasi`) · Kural 8 | Genel sapma fiyat aralığını belirliyor mu, uçlar kuruşa göre doğru mu? | Üç değerle çalıştır; her satırın `birim_fiyat / liste` oranını ve aralık dışı satır sayısını hesapla. | a) `--fiyat_sapmasi 0` · b) `0.1` · c) `0.5` | Her biri 8.208 satır, aralık dışı **0**; oran a) 1,000–1,000 · b) 0,900–1,100 · c) 0,500–1,500 içinde; uçlar kuruş hesabıyla içe yuvarlanır (200,50 ±%5 → 190,48–210,52) | | |
| G2-TC-30 | Parametreler (liste sütunu `fiyat_sapmasi`) | Ürün başına sapma genel sapmayı geçersiz kılıyor, boş hücre genel sapmayı kullanıyor mu? | 3 ürünlük listeye `fiyat_sapmasi` sütunu ekle; genel sapma 0,1 ile çalıştır; ürün başına min/maks fiyata bak. | U1 `100` sapma `0` · U2 `200` sapma `0.5` · U3 `300` sapma boş · `--fiyat_sapmasi 0.1` | U1 **100,00–100,00**; U2 **100,18–299,83** (0,5 aralığında); U3 genel 0,1 → **270,01–330,00** | | |
| G2-TC-31 | Parametreler (`urun_listesi` × `urun_agirliklari`) | Ağırlıklar listedeki ürün sayısına göre uygulanıyor mu? | Üç ürünlük listeyle: a) 3 ağırlık, b) 25 ağırlık, c) bir ürün dışında hepsi 0. | a) `--urun_agirliklari 1,2,3` · b) 25 değer · c) `--urun_agirliklari 0,0,1` | a) ürün payları `w_i / 6`'nın **±1,5 puan** içinde · b) çıkış **1**, mesajda `urun_agirliklari`, `3`, `25`; dosya yok · c) yalnızca U3; ürünü kalmayan A kategorisi dosyada **yok** | | |
| G2-TC-32 | Parametreler (`urun_listesi` biçimi) | BOM'lu UTF-8, farklı sütun sırası ve Türkçe karakter doğru okunuyor mu; ürün sırası dosya sırası mı? | BOM'lu UTF-8, sütunları `liste_fiyati,urun,kategori` sırasında, adları Şapka/Çay olan liste yaz; çalıştır; `urun_agirliklari=1,0` ile tekrar çalıştır. | Liste: `Giyim,Şapka,…` · `Gıda,Çay,…` (BOM'lu) | Yalnızca Şapka/Çay ve Giyim/Gıda; Türkçe karakterler bozulmaz; `--urun_agirliklari=1,0` → yalnızca **dosyadaki ilk ürün** (Şapka) | | |

### D — Hata yönetimi (Hafta 6, `fix/error-handling` sonrası koşulur)

Kaynak: sözlük → "Geçersiz parametre" kuralı ve PR #66 incelemesi (satır 148 ve 323).

| ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı |
|---|---|---|---|---|---|---|---|
| G2-TC-21 | Geçersiz parametre | Aralık dışı sayısal parametreler anlamlı hata veriyor mu? | Her girdiyle ayrı ayrı, var olmayan bir `--cikti` yoluna çalıştır; hata mesajını ve dosyanın oluşup oluşmadığını kaydet. | a) `--gun_sayisi 0` · b) `--gun_sayisi -3` · c) `--musteri_sayisi 10000` · d) `--gunluk_siparis 0` | Her biri `ValueError`; mesajda parametre adı + izinli aralık + verilen değer (ör. `gun_sayisi 1–366 arasında olmalı, verilen: 0`); çıktı dosyası **oluşmaz** | | |
| G2-TC-22 | Geçersiz parametre | Bozuk kampanya dönemi ve tarih anlamlı hata veriyor mu? | G2-TC-21 gibi. | a) `--kampanya_donemleri 2026-03-09` (`:` yok) · b) `--kampanya_donemleri 2026-03-15:2026-03-09` (BAŞ > SON) · c) `--baslangic_tarihi 2026-13-01` | Her biri `ValueError` ve Türkçe, parametre adını içeren mesaj; b) **sessizce kampanyasız dosya yazmaz**; çıktı dosyası oluşmaz | | |
| G2-TC-25 | Geçersiz parametre (`urun_agirliklari`) | Bozuk ürün ağırlığı anlamlı hata veriyor mu? | G2-TC-21 gibi; değer `--urun_agirliklari=<değer>` (eşittir ile) verilir. | a) 3 değer (`1,2,3`) · b) ilk değer `a` · c) ilk değer `-1` · d) ilk değer `nan` · e) ilk değer `inf` · f) 25 değerin hepsi `0` | Her biri çıkış **1**, `Hata (ValueError)` ve mesajda `urun_agirliklari`; Traceback yok; çıktı dosyası oluşmaz | | |
| G2-TC-25+ | Parametreler (`urun_agirliklari` izinli uç değerler) · Kural 6 istisnası | İzinli uç değerler hatasız çalışıyor mu? | Geçici dosyaya çalıştır. | a) 25 × `1e308` · b) 1. ürün (Kablosuz Kulaklık) `0`, diğerleri `1` | a) çıkış **0**, dosya yazılır (toplam taşmaz — PR #95 incelemesi) · b) çıkış 0; Kablosuz Kulaklık dosyada **hiç** geçmez | | |
| G2-TC-33 | Geçersiz parametre (`urun_listesi`) | Bozuk ürün listesi anlamlı hata veriyor mu? | G2-TC-21 gibi; her bozuk dosya ayrı ayrı verilir, çıktı dosyası ve hata mesajı kaydedilir. | 14 durum: a) dosya yok · b) UTF-8 değil (cp1254) · c) sütun eksik · d) liste boş · e) `kategori` boş · f) `urun` boş · g) aynı `urun` iki kez · h) fiyat `0` · i) fiyat negatif · j) fiyat 3 ondalık · k) fiyat sayı değil · l) ürün sapması `0.7` · m) `-0.1` · n) sayı değil | Her biri çıkış **1**, `Hata (ValueError)`, mesajda `urun_listesi` (veya `fiyat_sapmasi`) ve satır/sütun bilgisi; Traceback yok; çıktı dosyası **oluşmaz** | | |
| G2-TC-34 | Geçersiz parametre (`fiyat_sapmasi`) | Aralık dışı veya sayı olmayan genel sapma anlamlı hata veriyor mu? | G2-TC-25 gibi; değer `--fiyat_sapmasi=<değer>` (eşittir ile) verilir. | a) `0.6` · b) `-0.1` · c) `abc` | Her biri çıkış **1**, `Hata (ValueError)`, mesajda `fiyat_sapmasi` ve izinli aralık 0–0,5; Traceback yok; çıktı dosyası oluşmaz | | |

## Kapsama

| Sözlük kuralı / bölümü | Senaryo |
|---|---|
| Kural 1 — boş değer yok | G2-TC-06 |
| Kural 2 — sütunlar | G2-TC-02 |
| Kural 3 — satır sayısı | G2-TC-03, G2-TC-17…20, G2-TC-23, G2-TC-27, G2-TC-28 |
| Kural 4 — id ve sıralama | G2-TC-07 |
| Kural 5 — tarih aralığı | G2-TC-08, G2-TC-17 |
| Kural 6 — kategorik değerler | G2-TC-09 (listeye göre: G2-TC-27, 28, 32); istisna (ağırlığı 0 olan ürün) G2-TC-25+ |
| Kural 7 — ürün–kategori | G2-TC-10 (listeye göre: G2-TC-27, 28) |
| Kural 8 — fiyat (#30) | G2-TC-11 (listeye göre: G2-TC-27, 28); sapma G2-TC-29, G2-TC-30 |
| Kural 9 — 2 ondalık | G2-TC-12 |
| Kural 10 — hesaplanan alan | G2-TC-13 |
| Kural 11 — kampanya | G2-TC-14 |
| Kural 12 — tekrarlanabilirlik | G2-TC-16, G2-TC-20, G2-TC-24, G2-TC-26, G2-TC-27 |
| Alan tablosu (tip, aralık, `musteri_id`) | G2-TC-04, G2-TC-05 |
| Ağırlıklı alanlar | G2-TC-15; `urun` (`w_i / Σw`) G2-TC-23 |
| Satır sayısı tablosu (8.208 / 424 / 304 / 106) | G2-TC-03, G2-TC-17, G2-TC-18 |
| Geçersiz parametre (`ValueError`, dosya yazılmaz) | G2-TC-21, G2-TC-22, G2-TC-25, G2-TC-33, G2-TC-34 |
| Parametre `urun_agirliklari` (normalize, boş = varsayılan, izinli uç değerler) | G2-TC-23, G2-TC-24, G2-TC-25+ |
| Parametre `urun_listesi` (biçim, sıra, ağırlıkla birlikte) | G2-TC-26…28, G2-TC-31, G2-TC-32 |
| Parametre `fiyat_sapmasi` (genel, ürün başına, uç değerler) | G2-TC-26, G2-TC-29, G2-TC-30 |
