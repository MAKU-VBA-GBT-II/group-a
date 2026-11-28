---
name: ajan1-kaynak-ekleme
description: Ajan 1'e yeni bir rakip site ekleme kılavuzu (köprü). Sonraki haftalarda Koçtaş, MediaMarkt, Koton ve D&R'ı aynı yolla eklemek için kullan.
---

# ajan1-kaynak-ekleme: Yeni site ekleme (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114

Kod iki katmanlıdır: ortak iskelet (bekleme, fiyat okuma, eşleşme, tablo, tazelik kapısı) değişmez; her site için yalnızca küçük bir site parçası eklenir.

## Adımlar
1. **İzin kontrolü:** robots.txt ve kullanım şartları okunur; sonuç `docs/oneri.md` §3'e yazılır. Otomatik erişimi açıkça yasaklayan site eklenmez. Kategori sayfası otomatik erişime 403 gibi bir engel dönüyorsa engel aşılmaya çalışılmaz, başka bir site seçilir *(28 Kasım: Koçtaş Masa Lambası sayfası 403 verdi)*.
2. **Sözleşme ve diğer ajanlar:** Yeni site adı `rakip_site` sütununun izinli değerleri arasında olmalı (`docs/ajan1-cikti-semasi.md`); Ajan 2 (`src/ajan2_analiz.py`) ve Ajan 3 (`src/ajan3_denetim.py`) site adını alan adıyla eşleyen listeye (`SITE_ALAN_ADI`) sahiptir. Listede olmayan sitenin satırları bütün tabloyu reddettirir. Bu yüzden site eklenmeden önce sözleşme, iki ajanın listesi ve `docs/oneri.md` ekip onayıyla güncellenir. *(28 Kasım: Bauhaus bu nedenle 2. haftaya bırakıldı.)*
3. **Kategori sayfası:** Ürünün sitedeki kategori sayfası bulunur (arama sayfası kullanılmaz).
4. **Tarayıcı testi:** Sayfa bir kez düz istekle, bir kez tarayıcıyla açılır; ürünler ham HTML'de yoksa site parçası tarayıcı modunda yazılır.
5. **Site parçası:** Ürün adı, liste fiyatı, indirimli fiyat, indirim etiketi ve ürün adresinin sayfada nerede durduğu tanımlanır. *(Kod yazılınca örnekle netleşecek.)*
6. **Eşleşme kontrolü:** Kategori adı eşleşme tanımlarıyla uyuşmuyorsa (Nemlendirici örneği) Ajan 2'ye öneri götürülür.
7. **Deneme:** Yeni site tek başına çalıştırılır; okunan ürün sayısı ve medyan önceki taramayla karşılaştırılır.
8. **Kayıt:** `AGENTS.md` ve `ajan1-alma`'daki kaynak tablosu güncellenir.

## Karar kaydı (28 Kasım 2026)

- **Köprü (Hilal):** Bütün siteleri bu haftaya sığdırmak yerine, adım adım ve sağlam gitmek için IKEA + Gratis ile başlayıp diğer sitelere kolayca bağlanacak bir köprü kurmak.
- *Claude'un katkısı:* Köprüyü "ortak iskelet + her site için küçük bir parça" yapısına çevirdi.
- **İkinci kaynak (Hilal, 28 Kasım):** Masa Lambası için tek kaynağın sonucu taraflı bırakacağını söyledim. İkinci site fiyatlara bakılmadan bir ölçütle seçildi (geniş kitleye satan, çok markalı yapı market). Bauhaus kodu hazırlandı, ama sözleşmedeki site listesi ve Ajan 2 / Ajan 3'ün alan adı listeleri değişmeden eklenemeyeceği için 2. haftaya bırakıldı; bulgusu kanıt olarak PR'a yazıldı.
- *Claude'un katkısı (28 Kasım):* Bauhaus kodunu sözleşmeyi kontrol etmeden yazdı; göndermeden önceki kontrolde engeli buldu ve commit'lemedi. Bu yüzden 2. adım (sözleşme ve diğer ajanlar) eklendi.
