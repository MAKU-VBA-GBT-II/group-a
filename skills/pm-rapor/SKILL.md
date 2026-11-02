---
name: pm-rapor
description: Grup A'nın haftalık sprint raporunu (reports/report-wXX.md) GitHub izlerinden (Issue, commit, PR, pano) derler ve görev başında Issue taslaklarını (başlık, atanan, son tarih, kabul kriteri) üretir. Haftalık rapor ya da yeni görev Issue'ları hazırlanacağı zaman kullan.
---

# pm-rapor — Haftalık sprint raporu ve Issue taslakları

**Amaç:** PM'in iki yazılı teslimini — haftalık sprint raporu ve görev Issue'ları — depodaki gerçek izlere dayanarak, ders planının biçimine birebir uyacak şekilde üretmek.

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
3. **Yapılanları doğrula:** Her Issue için kapanış/kanıt yorumunu ve ilgili commit'i bul. Kabul kriteri dosyada gerçekten sağlanıyor mu kontrol et (dosya var mı, satır sayısı vb.). Kontrol edilecek dosya yollarını ilgili Issue'nun kabul kriterinden al (örn. Görev 1'de `data/siparisler.csv`, `docs/analiz-g1.md`, `visuals/*.png`); yol tahmin etme. Yollar görevden göreve değiştiği için skill'e sabit yazılmaz. Durum sütununa şu değerlerden yalnızca biri yazılır: **Tamamlandı** (tüm kabul kriterleri dosyada doğrulandı), **Kısmen** (en az bir kriter eksik; eksik olan Issue yorumunda belirtilir), **Yapılmadı** (kanıt yok).
4. **Devir teslim zincirini kontrol et:** DQ → BE ("Şema yayımlandı", Görev 2), BE → DQ/FE ("Veri hazır" yorumu analiz, görsel ve test kartlarında var mı?) ve DQ → FE ("Analiz hazır" yorumu görsel kartında var mı?). PR'larda DQ inceleme yorumu ve Approve var mı?
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
| #00 (örnek) | `dosya/yolu` · `abc1234` | Tamamlandı / Kısmen / Yapılmadı (birini seç) |

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

## Issue taslakları (görev başında)

Yeni görev duyurulduğunda PM, ders planındaki Issue tablosundan kartların taslağını bu skill ile üretir.

1. `ders/AGENTS.md`'de görevin "Hafta N — PM" adımındaki Issue tablosunu ve rol rotasyonunu (§1.3) oku; atanan kişiyi o görevdeki role göre seç.
2. Her Issue için: başlık (plandaki ile birebir, örn. `G2-veri — Parametreli simülasyon`), atanan (`@kullanıcı`), son tarih (duyurudan; yoksa PM'e sor), milestone, pano.
3. Gövde: **İş** (1 cümle) · **Kabul kriterleri** (`- [ ]` listesi; plandaki kriter birebir + dosya yolları + devir yorumu + skill + prompt özeti) · Görev kuralları alt bilgisi.
4. Bağımlılık sırasını son tarihlere yansıt (örn. şema → simülasyon → analiz/grafik): bir kartın girdisi başka kartın çıktısıysa onun son tarihi daha erken olur.
5. Taslağı PM gözden geçirir; Issue'yu PM açar.

## Çıktı formatı kuralları

- Rapor: yalnız `reports/report-wNN.md` (NN iki haneli); başlık `# Sprint Raporu — Hafta NN (GG.AA–GG.AA.YYYY)`; bölümler şablondaki sırayla ve adlarıyla.
- Her "Yapılan" satırında en az bir commit hash'i veya PR/Issue numarası; kanıt yoksa Durum = Yapılmadı.
- Planlanan tablosu Issue başlıklarını ve son tarihleri kabul kriteriyle birebir kullanır; kişi adı değil rol + kullanıcı adı.
- Bilgi yoksa hücreye "kayıt yok" yazılır; tahmin yazılmaz.
- Rapor ve Issue taslakları `main`'e doğrudan değil, dal + PR ile girer (Görev 2 kuralı).

## Örnek giriş / çıkış

**Giriş:** "pm-rapor skill'ini kullanarak Hafta 04 için report-w04.md yaz." + Duyuru-5 (son tarih 27 Ekim 23:59) + Issue #27 (bug, kapalı, `Fixes #27`, commit `1f8beb8`) + Issue #45 (açık).

**Çıkış (`reports/report-w04.md`, kesit):**

```markdown
# Sprint Raporu — Hafta 04 (22.10–27.10.2026)
## Yapılan
| Issue | Kanıt (commit / dosya) | Durum |
|---|---|---|
| #27 | `src/veri_uret.py`, `data/siparisler.csv` — `1f8beb8` (`Fixes #27`) | Tamamlandı |
## Tıkanan / riskler
- #45 açık (BE, devir yorumu notu)
```

## Reddetme durumları

Skill şu durumlarda üretmez, nedenini yazar ve PM'e sorar:
- Gerçek kişisel veri (gerçek müşteri adı, telefon, e-posta, TC kimlik vb.) rapora, Issue'ya veya veri dosyasına yazılması istenirse (plan §3.1: tüm veriler sentetik).
- Teslim tarihi duyuruda bulunamıyorsa (tarih tahmin edilmez).
- Bir iddia için Issue/commit kanıtı yoksa o iddia "tamamlandı" yazılmaz.
- Başka bir grubun deposuna yazma ya da bir Issue'yu sahibinin kanıt yorumu olmadan kapatma istenirse.
- Token, şifre veya API anahtarı dosyaya ya da çıktıya yazılması istenirse.

## Kullanılan dosyalar

- Okur: `ders/Duyuru-*.md` (son tarih ve kapsam), GitHub Issue'ları ve yorumları (kabul kriterleri dahil), `git log`, proje panosu
- Yazar: `reports/report-wXX.md`, görev Issue gövdeleri (taslak)

## Nasıl çalıştırılır

Ajana (Claude Code, Codex vb.): **"pm-rapor skill'ini kullanarak Hafta 03 için report-w03.md yaz."** Ajan GitHub'a erişemiyorsa Issue listesi ve `git log --since=... --pretty='%h %an %s'` çıktısı ona verilir.
