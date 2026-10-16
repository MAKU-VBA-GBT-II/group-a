# Git Keşfi — Tuğba Tuana Kaygısız

**Repo:** [Data-Centric-AI-Community/fg-data-profiling](https://github.com/Data-Centric-AI-Community/fg-data-profiling) (eski adıyla **ydata-profiling**, daha da önce *pandas-profiling*)

> Not: Paket yakın zamanda `ydata-profiling` → `fg-data-profiling` olarak yeniden adlandırıldı. Kurulum: `pip install fg-data-profiling`, içe aktarma: `from data_profiling import ProfileReport`.

## Çözdüğü problem

Yeni bir veri setiyle karşılaşınca "içinde ne var, temiz mi?" sorusuna cevap vermek için normalde onlarca satır pandas kodu (`describe()`, `isna()`, `duplicated()`, histogramlar, korelasyonlar…) yazmak gerekir. Bu kütüphane, tek satır kodla bir DataFrame'in tam keşifsel veri analizini (EDA) ve veri kalitesi raporunu çıkarır; sonucu paylaşılabilir bir HTML ya da otomasyona uygun bir JSON dosyası olarak verir.

## Güçlü yanları

- **Otomatik kalite uyarıları (Alerts):** Eksik değerler, tekrarlı satırlar, sabit sütunlar, aşırı çarpıklık, yüksek korelasyon gibi olası veri kalitesi sorunlarını kendiliğinden listeliyor — DQ rolünün aradığı şeylerin çoğunu tek raporda gösteriyor.
- **Tip algılama ve zengin özetler:** Her sütunun tipini (sayısal, kategorik, tarih, metin) otomatik tanıyıp ona uygun istatistik ve grafikleri (histogram, en sık değerler, zaman serisi için mevsimsellik/otokorelasyon) üretiyor.
- **Veri setlerini karşılaştırma ve kolay paylaşım:** İki sürümü (örn. temizlik öncesi/sonrası) tek komutla karşılaştırabiliyor; rapor HTML olarak ekip arkadaşlarına gönderilebiliyor, JSON olarak da test hattına bağlanabiliyor. Komut satırından da çalışıyor: `data_profiling data.csv report.html`.

## Kendi projemizde kullanabileceğimiz fikir

- BE `data/siparisler.csv` dosyasını yüklediğinde, `dq_test.py` testlerine ek olarak bu kütüphaneyle bir **profil raporu** (`reports/profil-siparisler.html`) üretip PR'a eklemek: testler şemaya uyumu "geçti/kaldı" olarak kontrol ederken, rapor dağılımları ve kategori dengesini görsel olarak gösterir; FE de grafik fikirlerini buradan alabilir.
