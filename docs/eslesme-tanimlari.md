# Ajan 2: 25 ürünün "benzer" eşleşme tanımları

Durum: Tuğba Tuana Kaygısız (Ajan 2) onayladı, 24 Kasım 2026. Hilal Elçin Şahin (Ajan 1) kontrol edecek. İlgili Issue: #96 (Ajan 1 çıktı şeması).

Kaynak: `src/simulasyon.py` içindeki `KATEGORI_URUN` (25 ürün, liste fiyatları TL).

## Ortak kurallar

1. **Eşleşme türü:** Sadece "benzer". Rakip ürün adında en az bir "dahil" ifadesi geçmeli, hiçbir "hariç" ifadesi geçmemeli (büyük/küçük harf ve Türkçe karakter duyarsız).
2. **Otomatik eleme (anlaşma):** Fiyat < 0,3x veya > 3x liste fiyatı → `elendi`, gerekçe "fiyat bandı dışı". Satır silinmez.
3. **Makul aralık:** Varsayılan 0,4x–2,5x liste fiyatı; Kitap kategorisinde 0,5x–2x (kitap fiyatları daha dar dağılıyor). Otomatik bandın içinde kalıp makul aralığın dışına düşen satırlar elenmez, `eslesme_guveni = dusuk` işaretlenir.
4. **Güven (`eslesme_guveni`):** Yalnızca üç değer alır: `yuksek` / `orta` / `dusuk`. Dahil ifadesi + birim/miktar uyumlu + makul aralıkta → `yuksek`; biri eksik → `orta`; makul aralık dışı → `dusuk`.
5. **Çoklu paket (2'li, 3'lü, set):** Şimdilik elenir, gerekçe "çoklu paket". (Saklama Kabı Seti hariç; o zaten set.)
6. **İkinci el / yenilenmiş / teşhir:** Hep elenir, gerekçe "ikinci el".
7. **Fiyat:** Karşılaştırmada indirimli fiyat varsa o, yoksa liste fiyatı kullanılır; TL dışı para birimi elenir.

## Tablo

TL sütunları web fiyat taramasına göre güncellenen liste fiyatlarından (`data/urun-listesi-web.csv`) hesaplandı; kaynak Hilal'in taraması (`data/web-fiyat-taramasi.csv`, 24.11.2026, PR #103). 22 üründe taramadaki `onerilen_liste_tl` kullanıldı. Üç üründe eski liste fiyatı korundu:

- **Spor Ayakkabı (1899):** Web karşılığı zayıf (ilk sayfada spor ayakkabı yok).
- **Masa Lambası (399):** 24 Kasım taramasında yalnızca Koçtaş "Çocuk Masa Lambası" bulunmuştu (n 37, medyan 936 TL). 25 Kasım'da IKEA "Masa Lambaları" kategorisinden yeniden tarandı: **52 ürün, medyan 1.699 TL** (p25 1.199, p75 2.461; liste fiyatının 4,3 katı; PR #107, `docs/fiyat-taramasi.md`). Liste fiyatı bu teslimde bilerek 399 TL'de bırakıldı; böylece `data/urun-listesi-web.csv`, TL bantları, `data/siparisler-web.csv` ve MD5 değişmedi (karar 5).
- **Kahve Makinesi (2999):** Tarama espresso ağırlıklı (medyan 14.999). Bu fiyat liste olsaydı otomatik bant 4.500 TL altını eleyecek, "dahil" listesindeki filtre kahve makinelerinin hepsi (taramada okunan tek örnek 1.299 TL) elenecekti.

Uyarı ile kullanılanlar:

- **Bluetooth Hoparlör (7499):** Medyanı parti hoparlörleri yükseltiyor (p25 2.799). Küçük taşınabilir hoparlörler makul aralığın altında kalıp `dusuk` güven alabilir.
- **Saklama Kabı Seti (639):** Taramada tekli kaplar da var; bizim kuralımızda tekli kap elenir. Medyan setlerin gerçek fiyatından düşük olabilir.

Varsayılan simülasyon (`data/siparisler-g2.csv`, betikteki 25 ürün) değişmedi; web fiyatlı veri `--urun_listesi data/urun-listesi-web.csv` ile üretilir.

| # | Kategori | Ürün | Liste (TL) | Dahil anahtar kelimeler | Hariç anahtar kelimeler | Beklenen birim/miktar | Makul aralık (TL) | Oto. eleme sınırı (TL) |
|---|---|---|---|---|---|---|---|---|
| 1 | Elektronik | Kablosuz Kulaklık | 2999 | kablosuz kulaklık, bluetooth kulaklık, tws kulaklık | kablolu, kılıf, kulaklık ucu, şarj kutusu, stand, adaptör | 1 adet (çift) | 1200–7500 | <899,70 / >8997 |
| 2 | Elektronik | Bluetooth Hoparlör | 7499 | bluetooth hoparlör, taşınabilir hoparlör, kablosuz hoparlör | soundbar, ev sinema, kablolu, kılıf, askı | 1 adet | 3000–18750 | <2249,70 / >22497 |
| 3 | Elektronik | Powerbank | 2999 | powerbank, taşınabilir şarj cihazı | güç istasyonu, kablo, adaptör, kılıf | 1 adet; 10.000–20.000 mAh | 1200–7500 | <899,70 / >8997 |
| 4 | Elektronik | Akıllı Saat | 14999 | akıllı saat, smartwatch | akıllı bileklik, kordon, kayış, ekran koruyucu, şarj kablosu, çocuk | 1 adet | 6000–37500 | <4499,70 / >44997 |
| 5 | Elektronik | Klavye | 1169 | klavye, mekanik klavye, oyuncu klavyesi, kablosuz klavye | elektronik klavye (müzik aleti), piyano, keycap, tuş seti, kılıf, bilek desteği, klavye mouse seti | 1 adet | 470–2920 | <350,70 / >3507 |
| 6 | Giyim | Tişört | 1099 | tişört, t-shirt, tshirt | uzun kollu, polo, çocuk, bebek, 2'li, 3'lü | 1 adet | 440–2750 | <329,70 / >3297 |
| 7 | Giyim | Kot Pantolon | 1599 | kot pantolon, jean, denim pantolon | kot ceket, kot şort, etek, çocuk | 1 adet | 640–4000 | <479,70 / >4797 |
| 8 | Giyim | Sweatshirt | 1199 | sweatshirt, kapüşonlu sweatshirt, hoodie | eşofman takımı, eşofman altı, çocuk | 1 adet | 480–3000 | <359,70 / >3597 |
| 9 | Giyim | Spor Ayakkabı | 1899 | spor ayakkabı, sneaker, koşu ayakkabısı | terlik, krampon, bağcık, ayakkabı boyası, temizleyici, çocuk | 1 çift | 760–4750 | <569,70 / >5697 |
| 10 | Giyim | Mont | 3499 | mont, şişme mont, parka | yelek, yağmurluk, çocuk | 1 adet | 1400–8750 | <1049,70 / >10497 |
| 11 | Ev & Yaşam | Kahve Makinesi | 2999 | kahve makinesi, filtre kahve makinesi, türk kahvesi makinesi, espresso makinesi | kahve çekirdeği, kapsül, filtre kağıdı, kireç çözücü, kahve değirmeni, yedek parça | 1 adet | 1200–7500 | <899,70 / >8997 |
| 12 | Ev & Yaşam | Battaniye | 999 | battaniye, polar battaniye, welsoft battaniye | elektrikli battaniye, bebek, kılıf | 1 adet; tek veya çift kişilik | 400–2500 | <299,70 / >2997 |
| 13 | Ev & Yaşam | Masa Lambası | 399 | masa lambası, çalışma lambası, led masa lambası | ampul, lambader, avize, abajur başlığı | 1 adet | 160–1000 | <119,70 / >1197 |
| 14 | Ev & Yaşam | Saklama Kabı Seti | 639 | saklama kabı seti, erzak saklama seti, vakumlu saklama kabı seti | tekli, beslenme çantası, yedek kapak | 1 set; 3–12 parça (parça sayısı kaydedilir) | 260–1600 | <191,70 / >1917 |
| 15 | Ev & Yaşam | Halı | 2239 | halı, salon halısı | paspas, kapı önü, banyo, yolluk, halı yıkama | 1 adet; yaklaşık 160x230 cm (120x180 – 200x290 kabul) | 900–5600 | <671,70 / >6717 |
| 16 | Kozmetik | Nemlendirici | 559 | Gratis kategori: Yüz Nemlendirici Gece Kremleri; nemlendirici krem, yüz nemlendirici | hava nemlendirici, ortam nemlendirici, saç, dudak, göz kremi, göz çevresi, serum, maske | 1 adet; 30–100 ml | 220–1400 | <167,70 / >1677 |
| 17 | Kozmetik | Şampuan | 269 | şampuan | kuru şampuan, köpek, kedi, evcil, halı, oto, saç kremi | 1 adet; 300–600 ml | 110–670 | <80,70 / >807 |
| 18 | Kozmetik | Parfüm | 1199 | parfüm, edp, edt, eau de parfum, eau de toilette | deodorant, vücut spreyi, body mist, oda parfümü, araç kokusu, tester | 1 adet; 50–100 ml | 480–3000 | <359,70 / >3597 |
| 19 | Kozmetik | Güneş Kremi | 619 | güneş kremi, güneş koruyucu, spf | bronzlaştırıcı, güneş sonrası, after sun, güneş gözlüğü | 1 adet; 40–100 ml | 250–1550 | <185,70 / >1857 |
| 20 | Kozmetik | Ruj | 379 | ruj, mat ruj, likit ruj | dudak kalemi, dudak balmı, dudak parlatıcısı, ruj seti | 1 adet | 150–950 | <113,70 / >1137 |
| 21 | Kitap | Roman | 299 | D&R kategori: Roman | e-kitap, sesli kitap, set, kutulu, ikinci el | 1 kitap | 150–600 | <89,70 / >897 |
| 22 | Kitap | Deneme | 249 | D&R kategori: Deneme Yazın | deneme sınavı, soru bankası, tyt, ayt, lgs, kpss, set | 1 kitap | 120–500 | <74,70 / >747 |
| 23 | Kitap | Ders Kitabı | 449 | D&R kategori: Ders ve Sınav Kitapları; konu anlatımlı, ders kitabı, yardımcı ders kitabı | deneme sınavı, soru bankası, e-kitap, set | 1 kitap | 220–900 | <134,70 / >1347 |
| 24 | Kitap | Çocuk Kitabı | 179 | D&R kategori: Çocuk ve Gençlik; masal, hikaye kitabı | boyama, çıkartma, set, kutulu, oyuncak | 1 kitap | 90–360 | <53,70 / >537 |
| 25 | Kitap | Şiir Kitabı | 189 | D&R kategori: Şiir | set, kutulu, ikinci el | 1 kitap | 90–380 | <56,70 / >567 |

## Dikkat edilecek tuzaklar

- **Klavye:** "klavye" müzik aletini (elektronik klavye/org) de yakalar; hariç listesinde.
- **Nemlendirici:** "hava/ortam nemlendirici" cihazları 189 TL'lik kremle karışır; hariç listesinde.
- **Nemlendirici (28 Kasım, Hilal önerisi #115):** Gratis'in "Yüz Nemlendirici Gece Kremleri" kategorisindeki gece kremlerinin çoğunun adında "nemlendirici" geçmez; ad kuralıyla eşleşmeden düşmesinler diye Kitap'taki "D&R kategori" kuralı gibi kategori kuralı eklendi. Eşleşme işleve göre yapılır: gece kremi de bir yüz nemlendiricisidir. Göz kremi, göz çevresi ürünleri, serum ve maske hariç.
- **Deneme:** "deneme" kelimesi sınav deneme kitaplarını yakalar; bu yüzden Kitap kategorisi + sınav kelimeleri hariç.
- **Ders Kitabı:** MEB ders kitapları satışta değil; piyasada karşılığı "konu anlatımlı / yardımcı ders kitabı". Eşleşme zayıf kalabilir, güven en fazla `orta` önerilir.
- **Kahve Makinesi, Parfüm, Akıllı Saat:** Fiyat yelpazesi çok geniş (markaya göre); üst segment ürünler otomatik bantta bile elenebilir, bu beklenen bir durum.
- **Kaynaklar:** Elektronik MediaMarkt, Giyim Koton, Kozmetik Gratis, Ev & Yaşam Koçtaş ve IKEA (yalnız Masa Lambası; tarayıcı gerektiren kaynak), Kitap D&R (Kitapyurdu robots.txt erişimi reddettiği için elendi). Tanımlar ürün adına dayanır, kaynaktan bağımsız uygulanır.

## Kararlar (24 Kasım 2026)

1. Makul aralık varsayılanı 0,4x–2,5x (Kitap: 0,5x–2x). Otomatik bant 0,3x–3x aynen kalır.
2. Çoklu paketler (2'li, 3'lü, set) şimdilik elenir; adet başı fiyata bölme yapılmaz.
3. Liste fiyatları web medyanlarına göre güncellendi (`data/urun-listesi-web.csv`); TL bantları bu fiyatlardan yeniden hesaplandı (Hilal'in #100 incelemesi, 1. madde; PR #102).
4. Kozmetikte ml başı fiyat karşılaştırması sonraki haftaya bırakıldı.

## Kararlar (25 Kasım 2026)

5. **Masa Lambası liste fiyatı 399 TL'de kalır (bilinen sınırlama).** IKEA taramasında medyan 1.699 TL olsa da liste fiyatı bu teslimde güncellenmedi. Sonuç: otomatik bant (kural 2) 1.197 TL'nin üstünü eler; IKEA'da p25 bile 1.199 TL olduğu için IKEA satırlarının **yaklaşık dörtte üçü** "fiyat bandı dışı" gerekçesiyle `elendi` olur. Satırlar silinmez, yalnız işaretlenir. Masa Lambası'nın rakip karşılaştırması bu yüzden az sayıda ucuz ürüne dayanır; analizde bu ürünün sonucu ihtiyatla yorumlanır. Liste fiyatını güncelleme kararı sonraki teslime bırakıldı.

---

Üretim: Bu tablo Claude ile taslaklandı, Tuğba Tuana Kaygısız gözden geçirip onayladı. Prompt özeti: "src/simulasyon.py'deki 25 ürün için benzer eşleşme tanımı taslakla: dahil/hariç anahtar kelimeler, beklenen birim/miktar, liste fiyatına göre makul rakip fiyat aralığı." 25 Kasım güncellemesi (Masa Lambası notu, karar 5) Claude ile yazıldı, Tuğba Tuana Kaygısız onayladı.
