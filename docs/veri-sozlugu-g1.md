# Veri Sözlüğü — Görev 1 (`data/siparisler.csv`)

**Şirket:** Sepetix Analitik (Grup A) · **Rol:** BE · **Issue:** #13
**Üreten betik:** `src/veri_uret.py` · **Skill:** [`skills/be-veri/SKILL.md`](../skills/be-veri/SKILL.md)
**Test eden:** `tests/test-cases.md` (TC-01 … TC-12) · `python src/dq_test.py`

> Tüm veriler simülasyon ürünüdür; gerçek kişi ya da işletme verisi içermez (AGENTS.md kural 2).

## Dosya özeti

| Özellik | Değer |
|---|---|
| Dosya | `data/siparisler.csv` |
| Satır sayısı | **400** (başlık satırı hariç) |
| Sütun sayısı | **9** |
| Ayraç | virgül (`,`) |
| Ondalık ayracı | nokta (`.`) |
| Kodlama | UTF-8 |
| Satır sonu | `\n` |
| Tarih biçimi | `YYYY-MM-DD` |
| Para birimi | TL (yalnızca sayı; binlik ayırıcı ve "TL" yazısı yok) |
| Para alanlarının yazımı | `birim_fiyat` ve `toplam_tutar` dosyada **her zaman tam 2 ondalıkla** yazılır (`1667.40`, `1667.4` değil) — #27 |
| **Tohum (seed)** | **42** |
| Tekrarlanabilirlik | `python src/veri_uret.py` her çalıştırmada birebir aynı dosyayı üretir |

## Alanlar

Sütunlar dosyada **tam olarak bu sırada** bulunur:

| # | Alan | Tip | Geçerli aralık / değerler | Birim | Açıklama |
|---|---|---|---|---|---|
| 1 | `siparis_id` | int | 1 – 400, **benzersiz**, 1'den başlar ve 1'er artar | – | Sipariş kimliği |
| 2 | `siparis_tarihi` | tarih (`YYYY-MM-DD`) | 2026-01-01 – 2026-09-30 | – | Sipariş tarihi; dosya bu alana göre artan sıralıdır |
| 3 | `kategori` | metin | Elektronik, Giyim, Ev & Yaşam, Kozmetik, Kitap | – | Ürün kategorisi; yazım her satırda birebir aynıdır |
| 4 | `urun` | metin | Ürün listesi (aşağıda), 25 farklı değer | – | Ürün adı; daima kendi kategorisine aittir |
| 5 | `adet` | int | 1 – 10 | adet | Sipariş edilen miktar |
| 6 | `birim_fiyat` | float | 50.00 – 5000.00, 2 ondalık | TL | Tek ürün fiyatı |
| 7 | `toplam_tutar` | float | 50.00 – 50000.00, 2 ondalık | TL | **Hesaplanmıştır:** `round(adet × birim_fiyat, 2)` |
| 8 | `sehir` | metin | İstanbul, Ankara, İzmir, Burdur, Antalya | – | Teslimat şehri |
| 9 | `odeme_tipi` | metin | Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme | – | Ödeme yöntemi |

### Veri kalitesi güvenceleri

- **Hiçbir alanda boş değer yok** — ne `NaN` ne boş metin (`""`).
- **`siparis_id` benzersizdir ve 1'den başlar**; birebir tekrar eden satır yoktur.
- **`toplam_tutar` rastgele üretilmez**, `adet × birim_fiyat` ile hesaplanıp 2 ondalığa yuvarlanır.
- **Kategori adları tutarlıdır** — `Ev & Yaşam` her satırda tam olarak böyle yazılır; büyük/küçük harf veya boşluk farkı yoktur.
- **Para alanları her satırda tam 2 ondalıklıdır** (`^\d+\.\d{2}$`); betik bunu dosyayı yazmadan önce ham metin üzerinde kontrol eder (TC-09).
- **Her ürün kendi kategorisine aittir** (TC-11); **`siparis_id` 1…400 ardışıktır ve dosya tarihe göre artan sıralıdır** (TC-12). Betik bunları da yazmadan önce kontrol eder, dosyayı yazdıktan sonra diskten geri okuyup doğrular.
- Bu dosya **temiz** sürümdür. Hatalı/kirli kopyalar DQ tarafında ayrıca üretilir.

## Geçerli değer listeleri

### `kategori` ve `urun`

| Kategori | Ürünler | Fiyat aralığı (TL) |
|---|---|---|
| Elektronik | Kablosuz Kulaklık, Bluetooth Hoparlör, Powerbank, Akıllı Saat, Klavye | 300 – 5000 |
| Giyim | Tişört, Kot Pantolon, Sweatshirt, Spor Ayakkabı, Mont | 100 – 2500 |
| Ev & Yaşam | Kahve Makinesi, Battaniye, Masa Lambası, Saklama Kabı Seti, Halı | 80 – 4000 |
| Kozmetik | Nemlendirici, Şampuan, Parfüm, Güneş Kremi, Ruj | 50 – 1200 |
| Kitap | Roman, Deneme, Ders Kitabı, Çocuk Kitabı, Şiir Kitabı | 50 – 400 |

Kategoriye özgü fiyat aralıkları gerçekçilik içindir; hepsi şemadaki **50 – 5000** sınırları içindedir.

### `sehir`

`İstanbul`, `Ankara`, `İzmir`, `Burdur`, `Antalya` — bu beş değer dışında değer yoktur.

### `odeme_tipi`

`Kredi Kartı`, `Banka Kartı`, `Havale/EFT`, `Kapıda Ödeme` — bu dört değer dışında değer yoktur.

## Üretilen dosyanın dağılımı

Dağılımlar rastgeledir; her kategorinin ve her şehrin en az bir kez geçmesi garanti edilir.

| Kategori | Satır | | Şehir | Satır | | Ödeme tipi | Satır |
|---|---|---|---|---|---|---|---|
| Ev & Yaşam | 89 | | Antalya | 88 | | Havale/EFT | 105 |
| Kozmetik | 88 | | İstanbul | 86 | | Kredi Kartı | 101 |
| Elektronik | 81 | | İzmir | 84 | | Kapıda Ödeme | 98 |
| Giyim | 72 | | Burdur | 80 | | Banka Kartı | 96 |
| Kitap | 70 | | Ankara | 62 | | | |

Gözlenen değerler: `adet` 1 – 10 · `birim_fiyat` 57.60 – 4994.50 TL · `toplam_tutar` 133.42 – 41991.00 TL · toplam ciro 3.114.411,51 TL.

## Yeniden üretme

```bash
python src/veri_uret.py
```

Tohum sabit (42) olduğu için çıktı her çalıştırmada aynıdır. Şema değişirse şu üç dosya **birlikte** güncellenir: bu sözlük, `src/veri_uret.py` içindeki sabitler ve `skills/be-veri/SKILL.md`. Ardından DQ'ya haber verilir — `tests/test-cases.md` ve `src/dq_test.py` de güncellenmelidir.
