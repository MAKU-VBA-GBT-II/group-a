# Git Keşfi — Sema Doğan

**Repo:** [recommenders-team/recommenders — Recommenders](https://github.com/recommenders-team/recommenders) (eski adıyla **microsoft/recommenders**)

## Çözdüğü problem

E-ticaret sitelerindeki "Bunu alanlar şunları da aldı" ya da "Size özel öneriler" gibi bölümlerin arkasında öneri sistemleri çalışır. Bu sistemleri kurmak için hangi algoritmanın seçileceği, verinin nasıl hazırlanacağı ve modelin başarısının nasıl ölçüleceği gibi soruların cevabı dağınık kaynaklarda kalır. Recommenders bunları tek bir yerde topluyor: klasik ve derin öğrenme tabanlı öneri algoritmalarını hazır Jupyter notebook'larla birlikte sunuyor ve **veri hazırlama → model → değerlendirme → ayar → canlıya alma** akışını adım adım gösteriyor.

## Güçlü yanları

- **Uçtan uca, öğretici yapı:** `examples/` klasörü sırayla numaralandırılmış (`00_quick_start`, `01_prepare_data`, `02_model_…`, `03_evaluate`…). Böylece hiç bilmeyen biri bile hangi notebook'tan başlayacağını biliyor. Hızlı başlangıç notebook'ları birkaç dakikada çalışan bir model gösteriyor.
- **Hazır değerlendirme metrikleri:** `recommenders/evaluation` içinde RMSE ve MAE gibi hata ölçülerinin yanı sıra `precision_at_k`, `recall_at_k`, `ndcg_at_k` gibi sıralama metrikleri ve hatta **çeşitlilik (diversity), yenilik (novelty), sürpriz (serendipity)** ölçüleri var. Yani yalnızca "model doğru mu?" değil, "öneriler hep aynı ürünler mi?" sorusu da sayısal olarak cevaplanabiliyor.
- **Sektör senaryoları ve topluluk:** `scenarios/retail` dosyası perakende/e-ticaret için hangi durumda hangi yaklaşımın kullanılacağını anlatıyor (kişiselleştirilmiş öneri, "bunu da beğenebilirsiniz" vb.). Proje 2018'de Microsoft'ta başladı, bugün Linux Foundation AI & Data çatısı altında. 150'yi aşkın katkıcısı, 9.000'den fazla commit'i var ve 20.000'i aşkın yıldız almış. MIT lisanslı.

## Kendi projemizde kullanabileceğimiz fikir

- Görev 1'deki `data/siparisler.csv` verimizde sipariş, kategori ve ürün var ama **müşteri kimliği yok**. Veri sözlüğüne bir `musteri_id` alanı eklersek "hangi müşteri hangi ürünleri aldı" tablosu oluşur. Bu tabloyla repodaki basit benzerlik yaklaşımını (örneğin SAR) örnek alarak **"birlikte en çok alınan ürünler"** analizi yapılabilir: DQ bunu bir top-3 metriği olarak raporlar, FE de bir grafikle gösterir. Repodaki `precision_at_k` mantığı da önerilerin ne kadar isabetli olduğunu test etmek için iyi bir örnek.
