# Git Keşfi — Ali Haydar Polat

**Repo:** [sdv-dev/SDV — The Synthetic Data Vault](https://github.com/sdv-dev/SDV)

## Çözdüğü problem

Gerçek veriyi (müşteri, sipariş vb.) gizlilik nedeniyle paylaşamadığımız ya da elimizde yeterli veri olmadığı durumlarda, gerçeğe benzeyen **sentetik tablo verisi** üretmek. SDV, örnek bir tablodaki desenleri makine öğrenmesiyle öğrenip aynı istatistiksel yapıya sahip yeni veri üretir; tek tablo, birbirine bağlı tablolar ve zaman sıralı veriler için çalışır.

## Güçlü yanları

- **Birden fazla model:** Klasik istatistik yöntemlerinden (GaussianCopula) derin öğrenmeye (CTGAN) kadar farklı üreticiler sunuyor; ihtiyaca göre hız ya da gerçekçilik seçilebiliyor.
- **Kalite ölçümü dahil:** Üretilen veriyi gerçek veriyle karşılaştıran değerlendirme ve kalite raporu çıkarıyor — "ürettiğimiz veri ne kadar inandırıcı?" sorusuna sayısal cevap veriyor.
- **İş kuralları ve anonimleştirme:** Kısıtlar tanımlanabiliyor (örn. "adet > 0", "teslim tarihi ≥ sipariş tarihi"), kişisel alanlar anonimleştirilebiliyor.

## Kendi projemizde kullanabileceğimiz fikir

- Görev 1'de sipariş verisini kuralları elle yazarak üretiyoruz. SDV'nin **kısıt (constraint) mantığını** örnek alıp iş kurallarımızı (adet > 0, fiyat aralığı, kampanya dönemlerinde satış artışı) veri sözlüğünde açıkça tanımlayabilir, DQ'nun testlerini de bu kurallara bağlayabiliriz. SDV'nin "gerçek vs sentetik" kalite raporu fikri, DQ'nun veri kalitesi testleri için iyi bir model.
