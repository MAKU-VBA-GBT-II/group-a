---
name: ajan3-isleme
description: Ajan 3'ün (denetim) ikinci aşaması. Ajan 2 çıktısındaki bütün sayıları ham dosyalardan bağımsız olarak yeniden hesaplar, kaynak kayıtlarını ve maliyetsiz kâr iddiası olmadığını denetler. ajan3-alma geçtikten sonra kullan.
---

# ajan3-isleme: bağımsız doğrulama (Ajan 3)

**Sahibi:** Sema Nur Doğan · **Issue:** #116 · **Önceki:** `ajan3-alma` · **Sonraki:** `ajan3-teslim`

## Kontroller (`src/ajan3_denetim.py` → `isleme()`)

`ajan2_analiz` modülü kullanılmaz; hesap `data/urun-listesi-web.csv`, `data/siparisler-web.csv` ve Ajan 1 CSV'sinden yeniden yapılır.

- Ürün kümesi ve kategoriler.
- Liste fiyatı, rakip medyanı, fiyat farkı, kullanılan/elenen sayısı, satış adedi, ciro.
- Pearson fark–adet ve fark–ciro, gözlem sayısı.
- Her CSV satırı için adresi, zamanı ve satır numarası uyan kaynak kaydı; liste ve sipariş dosyası için zamanlı kayıt.
- Eylem izinli değerlerden biri (medyan yoksa yalnız `veri_topla`); gerekçe boş değil.
- Maliyet girdisi olmadığı için `kar_durumu = maliyet_eksik`.

Medyana girmeyen satır: `elendi` dolu (Saklama Kabı Seti'nde `çoklu paket` hariç), `stok_durumu = yok`, `kdv_dahil ≠ evet` ya da işaretlenmemiş olsa da karşılaştırma fiyatı web liste fiyatının 0,3–3 katı dışında (eşleşme kuralı 2; sınırlar dahil). Hepsi "elenen" sayılır.

## Henüz yapılmayanlar

- **Kâr eşiği:** maliyet dosyasının biçimi ve eşik kararlaştırılmadı. Maliyet uydurulmaz.
- **Canlı fiyat doğrulaması:** gerçek Ajan 1 verisi gelince örnek satırların sayfası tarayıcıyla açılıp fiyat elle karşılaştırılacak, sonucu `runs/ajan3/` altına yazılacak. Sentetik `.example` adreslerine istek atılmaz.
- Kampanya eşiği gibi Ajan 2'nin öneri kuralları yeniden denetlenmiyor.
