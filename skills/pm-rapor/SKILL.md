---
name: pm-rapor
description: Grup A'nın haftalık sprint raporunu (reports/report-wXX.md) GitHub izlerinden (Issue, commit, PR, pano) derler. Haftalık rapor yazılacağı zaman kullan.
---

# pm-rapor — Haftalık sprint raporu

**Ne yapar:** Belirtilen haftanın sprint raporunu, depodaki gerçek izlere (Issue'lar, kanıt yorumları, commit'ler, PR'lar, proje panosu) dayanarak `reports/report-wXX.md` dosyasına yazar. Uydurma bilgi yazmaz; her iddia bir Issue numarasına veya commit hash'ine bağlanır.

## Girdiler

- Hafta numarası (örn. `03`) ve haftanın tarih aralığı
- Haftanın ders duyurusu: `MAKU-VBA-GBT-II/ders` deposundaki `Duyuru-*.md` dosyaları. Teslim tarihi ve kapsam için **"Son tarih" satırı içeren en yeni duyuru** esas alınır (en yeni duyuru her zaman son tarih içermez).
- Depo: `MAKU-VBA-GBT-II/group-a`
- O haftanın Issue'ları (örn. Görev 1 için G1-veri, G1-analiz, G1-gorsel, G1-test)
- Proje panosu: *Sepetix Analitik — Grup A Panosu* (Todo → In Progress → Review → Done)

## Adımlar

1. **Kapsamı ve son tarihi belirle:** İlgili `Duyuru-*.md` dosyasından haftanın teslim tarihini ve hedeflerini oku; planlanan Issue'ları buna göre filtrele. Son tarih bulunamazsa tahmin etme, raporu yazmadan önce PM'e sor.
2. **Planlananları topla:** O hafta açılan Issue'ları listele (numara, başlık, atanan kişi, son tarih, kabul kriteri).
3. **Yapılanları doğrula:** Her Issue için kapanış/kanıt yorumunu ve ilgili commit'i bul. Kabul kriteri dosyada gerçekten sağlanıyor mu kontrol et (dosya var mı, satır sayısı vb.). Kontrol edilecek dosya yollarını ilgili Issue'nun kabul kriterinden al (örn. Görev 1'de `data/siparisler.csv`, `docs/analiz-g1.md`, `visuals/*.png`); yol tahmin etme. Yollar görevden göreve değiştiği için skill'e sabit yazılmaz.
4. **Devir teslim zincirini kontrol et:** BE → DQ ("Veri hazır" yorumu G1-analiz ve G1-gorsel'de var mı?) ve DQ → FE ("Analiz hazır" yorumu G1-gorsel'de var mı?).
5. **Tıkananları yaz:** Açık kalan Issue'lar, kaçırılan son tarihler, cevapsız @mention'lar ve nedenleri.
6. **Kim ne yaptı:** Her üye için commit sayısı ve kapattığı Issue'lar.
7. Raporu aşağıdaki şablonla `reports/report-wXX.md` olarak yaz; commit mesajı: `Hafta XX sprint raporu eklendi`.

## Şablon

```markdown
# Sprint Raporu — Hafta XX (GG.AA–GG.AA.YYYY)

**Şirket:** Sepetix Analitik (Grup A) · **PM:** Ali Haydar Polat

## Planlanan
| Issue | Başlık | Atanan | Son tarih |
|---|---|---|---|

## Yapılan
| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|

## Devir teslim zinciri
- BE → DQ/FE: …
- DQ → FE: …

## Tıkanan / riskler
- …

## Kim ne yaptı
| Üye | Rol | Commit | Kapattığı Issue |
|---|---|---|---|

## Gelecek hafta
- …
```

## Kullanılan dosyalar

- Okur: `ders/Duyuru-*.md` (son tarih ve kapsam), GitHub Issue'ları ve yorumları (kabul kriterleri dahil), `git log`, proje panosu
- Yazar: `reports/report-wXX.md`

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.): **"pm-rapor skill'ini kullanarak Hafta 03 için report-w03.md yaz."** Ajan GitHub'a erişemiyorsa Issue listesi ve `git log --since=... --pretty='%h %an %s'` çıktısı ona verilir.
