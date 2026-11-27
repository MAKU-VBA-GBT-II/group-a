---
name: ajan1-kaynak-ekleme
description: Ajan 1'e yeni bir rakip site ekleme kılavuzu (köprü). Sonraki haftalarda Koçtaş, MediaMarkt, Koton ve D&R'ı aynı yolla eklemek için kullan.
---

# ajan1-kaynak-ekleme: Yeni site ekleme (Ajan 1)

**Sahibi:** Hilal Elçin Şahin · **Issue:** #114

Kod iki katmanlıdır: ortak iskelet (bekleme, fiyat okuma, eşleşme, tablo, tazelik kapısı) değişmez; her site için yalnızca küçük bir site parçası eklenir.

## Adımlar
1. **İzin kontrolü:** robots.txt ve kullanım şartları okunur; sonuç `docs/oneri.md` §3'e yazılır. Otomatik erişimi açıkça yasaklayan site eklenmez.
2. **Kategori sayfası:** Ürünün sitedeki kategori sayfası bulunur (arama sayfası kullanılmaz).
3. **Tarayıcı testi:** Sayfa bir kez düz istekle, bir kez tarayıcıyla açılır; ürünler ham HTML'de yoksa site parçası tarayıcı modunda yazılır.
4. **Site parçası:** Ürün adı, liste fiyatı, indirimli fiyat, indirim etiketi ve ürün adresinin sayfada nerede durduğu tanımlanır. *(Kod yazılınca örnekle netleşecek.)*
5. **Eşleşme kontrolü:** Kategori adı eşleşme tanımlarıyla uyuşmuyorsa (Nemlendirici örneği) Ajan 2'ye öneri götürülür.
6. **Deneme:** Yeni site tek başına çalıştırılır; okunan ürün sayısı ve medyan önceki taramayla karşılaştırılır.
7. **Kayıt:** `AGENTS.md` ve `ajan1-alma`'daki kaynak tablosu güncellenir.

## Karar kaydı (28 Kasım 2026)

- **Köprü (Hilal):** Bütün siteleri bu haftaya sığdırmak yerine, adım adım ve sağlam gitmek için IKEA + Gratis ile başlayıp diğer sitelere kolayca bağlanacak bir köprü kurmak.
- *Claude'un katkısı:* Köprüyü "ortak iskelet + her site için küçük bir parça" yapısına çevirdi.
