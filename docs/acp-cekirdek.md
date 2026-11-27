# Sepetix Analitik ACP Çekirdeği

İnşa Haftası 1 · #113. Çekirdek ayardan seçilen tek ajanı alt süreç olarak başlatır, terminalde ajan metnini ve araç durumlarını gösterir. Bağlantı Zed ACP v1 ve satır başına bir JSON-RPC 2.0 iletisi ile stdin/stdout üzerinden kurulur. Akış `initialize` → `session/new` → `session/prompt`.

## İlk çalıştırma

macOS veya Linux terminalinde Python 3.10+ ve Node.js 22+ gerekir. Örnek ayar Claude Agent ACP adaptörünü `0.113.0` sürümüne sabitler. İlk `npx` çağrısı adaptörü indirebilir. Claude Code'daki yerel hesabınızla oturum açıp `claude auth status` ile kontrol edin. Çekirdek bilinen API anahtarı ve oturum belirteci ortam değişkenlerini alt sürece aktarmaz. Yerel oturumun erişebildiği komut ve dosyalar için adaptörün kendi izin kuralları geçerlidir.

Repo kökünde çalıştırın.

```sh
python3 src/acp_cekirdek.py --demo --log /tmp/sepetix-acp-demo.jsonl
```

Demo Claude'dan `docs/oneri.md` içindeki satırları gerçekten saymasını ister. Kendi göreviniz için `--demo` yerine `--prompt "sorunuz"` kullanın. Çalışma dizinini `--cwd` ile seçebilirsiniz. Her çalıştırma için yeni bir kayıt yolu kullanın. İşlem kodu `0` ACP turunun `end_turn` ile bittiğini gösterir. Aracın çalıştığına dair kanıt, ilgili çağrının `completed` durumudur.

Araç değiştirmek için `config.example.json` dosyasının yerel bir kopyasında `ajanlar` altına yeni kayıt ekleyin, `ajan` ile seçin ve `--config` ile kopyayı verin. `komut` program ve argümanların JSON dizisidir. Yeni bir kabuk üzerinden yorumlanmaz. `zaman_asimi_saniye` her protokol isteğinin toplam süresidir, izin için bekleme de buna dâhildir. Seçilen araç ACP v1 ve bu istemciyle uyumlu yerel giriş akışı sunmalıdır. Bu teslimde gerçek uçtan uca deneme Claude ile yapıldı.

## İzin denemesi

Claude varsayılan politikasıyla bazı işlemler için izin istemeyebilir. Aynı güvenli komutla menüyü tekrar görmek için geçici bir deneme çalışma kopyasında Claude'un `.claude/settings.local.json` ayarına şu kuralı ekleyin. Mevcut bir dosyada diğer ayarları koruyun. Yerel ayar dosyasını repoya eklemeyin.

```json
{"permissions":{"ask":["Bash"]}}
```

Etkileşimli terminalde demoyu çalıştırın. İzin isteğinde adaptörün araç/komut ayrıntılarını inceleyip “Bir kez izin ver” veya “Bir kez reddet” seçeneğini seçin. Çekirdek kalıcı izin seçeneklerini sunmaz. Boş ya da geçersiz seçimde veya etkileşimli giriş yoksa izin isteği iptal edilir. İsteğin zaman sınırı aşılırsa tur hata ile biter ve alt süreç kapatılır.

## Oturum izi

Kayıt UTF-8 JSONL'dir. UTC zaman damgalarıyla protokol aşamalarını, araç sırası/türü/durumunu ve izin kararını kaydeder. Açıkça tanımlanmış salt okunur demo komutu ajan tarafından birebir bildirildiğinde metni de kaydedilir. Genel görevlerin serbest komut metni, model yanıtı, ham istek/yanıt, detaylı hata metni, kimlik, ortam değişkenleri ve araç çıktıları kayda yazılmaz. Canlı terminalde kullanıcının incelemesi için ajan metni ve izin ayrıntıları görünür.

27 Kasım 2026 tarihli gerçek Claude Code Pro oturumu kayıtları:

- [Onay denemesi](../runs/insa1-claude-demo-onay.jsonl) — Bash için tek seferlik izin seçildi, komut `completed` durumuna geçti. Canlı yanıtta 114 satır döndü.
- [Red denemesi](../runs/insa1-claude-demo-red.jsonl) — Aynı komut reddedildi ve araç durumu `failed` oldu. ACP turu sonuç mesajıyla kapandı.

Kayıt aracı Python ACP istemcisi ve Claude Agent ACP adaptörü. Claude'a verilen demo görevi özeti: Bash ile `docs/oneri.md` satırlarını salt okunur komutla bir kez say ve sayıyı bildir. Çekirdek ve testlerin üretim aracı Codex. Codex görev özeti: Duyuru 11 için ayarlanabilir tek ajan ACP istemcisini, canlı izin akışını, güvenli oturum izi ve testleri geliştir.

## Test komutları

```sh
python3 -m unittest discover -s tests -p 'test_acp_cekirdek.py' -v
python3 -m pip install -r requirements.txt
python3 src/dq_test_g2.py
```

İlk komut mock ACP alt süreciyle akışı, canlı çıktı, tek seferlik izin, kalıcı izin reddi, etkileşimsiz çalışma, bozuk yanıt, süreç kapanması ve zaman aşımı durumlarını doğrular. Simülasyon testi ayrı çalışır. Kod ve varsayılan veri dosyaları simülasyon tarafında değiştirilmedi.

Resmî kaynaklar: [Zed ACP v1](https://agentclientprotocol.com/protocol/v1/overview), [araç ve izin istekleri](https://agentclientprotocol.com/protocol/v1/tool-calls), [Claude Agent ACP](https://github.com/agentclientprotocol/claude-agent-acp).
