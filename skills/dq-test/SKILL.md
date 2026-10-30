---
name: dq-test
description: Grup A'nın veri kalitesi test senaryolarını (tests/test-cases.md) veri sözlüğüne göre yazar, testleri koşar ve sonuçları tarihli olarak tests/test-log.md'ye işler; BE/FE PR'larını DQ olarak inceler. Test senaryosu yazılacağı, testler çalıştırılacağı veya PR incelemesi yapılacağı zaman kullan.
---

# dq-test — Veri kalitesi testleri ve PR incelemesi (DQ)

**Amaç:** BE'nin ürettiği verinin ve FE'nin çıktılarının veri sözlüğüne uyduğunu **ölçülebilir** senaryolarla göstermek; uymayan her şeyi kayda (bug Issue'su, PR yorumu) geçirmek. Uydurma sonuç yazmaz: her sonuç bir komut çıktısına ve test edilen commit'e dayanır.

**Rol:** DQ (test) · **Sahibi:** Görev 1'de Tuğba Tuana Kaygısız, Görev 2'de Sema Nur Doğan (roller döner, skill rolle el değiştirir) · **Issue:** G2-test (#64)

## Görev 2 bağlamı

| | Görev 2 |
|---|---|
| Şema (tek doğru kaynak) | `docs/veri-sozlugu.md` (#60) — 14 alan, 8 parametre, satır sayısı formülü, 12 kalite kuralı |
| Test edilen veri | `data/siparisler-g2.csv` (BE, `src/simulasyon.py`, #61) |
| Senaryolar | `tests/test-cases.md` (Görev 1 senaryoları `tests/test-cases-g1.md`'de arşivde) |
| Sonuçlar | `tests/test-log.md` → "Görev 2" tablosu (tarihli satırlar) |

## Kurallar (hocanın #47 notu)

- Senaryolar **Hafta 5'te** `tests/test-cases.md`'ye yazılır; "Gerçekleşen" ve "Geçti/Kaldı" sütunları orada **boş kalır**.
- Testler **Hafta 6'da** koşuldukça sonuçlar `tests/test-log.md`'ye **tarihli satır** olarak eklenir: tarih, dosya, veri commit'i, komut, **kullanılan parametreler**, geçen/kalan, not. Eski satırlar düzenlenmez; düzeltme yeni satırdır.
- `main`'e doğrudan commit yok: senaryolar ve skill `feature/test-g2` gibi bir dalda PR ile girer (belge PR'ı — yazarı merge eder).

## Adımlar

### A) Senaryoları yaz (Hafta 5)

1. **Sözlüğü oku:** alan listesi ve sırası, tipler, aralıklar, değer listeleri ve ağırlıkları, parametreler ve izinli aralıkları, satır sayısı tablosu, 12 kalite kuralı.
2. **Zorunlu senaryo grupları** (ders planı Görev 2): satır sayısı · sütun adları · aralıklar · tip kontrolü · **parametre davranışı** (ör. `gun_sayisi=10` → satır sayısı formüle göre değişiyor mu?).
3. **Kapsama kuralı:** sözlükteki **her** kalite kuralı ve parametre satır sayısı tablosundaki **her** senaryo en az bir test senaryosuyla kapsanır. Dosyanın sonuna "Kapsama" tablosu konur (kural → senaryo ID).
4. **Beklenen sonucu sayıyla yaz:** "doğru olmalı" değil; "aralık dışı satır = 0", "satır sayısı = 424" gibi. Beklenen sayılar sözlükteki formülden hesaplanır, veriden kopyalanmaz.
5. **Hata yönetimi senaryoları:** sözlükteki "Geçersiz parametre" kuralı için geçersiz girdiler (aralık dışı, bozuk biçim) yazılır; beklenen: `ValueError` + mesajda parametre adı ve izinli aralık + dosya **yazılmaz**. Bunlar Hafta 6 `fix/error-handling` PR'ından sonra koşulur.
6. Sonuç sütunlarını boş bırak → kontrol listesi → PR → merge → #64'e kanıt yorumu.

### B) PR incelemesi (Hafta 5–6)

1. **Files changed** üzerinden en az 2 **somut** satır yorumu (soru da geçerlidir: "`--gun_sayisi 0` verilirse ne olur?").
2. Verinin sözlüğe uygunluğunu betikten **bağımsız** kontrol et (kendi kontrolün; BE'nin betiğinin kendi kendini doğrulamasına güvenme).
3. Cevap gelmeden **Approve** verme; merge'ü PR sahibi yapar. İncelemenin özeti ilgili Issue'ya kanıt olarak yazılır.

### C) Testleri koş (Hafta 6)

1. BE'nin "Veri hazır" yorumunu ve merge commit'ini doğrula.
2. Tüm senaryoları merge edilmiş ürün üzerinde koş (parametre senaryoları için betik farklı parametrelerle **geçici bir dosyaya** çalıştırılır; geçici dosyalar commit'lenmez).
3. Her koşu `tests/test-log.md` Görev 2 tablosuna tarihli satır olarak; kalan her test için **bug Issue'su** (en az 2): yeniden üretme adımları (komut + parametre + commit), beklenen, gözlenen, ilgili senaryo ID'si; atanan: veri → BE, grafik → FE.
4. Düzeltme merge edilince yeniden test → yeni satır + bug Issue'suna "yeniden test edildi" kanıt yorumu.

## Çıktı formatı kuralları

- `tests/test-cases.md` başlıkları bu sırada: `Kapsam` → `Senaryolar` (gruplar: A Dosya ve şema · B Değerler ve kurallar · C Parametre davranışı · D Hata yönetimi) → `Kapsama`.
- Senaryo tablosu sütunları (ders şablonu §7.3): `ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı`. ID biçimi `G2-TC-NN`. **Kaynak**: sözlük kural no'su veya parametre tablosu.
- `tests/test-log.md` Görev 2 satırı: `Tarih | Test edilen dosya | Veri commit'i | Komut | Geçti | Kaldı | Not (parametreler + Issue)`.

## Örnek giriş → çıkış

**Giriş (ajana):** "dq-test skill'ini kullanarak docs/veri-sozlugu.md'ye göre Görev 2 için tests/test-cases.md yaz; parametre davranışı senaryolarını satır sayısı tablosundan türet."

**Çıkış (bir satır):**

| ID | Kaynak | Senaryo | Adımlar | Girdi | Beklenen | Gerçekleşen | Geçti/Kaldı |
|---|---|---|---|---|---|---|---|
| G2-TC-17 | Satır sayısı tablosu | `gun_sayisi=10` satır sayısını değiştiriyor mu? | 1) `python src/simulasyon.py --gun_sayisi 10 --cikti <geçici>` 2) satır say | `--gun_sayisi 10`, diğerleri varsayılan | 424 satır; son tarih 2026-01-14; farklı tarih = 10 | | |

**Hafta 6 test-log satırı:** `| 2026-11-xx | data/siparisler-g2.csv | <commit> | … | 22 | 0 | gun_sayisi=182 … tohum=42 |`

## Ne zaman üretmez (reddeder)

- Test edilecek dosyada **gerçek kişisel veri** (ad-soyad, TC no, telefon, e-posta, adres, kart no) varsa ya da gerçek veri ile test istenirse — durur, PM'e bildirir (ders kuralı §3.1).
- Şema (`docs/veri-sozlugu.md`) yoksa — senaryo yazmaz, G2-sem Issue'sunda şema ister.
- Komut çalıştırılmadan "Gerçekleşen" / "Geçti" doldurulması istenirse — doldurmaz.
- Beklenen sonucu veriden kopyalayarak yazma isteği — reddeder; beklenen her zaman sözlükten türetilir.

## Kontrol listesi (PR'dan önce)

- [ ] En az 5 senaryo; satır sayısı, sütun adları, aralıklar, tip ve parametre davranışı gruplarının her biri var.
- [ ] Her senaryoda ID, kaynak, adımlar, girdi, sayısal beklenen var; sonuç sütunları boş.
- [ ] Kapsama tablosunda sözlüğün 12 kuralı ve satır sayısı tablosunun 4 senaryosu karşılanmış.
- [ ] Beklenen satır sayıları formülden hesaplanmış (varsayılan 8.208).

## Kullanılan dosyalar

- **Okur:** `docs/veri-sozlugu.md`, `data/siparisler-g2.csv`, `src/simulasyon.py` (yalnızca çalıştırır / inceler)
- **Yazar:** `tests/test-cases.md`, `tests/test-log.md`, bug Issue'ları, PR inceleme yorumları
- **Çalıştırır (Hafta 6):** `python src/simulasyon.py [--parametre değer] --cikti <geçici>` ve test kontrolleri (Python 3 + pandas; `pip install pandas`)

## Nasıl çalıştırılır

Ajana (Claude):

- Senaryo yazımı: "dq-test skill'ini kullanarak docs/veri-sozlugu.md'ye göre Görev 2 için tests/test-cases.md yaz."
- PR incelemesi: "dq-test skill'ini kullanarak PR #<no>'yu DQ olarak incele; veriyi sözlüğe karşı bağımsız kontrol et, en az 2 somut satır yorumu öner."
- Test koşusu: "dq-test skill'ini kullanarak tests/test-cases.md'deki senaryoları koş ve sonuçları tests/test-log.md Görev 2 tablosuna yaz."

## Üretim kaydı (hangi araç, hangi prompt)

**Görev 2 (Sema Nur Doğan, DQ):**
- **Araç:** Claude. Skill Görev 2'ye bu sürümle uyarlandı (şema → `docs/veri-sozlugu.md`, parametre ve hata yönetimi senaryoları, #47 kuralı, PR inceleme adımları); ardından `tests/test-cases.md` bu skill ile yazıldı (#64).
- **PR #66 incelemesi:** veri sözlüğe karşı bağımsız kontrol edildi (kural 1–11 geçti, 8.208 satır, MD5 `1b7f765e…`); satır 148, 301, 323'e yorum; cevaplardan sonra Approve.

**Görev 1 (Tuğba Tuana Kaygısız, DQ) — arşiv:**
- Senaryolar `tests/test-cases-g1.md` (TC-01…TC-12), betik `src/dq_test.py`; testler, hata Issue'ları (#27, #28, #29) ve #27 sonrası yeniden test (9/9, `1868546`) Claude (Claude Code) ile yapıldı.
- Ajan izi olmayan commit'ler (`943b75d`, `95c3e0a`, `29c306e`, `8fee1dd`, `7459286`, `778e7dd`) de Claude ile üretildi; dosyalar web'den yüklendiği için `Co-Authored-By` satırı yok.
