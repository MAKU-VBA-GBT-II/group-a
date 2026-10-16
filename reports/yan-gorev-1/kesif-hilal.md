# Git Keşfi — Hilal Elçin Şahin

**Repo:** [anthropics/prompt-eng-interactive-tutorial — Anthropic's Interactive Prompt Engineering Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

## Çözdüğü problem

Yapay zekâ modellerinden istenen sonucu almak büyük ölçüde talimatın (prompt) nasıl yazıldığına bağlı; belirsiz bir prompt tutarsız, hatalı ya da uydurma cevaplar üretir. Bu repo, prompt yazmayı deneme-yanılmaya bırakmak yerine adım adım öğreten, ücretsiz ve açık kaynak etkileşimli bir eğitim sunuyor: temel prompt yapısından rol verme, veriyi talimattan ayırma, örnekle yönlendirme ve halüsinasyonu azaltmaya kadar.

## Güçlü yanları

- **Uygulamalı ve kademeli yapı:** Başlangıç, orta ve ileri seviyeye ayrılmış 9 bölüm var; her bölümde ders, alıştırmalar ve cevap anahtarı bulunuyor, sırayla ilerlenecek şekilde tasarlanmış.
- **Deneyerek öğrenme:** Her dersin sonundaki "Example Playground" alanında prompt değiştirilip modelin cevabının nasıl değiştiği doğrudan görülebiliyor; bu, kuralları ezberlemek yerine neden işe yaradığını anlamayı sağlıyor.
- **Gerçek kullanım senaryoları:** İleri bölümlerde sıfırdan karmaşık prompt kurma (chatbot, hukuk, finans, kodlama örnekleri), ekte ise prompt zincirleme ve araç kullanımı (tool use) gibi ileri yöntemler var.

## Kendi projemde kullanabileceğim fikir

- Görev 1'de G1-veri adımı için yazacağım `skills/be-veri/SKILL.md` dosyasını bu eğitimin teknikleriyle yazmak: net rol tanımı, veriyi (şema, aralıklar, kategori değerleri) talimattan XML etiketleriyle ayırmak, adım adım talimat ve örnek çıktı vermek. Böylece ajan aynı tohumla her seferinde DQ ile kararlaştırılan kurallara uyan `data/siparisler.csv` dosyasını tutarlı biçimde üretir.
