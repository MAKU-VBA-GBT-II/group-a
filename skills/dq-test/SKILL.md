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
3. **Ek senaryolar ekle** (önerilen): TC-06 eksik değer, TC-07 kimlik benzersizliği, TC-08 türetilmiş alan tutarlılığı (`toplam_tutar = adet × birim_fiyat`).
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
5. Kalan bir test varsa BE'nin Issue'suna hangi senaryonun neden kaldığını yaz (@BE etiketiyle).

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

Ajana (Claude Code, Codex vb.):

- Senaryo yazımı: "dq-test skill'ini kullanarak docs/veri-sozlugu-g1.md şemasına göre tests/test-cases.md yaz."
- Test çalıştırma: "dq-test skill'ini kullanarak testleri çalıştır ve sonuçları test-cases.md ile test-log.md'ye işle."

Elle çalıştırma: depo kökünde `python src/dq_test.py` (farklı dosya için `python src/dq_test.py yol/dosya.csv`). Tüm testler geçerse çıkış kodu 0, en az biri kalırsa 1 olur.
