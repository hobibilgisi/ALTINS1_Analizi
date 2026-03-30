# ALTINS1 ANALİZ - PROJE TALİMATLARI

> Bu dosya, projenin ana fikrini, tüm yazılı talimatları, mimari kararları, bağımlılıkları
> ve geliştirme prensiplerini içerir. Her oturum başında bu dosya okunmalıdır.

---

## 1. PROJE ANA FİKRİ

ALTINS1 sertifikasının gram altın ve ons altın karşısındaki değişimini analiz ederek
alım için avantajlı olduğu dönemleri yakalayan bir Python masaüstü/web uygulaması.

### Temel Hedefler
- ALTINS1, gram TL altın, ons altın (XAU/USD), dolar/TL fiyatlarını canlı takip
- Bu parametrelerin gramaj olarak birbirleriyle ilişkisini hesaplama
- Makas aralığını (spread) sürekli değerlendirme
- ALTINS1 gram altın fiyatına yaklaştığında **ALIM SİNYALİ** üretme
- Makas çok açıldığında **SATIM SİNYALİ** üretme
- TradingView benzeri grafiklerle görsel sunum
- Merkez bankası altın rezerv takibi (Çin, ABD, Avrupa, TC)
- Güvenilir haber kaynaklarından RSS haber akışı

---

## 2. KULLANICI TALİMATLARI (Orijinal)

### Talimat #1 — İlk Tanım (27 Mart 2026)
- Program ALTINS1 sertifikasının gr altın ve ons altın karşısındaki değişimini analiz etmeli
- Grafik olarak görsel sunmalı (TradingView benzeri)
- Altın S1, gr TL altın, ons altın, dolar/TL parametreleri ve bunların gramaj olarak
  birbirleriyle ilişkilerini hesaplamalı
- Makas aralıklarını değerlendirmeli
- ALTINS1'in alım için avantajlı olduğu (gr altın fiyatına yaklaştığı) dönemleri
  alım sinyali olarak algılamalı
- Makasın çok açıldığı zamanları satış sinyali olarak görmeli
- Uyarı vermeli
- Güvenilir haber kaynakları takip etmeli
- Büyük merkez bankalarının altın stoklama seviyelerini takip edebilmeli
- Bir arayüzü olmalı: güncel fiyatlar, al-sat sinyali, haber akışı, grafikler

### Talimat #2 — Teknik Tercihler (27 Mart 2026)
- Arayüz: Modern ve sade, kolay geliştirilebilir → **Streamlit** seçildi
- Veri kaynağı: Ücretsiz web kaynakları + TradingView (tvDatafeed ile ücretsiz deneme)
- ALTINS1: BIST verisi, %100 doğruluk şartı
- Haber: RSS + güvenilir finans haberleri
- Merkez bankası: Çin, ABD, Avrupa ve TC merkez bankalarının altın rezerv verileri
- Ülke bazlı altın alım/satım özetleri

---

## 3. MİMARİ KARARLAR

### 3.1 Arayüz Teknolojisi
- **Streamlit** (v1.30+)
- Neden: Modern, sade, hızlı prototip, kolay genişletilebilir, grafik desteği güçlü
- Plotly grafikleri ile TradingView benzeri mum grafikleri

### 3.2 Veri Kaynakları (Öncelik Sırasına Göre)

| Veri | Birincil Kaynak | Yedek Kaynak | Not |
|------|----------------|--------------|-----|
| ALTINS1 fiyatı (anlık + tarihsel) | Mynet Finans (scraping) | — | BIST sertifika, ~374 bar tarihsel chart data |
| Gram Altın TL (anlık) | truncgil API (`GRA`) | Hesaplanan: (Ons×USDTRY)/31.1035 | Ücretsiz, auth gereksiz |
| Ons Altın USD (anlık + tarihsel) | `yfinance` (`GC=F`) | — | 7/24 veri |
| Ons Gümüş USD (anlık + tarihsel) | `yfinance` (`SI=F`) | — | COMEX Gümüş Vadeli İşlemleri |
| Dolar/TL (anlık + tarihsel) | truncgil API (`USD`) + `yfinance` (`USDTRY=X`) | — | truncgil anlık, yfinance tarihsel |
| Gram Altın TL (tarihsel) | **Hesaplanır**: (Ons×USDTRY)/31.1035 (yfinance) | — | Tarihsel grafiklerde kullanılır |
| Gram Gümüş TL (tarihsel) | **Hesaplanır**: (SI=F×USDTRY)/31.1035 | — | Troy ons → gram dönüşümü |
| GLDTR Fon (tarihsel) | `yfinance` (`GLDTR.IS`) | — | BIST Altın Borsa Yatırım Fonu |
| Altın çeşitleri (çeyrek, yarım, tam, has) | truncgil API | — | Sadece anlık |
| Mesai dışı fiyatlar | `data/cache/last_prices.json` | — | Son geçerli seans verisi otomatik kaydedilir |

### 3.3 Sinyal Mantığı (Makas Analizi)

```
Gram Altın TL = (Ons_Altın_USD × Dolar_TL) / 31.1035
Makas (%) = (ALTINS1 - Gram_Altın_TL) / Gram_Altın_TL × 100

ALIM SİNYALİ: Makas ≤ eşik_alt (örn: %0.5 veya altı)
SATIM SİNYALİ: Makas ≥ eşik_üst (örn: %3.0 veya üstü)
NÖTR: eşik_alt < Makas < eşik_üst
```

> Eşik değerleri tarihsel veri analizi ile kalibre edilecek.

### 3.4 Haber Kaynakları (RSS)
- Bloomberg Türkiye
- Reuters Türkçe
- Dünya Gazetesi (Ekonomi)
- Investing.com TR
- TCMB duyuruları

### 3.5 Merkez Bankası Altın Rezerv Kaynakları

| Kurum | Kaynak | URL | Güncelleme |
|-------|--------|-----|------------|
| World Gold Council | GoldHub | https://www.gold.org/goldhub/data | Çeyreklik |
| IMF | International Financial Statistics (IFS) | https://data.imf.org | Aylık |
| TCMB | Haftalık rezerv verileri | https://www.tcmb.gov.tr | Haftalık |
| PBoC (Çin) | SAFE | https://www.safe.gov.cn | Aylık |
| US Treasury | TIC Data | https://home.treasury.gov | Aylık |
| ECB | Euro System Reserves | https://www.ecb.europa.eu | Haftalık |

---

## 4. PROJE KLASÖR YAPISI

```
altins1_analiz/
├── app/
│   ├── __init__.py            # Paket başlatma
│   ├── config.py              # Tüm konfigürasyon, YF_SYMBOLS, EmailConfig
│   ├── data_fetcher.py        # Fiyat verisi çekme (yfinance, truncgil, Mynet)
│   ├── calculator.py          # Gram altın hesaplama, makas hesaplama
│   ├── signal_engine.py       # Alım/satım sinyal motoru (5 seviye)
│   ├── news_fetcher.py        # RSS haber çekme (günlük/haftalık)
│   ├── email_notifier.py      # Günlük sinyal özeti e-posta gönderimi
│   ├── reserve_tracker.py     # Merkez bankası altın rezerv takibi
│   └── charts.py              # Plotly grafik bileşenleri (7 grafik)
├── data/
│   └── cache/                 # Önbellek verileri (last_prices.json)
├── logs/
│   └── app.log                # Uygulama logları
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py   # Veri çekme testleri
│   ├── test_calculator.py     # Hesaplama testleri
│   └── test_signal_engine.py  # Sinyal testleri
├── main.py                    # Streamlit giriş noktası (690+ satır, 7 sekme)
├── start.bat                  # Masaüstü kısayol başlatıcı
├── requirements.txt           # Python bağımlılıkları
├── README.md                  # Proje açıklaması
├── TALIMATLAR.md              # Bu dosya
└── ISLEMLER.md                # İşlem günlüğü
```

---

## 5. BAĞIMLILIKLAR (requirements.txt)

```
streamlit>=1.30.0        # Web arayüzü
yfinance>=0.2.30         # Yahoo Finance veri çekme (GC=F, SI=F, USDTRY=X, GLDTR.IS)
plotly>=5.18.0           # İnteraktif grafikler
pandas>=2.1.0            # Veri işleme
numpy>=1.25.0            # Sayısal hesaplamalar
feedparser>=6.0.0        # RSS haber okuma
requests>=2.31.0         # HTTP istekleri
beautifulsoup4>=4.12.0   # Web scraping (Mynet, rezerv verileri)
schedule>=1.2.0          # Zamanlama
python-dateutil>=2.8.0   # Tarih işlemleri
```

> **Not**: E-posta gönderimi Python standart kütüphaneleri (`smtplib`, `email`) ile yapılır — ek paket gerektirmez.

---

## 6. GELİŞTİRME AŞAMALARI

### Aşama 1: Proje İskeleti ✅
- Klasör yapısı oluşturma
- Talimat ve log dosyaları
- requirements.txt

### Aşama 2: Veri Çekme Motoru ✅
- yfinance ile GC=F, SI=F, USDTRY=X, GLDTR.IS veri çekme
- Mynet Finans ALTINS1 scraping (anlık + tarihsel)
- truncgil API (anlık gram altın, dolar, altın çeşitleri)
- Veri doğrulama ve hata yönetimi
- Veri önbellekleme (`data/cache/last_prices.json`)

### Aşama 3: Hesaplama ve Sinyal Motoru ✅
- Gram altın TL hesaplama (ons×USDTRY/31.1035)
- Gram gümüş TL hesaplama (SI=F×USDTRY/31.1035)
- Makas (spread) hesaplama + kümülatif ortalama
- Dinamik alım eşikleri (tarihsel ortalamaya bağlı)
- 5 seviyeli sinyal motoru (STRONG_BUY → STRONG_SELL)

### Aşama 4: Grafik Arayüzü ✅
- Streamlit dashboard yapısı (7 sekme)
- ALTINS1 vs Beklenen grafiği (TL/USD toggle)
- Makas tarihsel grafiği (kümülatif ortalama + eşik çizgileri)
- Normalize karşılaştırma (ALTINS1, Gram, Ons, GLDTR)
- Ons Altın XAU/USD mum grafiği + hacim
- Ons Altın vs Ons Gümüş dual Y-axis
- Gram Altın vs Gram Gümüş (TL/USD toggle)
- Altın/Gümüş oranı + dönem ortalaması
- Tüm grafiklerde checkbox ile çizgi kontrolü

### Aşama 5: Haber Takibi ✅ + Merkez Bankası (Kısmen)
- RSS haber çekme (Bloomberg HT, Dünya Gazetesi, Investing.com TR)
- HTML/CSS temizleme (`_strip_html()`)
- Günlük (24h, 15 haber) ve haftalık (7d, 20 haber) bölümler
- Genişletilmiş anahtar kelimeler (30+ jeopolitik, ekonomi, forex)
- Merkez bankası rezerv: skeleton hazır, veri çekme bekliyor

### Aşama 6: Bildirim Sistemi ✅
- Günlük sinyal özeti e-posta gönderimi (SMTP)
- Birden fazla alıcıya HTML formatında gönderim
- Masaüstü kısayol başlatıcı (`start.bat`)

### Aşama 7: Web Deployment (Planlanan)
- Vercel veya Streamlit Cloud'a taşıma
- Otomatik periyodik yenileme
- Performans optimizasyonu

---

## 7. GELİŞTİRME PRENSİPLERİ

1. **%100 Doğruluk**: Tüm fiyat verileri doğrulanmış kaynaklardan gelmeli
2. **Aşamalı İlerleme**: Her aşama onaylandıktan sonra bir sonrakine geçilir
3. **Log Kaydı**: Her işlem ISLEMLER.md'ye kaydedilir
4. **Talimat Takibi**: Her yeni talimat TALIMATLAR.md'ye eklenir
5. **Bağlam Koruma**: Her oturum başında TALIMATLAR.md ve ISLEMLER.md okunur
6. **Test**: Kritik hesaplamalar test edilir
7. **Hata Yönetimi**: Veri kaynağı erişilemezse yedek kaynağa geçilir
8. **Modüler Yapı**: Her dosya tek bir sorumluluk taşır

---

## 8. HER OTURUM BAŞINDA VE SONUNDA YAPILACAKLAR (ZORUNLU)

### 8.1 Oturum Başı (her yeni oturum açıldığında otomatik uygulanır)

1. **TALIMATLAR.md** dosyasını oku — proje kuralları, mimari kararlar, yapılacaklar listesi
2. **ISLEMLER.md** son 50 satırını oku — son oturumdaki işlemler ve açık kalanlar
3. **Yapılacaklar listesini** (§9) kontrol et — açık maddeler, öncelikler
4. **`logs/app.log`** son 30 satırını kontrol et — hata veya uyarı var mı?
5. Kullanıcıya mevcut durumu kısa özetle ve hangi maddeden devam edileceğini sor
6. Onay alındıktan sonra çalışmaya başla

### 8.2 Oturum Sonu (kullanıcı oturumu kapatmadan önce otomatik uygulanır)

> Kullanıcı "bitirdik", "kapatalım", "sonraki oturumda devam", "yeter" vb. dediğinde
> veya oturum sonlandırılıyormuş gibi göründüğünde bu adımlar uygulanır.

1. **Tamamlanmamış işleri tespit et** — oturumda başlayıp bitirilmemiş veya kısmen yapılmış işler
2. **ISLEMLER.md sonuna "Oturum Sonu Notu" yaz** — şu bilgileri içerir:
   - Oturumda tamamlanan işlerin kısa özeti
   - **Tamamlanmamış / yarım kalan işler** (varsa, detaylı açıklama ile)
   - Devam noktası: sonraki oturum nereden başlamalı?
   - Bilinen sorunlar veya dikkat edilmesi gerekenler
3. **TALIMATLAR.md §9 Yapılacaklar** listesini güncelle — yeni maddeler ekle, tamamlananları ✅ işaretle
4. Kullanıcıya oturum özetini göster

---

## 9. YAPILACAKLAR LİSTESİ

> Açık maddeler her oturum başında kontrol edilir. Tamamlanan maddeler ✅ ile işaretlenir.

### Öncelikli (Kısa Vadeli)
- [ ] Vercel veya Streamlit Cloud'a web deployment
- [ ] Merkez bankası altın rezerv verilerini otomatik çekme

### Orta Vadeli
- [ ] Otomatik periyodik yenileme ve geçmiş veri saklama (SQLite/CSV)
- [ ] Telegram bildirim entegrasyonu (opsiyonel)
- [ ] ALTINS1 için alternatif BIST veri kaynağı araştırma

### Tamamlananlar
- [x] ALTINS1 BIST fiyat kaynağı bulma → Mynet Finans (82.33 TL, 419 bar tarihsel)
- [x] Makas formülü: (Gerçek - Beklenen) / Beklenen × 100, Beklenen = Gram Altın × 0.01
- [x] Sinyal eşikleri: dinamik (tarihsel ortalamaya bağlı) + satım slider
- [x] Normalize karşılaştırma grafiği (ALTINS1 / Gram Altın TL / Ons Altın USD / GLDTR)
- [x] Dashboard yeniden tasarım — ALTINS1 makas odaklı, 7 sekme
- [x] Mesai dışı veri görüntüleme (cache: `data/cache/last_prices.json`)
- [x] Tarihsel makas grafiğinde tarih indeksleri normalize edildi
- [x] Gümüş (SI=F) ve GLDTR.IS fon entegrasyonu + 3 yeni sekme
- [x] Tüm grafiklerde checkbox ile çizgi açma/kapama
- [x] Haber HTML temizliği + günlük/haftalık bölümler
- [x] Dinamik alım eşikleri (tarihsel ortalamaya bağlı)
- [x] Günlük sinyal özeti e-posta bildirim sistemi
- [x] TL/USD para birimi toggle (Tab1, Tab3, Tab6)

---

## 8. ÖNEMLİ NOTLAR

- ALTINS1 BIST'te işlem görür; piyasa saatleri 10:00-18:10 (Türkiye saati)
- Ons altın 7/24 işlem görür ama Türkiye piyasası kapanınca spread hesaplaması dikkatli yapılmalı
- Gram altın = Ons altın × Dolar/TL / 31.1035 (troy ounce)
- ALTINS1 1 gram altını temsil eder, ancak BIST arz-talep dinamiklerine göre fiyatlanır
- Makas tarihsel olarak genellikle %0-5 arasında seyreder
- tvDatafeed resmi olmayan bir kütüphanedir, güncellemelerle bozulabilir
