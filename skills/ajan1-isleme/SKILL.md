---
name: ajan1-isleme
description: Ajan 1'in (toplama) ikinci aşaması. ajan1-alma'nın getirdiği ham ürün kartlarından fiyatı okur, ürünleri bizim ürünlerle eşleştirir, eleme kurallarını uygular, tekrarları ayıklar ve fiyat değişiminin nedenini not eder. Sayfalar alındıktan sonra kullan.
---

# ajan1-isleme: Fiyat okuma, eşleştirme ve eleme (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114 · **Önceki:** `ajan1-alma` · **Sonraki:** `ajan1-teslim`

## 1. Fiyat okuma
- Sayfada görünen fiyat metni olduğu gibi `ham_fiyat_metni`'ne yazılır (`₺1.299,90`).
- Türkçe biçim sayıya çevrilir: nokta binlik, virgül kuruş → `1299.90`.
- Sayfada iki fiyat varsa üstü çizili olan `liste_fiyati`, indirimli olan `indirimli_fiyat` olur.
- `fiyat_turu` sayfadaki etikete göre doldurulur: etiket yoksa `liste`, indirim etiketi varsa `indirimli`, kampanya etiketi varsa `kampanya`.

## 2. Eşleştirme (`docs/eslesme-tanimlari.md`)
- Ürün adında en az bir "dahil" ifadesi geçmeli, hiçbir "hariç" ifadesi geçmemeli (örnek: Şampuan'da "kuru şampuan", "köpek" hariç).
- **Nemlendirici (Gratis):** Ürün, adından çok Gratis'in "Yüz Nemlendirici Gece Kremleri" kategorisinde bulunmasına göre dahil sayılır; "hariç" listesi (göz kremi, göz çevresi, serum, maske) yine uygulanır. Kitaplardaki "D&R kategori" kuralıyla aynı mantık. *Tuğba'nın onayı bekleniyor (#115).*
- Miktar okunabiliyorsa `birim_miktar`'a yazılır (`400 ml`).
- `eslesme_guveni`: dahil ifadesi + miktar uyumlu + makul aralıkta → `yuksek`; biri eksik → `orta`; makul aralık dışı → `dusuk`.

## 3. Eleme (satır silinmez, `elendi` alanına gerekçe yazılır)
- Karşılaştırma fiyatı liste fiyatımızın 0,3 katından az ya da 3 katından fazla → `fiyat bandı dışı`.
- 2'li, 3'lü paketler → `çoklu paket` (Saklama Kabı Seti hariç).
- Stokta yok → `stok yok`.
- **Masa Lambası notu:** Liste fiyatımız 399 TL olduğu için IKEA satırlarının çoğu bant dışı kalacak (karar 5). Bu beklenen bir durum, hata değil.

## 4. Tekrar ayıklama
- Aynı `urun_url` birden fazla kez geldiyse tek satır kalır. *(Neden: "öne çıkanlar" ve liste alanında aynı ürün iki kez görünürse medyana iki kez girer.)*

## 5. Fiyat değişimi notu (çalışma raporuna)
Her ürün için rapora yazılır:
- Kaç satır kampanyalı/indirimli, kaç satır normal fiyatlı.
- Normal ve kampanyalı fiyatların **ayrı ayrı** medyanı.
- Değişimin nedeni, ürün sayfasındaki etikete ve önceki taramaya (`data/web-fiyat-taramasi.csv`) göre:
  - Etiket var, liste fiyatı aynı → "Kampanyalı fiyat (liste fiyatı X TL); normal fiyat değişmedi."
  - Etiket yok, fiyat düşmüş → "Liste fiyatı düştü; kalıcı olabilir."
  - Etiket yok, fiyat yükselmiş → "Liste fiyatı yükseldi."
- Medyan önceki taramadan **%50'den fazla** saparsa uyarı verilir (öneri: Claude · onay: Hilal). *(Bu kadar büyük bir fark genellikle fiyatın yanlış okunduğunu gösterir.)*

Bu notlar 19 sütunlu tabloya eklenmez; tablo ortak sözleşmeye (#117) bağlı. Notlar `runs/ajan1/` raporunda durur, Ajan 2 ve 3 oradan okur.

## Karar kaydı (28 Kasım 2026)

- **Fiyat değişiminin nedeni (Hilal):** 3 günlük bir indirim ya da zam medyanı bir anda kaydırırsa, değişimin sitenin yaptığı bir işlemden kaynaklandığı bildirilmeli; böylece fiyat karşılaştırması yanlış yorumlanmaz. Kampanya değilse, rakibin artık gerçekten daha düşük fiyattan sattığını da bilmeliyiz.
- **İndirim etiketi (Hilal):** Nedeni medyan karşılaştırmasıyla tahmin etmek yerine, her ürünün sayfasındaki indirim/kampanya etiketinden doğrudan okumak.
- **Nemlendirici eşleşmesi (Hilal):** Ürünü adına göre değil işlevine göre eşleştirmek; gece kremi de bir yüz nemlendiricisi. Gratis'in kategorisine güvenmek, çünkü müşteri rakip fiyatını o kategori üzerinden görüyor. Öneri Tuğba'ya #115'te sunuldu.
- **Kontrollerin seçimi (Hilal):** Önceki taramayla karşılaştırma ve tekrar ayıklama, skill'leri zenginleştirme isteğim üzerine önerilen kontroller arasından seçildi.
- *Claude'un katkısı:* Kampanya süresi çoğu zaman sayfada yazmadığı için "geçici" yerine "kampanyalı" ifadesini önerdi. Notların 19 sütunlu tabloya değil çalışma raporuna yazılmasını önerdi (sözleşme #117). Nemlendirici kategorisindeki eşleşme riskini fark etti.
