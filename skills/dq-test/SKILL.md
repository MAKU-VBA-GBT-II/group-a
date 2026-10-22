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
3. **Ek senaryolar ekle** (önerilen): TC-06 eksik değer, TC-07 kimlik benzersizliği, TC-08 türetilmiş alan tutarlılığı (`toplam_tutar = adet × birim_fiyat`), TC-09 para alanlarının dosyada sözlükteki biçimde (2 ondalık) yazılması — bu kontrol dosyayı ham metin olarak okur (`dtype=str`), çünkü pandas sayıya çevirince sondaki sıfır görünmez.
4. **Beklenen sonuçları ölçülebilir yaz:** "doğru olmalı" değil, "aralık dışı değer sayısı = 0" gibi somut bir eşik ver.
5. **"Gerçekleşen sonuç" ve "Geçti/Kaldı" sütunlarını boş bırak.**
6. **`src/dq_test.py` içindeki şema sabitlerini** (`SUTUNLAR`, `KATEGORILER`, aralıklar, `SEMA_SATIR`) şemayla eşitle.
7. **Commit at:** `G1-test: test-cases.md, dq-test skill'i ve test betiği eklendi (#16)`
8. **Issue'ya kanıt yorumu yaz** (commit hash + dosya + senaryo sayısı) ve Issue'yu kapat.

### B) Testleri çalıştır (Hafta 4)

1. BE'nin "Veri hazır" yorumunu ve commit'ini doğrula.
2. Depo kökünde `python src/dq_test.py` komutunu çalıştır.
3. Çıktıdaki her satırı `tests/test-cases.md`'deki ilgili senaryonun "Gerçekleşen sonuç" ve "Geçti/Kaldı" hücrelerine aktar; Özet tablosunu doldur.
4. `tests/test-log.md`'ye kayıt ekle: tarih, test edilen commit, geçen/kalan sayısı.
5. **Kalan test varsa ayrı bir hata Issue'su aç:** başlıkta Issue adı ve kısa sorun (örn. `G1-veri: birim_fiyat / toplam_tutar CSV'de 2 ondalıkla yazılmıyor`), etiket `bug`, atanan: ilgili dosyanın sahibi (BE/FE). İçerikte kalan senaryo, örnek satır, beklenen ve gerçekleşen sonuç, önerilen düzeltme olsun. Senaryonun "Gerçekleşen sonuç" hücresine Issue numarasını yaz (örn. #27).
6. **Hata düzeltilince yeniden test et:** Düzeltme commit'i `main`'e girince `python src/dq_test.py`'yi tekrar çalıştır; senaryonun sonucunu güncelle (ilk turda kaldığını ve düzeltme commit'ini not et), Özet tablosuna ve `tests/test-log.md`'ye yeni satır ekle. Hata Issue'suna "Yeniden test edildi — geçti, commit <hash>" kanıt yorumu yaz.

## Şablon

```markdown
| ID | Senaryo | Adımlar | Girdi | Beklenen sonuç | Gerçekleşen sonuç | Geçti/Kaldı |
|---|---|---|---|---|---|---|
| TC-01 | Veri dosyası var mı, boş değil mi? | 1) … 2) … | data/siparisler.csv | Dosya mevcut, boyut > 0 | | |
```

## Kullanılan dosyalar

- **Okur:** `docs/veri-sozlugu-g1.md`, `data/siparisler.csv`
- **Yazar:** `tests/test-cases.md`, `tests/test-log.md`
- **Çalıştırır:** `src/dq_test.py` (Python 3 + pandas)

## Nasıl çalıştırılır

Ajana (bu depoda Claude Code kullanıldı):

- Senaryo yazımı: "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz."
- Test çalıştırma: "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle."

Elle çalıştırma: depo kökünde `python src/dq_test.py` (farklı dosya için `python src/dq_test.py yol/dosya.csv`). Tüm testler geçerse çıkış kodu 0, en az biri kalırsa 1 olur.

## Üretim kaydı (hangi araç, hangi prompt)

- **Araç:** Claude (Claude Code, yapay zekâ ajanı).
- **Senaryo yazımı (#16) ve şema güncellemesi (#13):** `tests/test-cases.md`, `src/dq_test.py` ve bu skill Claude ile yazıldı ve güncellendi (örn. commit `9c9b658`, `146d5d3`; commit'lerde `Co-Authored-By: Claude` izi var).
- **Prompt'lar:** "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz." · "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle."
- **Hafta 4 test turu ve yeniden test:** TC-09 eklendi, testler çalıştırıldı, hata Issue'ları açıldı (#27, #28, #29) ve #27 düzeltmesi sonrası yeniden test (9/9) Claude ile yapıldı.
- **Kural (Görev 2'den itibaren):** Commit'i ajan atar veya mesajın sonuna `Co-Authored-By:` satırı eklenir; kapanan Issue'ya "Üretim: dq-test skill'i ile, Claude" satırı yazılır.
