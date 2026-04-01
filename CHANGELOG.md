# Changelog — ALTINS1 Analiz

Tüm önemli değişiklikler bu dosyada kaydedilir.

---

## [1.0.0] — 2026-04-01

### Eklenmiş Özellikler
- ✅ **7 Etkileşimli Sekme**:
  - ALTINS1 Analizi (TL/USD seçeneği)
  - S1/Gram Oranı Analizi
  - Normalize Karşılaştırma (faiz verisi dahil)
  - Ons Altın (XAU/USD) — Candlestick + Volume
  - Altın vs Gümüş Karşılaştırması
  - Haberler (Günlük + Haftalık)
  - Merkez Bankaları (Altın Rezervleri)

- ✅ **ALTINS1 Hacim & Takas Miktarı** — Mynet Finans'tan gerçek zamanlı
- ✅ **Makas Analizi** — Dinamik eşikler, kümülatif ortalama, 4 sinyal seviyesi
- ✅ **Normalize Karşılaştırma** — ALTINS1, Gram Altın, Ons Altın (USD), GLDTR Fonu
- ✅ **E-posta Bildirim Sistemi** — Günlük sinyal özeti, SMTP desteği
- ✅ **Haber Filtresi** — 30+ anahtar kelime, günlük + haftalık bölüm
- ✅ **Mesai Dışı Görüntüleme** — BIST kapalı olduğunda cache'den veri
- ✅ **Checkbox Kontroller** — Her sekmedeki çizgileri göster/gizle
- ✅ **EMA Desteği** — 20, 50, 100, 200 günlük hareketli ortalamalar
- ✅ **Dinamik Font Ayarları** — Metin boyutu ve grafik yüksekliği özelleştirme

### Veri Kaynakları
- **Anlık**: truncgil API (Gram Altın, Dolar/TL, 80+ altın/döviz çeşidi)
- **ALTINS1 BIST**: Mynet Finans (Anlık fiyat + tarihsel chart)
- **Tarihsel**: yfinance (Ons Altın USD, USD/TRY, Gümüş, Faiz)
- **Yedek**: tvDatafeed (nologin XAUUSD, USDTRY)
- **Haberler**: Bloomberg HT, Dünya Gazetesi, Investing.com (RSS)
- **Cache**: JSON disk cache (mesai dışı ve bağlantı kopması durumunda)

### İstatistikler
- **Tarihsel Veri**: ~240 ortak iş günü (Kasım 2022 – Nisan 2026)
- **Makas Eşikleri**: Güçlü Alım ≤%5 | Alım ≤%15 | Satım ≥%35 | Güçlü Satım ≥%50
- **Haber Kaynakları**: 3 RSS feed, günde 40-50 haber, 15 ilgili filtreli

### Teknik Detaylar
- **Framework**: Streamlit
- **Veri**: pandas, yfinance, tvDatafeed, requests, BeautifulSoup
- **Grafikler**: Plotly (Interactive candlestick, dual-axis, normalize serileri)
- **E-posta**: SMTP (HTML şablon, renkli sinyaller)
- **Logging**: Python logging (dosya + konsol)
- **Mimari**: Modüler (config, data_fetcher, calculator, charts, signal_engine, email_notifier, reserve_tracker, news_fetcher)

### Dosya Yapısı
```
altins1_analiz/
├── main.py                 # Streamlit giriş noktası (1000+ satır)
├── README.md               # Bu dosya
├── CHANGELOG.md            # Versiyon geçmişi
├── TALIMATLAR.md           # Detaylı teknik talimatlar
├── ISLEMLER.md             # İşlem günlüğü
├── requirements.txt        # Python bağımlılıkları
├── start.bat               # Windows başlatma scripti
├── app/
│   ├── __init__.py
│   ├── config.py           # Konfigürasyon (API URL, eşikler, kaynaklar)
│   ├── data_fetcher.py     # Veri çekme (truncgil, yfinance, tvdatafeed, mynet, cache)
│   ├── calculator.py       # Makas, beklenen fiyat hesaplamaları
│   ├── signal_engine.py    # Sinyal evaluasyonu (4 seviye)
│   ├── charts.py           # Plotly grafikler (7 fonksiyon)
│   ├── news_fetcher.py     # RSS haber çekme ve filtreleme
│   ├── email_notifier.py   # E-posta gönderimi
│   └── reserve_tracker.py  # Merkez bankası altın rezerv verisi
├── tests/
│   └── __init__.py
├── logs/
│   └── app.log             # Uygulama logları
└── data/
    └── cache/
        └── last_prices.json # Son başarılı veri cache'i
```

---

## Gelecek Sürümler (Roadmap)

### v1.1.0
- [ ] TCMB EVDS API entegrasyonu (otomatik merkez bankası verisi)
- [ ] Otomatik periyodik yenileme (cron / APScheduler)
- [ ] Vercel/Railway deployment hazırlığı
- [ ] Dark/Light tema seçeneği
- [ ] Petrol (Brent) entegrasyonu

### v1.2.0
- [ ] WebSocket gerçek zamanlı güncellemeler
- [ ] Veritabanı (SQLite/PostgreSQL) — tarihsel veri saklama
- [ ] Export (CSV, PDF rapor)
- [ ] Slack/Telegram bot entegrasyonu
- [ ] Kullanıcı tercihleri (profil, eşik özelleştirme)

---

## Bilinen Sorunlar
- Mynet Finans HTML yapısı değişikliğine duyarlı (site güncelleme → parse kırılması riski)
- BIST sertifika (ALTINS1) tvDatafeed nologin modunda erişim yok (login eklenirse açılacak)
- TCMB EVDS API şu an placeholder (Aşama 5'te tam implementasyon)

---

## Katkıda Bulunma

Bu proje açık kaynaklıdır. İyileştirme önerileri ve bug raporları için lütfen issue açın.

---

## Lisans

Bu proje MIT lisansıyla sunulmaktadır.

---

**Son Güncelleme**: 2026-04-01
