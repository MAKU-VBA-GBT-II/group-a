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
- **Karşılaştırma fiyatı:** Herkesin şartsız, peşin, tek ürün için ödediği ve sayfada görebildiğimiz en düşük fiyat. `ham_fiyat_metni` bu fiyatın sayfadaki metnidir.
  - Şartsız sepette indirim ("Sepette %20", başka koşul yok) kategori sayfasında görünüyorsa diğer indirimler gibi karşılaştırma fiyatı olur (`fiyat_turu = indirimli`).
  - Koşullu indirimler karşılaştırmaya girmez, yalnız rapora yazılır: üyelik/kart (ör. Gratis Card), kupon, banka kampanyası, alt sepet tutarı, çoklu alım ("2. ürün %50").
  - Taksit vade farkı ürünün değil ödeme şeklinin fiyatıdır; peşin fiyat kullanılır. Kargo ücreti ürün fiyatına katılmaz.

## 2. Eşleştirme (`docs/eslesme-tanimlari.md`)
- Ürün adında en az bir "dahil" ifadesi geçmeli, hiçbir "hariç" ifadesi geçmemeli (örnek: Şampuan'da "kuru şampuan", "köpek" hariç).
- **Nemlendirici (Gratis):** Ürün, adından çok Gratis'in "Yüz Nemlendirici Gece Kremleri" kategorisinde bulunmasına göre dahil sayılır; "hariç" listesi (göz kremi, göz çevresi, serum, maske) yine uygulanır. Kitaplardaki "D&R kategori" kuralıyla aynı mantık. Bu kural #122 ile `docs/eslesme-tanimlari.md`'ye girdi; adı yetmeyip yalnız kategoriyle gelen satır `orta` güven alır.
- Miktar okunabiliyorsa `birim_miktar`'a yazılır (`400 ml`).
- `eslesme_guveni`: dahil ifadesi + miktar uyumlu + makul aralıkta → `yuksek`; biri eksik → `orta`; makul aralık dışı → `dusuk`.

## 3. Eleme (satır silinmez, `elendi` alanına gerekçe yazılır)
- Karşılaştırma fiyatı, **web fiyatlı listedeki** (`data/urun-listesi-web.csv`) liste fiyatımızın 0,3 katından az ya da 3 katından fazla → `fiyat bandı dışı`. Bu kural katıdır: bant dışı her satır mutlaka işaretlenir. *(Ajan 3, işaretlenmemiş bant dışı satırları da kendisi "elenen" sayıyor; işaretlenmezse Ajan 2 ile Ajan 3'ün sayıları tutmaz ve zincir geri döner.)*
- 2'li, 3'lü paketler → `çoklu paket` (Saklama Kabı Seti hariç). Paket ancak miktarla birlikte yazılmışsa sayılır ("3'lü", "3x", "2x400 ml", "400 ml x 2", "set", "paket"); "Lazer X3", "X5 Max" gibi ürün adları ve "60x20 cm" gibi ölçüler paket değildir.
- Stokta yok → `stok yok`.
- **Masa Lambası notu:** Liste fiyatımız 399 TL olduğu için IKEA satırlarının çoğu bant dışı kalacak (karar 5). Bu beklenen bir durum, hata değil.

## 4. Tekrar ayıklama
- Aynı `urun_url` birden fazla kez geldiyse tek satır kalır. *(Neden: "öne çıkanlar" ve liste alanında aynı ürün iki kez görünürse medyana iki kez girer.)*

## 5. Fiyat değişimi notu (çalışma raporuna)
Her ürün için rapora yazılır:
- Kaç satır kampanyalı/indirimli, kaç satır normal fiyatlı.
- Normal ve kampanyalı fiyatların **ayrı ayrı** medyanı.
- Değişimin nedeni, sayfadaki etikete ve önceki taramaya (`data/web-fiyat-taramasi.csv`) göre. Karşılaştırma ürün düzeyindedir: bugünkü satırların liste fiyatı medyanı, önceki taramada aynı ürün ve sitenin medyanıyla karşılaştırılır; %5'ten küçük fark "aynı" sayılır:
  - Kampanyalı/indirimli satır var, liste fiyatı aynı → "Kampanyalı fiyat (liste fiyatı medyanı X TL); normal fiyat değişmedi."
  - Liste fiyatı aynı, kampanya yok → "Liste fiyatı önceki taramayla aynı düzeyde."
  - Liste fiyatı düşmüş → "Liste fiyatı düştü (eski → yeni); kalıcı olabilir."
  - Liste fiyatı yükselmiş → "Liste fiyatı yükseldi (eski → yeni)."
  - Önceki taramada bu ürün ve site yoksa → "karşılaştırılamadı".
  - Önceki tarama kategori sayfasının ilk ürünleriyle yapıldığı için (`n` sütunu) örneklem bugünküyle birebir aynı değildir; rapora bu not ve önceki `n` de yazılır.
- **Kampanya tarihleri:** Kampanyanın başlangıç ve bitiş tarihi kategori sayfasında görünüyorsa rapora yazılır. Görünmüyorsa ürün sayfası ayrıca açılmaz (düşük hacim sözü); raporda "kampanyalı, bitiş tarihi bilinmiyor" yazar. Bitiş tarihi geçmiş bir kampanya fiyatı, satır taze olsa bile yeniden toplanmalıdır; bunu Ajan 2 ve Ajan 3 rapordan okuyarak bildirir.
- **Fiyat nedenleri:** Her ürün için karşılaştırmaya girmeyen fiyatlar ve nedeni yazılır: kart/üyelik, kupon, çoklu alım, koşullu sepette indirim, taksit, kargo eşiği. Sepette indirim kategori sayfasında görünmüyorsa "sepette indirim olup olmadığı bilinmiyor" yazılır.
- **Kategori ve ürün sayfası farkı:** Fiyat kategori sayfasından okunur. Ajan 3 onaydan önce ürün sayfasındaki fiyatı elle kontrol ettiği için raporda "fiyat kategori sayfasından okundu; ürün sayfasında sepette ya da kartla ek indirim görünebilir" notu bulunur.
- Medyan önceki taramadan **%50'den fazla** saparsa uyarı verilir (öneri: Claude · onay: Hilal). *(Bu kadar büyük bir fark genellikle fiyatın yanlış okunduğunu gösterir.)*

Bu notlar 19 sütunlu tabloya eklenmez; tablo ortak sözleşmeye (#117) bağlı. Notlar `runs/ajan1/` raporunda durur, Ajan 2 ve 3 oradan okur.

## Karar kaydı (28 Kasım 2026)

- **Fiyat değişiminin nedeni (Hilal):** 3 günlük bir indirim ya da zam medyanı bir anda kaydırırsa, değişimin sitenin yaptığı bir işlemden kaynaklandığı bildirilmeli; böylece fiyat karşılaştırması yanlış yorumlanmaz. Kampanya değilse, rakibin artık gerçekten daha düşük fiyattan sattığını da bilmeliyiz.
- **İndirim etiketi (Hilal):** Nedeni medyan karşılaştırmasıyla tahmin etmek yerine, her ürünün sayfasındaki indirim/kampanya etiketinden doğrudan okumak.
- **Nemlendirici eşleşmesi (Hilal):** Ürünü adına göre değil işlevine göre eşleştirmek; gece kremi de bir yüz nemlendiricisi. Gratis'in kategorisine güvenmek, çünkü müşteri rakip fiyatını o kategori üzerinden görüyor. Öneri Tuğba'ya #115'te sunuldu.
- **Kampanya bitişi (Hilal):** Veri Ajan 3'e ulaşana kadar kampanya bitebilir. Kampanya tarihleri belliyse Ajan 2 ve 3'e bildirilmeli; kampanyası bitmiş ürünün verisi, tazelik kontrolünü geçse bile yeniden toplanmalı.
- **Katı bant kuralı (Hilal):** Bant dışı satırlar kesinlikle işaretlenecek. Gratis fiyatlarımıza yakın olsa da uçuk fiyatları asıl diğer sitelerde göreceğiz; bunlar gözden kaçmamalı.
- **Karşılaştırma fiyatı ilkesi (Hilal):** Herkesin koşulsuz, şartsız alabileceği fiyat kullanılacak. Kart indirimi gibi her sitede olmayan uygulamalar ve taksit vade farkı gibi online alışverişte fiyat farkı yaratan sebepler tespit edilip Ajan 2 ve 3'e gönderilmeden önce nedenleriyle belirtilecek. Sepette indirim de bir indirimdir; müşteri için fark yaratmaz, diğer indirimlerle aynı yöntemle ele alınır.
- **Kontrollerin seçimi (Hilal):** Önceki taramayla karşılaştırma ve tekrar ayıklama, skill'leri zenginleştirme isteğim üzerine önerilen kontroller arasından seçildi.
- **Skill ile kod uyumu (Hilal, 28 Kasım akşamı):** Skill ajanın işleyişini tanımlar; kod skill'e göre şekillenir, tersi değil. Kuralları ve mantığı belli bir yapıya göre yazılan kod hem geliştirmeyi hızlandırır hem de sistemin sürdürülebilirliğini korur. Bu yüzden skill'de yazıp kodda olmayan önceki taramayla karşılaştırma koda eklendi.
- *Claude'un katkısı:* Kampanya süresi çoğu zaman sayfada yazmadığı için "geçici" yerine "kampanyalı" ifadesini önerdi. Notların 19 sütunlu tabloya değil çalışma raporuna yazılmasını önerdi (sözleşme #117). Nemlendirici kategorisindeki eşleşme riskini fark etti. Kampanya tarihlerinin çoğu zaman yalnız ürün sayfasında yazdığını, her ürün sayfasını açmanın düşük hacim sözüyle çeliştiğini belirtip tarihin yalnız kategori sayfasında görünüyorsa alınmasını önerdi. Bandın web fiyatlı listeye göre hesaplandığının yazılmasını ve Ajan 3'ün işaretlenmemiş bant dışı satırları saydığını fark etti. Koşullu sepette indirimlerin (alt sepet tutarı, çoklu alım) şartsız olanlardan ayrılmasını, sepette indirimin yalnız görünüyorsa kullanılmasını, vade farkının finansman maliyeti olduğu için katılmamasını ve Ajan 3'ün ürün sayfası kontrolü için kategori/ürün sayfası farkının rapora not edilmesini önerdi. Önceki tarama satır satır fiyat değil ürün başına özet (medyan, n) tuttuğu için karşılaştırmanın ürün düzeyinde, liste fiyatı medyanıyla ve %5 eşiğiyle yapılmasını önerdi; kampanya/indirim etiketi satır düzeyinde okunmaya devam ediyor.
