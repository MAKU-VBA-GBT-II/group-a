# Ajan 2: 25 ürünün "benzer" eşleşme tanımları

Durum: Tuğba Tuana Kaygısız (Ajan 2) onayladı, 24 Kasım 2026. Hilal Elçin Şahin (Ajan 1) kontrol edecek. İlgili Issue: #96 (Ajan 1 çıktı şeması).

Kaynak: `src/simulasyon.py` içindeki `KATEGORI_URUN` (25 ürün, liste fiyatları TL).

## Ortak kurallar

1. **Eşleşme türü:** Sadece "benzer". Rakip ürün adında en az bir "dahil" ifadesi geçmeli, hiçbir "hariç" ifadesi geçmemeli (büyük/küçük harf ve Türkçe karakter duyarsız).
2. **Otomatik eleme (anlaşma):** Fiyat < 0,3x veya > 3x liste fiyatı → `elendi`, gerekçe "fiyat bandı dışı". Satır silinmez.
3. **Makul aralık (bu taslağın önerisi):** Varsayılan 0,4x–2,5x liste fiyatı; Kitap kategorisinde 0,5x–2x (kitap fiyatları daha dar dağılıyor). Otomatik bandın içinde kalıp makul aralığın dışına düşen satırlar elenmez, `eslesme_guveni = dusuk` işaretlenir.
4. **Güven:** Dahil ifadesi + birim/miktar uyumlu + makul aralıkta → `yuksek`; biri eksik → `orta`; makul aralık dışı → `dusuk`.
5. **Çoklu paket (2'li, 3'lü, set):** Şimdilik elenir, gerekçe "çoklu paket". (Saklama Kabı Seti hariç; o zaten set.)
6. **İkinci el / yenilenmiş / teşhir:** Hep elenir, gerekçe "ikinci el".
7. **Fiyat:** Karşılaştırmada indirimli fiyat varsa o, yoksa liste fiyatı kullanılır; TL dışı para birimi elenir.

## Tablo

| # | Kategori | Ürün | Liste (TL) | Dahil anahtar kelimeler | Hariç anahtar kelimeler | Beklenen birim/miktar | Makul aralık (TL) | Oto. eleme sınırı (TL) |
|---|---|---|---|---|---|---|---|---|
| 1 | Elektronik | Kablosuz Kulaklık | 1299 | kablosuz kulaklık, bluetooth kulaklık, tws kulaklık | kablolu, kılıf, kulaklık ucu, şarj kutusu, stand, adaptör | 1 adet (çift) | 520–3250 | <389,70 / >3897 |
| 2 | Elektronik | Bluetooth Hoparlör | 899 | bluetooth hoparlör, taşınabilir hoparlör, kablosuz hoparlör | soundbar, ev sinema, kablolu, kılıf, askı | 1 adet | 360–2250 | <269,70 / >2697 |
| 3 | Elektronik | Powerbank | 599 | powerbank, taşınabilir şarj cihazı | güç istasyonu, kablo, adaptör, kılıf | 1 adet; 10.000–20.000 mAh | 240–1500 | <179,70 / >1797 |
| 4 | Elektronik | Akıllı Saat | 3499 | akıllı saat, smartwatch | akıllı bileklik, kordon, kayış, ekran koruyucu, şarj kablosu, çocuk | 1 adet | 1400–8750 | <1049,70 / >10497 |
| 5 | Elektronik | Klavye | 749 | klavye, mekanik klavye, oyuncu klavyesi, kablosuz klavye | elektronik klavye (müzik aleti), piyano, keycap, tuş seti, kılıf, bilek desteği, klavye mouse seti | 1 adet | 300–1870 | <224,70 / >2247 |
| 6 | Giyim | Tişört | 249 | tişört, t-shirt, tshirt | uzun kollu, polo, çocuk, bebek, 2'li, 3'lü | 1 adet | 100–620 | <74,70 / >747 |
| 7 | Giyim | Kot Pantolon | 699 | kot pantolon, jean, denim pantolon | kot ceket, kot şort, etek, çocuk | 1 adet | 280–1750 | <209,70 / >2097 |
| 8 | Giyim | Sweatshirt | 549 | sweatshirt, kapüşonlu sweatshirt, hoodie | eşofman takımı, eşofman altı, çocuk | 1 adet | 220–1370 | <164,70 / >1647 |
| 9 | Giyim | Spor Ayakkabı | 1899 | spor ayakkabı, sneaker, koşu ayakkabısı | terlik, krampon, bağcık, ayakkabı boyası, temizleyici, çocuk | 1 çift | 760–4750 | <569,70 / >5697 |
| 10 | Giyim | Mont | 2299 | mont, şişme mont, parka | yelek, yağmurluk, çocuk | 1 adet | 920–5750 | <689,70 / >6897 |
| 11 | Ev & Yaşam | Kahve Makinesi | 2999 | kahve makinesi, filtre kahve makinesi, türk kahvesi makinesi, espresso makinesi | kahve çekirdeği, kapsül, filtre kağıdı, kireç çözücü, kahve değirmeni, yedek parça | 1 adet | 1200–7500 | <899,70 / >8997 |
| 12 | Ev & Yaşam | Battaniye | 449 | battaniye, polar battaniye, welsoft battaniye | elektrikli battaniye, bebek, kılıf | 1 adet; tek veya çift kişilik | 180–1120 | <134,70 / >1347 |
| 13 | Ev & Yaşam | Masa Lambası | 399 | masa lambası, çalışma lambası, led masa lambası | ampul, lambader, avize, abajur başlığı | 1 adet | 160–1000 | <119,70 / >1197 |
| 14 | Ev & Yaşam | Saklama Kabı Seti | 299 | saklama kabı seti, erzak saklama seti, vakumlu saklama kabı seti | tekli, beslenme çantası, yedek kapak | 1 set; 3–12 parça (parça sayısı kaydedilir) | 120–750 | <89,70 / >897 |
| 15 | Ev & Yaşam | Halı | 1799 | halı, salon halısı | paspas, kapı önü, banyo, yolluk, halı yıkama | 1 adet; yaklaşık 160x230 cm (120x180 – 200x290 kabul) | 720–4500 | <539,70 / >5397 |
| 16 | Kozmetik | Nemlendirici | 189 | nemlendirici krem, yüz nemlendirici | hava nemlendirici, ortam nemlendirici, saç, dudak | 1 adet; 30–100 ml | 80–470 | <56,70 / >567 |
| 17 | Kozmetik | Şampuan | 129 | şampuan | kuru şampuan, köpek, kedi, evcil, halı, oto, saç kremi | 1 adet; 300–600 ml | 50–320 | <38,70 / >387 |
| 18 | Kozmetik | Parfüm | 999 | parfüm, edp, edt, eau de parfum, eau de toilette | deodorant, vücut spreyi, body mist, oda parfümü, araç kokusu, tester | 1 adet; 50–100 ml | 400–2500 | <299,70 / >2997 |
| 19 | Kozmetik | Güneş Kremi | 279 | güneş kremi, güneş koruyucu, spf | bronzlaştırıcı, güneş sonrası, after sun, güneş gözlüğü | 1 adet; 40–100 ml | 110–700 | <83,70 / >837 |
| 20 | Kozmetik | Ruj | 159 | ruj, mat ruj, likit ruj | dudak kalemi, dudak balmı, dudak parlatıcısı, ruj seti | 1 adet | 60–400 | <47,70 / >477 |
| 21 | Kitap | Roman | 149 | Kitapyurdu kategori: Roman | e-kitap, sesli kitap, set, kutulu, ikinci el | 1 kitap | 70–300 | <44,70 / >447 |
| 22 | Kitap | Deneme | 129 | Kitapyurdu kategori: Deneme | deneme sınavı, soru bankası, tyt, ayt, lgs, kpss, set | 1 kitap | 60–260 | <38,70 / >387 |
| 23 | Kitap | Ders Kitabı | 349 | konu anlatımlı, ders kitabı, yardımcı ders kitabı | deneme sınavı, soru bankası, e-kitap, set | 1 kitap | 170–700 | <104,70 / >1047 |
| 24 | Kitap | Çocuk Kitabı | 99 | Kitapyurdu kategori: Çocuk Kitapları; masal, hikaye kitabı | boyama, çıkartma, set, kutulu, oyuncak | 1 kitap | 50–200 | <29,70 / >297 |
| 25 | Kitap | Şiir Kitabı | 119 | Kitapyurdu kategori: Şiir | set, kutulu, ikinci el | 1 kitap | 60–240 | <35,70 / >357 |

## Dikkat edilecek tuzaklar

- **Klavye:** "klavye" müzik aletini (elektronik klavye/org) de yakalar; hariç listesinde.
- **Nemlendirici:** "hava/ortam nemlendirici" cihazları 189 TL'lik kremle karışır; hariç listesinde.
- **Deneme:** "deneme" kelimesi sınav deneme kitaplarını yakalar; bu yüzden Kitap kategorisi + sınav kelimeleri hariç.
- **Ders Kitabı:** MEB ders kitapları satışta değil; piyasada karşılığı "konu anlatımlı / yardımcı ders kitabı". Eşleşme zayıf kalabilir, güven en fazla `orta` önerilir.
- **Kahve Makinesi, Parfüm, Akıllı Saat:** Fiyat yelpazesi çok geniş (markaya göre); üst segment ürünler otomatik bantta bile elenebilir, bu beklenen bir durum.
- **Kitap dışı kategoriler:** `docs/oneri.md`'ye göre henüz kaynak yok; tanımlar kaynaktan bağımsız yazıldı.

## Kararlar (24 Kasım 2026)

1. Makul aralık varsayılanı 0,4x–2,5x (Kitap: 0,5x–2x). Otomatik bant 0,3x–3x aynen kalır.
2. Çoklu paketler (2'li, 3'lü, set) şimdilik elenir; adet başı fiyata bölme yapılmaz.
3. Kozmetikte ml başı fiyat karşılaştırması sonraki haftaya bırakıldı.

---

Üretim: Bu tablo Claude ile taslaklandı, Tuğba Tuana Kaygısız gözden geçirip onayladı. Prompt özeti: "src/simulasyon.py'deki 25 ürün için benzer eşleşme tanımı taslakla: dahil/hariç anahtar kelimeler, beklenen birim/miktar, liste fiyatına göre makul rakip fiyat aralığı."
