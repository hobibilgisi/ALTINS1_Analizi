# Changelog — ALTINS1 Analiz

Tüm önemli değişiklikler bu dosyada kaydedilir.

---

## [0.5.0] — 2026-04-10

### Eklenen Özellikler — Tarihsel MB Altın Rezerv Verisi & Sinyal Analizi
- **Tarihsel Veri Entegrasyonu**: WGC/IMF IFS kaynaklı 11 ülke × 32 çeyreklik dönem (2018-Q1 → 2025-Q4) gömülü veri. Wikipedia güncel snapshot'ları ile birleştirildi.
- **Sinyal Analiz Paneli (Tab7)**: Merkez bankası hareketlerinden altın yönü sinyali:
  - Net Alım Momentum — Son N çeyrekte toplam tonaj değişimi
  - Alıcı/Satıcı Oranı — Alıcı vs satıcı MB dağılımı
  - Ağırlıklı Talep Endeksi — MB önemine göre ağırlıklı (Çin 3×, Hindistan/Polonya/Türkiye 2×, Rusya 1.5×)
  - Bileşik Sinyal — Ortalamalı genel yön göstergesi
- **Yeni Periyot Seçenekleri**: Tab7'de 1a/3a/6a/1y/3y/5y/tümü (eski: 1g/1h kaldırıldı)
- **Genişletilmiş Ülke Kapsamı**: Tarihsel 11 + güncel 53 ülke

### Yeni Dosyalar
- `app/historical_reserves.py` — Gömülü WGC/IMF IFS tarihsel veri
- `app/reserve_signals.py` — Sinyal hesaplama modülü (3 sinyal + bileşik)
- `tests/test_data_sources.py`, `tests/test_fred_series.py`, `tests/test_imf_api.py`, `tests/test_signals.py`, `tests/check_syntax.py`

### Güncellenen Dosyalar
- `app/reserve_tracker.py` — build_history_dataframe() yeniden yazıldı, yeni periyotlar
- `main.py` — Tab7 sinyal paneli, güncel açıklama metinleri, periyot seçici

---

## [0.4.0] — 2026-04-10

### Düzeltmeler (Mobil UX)
- **Grafik Kilidi**: Sidebar'da "📌 Grafik Kilidi" toggle eklendi. Varsayılan: AÇIK. Mobilde grafiklere dokunma artık yanlışlıkla yakınlaştırma yapmaz. Kaydırma ve tarih değerlerini okuma rahatlaştı.
- **Grafik Başlık/Araç Çubuğu Çakışması**: Başlık sol kenara sabitlendi (`title_x=0`), üst kenar boşluğu artırıldı (50 → 80 px). Modebar ile çakışma engellendi.
- **Plotly Modebar**: `select2d`, `lasso2d` araçları kaldırıldı. Plotly logosu gizlendi, `scrollZoom` devre dışı.

### Düzeltmeler (Merkez Bankaları)
- **"%" Etiket Karışıklığı**: "Rez:" → "Altın Payı:" olarak düzeltildi. "Altın Payı" açıklaması eklendi: "Ülkenin toplam döviz rezervleri içinde altının yüzdesel ağırlığı".
- **Yetersiz Veri**: Grafik 2 günden az veri varsa tablo formatına düşer. 30 günden az olduğunda bilgilendirme uyarısı gösterilir.
- **Varsayılan Görünüm**: % Değişim toggle varsayılanı → Kapalı (ton bazlı görünüm). Değişim özeti varsayılan → açık.

### Eklenen Özellikler
- **GitHub/Fork Gizleme**: Streamlit Cloud'daki GitHub badge, fork butonu ve deploy butonu CSS ile gizlendi.
- **Streamlit Footer Gizleme**: "Made with Streamlit" footer'ı ve download sekmesi CSS ile gizlendi.
- **PWA Desteği**: Web App Manifest (`.streamlit/static/manifest.json`) ve meta etiketleri eklendi. Chrome/Safari'de "Ana Ekrana Ekle" seçeneği artık çalışır.

### Dosya Değişiklikleri
- `main.py` — Grafik kilidi, plotly config, CSS gizleme, PWA meta, MB iyileştirmeler
- `.streamlit/config.toml` — `enableStaticServing = true`
- `.streamlit/static/manifest.json` — Yeni (PWA manifest)
- `ISLEMLER.md` — Oturum 5 kayıtları
- `TALIMATLAR.md` — §9 yapılacaklar güncellemesi

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
