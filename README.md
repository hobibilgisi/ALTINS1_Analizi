# ALTINS1 Analiz — Altın Sertifikası Takip ve Sinyal Sistemi

BIST ALTINS1 sertifikasının gram altın, ons altın ve gümüş karşısındaki değişimini analiz eden,
dinamik eşiklerle alım-satım sinyalleri üreten, günlük e-posta bildirimi gönderen
bir Streamlit dashboard uygulaması.

## Özellikler

- **7 Sekmeli Dashboard**: ALTINS1 vs Beklenen, Makas Tarihsel, Normalize Karşılaştırma, Ons Altın XAU/USD, Ons Au vs Ag, Gram Au vs Ag, Au/Ag Oranı
- **Dinamik Sinyal Motoru**: Tarihsel makas ortalamasına bağlı alım eşikleri (5 seviye: Güçlü Alım → Güçlü Satım)
- **Checkbox Kontrolleri**: Her grafikte çizgileri tek tek açıp kapatma
- **TL/USD Toggle**: Tab1, Tab3, Tab6'da para birimi seçimi
- **Canlı Fiyat Takibi**: ALTINS1, gram altın, ons altın, ons gümüş, dolar/TL, GLDTR fonu
- **Haber Akışı**: Günlük (24h) ve haftalık (7d) RSS haberleri — Bloomberg HT, Dünya Gazetesi, Investing.com TR
- **E-posta Bildirim**: Günlük sinyal özeti birden fazla alıcıya HTML formatında SMTP gönderim
- **Mesai Dışı Destek**: Seans kapalıyken cache'den son fiyat gösterimi

## Kurulum

```bash
cd altins1_analiz
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Çalıştırma

```bash
streamlit run main.py
```

Veya masaüstü kısayolu: `start.bat`

## Veri Kaynakları

| Veri | Kaynak | Sembol / Yöntem |
|------|--------|----------------|
| ALTINS1 (anlık + tarihsel) | Mynet Finans (scraping) | — |
| Gram Altın TL (anlık) | truncgil API | `GRA` |
| Ons Altın USD (tarihsel) | yfinance | `GC=F` |
| Ons Gümüş USD (tarihsel) | yfinance | `SI=F` |
| Dolar/TL (anlık + tarihsel) | truncgil + yfinance | `USD` / `USDTRY=X` |
| GLDTR Fon (tarihsel) | yfinance | `GLDTR.IS` |
| Gram Altın TL (tarihsel) | Hesaplanan | (GC=F × USDTRY) / 31.1035 |
| Gram Gümüş TL (tarihsel) | Hesaplanan | (SI=F × USDTRY) / 31.1035 |
| Haberler | RSS | Bloomberg HT, Dünya Gazetesi, Investing.com TR |

## E-posta Bildirim Ayarları

E-posta gönderimi için ortam değişkenleri:

```
ALTINS1_SMTP_SERVER=smtp.gmail.com
ALTINS1_SMTP_PORT=587
ALTINS1_SENDER_EMAIL=ornek@gmail.com
ALTINS1_SENDER_PASSWORD=uygulama-sifresi
ALTINS1_RECIPIENTS=alici1@mail.com,alici2@mail.com
```

## Proje Dokümantasyonu

- [TALIMATLAR.md](TALIMATLAR.md) — Proje talimatları, mimari kararlar, geliştirme prensipleri
- [ISLEMLER.md](ISLEMLER.md) — Yapılan işlemlerin kronolojik günlüğü

## Teknolojiler

Python 3.13+ · Streamlit · Plotly · yfinance · pandas · feedparser · BeautifulSoup4

## Lisans

Kişisel kullanım.
