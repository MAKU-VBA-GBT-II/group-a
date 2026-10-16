---
name: be-veri
description: Grup A'nın sipariş veri setini (data/siparisler.csv) sabit tohumla üretir ve şemayı docs/veri-sozlugu-g1.md dosyasına yazar. Veri seti üretilecek, yeniden üretilecek veya şema güncellenecek zaman kullan.
---

# be-veri — Sipariş verisi üretimi

**Ne yapar:** `src/veri_uret.py` betiğiyle sabit tohumlu, tekrarlanabilir sentetik sipariş verisi üretir (`data/siparisler.csv`) ve bu verinin şemasını `docs/veri-sozlugu-g1.md` dosyasına yazar. Üretilen ana dosya **temizdir**: eksik değer, aralık dışı değer veya tutarsız kategori adı içermez. Kirli (hatalı) kopyaları DQ kendi tarafında üretir; bu skill kirli veri üretmez.

Gerçek kişi verisi asla kullanılmaz — tüm değerler simülasyon ürünüdür (AGENTS.md kural 2).

## Girdiler

- Anlaşılan şema (aşağıdaki **Şema** bölümü — tek doğru kaynak budur)
- DQ test senaryoları: `tests/test-cases.md` (üretim bunları geçecek şekilde yapılır)
- İlgili Issue: G1-veri (#13), ciro metriği (#14)

## Şema

Sütunlar **tam olarak bu sırada**, 9 sütun, fazla/eksik yok:

| # | Alan | Tip | Geçerli aralık / değerler | Birim |
|---|---|---|---|---|
| 1 | `siparis_id` | int | 1'den başlar, 1'er artar, benzersiz | – |
| 2 | `siparis_tarihi` | tarih (`YYYY-MM-DD`) | 2026-09-01 – 2026-09-30 | – |
| 3 | `kategori` | metin | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Kitap | – |
| 4 | `urun` | metin | kategorisine ait ürün adı (her kategoride 5 ürün) | – |
| 5 | `adet` | int | 1 – 10 | adet |
| 6 | `birim_fiyat` | float | 20.00 – 5000.00, 2 ondalık | TL |
| 7 | `toplam_tutar` | float | `adet × birim_fiyat`, 2 ondalığa yuvarlı | TL |
| 8 | `sehir` | metin | İstanbul, Ankara, İzmir, Burdur, Antalya | – |
| 9 | `odeme_tipi` | metin | Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme | – |

- **Satır sayısı:** 400 (başlık hariç, tam olarak)
- **Tohum (seed):** 42
- **Biçim:** virgül ayraçlı, nokta ondalıklı, UTF-8, satır sonu `\n`
- **Boş değer:** hiçbir alanda yok

### Ürün listesi

| Kategori | Ürünler |
|---|---|
| Elektronik | Kablosuz Kulaklık, Bluetooth Hoparlör, Powerbank, Akıllı Saat, Klavye |
| Giyim | Tişört, Kot Pantolon, Sweatshirt, Spor Ayakkabı, Mont |
| Ev & Yaşam | Kahve Makinesi, Battaniye, Masa Lambası, Saklama Kabı Seti, Halı |
| Kozmetik | Nemlendirici, Şampuan, Parfüm, Güneş Kremi, Ruj |
| Kitap | Roman, Deneme, Ders Kitabı, Çocuk Kitabı, Şiir Kitabı |

### Üretim kuralları

1. **Kategori adları birebir aynı yazılır.** `Ev & Yaşam` her satırda tam olarak böyledir — büyük/küçük harf, boşluk veya `&` farkı olmaz.
2. **`urun` daima kendi kategorisinden seçilir.** Kategoriler arası karışma olmaz.
3. **`birim_fiyat` kategoriye göre makul aralıkta üretilir** (ör. Kitap 20–300, Elektronik 300–5000); ama hepsi şemadaki 20–5000 sınırları içinde kalır.
4. **`toplam_tutar` hesaplanır, rastgele üretilmez:** `round(adet * birim_fiyat, 2)`. DQ bunu TC-08'de test eder.
5. **Fiyatlarda biçimlendirme yok:** binlik ayırıcı yok, "TL" yazısı yok, sadece sayı (`1249.90`).
6. **Her kategori ve her şehir en az bir kez geçer**; dağılım tamamen düzgün olmak zorunda değil.
7. **Tohum sabittir:** `random.seed(42)` / `numpy.random.default_rng(42)`. Betik iki kez çalıştırıldığında **birebir aynı** dosya üretilmelidir.

## Adımlar

1. **Şemayı doğrula:** Yukarıdaki şemayı `tests/test-cases.md`'deki referans şema ile karşılaştır. Fark varsa DQ (Tuğba Tuana) ile netleştir; şemayı tek taraflı değiştirme.
2. **`src/veri_uret.py` betiğini yaz/güncelle:** Şema sabitlerini (`SUTUNLAR`, `KATEGORI_URUN`, `SEHIRLER`, `ODEME_TIPLERI`, `SEED`, `SATIR_SAYISI`) dosyanın başında sabit olarak tanımla — gömülü sihirli sayı bırakma.
3. **Üret:** Depo kökünde `python src/veri_uret.py` çalıştır. Çıktı: `data/siparisler.csv`.
4. **Kendi kontrolünü yap** (DQ'ya göndermeden önce):
   - Satır sayısı tam 400 mü?
   - Sütun adları ve sırası şemayla birebir mi?
   - `df.isna().sum().sum() == 0` mı?
   - `(df.toplam_tutar - (df.adet * df.birim_fiyat).round(2)).abs().max() == 0` mı?
   - `df.siparis_id.duplicated().sum() == 0` mı?
   - `set(df.kategori)` tam olarak şemadaki 5 değer mi?
   - Betiği ikinci kez çalıştırıp dosyanın değişmediğini doğrula (tekrarlanabilirlik).
5. **Şemayı yaz:** `docs/veri-sozlugu-g1.md` dosyasını yukarıdaki **Şema** bölümünden üret. Şu dördü mutlaka yazılı olsun: geçerli `sehir` ve `odeme_tipi` listesi, `siparis_id` benzersiz ve 1'den başlıyor, hiçbir alanda boş değer yok, kullanılan tohum değeri (42) ve satır sayısı (400).
6. **Commit at:** `G1-veri: siparisler.csv, veri-sozlugu-g1.md ve be-veri skill'i eklendi (#13)`
7. **Issue'ya kanıt yorumu yaz:** commit hash + üretilen dosyalar + satır sayısı + tohum. Ardından DQ'ya "Veri hazır" yorumu bırak ki testleri çalıştırabilsin.

## Şema değişirse

Şema her değiştiğinde **üç dosya birlikte** güncellenir, yoksa testler kalır:

1. Bu skill'in **Şema** bölümü
2. `src/veri_uret.py` içindeki sabitler
3. `docs/veri-sozlugu-g1.md`

Ardından DQ'ya haber ver — `tests/test-cases.md` ve `src/dq_test.py` içindeki şema sabitleri de güncellenmeli.

## Kullanılan dosyalar

- **Okur:** `tests/test-cases.md`
- **Yazar:** `data/siparisler.csv`, `docs/veri-sozlugu-g1.md`
- **Çalıştırır:** `src/veri_uret.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.):

- Üretim: "be-veri skill'ini kullanarak data/siparisler.csv ve docs/veri-sozlugu-g1.md dosyalarını üret."
- Şema değişikliği: "be-veri skill'ini kullanarak şemaya `kargo_ucreti` alanını ekle ve veriyi yeniden üret."

Elle çalıştırma: depo kökünde `python src/veri_uret.py`. Aynı tohumla her çalıştırmada aynı dosya üretilir.
