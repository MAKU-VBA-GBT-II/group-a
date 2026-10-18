---
name: fe-gorsel
description: Grup A'nın sipariş verisinden (data/siparisler.csv) src/fe_gorsel.py ile 2 PNG grafik (zaman serisi + kırılım) üretip visuals/ klasörüne kaydeder; önce grafik taslaklarını hazırlar. Grafik, görselleştirme veya grafik taslağı istendiğinde kullan.
---

# fe-gorsel — Grafik taslağı ve PNG grafikler

**Ne yapar:** BE'nin ürettiği veriden (`data/siparisler.csv`) ve DQ'nun metrik tanımlarından (`docs/analiz-g1.md`) yola çıkarak `src/fe_gorsel.py` ile iki grafik üretir:

| Dosya | Tür | Metrik | Ne gösterir |
|---|---|---|---|
| `visuals/haftalik-ciro.png` | Zaman serisi (çizgi) | M4 — Haftalık ciro trendi | Pazartesi başlangıçlı haftalara göre Σ `toplam_tutar` (bin TL); tam haftaların ortalaması, en yüksek hafta ve kısmi ilk/son hafta işaretli |
| `visuals/kategori-ciro-payi.png` | Kırılım (yatay çubuk) | M3 — Kategori bazlı ciro | Kategoriye göre Σ `toplam_tutar` (bin TL) ve toplam ciro içindeki payı (%); ilk iki kategori vurgulu |

Her grafikte **başlık, eksen etiketleri ve birim** (bin TL) vardır; altta veri kaynağı ve metrik kodu yazar. Grafikteki her sayı veriden hesaplanır, elle yazılmaz; sayılar `docs/analiz-g1.md` ile birebir tutmalıdır.

## Girdiler

- Veri: `data/siparisler.csv` (BE'nin "Veri hazır" yorumundaki commit)
- Şema: `docs/veri-sozlugu-g1.md`
- Metrik tanımları ve sonuçları: `docs/analiz-g1.md` (DQ'nun "Analiz hazır" yorumu)
- İlgili Issue'lar: G1-gorsel (#15), G1-veri (#13), G1-analiz (#14)

## Adımlar

1. **Önce taslak (zorunlu):** `python src/fe_gorsel.py --taslak` çalıştır. `visuals/taslak/` altına iki taslak PNG düşer (eksenler, başlık, gösterilecek metrik; gerçek veri yok). Bunları #15'e ekran görüntüsü olarak ekle. **Taslak Issue'ya eklenmeden gerçek grafiğe geçme** — kural ihlalidir.
2. **Devir teslimleri kontrol et:** BE'nin "Veri hazır" (#13) ve DQ'nun "Analiz hazır" (#15/#14) yorumları var mı? Yoksa dur ve sor.
3. **Güncel veriyi çek:** `git pull`.
4. **Grafikleri üret:** depo kökünde `python src/fe_gorsel.py`. Çıktı: `visuals/haftalik-ciro.png`, `visuals/kategori-ciro-payi.png`.
5. **Kendi kontrolünü yap:**
   - İki PNG'yi aç: başlık, x ve y eksen etiketleri, birim (bin TL) görünüyor mu? Türkçe karakterler (ş, ğ, İ) bozuk mu?
   - Kırılım grafiğindeki paylar `docs/analiz-g1.md` M3 tablosuyla aynı mı (ör. Elektronik %38,1)?
   - Zaman serisindeki en yüksek hafta M4 ile aynı mı? Kısmi ilk/son hafta işaretli mi?
   - Betiği ikinci kez çalıştır; PNG'ler değişmemeli (`md5sum visuals/*.png`).
6. **Commit at:** `G1-gorsel: haftalik-ciro.png, kategori-ciro-payi.png ve fe-gorsel skill'i eklendi (#15)` — Hafta 5'ten itibaren PR ile.
7. **Kanıt yorumu yaz (#15):** commit hash + iki dosya adı + hangi metrikleri gösterdikleri. Ardından Issue'yu kapat / panoda Done'a taşı.

## Tasarım kuralları

- Renkler betiğin başındaki sabitlerde (`RENK_ANA`, `RENK_VURGU`, `RENK_GRI`); grafik içinde sihirli değer kullanma.
- Para ekseni **bin TL**, Türkçe binlik ayırıcı (`1.185`), yüzdeler `%38,1` biçiminde.
- Hafta tanımı `dq_analiz.py` ile aynı: `resample("W-MON", label="left", closed="left")`. DQ tanımı değiştirirse betik de güncellenir.
- Dosya adları sabit (`ZAMAN_SERISI`, `KIRILIM`); değişirse README ve rapordaki bağlantılar da güncellenir.

## Kullanılan dosyalar

- **Okur:** `data/siparisler.csv`, `docs/analiz-g1.md` (kontrol için)
- **Yazar:** `visuals/haftalik-ciro.png`, `visuals/kategori-ciro-payi.png`, `visuals/taslak/*.png`
- **Çalıştırır:** `src/fe_gorsel.py` (Python 3 + pandas + matplotlib)

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.):

- Taslak: "fe-gorsel skill'ini kullanarak grafik taslaklarını üret."
- Grafik: "fe-gorsel skill'ini kullanarak data/siparisler.csv'den visuals/ altındaki iki grafiği üret ve kontrol et."
- Değişiklik: "fe-gorsel skill'ini kullanarak kırılım grafiğini şehir bazlı ciroya çevir."

Elle çalıştırma (depo kökünde):

```bash
python src/fe_gorsel.py --taslak   # taslaklar → visuals/taslak/
python src/fe_gorsel.py            # grafikler → visuals/
```
