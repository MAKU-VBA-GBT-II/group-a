---
name: pm-rapor
description: Grup A'nın haftalık sprint raporunu (reports/report-wXX.md) GitHub izlerinden (Issue, commit, PR, pano) derler. Haftalık rapor yazılacağı zaman kullan.
---

# pm-rapor — Haftalık sprint raporu

**Ne yapar:** Belirtilen haftanın sprint raporunu, depodaki gerçek izlere (Issue'lar, kanıt yorumları, commit'ler, PR'lar, proje panosu) dayanarak `reports/report-wXX.md` dosyasına yazar. Uydurma bilgi yazmaz; her iddia bir Issue numarasına veya commit hash'ine bağlanır.

## Girdiler

- Hafta numarası (örn. `03`) ve haftanın tarih aralığı
- Depo: `MAKU-VBA-GBT-II/group-a`
- O haftanın Issue'ları (örn. Görev 1 için G1-veri, G1-analiz, G1-gorsel, G1-test)
- Proje panosu: *Sepetix Analitik — Grup A Panosu* (Todo → In Progress → Review → Done)

## Adımlar

1. **Planlananları topla:** O hafta açılan Issue'ları listele (numara, başlık, atanan kişi, son tarih, kabul kriteri).
2. **Yapılanları doğrula:** Her Issue için kapanış/kanıt yorumunu ve ilgili commit'i bul. Kabul kriteri dosyada gerçekten sağlanıyor mu kontrol et (dosya var mı, satır sayısı vb.).
3. **Devir teslim zincirini kontrol et:** BE → DQ ("Veri hazır" yorumu G1-analiz ve G1-gorsel'de var mı?) ve DQ → FE ("Analiz hazır" yorumu G1-gorsel'de var mı?).
4. **Tıkananları yaz:** Açık kalan Issue'lar, kaçırılan son tarihler, cevapsız @mention'lar ve nedenleri.
5. **Kim ne yaptı:** Her üye için commit sayısı ve kapattığı Issue'lar.
6. Raporu aşağıdaki şablonla `reports/report-wXX.md` olarak yaz; commit mesajı: `Hafta XX sprint raporu eklendi`.

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

- Okur: GitHub Issue'ları ve yorumları, `git log`, proje panosu
- Yazar: `reports/report-wXX.md`

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.): **"pm-rapor skill'ini kullanarak Hafta 03 için report-w03.md yaz."** Ajan GitHub'a erişemiyorsa Issue listesi ve `git log --since=... --pretty='%h %an %s'` çıktısı ona verilir.
