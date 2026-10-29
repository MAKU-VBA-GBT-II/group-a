---
name: dq-sozluk
description: Grup A'nın Görev 2 mini ürünü için veri sözlüğünü (docs/veri-sozlugu.md) üretir — alanlar, tipler, aralıklar, simülasyon parametreleri, beklenen satır sayısı ve 5 metrik. Veri şeması, veri sözlüğü veya analiz planı istendiğinde kullan.
---

# dq-sozluk — Veri sözlüğü ve analiz planı (DQ)

**Amaç:** BE'nin simülasyonu yazmadan önce uyacağı, DQ'nun test edeceği ve FE'nin görselleştireceği **tek doğru kaynağı** üretmek: `docs/veri-sozlugu.md`. Sözlükteki her kural test edilebilir olmalı; "uygun bir değer" gibi belirsiz ifade kullanılmaz.

**Rol:** DQ (analiz) · **Issue:** G2-sem (#60) · **Okuyanlar:** BE (#61), FE (#63), DQ test (#64)

## Ne zaman kullanılır / kullanılmaz

- Kullan: yeni bir görevin veri şeması yazılırken, şema değişikliği istendiğinde, metrik tanımı eklenirken.
- Kullanma: veri üretmek (BE'nin `be-simulasyon` skill'i), metrik hesaplamak (`dq-analiz`), test koşmak (`dq-test`).

## Girdiler

- Görev tanımı: `ders/AGENTS.md` → ilgili görev (Görev 2: "Şirket Mini Ürünü", Hafta 5–6) ve G2-sem Issue'su (#60) kabul kriterleri
- Önceki sözlük: `docs/veri-sozlugu-g1.md` (alan adları ve değer listelerinde süreklilik için)
- Bilinen sınırlılıklar: #30 (haftalık oynaklık, ürün bazlı fiyat yok), `docs/analiz-g1.md` → Sınırlılıklar
- PM önerileri: #60 gövdesi (ek alan ve parametre fikirleri)

## Adımlar

1. **Kapsamı yaz:** dosya adı, sektör, satır birimi (1 satır = 1 sipariş), tohum, kodlama, ayraç, tarih ve para biçimi.
2. **Parametreleri belirle (en az 2):** her biri için ad, tip, varsayılan, izinli aralık ve satır sayısına etkisi. Geçersiz değerde ne olacağını yaz (Hafta 6 hata yönetimi testlerinin dayanağı).
3. **Satır sayısını formülle ver:** rastgele değil, parametrelerden **hesaplanabilir** olsun; varsayılanla beklenen sayıyı ve en az 2 parametre değişikliğinin sonucunu tabloya yaz (DQ test "parametre davranışı" senaryosu bunu kullanır).
4. **Alanları yaz:** dosyadaki sırayla; her alan için ad, tip, aralık/kural, birim, örnek değer, açıklama. Hesaplanan alanların formülünü ver. Kategorik alanların değer listesini ve ağırlıklarını ver.
5. **Önceki sınırlılıkları çöz:** #30'daki her madde için şemada hangi kuralın onu çözdüğünü yaz.
6. **Veri kalitesi kurallarını listele:** boş değer, benzersizlik, sıralama, biçim (2 ondalık), çapraz alan kuralları. Her biri bir test senaryosuna dönüşebilecek kadar net olmalı.
7. **Metrikleri yaz (en az 5):** toplam + ortalama + 2 kırılım (biri zaman: haftalık) + top-N. Her biri için kod (M1…), ad, formül (pandas'a çevrilebilir), hangi satırlar dahil, neyi ölçtüğü, hangi grafikte kullanılacağı.
8. **Kontrol et** (aşağıdaki liste), sonra `feature/sozluk-g2` gibi bir dalda PR aç; belge PR'ı olduğu için yazarı merge eder.
9. **Devir teslim:** BE (G2-veri) ve FE (G2-gorsel) Issue'larına: *"Şema yayımlandı — commit `<hash>`. Alanlar, aralıklar ve 5 metrik `docs/veri-sozlugu.md`'de. BE üretebilir."*

## Çıktı formatı kuralları

- Dosya: `docs/veri-sozlugu.md` (Görev 1 sözlüğü `docs/veri-sozlugu-g1.md` olarak kalır, üzerine yazılmaz).
- Başlıklar **bu sırada**: `Dosya özeti` → `Simülasyon parametreleri` → `Satır sayısı` → `Alanlar` → `Geçerli değer listeleri` → `Veri kalitesi kuralları` → `#30 sınırlılıklarının çözümü` → `Metrikler` → `Grafik eşlemesi (FE)` → `Değişiklik günlüğü`.
- Alan tablosu sütunları: `# | Alan | Tip | Aralık / kural | Birim | Örnek | Açıklama`.
- Metrik tablosu sütunları: `Kod | Metrik | Formül | Dahil satırlar | Neyi ölçer | Grafik`.
- Para: TL, dosyada 2 ondalık (`1299.00`); belgede Türkçe biçim (`1.299,00 TL`). Tarih: `YYYY-MM-DD`.
- Kabul kriterleriyle birebir: her alanın adı/tipi/aralığı/örneği ✔ · hedef satır sayısı ✔ · ≥2 parametre + varsayılan ✔ · ≥5 metrik (toplam, ortalama, 2 kırılım, top-N) ✔.

## Örnek giriş / çıkış

**Giriş (ajana):**
> "dq-sozluk skill'ini kullanarak #60'taki kabul kriterlerine göre `docs/veri-sozlugu.md` yaz. Alan: e-ticaret siparişleri. #30'daki ürün bazlı fiyat sorununu çöz."

**Çıkış (kısaltılmış):**

| # | Alan | Tip | Aralık / kural | Birim | Örnek | Açıklama |
|---|---|---|---|---|---|---|
| 8 | `birim_fiyat` | float | ürünün liste fiyatı × [0,95 – 1,05], 2 ondalık | TL | `1302.47` | Ürüne özgü fiyat (#30) |
| 11 | `toplam_tutar` | float | `round(adet × birim_fiyat × (1 − indirim_orani), 2)` | TL | `2083.95` | Hesaplanır, rastgele değil |

| Kod | Metrik | Formül | Dahil satırlar | Neyi ölçer | Grafik |
|---|---|---|---|---|---|
| M1 | Net ciro | `Σ toplam_tutar` | `durum == "Teslim Edildi"` | Dönemin gerçekleşen geliri | — |

## Reddetme durumları

Aşağıdaki isteklerde sözlük **üretilmez**, durum Issue'ya yazılır:

- **Gerçek kişisel veri** isteyen alan: ad-soyad, TC kimlik no, telefon, e-posta, açık adres, kart numarası, IP vb. (ders kuralı §3.1 — depolar herkese açık). Müşteri yalnızca sentetik kimlikle (`M0001`) temsil edilir.
- Gerçek bir şirketten/kaynaktan alınmış veri kullanma talebi.
- Test edilemeyen kural ("makul fiyat", "gerçekçi dağılım" gibi sayısız ifade) — sayıya çevrilmeden yazılmaz.
- Kabul kriterinin altında kalan istek (5'ten az metrik, parametresiz simülasyon).

## Kontrol listesi (PR'dan önce)

- [ ] Her alanın adı, tipi, aralığı, birimi, örneği var; örnek değer kendi aralığında.
- [ ] Varsayılan parametrelerle satır sayısı formülden hesaplanıp yazıldı; en az 2 değişiklik senaryosu tabloda.
- [ ] Hesaplanan alanların formülü var; kategorik listeler ve ağırlıklar tam (toplam %100).
- [ ] 5 metrik: toplam + ortalama + 2 kırılım (biri haftalık) + top-N; formüller pandas'a doğrudan çevrilebilir.
- [ ] Hiçbir alan gerçek kişisel veri içermiyor.
- [ ] #30'daki her sınırlılık için çözüm kuralı yazıldı.

## Kullanılan dosyalar

- **Okur:** `ders/AGENTS.md` (Görev 2), `docs/veri-sozlugu-g1.md`, `docs/analiz-g1.md`, Issue #30 ve #60
- **Yazar:** `docs/veri-sozlugu.md`
- **Çalıştırır:** — (belge skill'i; kod çalıştırmaz. Satır sayısı tablosu formülle elle/ajanla doğrulanır.)

## Nasıl çalıştırılır

Ajana (Claude, Claude Code vb.):

- Yeni sözlük: "dq-sozluk skill'ini kullanarak #60'ın kabul kriterlerine göre `docs/veri-sozlugu.md` yaz."
- Değişiklik: "dq-sozluk skill'ini kullanarak sözlüğe `<alan>` alanını ekle; satır sayısı, kalite kuralları ve değişiklik günlüğünü güncelle."

Sonra: dal (`feature/sozluk-g2`) → PR → merge → devir yorumları (adım 9).

## Üretim kaydı

- **Araç:** Claude (yapay zekâ ajanı).
- **Görev 2 (#60):** Claude'a ders planı (Görev 2), #60, #30 ve Görev 1 sözlüğü verildi; önce bu skill yazıldı ve commit'lendi, ardından `docs/veri-sozlugu.md` bu skill'in adımlarıyla üretildi.
