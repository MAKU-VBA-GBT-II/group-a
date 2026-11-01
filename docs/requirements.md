# Gereksinimler — Görev 2 Mini Ürün: Parametreli Sipariş Simülasyonu

**Şirket:** Sepetix Analitik (Grup A) · **Sektör:** E-ticaret · **Sürüm:** Görev 2 (Hafta 5–6) · **Yazan:** DQ — Sema Nur Doğan (#62)
**Kaynaklar:** `docs/veri-sozlugu.md` (#60) · `src/simulasyon.py` (#61, PR #66, #72) · `docs/analiz-g2.md` (#62) · `src/fe_gorsel.py` (#63) · `tests/test-cases.md` (#64)

## Amaç

Bir e-ticaret şirketinin sipariş verisini **gerçek kişi verisi kullanmadan**, ayarlanabilir parametrelerle ve tekrarlanabilir biçimde üretmek; bu veri üzerinde tanımlı 5 metriği hesaplayıp yorumlamak ve 3 grafikle sunmak. Ürün, Görev 1'deki sınırlılıkları (#30: haftada ~10 sipariş, ürüne özgü fiyat yok, nedensiz dalgalanma) gidermeyi ve büyük proje önerisine şablon olmayı hedefler.

## Ürünün yaptıkları

1. **Veri üretir:** `python src/simulasyon.py` ile `data/siparisler-g2.csv` dosyasını 14 sütunlu şemaya birebir uygun üretir (varsayılanla 8.208 sipariş, 26 hafta).
2. **Parametre alır:** 8 parametre betiğin başında ve komut satırından değiştirilebilir: `gun_sayisi`, `gunluk_siparis`, `hafta_sonu_katsayisi`, `kampanya_katsayisi`, `kampanya_donemleri`, `baslangic_tarihi`, `musteri_sayisi`, `tohum`.
3. **Satır sayısını öngörülebilir kılar:** satır sayısı parametrelerden formülle hesaplanır (örn. `gun_sayisi=10` → 424); her gün en az bir sipariş vardır (`max(1, …)`, PR #72).
4. **Tekrarlanabilirdir:** aynı parametre ve tohumla her çalıştırmada birebir aynı dosyayı (aynı MD5) üretir.
5. **Gerçekçi örüntü kurar:** ürüne özgü liste fiyatı (±%5), hafta sonu ve kampanya etkisi, kampanyada %10–30 indirim, %10 iade/iptal.
6. **Kendi çıktısını doğrular:** dosyayı yazmadan önce sözlükteki 11 kalite kuralını kontrol eder, yazdıktan sonra diskten geri okur.
7. **Geçersiz girdide durur:** aralık dışı, yanlış tipte ya da bozuk biçimli parametrede çökmeden Türkçe `ValueError` mesajı verir, 1 ile çıkar ve dosya yazmaz (PR #72).
8. **Analiz eder:** `python src/dq_analiz_g2.py --ek` ile M1 net ciro, M2 ortalama sepet, M3 haftalık ciro, M4 kanal kırılımı, M5 ilk 5 ürün ve M6 iade/iptal oranını hesaplar; sonuçlar `docs/analiz-g2.md`'dedir.
9. **Görselleştirir:** `python src/fe_gorsel.py` ile 3 PNG üretir: haftalık net ciro (zaman serisi), kanal bazlı ciro (kırılım), sipariş tutarı dağılımı (histogram).
10. **Test edilebilirdir:** `tests/test-cases.md`'deki 22 senaryo (şema, değerler, parametre davranışı, hata yönetimi) ile sınanır; sonuçlar `tests/test-log.md`'ye tarihli yazılır.

## Ürünün yapmadıkları

- **Gerçek kişi ya da işletme verisi içermez ve kabul etmez** (ad, TC no, telefon, e-posta, adres, kart no). Müşteriler yalnızca sentetik kimlikle (`M0001`) temsil edilir.
- **Gerçek müşteri davranışını modellemez:** ürünler eşit olasılıkla seçilir, iade/iptal ürün ve kanaldan bağımsızdır, müşteri sadakati ya da sepet tercihi yoktur (bkz. `docs/analiz-g2.md` → Sınırlılıklar).
- **Tahmin yapmaz:** geleceğe dönük satış tahmini, makine öğrenmesi modeli veya fiyat optimizasyonu içermez.
- **Stok, kargo süresi, maliyet ve kâr hesaplamaz;** ciro yalnızca satış tutarıdır (indirim düşülmüş, kâr marjı yok).
- **Canlı sistem değildir:** veritabanı, web arayüzü veya otomatik zamanlanmış çalışma yoktur; tüm çıktılar komut satırından üretilen dosyalardır.
- **İndirim oranlarını ve kategori ağırlıklarını parametre olarak almaz;** bunlar sözlükte sabittir (sonraki sürüm için öneri, bkz. analiz → Eylem önerisi).

## Kabul ve çalıştırma

```bash
pip install pandas matplotlib numpy
python src/simulasyon.py          # veri
python src/dq_analiz_g2.py --ek   # analiz
python src/fe_gorsel.py           # grafikler
```

Ürün; `gorev2-final` sürümünde, `main`'e PR ve DQ incelemesiyle girmiş kod, veri, analiz ve grafiklerle teslim edilmiş sayılır.
