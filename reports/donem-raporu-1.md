# Dönem Raporu 1 — Sepetix Analitik (Grup A)

**PM:** Ali Haydar Polat · **Dönem:** Görev 1 kapanışı (`gorev1-final`, 24.10.2026) – 07.11.2026 · **Kaynak:** GitHub izleri ve üyelerin #73'teki yanıtları

## 1. Yönetici Özeti

Grup A, bu dönemde iki görevi de sürümüyle ve son tarihten önce teslim etti: Görev 1 `gorev1-final` (24.10), Görev 2 `gorev2-final` (02.11). Görev 2'nin beş rol Issue'su Duyuru-7'nin 05.11 bitiş hattından dört gün önce kapandı; kod içeren her değişiklik `main`'e PR + inceleme + Approve ile girdi ve incelemelerde iki gerçek hata (#76, #77) merge'den önce yakalanıp düzeltildi. Görev 1'de kayda geçirdiğimiz veri sınırlılığı (#30) Görev 2 simülasyonunda ölçülerek çözüldü. Zayıf yanlarımız: junior üyeye Görev 2'de ayrı kart açılmadı ve teslimatların büyük kısmı yapay zekâ ajanlarıyla üretildi; Görev 3 öncesi rol değişiminde devralınan işin gerçekten anlaşılması için bir devir programı başlattık (#86–#90).

## 2. Teslim Edilenler

| İş | Kanıt | Sahibi |
|---|---|---|
| Görev 1 sürümü | [`gorev1-final`](https://github.com/MAKU-VBA-GBT-II/group-a/releases/tag/gorev1-final) (`1dfb4a4`), `reports/report-w04.md` (PR #50) | Ekip / Ali |
| Görev 1 BE skill'inin son hali | `be-veri` kontrolleri TC-01…TC-12 ile eşitlendi, örnek giriş/çıkış, devir şablonu, MD5 özeti — PR #51, #52, #55, #57 | Hilal |
| Grup B incelemelerine cevaplar | #39 → PR #49 (Ali) · #53 → `a6a856a` (Tuğba) · #54 → `026f504` (Sema) · #56 → PR #57 (Hilal) · #58 → PR #59 (Ali) | Herkes |
| G2 şema | `docs/veri-sozlugu.md` (14 alan, 8 parametre, 12 kalite kuralı, M1–M6) + `skills/dq-sozluk` — PR #65, #67, #74 | Sema |
| G2 simülasyon | `src/simulasyon.py`, `data/siparisler-g2.csv` (8.208 satır) + `skills/be-simulasyon` — PR #66; hata yönetimi (`ValueError`) — PR #72 | Tuğba |
| G2 analiz | `docs/analiz-g2.md` (5 metrik + M6, 3 bulgu + 1 eylem önerisi), `docs/requirements.md`, `src/dq_analiz_g2.py` — PR #75 | Sema |
| G2 grafikler | 3 PNG + `src/fe_gorsel.py`; elle çizilmiş taslak kod öncesi #63'te — PR #79 | Hilal |
| G2 test | 22 senaryo, test koşucusu `src/dq_test_g2.py`, son tur 23/23, bug #76/#77, `docs/user-manual.md` — PR #68, #78, #80, #81 | Sema |
| PM | Milestone + #60–#64, `pm-rapor` Görev 2 güncellemesi (PR #70), `reports/report-w05.md` (PR #82), [`gorev2-final`](https://github.com/MAKU-VBA-GBT-II/group-a/releases/tag/gorev2-final) (`a3a4c2b`), PR #75 ve #78 incelemesi | Ali |
| Görev 1 sınırlılığının çözümü | #30: haftalık ciro değişim katsayısı %40,2 → %13,0, ürün bazlı fiyat (PR #66) | Tuğba / Sema |
| Devir programı (Görev 3 hazırlığı) | #86–#90 | Ali |

Görev 2'nin Duyuru-7 bitiş hattı (05.11 23:59) öncesinde, 01.11'de tüm Issue'lar kapanmış ve milestone 02.11'de kapatılmıştır.

## 3. Sayılarla Dönem

Dönem: 24.10.2026 19:03 (`gorev1-final`) – 07.11.2026. Kaynak: GitHub REST API (Issue, PR, review, yorum ve commit kayıtları), 07.11.2026'da çekildi.

| KPI | Değer | Not |
|---|---|---|
| Açılan Issue | **15** | #56, #58 (Grup B incelemeleri), #60–#64 (Görev 2), #73, #76–#77 (bug), #86–#90 (devir programı) |
| Kapatılan Issue | **13** | Görev 2'nin 5 rol Issue'su, 2 bug, 3 inceleme Issue'su, #30, #32, #73 |
| Açık Issue (07.11) | **5** | Yalnız #86–#90 (devir programı, 05.11'den sonra açıldı); Duyuru-7 bitiş hattında (05.11 23:59) açık Issue **0** |
| Merge edilmiş PR | **19** | `src/` veya `data/` değiştiren 5 PR (#66, #72, #75, #78, #79) ve 14 belge/skill PR'ı (ders §3.5: belge PR'ını yazarı merge eder) |
| İnceleme alan PR | **7 / 19** | `src/`/`data/` değiştiren 5 PR'ın tamamı inceleme + Approve ile girdi; ayrıca belge PR'ları #57 ve #83 de incelendi |
| PR açılışı → ilk inceleme yorumu | **medyan 0,4 saat (~23 dk)**, ortalama 5,2 saat | 7 incelemeli PR: #83 0,06 · #78 0,17 · #57 0,29 · #75 0,39 · #79 0,58 · #66 2,51 · #72 32,52 saat (#72 31.10'da açıldı, ertesi gün incelendi) |
| Son tarihi geçen iş | **0** | Dönemde kapanan Issue'ların hiçbiri gövdesindeki son tarihten sonra kapanmadı. (Dönem öncesi: W03 raporu 1 gün geç, #44) |
| Toplam (dönem başından bu yana) | 52 Issue (47 kapalı) · 36 merge edilmiş PR | — |

**Üye bazında (dönem içi):**

| Üye | Commit (merge hariç) | Merge commit | Üstlendiği ve kapanan Issue |
|---|---|---|---|
| Sema Nur Doğan | 25 | 10 | 4 — #54, #60, #62, #64 |
| Tuğba Tuana Kaygısız | 9 | 3 | 4 — #30, #61, #76, #77 |
| Hilal Elçin Şahin | 7 | 3 | 1 — #63 |
| Ali Haydar Polat | 4 | 4 | 2 — #32, #73 |
| Ebru Türk | 0 | 0 | 0 (Görev 2'de kart açılmadı) |

Not: Commit sayısı iş miktarını değil iz sayısını gösterir; Sema'nın Görev 2'de üç Issue'su (şema, analiz, test) olduğu için sayısı yüksektir. Grup B'nin açtığı #56 ve #58 atanmamış olarak kapandı (sırasıyla Hilal ve Ali'nin PR'ları ile).

## 4. Tıkananlar

| Ne oldu | Neden | Nasıl çözüldü | Kanıt |
|---|---|---|---|
| İzinli parametrelerle (`gunluk_siparis=1`, `hafta_sonu_katsayisi=0.4`) 0 siparişli gün oluştu, iç kontrol düştü | Sözlükte "her gün en az bir sipariş" varsayımı formüle yazılmamıştı | DQ, BE PR'ını incelerken buldu; sözlük ve koda `max(1, …)` eklendi, varsayılan veri değişmedi | #76, PR #72, PR #74 |
| Geçersiz parametrede anlaşılmaz hata, ters kampanya aralığında sessizce kampanyasız dosya | Parametre doğrulaması yoktu | Üretimden önce çalışan doğrulama + Türkçe `ValueError`, çıkış kodu 1 | #77, PR #72 |
| Histogramda taşan siparişler son kovaya düşüyordu (çubuk 359, dipnot 304) | `clip(upper=7000)` | DQ incelemesinde bulundu; taşanlar için ayrı kova | PR #79, `c85a4e0` |
| Analiz betiğinde kampanya haftaları sabit yazılmıştı | Parametre değişince sonuç yanlış çıkacaktı | Haftalar veriden türetildi | `7f15393` |
| Görev 2 bitişi 10.11'den 05.11'e çekildi | Duyuru-7 | Ekip işleri 01.11'de bitirdi | `gorev2-final` |
| PR #70'te AGENTS.md çakışması | Aynı satır PR #71 ile de güncellenmişti | Çakışma çözüldü | `7132a05` |
| Rol değişiminde devralınan kodu anlamak (FE) | Kod ve skill başkası tarafından yazılmıştı | Commit geçmişi okunarak kararların nedeni çıkarıldı | #73 (Hilal) |

## 5. Kim Ne Yaptı

| Üye | Görev 2 rolü | Teslim ettikleri (öz) | Takıldığı / aştığı | Kaynak |
|---|---|---|---|---|
| Ali Haydar Polat | PM | Milestone + 5 Issue, `pm-rapor` Görev 2 güncellemesi, W05 raporu, `gorev2-final`, 2 PR incelemesi, devir programı | Raporun otomasyonu Duyuru-7'yi okuyamadı; W05 elle derlendi | PR #70, #82 |
| Hilal Elçin Şahin | FE (G1: BE) | `be-veri` son hali (4 PR), #27 düzeltmesi; G2'de elle taslak, 3 grafik, `fe-gorsel` Görev 2 | Devralınan FE kodunu anlamak; histogram kova hatası (DQ buldu) | #73 yorumu, PR #79 |
| Sema Nur Doğan | DQ | Sözlük, 22 test senaryosu, analiz ve bulgular, test koşucusu, 2 bug, kullanım kılavuzu, 3 PR incelemesi | Sözlükteki "en az 1 sipariş" varsayımı; sabit kampanya haftaları | #73 yorumu, PR #65, #75, #78 |
| Tuğba Tuana Kaygısız | BE (G1: DQ) | Parametreli simülasyon, 8.208 satırlık veri, hata yönetimi, #30'un çözümü | Parametre aralığı ve 0 siparişli gün bulguları (DQ incelemesi) | #73 yorumu, PR #66, #72 |
| Ebru Türk | Junior | Görev 1: gözlem raporu (#31), TC-03 elle kontrol (#38), Grup G junior-kontrol incelemesi | TC-03'te sütunları sözlükle elle eşleştirmek | #73 yorumu |

Üye hedef/önerileri (#73): Sema ve Tuğba test koşucusunun her kod PR'ında GitHub Actions ile otomatik çalışmasını; Hilal skill'i işten önce yazmanın grup standardı olmasını; Ebru test ve veri kontrolünde daha fazla sorumluluk almayı önerdi.

## 6. Dersler

1. **Önce skill, sonra iş.** Görev 2'de skill'ini işten önce commit'leyen üyelerde (Tuğba `bf7b4d7`, Hilal `99c0902`) ne üretileceği baştan netti ve inceleme turu kısaldı. Görev 3'te bunu grup standardı yapıyoruz.
2. **Varsayımı kurala ve teste çevir.** "Her gün en az bir sipariş olur" varsayımı sözlükte yazılı ama formülde yoktu; ancak PR incelemesinde (#76) ortaya çıktı. Görev 3'te sözlükteki her varsayım bir test senaryosuna dönüşecek; üyelerin önerisi doğrultusunda test koşucusunu her kod PR'ında GitHub Actions ile otomatik çalıştırmayı deneyeceğiz.
3. **Otomasyonun son kontrolü insanda.** Rapor otomasyonu W03'te duyuruyu yanlış okuyup gecikmeye (#44), W05'te de yanlış duyuruyu seçmeye yol açtı. Teslimden önce dosyanın `main`'de olduğunu PM kendi gözüyle kontrol ediyor; yapay zekâ ile üretilen işin de sahibince anlatılabilir olması devir programıyla takip edilecek.

## 7. Görev 3 Hazırlığı

Grup A, Görev 3'te **G → A → B → G** üçlü döngüsündedir (ders/AGENTS.md, Görev 3):

| Akış | Ne | Grup A'daki sorumlu (Görev 3 rolü) |
|---|---|---|
| **G → A** (içe aktarma) | Grup G'nin kampanya verisini alıp siparişlerimizle ilişkilendirmek (analiz + görselleştirme) | Hilal (DQ) analiz, Tuğba (FE) grafik |
| **A → B** (dışa aktarma) | Görev 2 sipariş verimizden `exchange/output.csv` üretip Grup B'ye göndermek | Sema (BE) `ExportCSV`, Tuğba (FE) tek komutla üretim |
| Sözleşme | `docs/veri-sozlesmesi.md` — üç akış ayrı başlıklarla, üç depoda birebir aynı | Hilal (DQ), G ve B DQ'larıyla |
| Ortak toplantı | `reports/joint-meeting-w07.md`, üç depoya | Ali (PM) |

Hazırlık:
- Görev 2 simülasyonu kampanya dönemlerini ve `kampanya` alanını zaten içeriyor; G'nin kampanya verisiyle eşleştirme için **tarih + kanal** ortak anahtar adayıdır (sözleşmede netleşecek).
- B'ye gidecek sipariş verisi için Görev 2 şeması (14 alan) temel alınır; B'nin teslimat analizi için `siparis_tarihi`, `sehir`, `durum` alanları kritik.
- Rol değişimi öncesi devir programı (#86–#90): tahmin soruları, akış çizimi ve 9 Kasım'da canlı devir oturumu; küçük değişiklikler Görev 3'ün ilk PR'ları olacak.

---

Üretim: pm-rapor skill'i ile, Claude — prompt özeti: "pm-rapor skill'ini kullanarak Duyuru-7 Bölüm 2 şablonuyla Dönem Raporu 1'i yaz; üyelerin #73 yanıtlarını, PR #49–#84 ve commit izlerini kaynak göster; süreç KPI'larını GitHub API'den hesapla." Rapor PM tarafından gözden geçirilmiştir.
