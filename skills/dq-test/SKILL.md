---
name: dq-test
description: Grup A'nın veri kalitesi test senaryolarını (tests/test-cases.md) şemaya göre yazar ve src/dq_test.py ile çalıştırıp sonuçları kaydeder. Veri dosyası için test senaryosu yazılacağı veya testler çalıştırılacağı zaman kullan.
---

# dq-test — Veri kalitesi testleri

**Ne yapar:** BE'nin ürettiği veri dosyası (`data/siparisler.csv`) için, şemaya (`docs/veri-sozlugu-g1.md`) dayanan test senaryolarını `tests/test-cases.md` dosyasına yazar. Testleri çalıştırma aşamasında `src/dq_test.py` betiğini kullanır, "Gerçekleşen sonuç" ve "Geçti/Kaldı" sütunlarını doldurur ve çalıştırma kaydını `tests/test-log.md`'ye ekler. Uydurma sonuç yazmaz; her sonuç betik çıktısına ve test edilen commit'e dayanır.

## Girdiler

- Şema: `docs/veri-sozlugu-g1.md` (alan adları, sıra, tipler, aralıklar, kategori değerleri, birimler, satır hedefi). Henüz yoksa BE ile kesinleştirilen taslak şema (#13).
- Veri: `data/siparisler.csv` (yalnızca çalıştırma aşamasında gerekir)
- İlgili Issue: G1-test (#16)

## Adımlar

### A) Senaryoları yaz (Hafta 3)

1. **Şemayı oku:** Alan listesini, sırasını, her alanın tipini, geçerli aralığını, birimini, ana kategorik alanın izinli değerlerini ve satır hedefini çıkar.
2. **Zorunlu 5 senaryoyu yaz** (her birinde ID, Senaryo, Adımlar, Girdi, Beklenen sonuç):
   - TC-01 — Dosya var mı, boş değil mi?
   - TC-02 — Satır sayısı şemadaki hedefi karşılıyor mu?
   - TC-03 — Sütun adları ve sırası şemayla aynı mı?
   - TC-04 — Tipler, aralıklar ve birimler doğru mu?
   - TC-05 — Ana kategorik alanda yalnızca şemadaki değerler mi var?
3. **Ek senaryolar ekle** (önerilen): TC-06 eksik değer, TC-07 kimlik benzersizliği, TC-08 türetilmiş alan tutarlılığı (`toplam_tutar = adet × birim_fiyat`), TC-09 para alanlarının dosyada sözlükteki biçimde (2 ondalık) yazılması — bu kontrol dosyayı ham metin olarak okur (`dtype=str`), çünkü pandas sayıya çevirince sondaki sıfır görünmez; TC-10 diğer kategorik alanlar (`sehir`, `odeme_tipi`) yalnızca izinli değerleri içeriyor; TC-11 her `urun` sözlükteki listede ve kendi `kategori`sine ait; TC-12 `siparis_id` 1…N ardışık ve dosya tarihe göre sıralı.
   - **Kural:** Veri sözlüğündeki **her** "geçerli değer / aralık / güvence" satırı en az bir senaryoyla kapsanmalı. Senaryoları yazdıktan sonra sözlüğü satır satır gez ve kapsanmayan kural kalmadığını kontrol et.
4. **Beklenen sonuçları ölçülebilir yaz:** "doğru olmalı" değil, "aralık dışı değer sayısı = 0" gibi somut bir eşik ver.
5. **"Gerçekleşen sonuç" ve "Geçti/Kaldı" sütunlarını boş bırak.**
6. **`src/dq_test.py` içindeki şema sabitlerini** (`SUTUNLAR`, `SEMA_SATIR`, `KATEGORILER`, `URUNLER`, `SEHIRLER`, `ODEME_TIPLERI`, `ADET_ARALIK`, `FIYAT_ARALIK`, `TUTAR_ARALIK`, `TARIH_ARALIK`) şemayla eşitle. Yeni senaryo eklediysen betiğe aynı ID ile `tcNN` fonksiyonu ekle.
   - **Betiği sına:** Temiz dosyada tüm testler geçmeli; sonra bir kopyada her kurala aykırı bir değer yaz (ör. `sehir=Paris`, Kozmetik satırında `urun=Roman`) ve ilgili testin **kaldığını** gör. Kopyayı commit'leme.
7. **Commit at:** `G1-test: test-cases.md, dq-test skill'i ve test betiği eklendi (#16)`
8. **Issue'ya kanıt yorumu yaz** (commit hash + dosya + senaryo sayısı) ve Issue'yu kapat.

### B) Testleri çalıştır (Hafta 4)

1. BE'nin "Veri hazır" yorumunu ve commit'ini doğrula.
2. Depo kökünde `python src/dq_test.py` komutunu çalıştır.
3. Çıktıdaki her satırı `tests/test-cases.md`'deki ilgili senaryonun "Gerçekleşen sonuç" ve "Geçti/Kaldı" hücrelerine aktar; Özet tablosunu doldur.
4. `tests/test-log.md`'ye kayıt ekle (biçim aşağıda): tarih, test edilen dosya, veri commit'i, komut, geçen/kalan sayısı, not.
5. **Grafik–analiz çapraz kontrolü:** `visuals/` altındaki her grafikteki sayıları (pay %, ortalama çizgisi, en yüksek/en düşük hafta, tarih etiketleri) `docs/analiz-g1.md` ile karşılaştır. Uyuşmazlık bir grafik hatasıdır (örn. #28 ortalama, #29 tarih biçimi).
6. **Hata Issue'ları aç (Hafta 4'te en az 2):** Her hata için ayrı Issue:
   - Başlık: `<Issue adı>: <kısa sorun>` (örn. `G1-veri: birim_fiyat / toplam_tutar CSV'de 2 ondalıkla yazılmıyor`).
   - Etiket `bug`. Atanan: veri hatası → BE, grafik hatası → FE.
   - Gövde: **Yeniden üretme adımları** (komut + dosya + commit), **Beklenen davranış**, **Gözlenen davranış** (örnek satır/değer), önerilen düzeltme, ilgili senaryo ID'si.
   - Senaryonun "Gerçekleşen sonuç" hücresine Issue numarasını yaz (örn. #27).
   - **Hata bulunamazsa** aynı yapıda (yeniden üretme / beklenen / gözlenen) 2 somut iyileştirme Issue'su aç, etiket `enhancement`.
7. **Hata düzeltilince yeniden test et:** Düzeltme commit'i `main`'e girince `python src/dq_test.py`'yi tekrar çalıştır; senaryonun sonucunu güncelle (ilk turda kaldığını ve düzeltme commit'ini not et), Özet tablosuna ve `tests/test-log.md`'ye yeni satır ekle. Hata Issue'suna "Yeniden test edildi — geçti, commit <hash>" kanıt yorumu yaz.

## Şablonlar

`tests/test-cases.md` senaryo satırı:

```markdown
| ID | Senaryo | Adımlar | Girdi | Beklenen sonuç | Gerçekleşen sonuç | Geçti/Kaldı |
|---|---|---|---|---|---|---|
| TC-01 | Veri dosyası var mı, boş değil mi? | 1) … 2) … | data/siparisler.csv | Dosya mevcut, boyut > 0 | | |
```

`tests/test-log.md` kayıt satırı:

```markdown
| Tarih | Test edilen dosya | Veri commit'i | Komut | Geçti | Kaldı | Not |
|---|---|---|---|---|---|---|
| 2026-10-22 | `data/siparisler.csv` | `1f8beb8` | `python src/dq_test.py` | 12 | 0 | Ne değişti, hangi Issue |
```

## Örnek giriş → çıkış

**Giriş:** "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle." (veri commit `1f8beb8`)

**Betik çıktısı (kısaltılmış):**

```text
| TC-09 | 2 ondalıklı olmayan satır: 0 | Geçti |
| TC-10 | şema dışı değerli satır: 0; şehir: yok, ödeme: yok | Geçti |
Özet: 12/12 geçti
```

**Yazılanlar:** `tests/test-cases.md`'de her senaryonun "Gerçekleşen sonuç" ve "Geçti/Kaldı" hücreleri + Özet'e yeni satır; `tests/test-log.md`'ye yukarıdaki biçimde bir satır. Kalan test olsaydı (ör. ilk turda TC-09: 128 satır) aynı turda `bug` Issue'su açılırdı (#27).

## Ne zaman üretmez (reddeder)

- Test edilecek dosyada gerçek kişi/müşteri verisi varsa veya gerçek veri istenirse (AGENTS.md kural 2) — durur, PM'e bildirir.
- Şema (`docs/veri-sozlugu-g1.md`) yoksa ve BE ile kesinleşmiş taslak da yoksa — senaryo yazmaz, #13'te şema ister.
- Betiği çalıştırmadan "Gerçekleşen sonuç" doldurulması istenirse — doldurmaz; sonuç yalnızca `dq_test.py` çıktısından veya kaydı tutulan elle kontrolden gelir.

## Kullanılan dosyalar

- **Okur:** `docs/veri-sozlugu-g1.md`, `data/siparisler.csv`
- **Yazar:** `tests/test-cases.md`, `tests/test-log.md` (gerekirse `src/dq_test.py` şema sabitleri)
- **Çalıştırır:** `src/dq_test.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (bu depoda Claude Code kullanıldı):

- Senaryo yazımı: "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz."
- Test çalıştırma: "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle."

Elle çalıştırma: depo kökünde `python src/dq_test.py` (farklı dosya için `python src/dq_test.py yol/dosya.csv`). Tüm testler geçerse çıkış kodu 0, en az biri kalırsa 1 olur. Gereken: Python 3 + pandas (`pip install pandas`).

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **Senaryo yazımı (#16) ve şema güncellemesi (#13):** `tests/test-cases.md`, `src/dq_test.py` ve bu skill Claude ile yazıldı ve güncellendi (örn. commit `9c9b658`, `146d5d3`; commit'lerde `Co-Authored-By: Claude` izi var).
- **Prompt'lar:** "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz." · "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle."
- **Çapraz skill incelemesi öncesi (Yan Görev 3):** TC-10…TC-12 eklendi (sözlükteki şehir/ödeme, ürün–kategori ve id/sıra kuralları önceden test edilmiyordu); skill'e grafik–analiz kontrolü, Hafta 4 hata Issue'su kuralları, örnek ve reddetme koşulları eklendi — Claude ile.
- **Hafta 4 test turu ve yeniden test:** TC-09 eklendi, testler çalıştırıldı, hata Issue'ları açıldı (#27, #28, #29) ve #27 düzeltmesi sonrası yeniden test (9/9) Claude ile yapıldı.
- **Ajan izi olmayan commit'ler:** `943b75d`, `95c3e0a`, `29c306e`, `c06e97a`, `8fee1dd`, `7459286`, `778e7dd` da Claude ile üretildi; dosyalar Tuana'nın hesabından yüklendiği için bu commit'lerde `Co-Authored-By` satırı yok.
- **Kural (Görev 2'den itibaren):** Commit'i ajan atar veya mesajın sonuna `Co-Authored-By:` satırı eklenir; kapanan Issue'ya "Üretim: dq-test skill'i ile, Claude" satırı yazılır.
