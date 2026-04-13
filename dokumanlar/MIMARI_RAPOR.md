# ALTINS1 ANALİZ — Teknik Mimari Raporu

> Oluşturulma: 13 Nisan 2026 | Güncelleme: Temmuz 2026 | Toplam ~4,500+ satır Python kodu

---

## 1. DOSYA YAPISI VE SATIR SAYILARI

### Kök Dizin
| Dosya | Satır | Açıklama |
|-------|-------|----------|
| `altins1_app.py` | ~555 | Ana Streamlit orkestratör (veri yükleme, sidebar, tab yönlendirme) |
| `requirements.txt` | 11 | Python bağımlılıkları |
| `start.bat` | ~30 | Masaüstü başlatıcı |
| `stop.bat` | ~15 | Uygulamayı durdurma |
| `README.md` | — | Proje açıklaması |

### `app/` Paketi
| Dosya | Satır | Açıklama |
|-------|-------|----------|
| `__init__.py` | 1 | Paket işaretçi |
| `config.py` | ~180 | Konfigürasyon, sabitler, eşik değerleri |
| `data_fetcher.py` | ~480 | Fiyat verisi çekme (yfinance, truncgil, Mynet) |
| `data_preparer.py` | ~110 | Tarihsel veri hazırlama (PreparedSeries) |
| `calculator.py` | ~95 | Gram altın/gümüş hesaplama, makas hesaplama |
| `signal_engine.py` | ~50 | Alım/satım sinyal motoru (5 seviye) |
| `charts.py` | ~620 | Plotly grafik bileşenleri + Türkçe tarih |
| `ui_helpers.py` | ~150 | UI yardımcıları (EMA, chart font, PLOTLY_CONFIG) |
| `news_fetcher.py` | ~200 | RSS haber çekme ve filtreleme |
| `email_notifier.py` | ~200 | SMTP e-posta gönderimi |
| `reserve_tracker.py` | ~350 | Wikipedia scraping, günlük snapshot, tarihsel kayıt |
| `reserve_signals.py` | ~600 | MB rezerv sinyal analizi (8 sinyal + bileşik) |
| `historical_reserves.py` | ~95 | WGC/IMF IFS tarihsel veri (2018+, sabit) |

### Diğer Klasörler
```
data/cache/          → last_prices.json, volume_history.json
dokumanlar/          → CHANGELOG.md, ISLEMLER.md, TALIMATLAR.md, YAPILACAKLAR.md, WEB_TASIMA_REHBERI.md
logs/                → app.log
tests/               → test_data_fetcher.py, test_calculator.py, test_signal_engine.py
static/              → manifest.json (PWA desteği)
```

---

## 2. MODÜL İÇ BAĞIMLILIKLARI (Import Haritası)

### altins1_app.py (GİRİŞ NOKTASI — Orkestratör)
```
app.config           → AppConfig, SignalThresholds, ALTINS1_GRAM_KATSAYI, EmailConfig
app.data_fetcher     → fetch_current_prices, fetch_all_history, fetch_altins1_mynet,
                        is_bist_open, load_prices_from_cache
app.signal_engine    → evaluate_signal, generate_signal_message, SignalType
app.news_fetcher     → get_daily_and_weekly_news
app.email_notifier   → send_daily_signal_email
app.data_preparer    → prepare_all_series
app.tabs             → TabContext
app.tabs.tab_*       → (8 tab modülü, her birinden render() çağrılır)
```

### Tab Modülleri (app/tabs/)
| Modül | İç Bağımlılıklar |
|-------|------------------|
| `tab_altins1.py` | `charts`, `ui_helpers`, `config` |
| `tab_spread.py` | `charts`, `ui_helpers`, `calculator` |
| `tab_normalize.py` | `charts`, `ui_helpers` |
| `tab_ons.py` | `charts`, `ui_helpers` |
| `tab_gold_silver.py` | `charts`, `ui_helpers`, `config` |
| `tab_news.py` | — (sadece streamlit) |
| `tab_reserves.py` | `reserve_tracker`, `reserve_signals`, `historical_reserves`, `charts`, `ui_helpers` |
| `tab_guide.py` | — (sadece streamlit) |

### Alt Modüller (app/)
| Modül | İç Bağımlılıklar |
|-------|------------------|
| `config.py` | — (bağımsız, saf konfigürasyon) |
| `historical_reserves.py` | — (bağımsız, saf veri) |
| `reserve_signals.py` | — (bağımsız, saf sinyal mantığı) |
| `calculator.py` | `config` (TROY_OUNCE_GRAM, ALTINS1_GRAM_KATSAYI) |
| `signal_engine.py` | `config` (SignalThresholds) |
| `news_fetcher.py` | `config` (RSS_FEEDS, NEWS_KEYWORDS) |
| `reserve_tracker.py` | `config` (RESERVE_SOURCES) |
| `data_fetcher.py` | `config` (URL'ler, YF_SYMBOLS, sabitler) |
| `data_preparer.py` | `config` + `calculator` |
| `charts.py` | `config` (ALTINS1_GRAM_KATSAYI) |
| `email_notifier.py` | `config` + `signal_engine` |
| `ui_helpers.py` | `charts` (turkce_tarih_ekseni) |

### Bağımlılık Seviyeleri
```
Seviye 0 (Bağımsız):    config, historical_reserves, reserve_signals
Seviye 1 (Seviye 0):    calculator, signal_engine, news_fetcher, reserve_tracker
Seviye 2 (Seviye 0-1):  data_fetcher, data_preparer, charts, email_notifier
Seviye 3 (Seviye 0-2):  ui_helpers
Seviye 4 (Seviye 0-3):  app/tabs/* (tab modülleri — charts, ui_helpers, config kullanır)
Seviye 5 (Tümü):        altins1_app (orkestratör — TabContext oluşturur, tab render çağırır)
```

### Bağımlılık Diyagramı
```
altins1_app.py (orkestratör)
    ├── config ─────────────────────────────────────────┐
    ├── data_fetcher ──→ config                         │
    ├── signal_engine ─→ config                         │
    ├── data_preparer ─→ config + calculator            │
    ├── email_notifier → config + signal_engine         │
    ├── news_fetcher ──→ config                         │
    └── tabs/ ─────────────────────────────────────────┐│
        ├── tab_altins1 ──→ charts, ui_helpers, config ││
        ├── tab_spread ───→ charts, ui_helpers, calc   ││
        ├── tab_normalize → charts, ui_helpers         ││
        ├── tab_ons ──────→ charts, ui_helpers         ││
        ├── tab_gold_silver → charts, ui_helpers, conf ││
        ├── tab_news ─────→ (bağımsız)                 ││
        ├── tab_reserves ─→ reserve_tracker,           ││
        │                    reserve_signals,           ││
        │                    historical_reserves,       ││
        │                    charts, ui_helpers         ││
        └── tab_guide ────→ (bağımsız)                 ││
```

---

## 3. DIŞ BAĞIMLILIKLAR

### PyPI Paketleri (requirements.txt)
| Paket | Versiyon | Kullanım Yeri |
|-------|----------|---------------|
| `streamlit` | ≥1.30.0 | Web UI framework |
| `yfinance` | ≥0.2.30 | Yahoo Finance veri (GC=F, SI=F, USDTRY=X) |
| `plotly` | ≥5.18.0 | İnteraktif grafikler |
| `pandas` | ≥2.1.0 | Zaman serisi veri işleme |
| `numpy` | ≥1.25.0 | Sayısal hesaplamalar |
| `feedparser` | ≥6.0.0 | RSS haber okuma |
| `requests` | ≥2.31.0 | HTTP (truncgil API, Wikipedia) |
| `beautifulsoup4` | ≥4.12.0 | Web scraping (Mynet, reserve) |
| `schedule` | ≥1.2.0 | Zamanlama (altyapı hazır, aktif değil) |
| `python-dateutil` | ≥2.8.0 | Tarih işlemleri |
| `lxml` | ≥4.9.0 | XML parsing (BS4 backend) |

### Dış Veri Kaynakları (API/Scraping)
| Kaynak | URL | Veri | Yöntem |
|--------|-----|------|--------|
| Mynet Finans | `finans.mynet.com` | ALTINS1 BIST fiyat + tarihsel chart | Scraping |
| Truncgil API | `finans.truncgil.com/v4/today.json` | Gram altın TL, dolar/TL, altın çeşitleri | REST API |
| Yahoo Finance | `yfinance` kütüphanesi | GC=F, SI=F, USDTRY=X, ^TNX, GLDTR.IS | Python API |
| RSS Feeds | Bloomberg HT, Dünya, Investing.com TR | Altın/ekonomi haberleri | feedparser |
| Wikipedia | `en.wikipedia.org/wiki/Gold_reserve` | MB altın rezervleri (güncel tablo) | Scraping |
| WGC/IMF IFS | Sabit veri (historical_reserves.py) | Çeyreklik tarihsel rezerv (2018+) | Hardcoded |

---

## 4. ANA SINIFLAR VE FONKSİYONLAR

### config.py — Dataclass'lar
```python
@dataclass SignalThresholds:
    strong_buy: float = 5.0        # Makas ≤%5 → GÜÇLÜ ALIM
    buy_threshold: float = 15.0    # Makas ≤%15 → ALIM
    sell_threshold: float = 35.0   # Makas ≥%35 → SATIM
    strong_sell: float = 50.0      # Makas ≥%50 → GÜÇLÜ SATIM

@dataclass AppConfig:
    page_title, page_icon, cache_ttl_sec=600, price_cache_file

@dataclass EmailConfig:
    smtp_server, smtp_port, sender_email, sender_password, recipients
```

### data_fetcher.py — Fonksiyonlar
```python
fetch_current_prices() → Dict          # Çoklu kaynak birleştirici (Mynet+Truncgil+yfinance)
fetch_altins1_mynet() → (float, DataFrame)  # ALTINS1 anlık + tarihsel
fetch_truncgil() → Dict                # truncgil API (JSON tamir desteği)
fetch_all_history(period) → Dict       # yfinance tarihsel (ons, gümüş, dolar)
is_bist_open() → bool                  # BIST seans kontrolü (10:00-18:10)
save_prices_to_cache() / load_prices_from_cache()  # Disk cache fallback
```

### calculator.py
```python
calculate_gram_gold_tl(ons_usd, usd_try) → float     # (Ons×Dolar) / 31.1035
calculate_expected_altins1(gram_gold_tl) → float       # Gram × 0.01
calculate_spread(altins1, gram_gold_tl) → float        # Makas %
calculate_spread_series(s1, s2) → Series               # Vektörel makas
spread_statistics(spread) → dict                       # Ort, medyan, std, min/max
```

### signal_engine.py
```python
class SignalType(Enum):
    STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL

evaluate_signal(spread_pct, thresholds) → SignalType
generate_signal_message(signal_type, spread_pct) → str
```

### data_preparer.py
```python
@dataclass PreparedSeries:
    gram_gold_tl, ons_gold_tl, ons_usd, usdtry, altins1,
    ons_silver_usd, gram_silver_tl, faiz, spread  (hepsi Optional[Series])

prepare_all_series(history, altins1_hist, prices) → PreparedSeries
```

### charts.py
```python
COLORS = {"altins1": "#42a5f5", "gram_altin": "#ffa726", ...}  # 15 renk

apply_base_layout(fig, title, height, yaxis_title, **extra)  # Merkezi layout
turkce_tarih_ekseni(fig) → Figure  # Tüm tarihleri Türkçe'ye çevir

create_price_chart(df, title, show_volume)      # Mum grafik + hacim
create_spread_chart(spread, thresholds)          # Makas % + eşik çizgileri
create_altins1_vs_expected_chart(a1, gram, ...)  # ALTINS1 vs Beklenen
create_overlay_chart(a1, gram, ons, ...)         # Normalize karşılaştırma
create_gold_silver_chart(gold, silver, unit, ccy) # Altın vs Gümüş dual-Y
```

### ui_helpers.py
```python
PLOTLY_CONFIG = {scrollZoom: False, displaylogo: False, ...}

add_ema_traces(fig, series, ema_states, label_prefix, ...)
ema_checkboxes(container, prefix, default_on) → dict
apply_chart_font(fig, font_size, chart_height, grafik_kilidi)
    → font boyutu, hover, crosshair, son 2 gün uzatma, turkce_tarih_ekseni çağırır
```

### reserve_signals.py — 8 Sinyal Fonksiyonu
```python
@dataclass ReserveSignal:
    name, value(-100..+100), label, emoji, detail

compute_net_change_momentum(df, quarters)     # Net alım/satım momentum
compute_buyer_ratio(df)                        # Alıcı/toplam MB oranı
compute_weighted_demand_index(df)              # Ağırlıklı talep (Çin 3x)
compute_momentum_acceleration(df, window)      # İvme değişimi (2. türev)
compute_china_leading_indicator(df, quarters)   # PBoC öncü gösterge
compute_buying_concentration(df, quarters)      # HHI yoğunlaşma
compute_gold_share_trend(reserves_data)         # Altın payı trendi
compute_price_correlation(df, gold_prices)      # Fiyat korelasyonu

compute_all_signals(df, reserves, gold_prices) → List[ReserveSignal]
compute_composite_signal(signals) → ReserveSignal  # Bileşik sinyal
```

---

## 5. VERİ AKIŞI

### Canlı Fiyat Akışı
```
Kullanıcı Yenile →
  fetch_current_prices()
    ├─ fetch_altins1_mynet()      → ALTINS1 BIST + Hacim (Mynet scraping)
    ├─ fetch_truncgil()           → Gram Altın TL, Dolar/TL (REST API)
    ├─ yfinance GC=F              → Ons Altın USD
    └─ Hesaplamalar:
        gram_altin = (ons×dolar) / 31.1035
        beklenen   = gram_altin × 0.01
        makas_%    = (altins1 - beklenen) / beklenen × 100
  → save_prices_to_cache() (disk yedek)
  → Sonuç: {altins1_fiyat, gram_altin_tl, makas_pct, ons_altin_usd, ...}
```

### Sinyal Üretimi
```
makas_pct → evaluate_signal(makas_pct, thresholds)
  ≤%5  → STRONG_BUY | ≤%15 → BUY | ≥%50 → STRONG_SELL | ≥%35 → SELL | else → NEUTRAL
→ generate_signal_message() → "🟢 GÜÇLÜ ALIM SİNYALİ! Makas: %X.XX"
→ Sidebar + E-posta
```

### Tarihsel Veri Akışı
```
Periyot seçimi → fetch_all_history(period)
  ├─ yfinance GC=F, SI=F, USDTRY=X (tarihsel)
  └─ fetch_altins1_mynet() (tarihsel chart Mynet)
→ prepare_all_series()
  ├─ İndeks normalleştirme (timezone, deduplicate)
  ├─ Ortak tarih aralığı bulma
  ├─ gram_gold_tl hesaplama
  └─ spread % hesaplama
→ PreparedSeries → Grafiklere dağıtım
```

### Grafik Render Akışı (Tab Modül Deseni)
```
altins1_app.py:
  TabContext oluştur (series, prices, history, thresholds, UI ayarları)
  → tab_*.render(ctx) çağır

Her Tab Modülü (render fonksiyonu):
  create_*_chart(series) → Plotly Figure oluştur
  → add_ema_traces() (EMA 20/50/100/200 checkbox'a göre)
  → apply_chart_font() → font, hover, crosshair, son 2 gün uzatma
     └─ turkce_tarih_ekseni() → Türkçe tarih ekseni
  → st.plotly_chart(fig, config=PLOTLY_CONFIG)
```

---

## 6. ANA UYGULAMA AKIŞI (altins1_app.py)

```
┌─ BAŞLATMA ────────────────────────────────────────────┐
│ 1. Logging kurulumu (console + file)                  │
│ 2. Streamlit sayfa config (wide layout, sidebar)      │
│ 3. PWA meta etiketleri                                │
│ 4. CSS enjeksiyonu (font, responsive, tab wrap)       │
└───────────────────────────────────────────────────────┘
        ↓
┌─ SİDEBAR ─────────────────────────────────────────────┐
│ • Yenile butonu (cache temizle + rerun)               │
│ • Son güncelleme tarihi + BIST durumu                 │
│ • Ayarlar: Font boyutu, grafik yüksekliği, kilidi    │
│ • Periyot seçici (1ay, 3ay, 6ay, 1yıl, 2yıl)        │
│ • Sinyal eşik sliderları                              │
│ • Piyasa verileri paneli (dinamik doldurulur)        │
└───────────────────────────────────────────────────────┘
        ↓
┌─ VERİ YÜKLEME (@st.cache_data, TTL=600s) ────────────┐
│ load_prices() → fetch_current_prices()               │
│ load_altins1_history() → Mynet tarihsel              │
│ load_history(period) → yfinance tarihsel             │
│ prepare_all_series() → Hizalanmış seriler            │
│ FALLBACK: API hata → load_prices_from_cache()        │
└───────────────────────────────────────────────────────┘
        ↓
┌─ BAŞLIK + SİNYAL GÖSTERGE ────────────────────────────┐
│ Renkli sinyal kutusu (yeşil→kırmızı)                 │
│ 3 metrik: ALTINS1 | %1 Gr | Makas %                  │
│ Piyasa verileri: Gram, Ons, Dolar, Çeyrek, Hacim     │
└───────────────────────────────────────────────────────┘
        ↓
┌─ 8 TAB ARAYÜZÜ ──────────────────────────────────────┐
│ Tab 1: 🎯 ALTINS1 Analizi (vs beklenen, EMA)         │
│ Tab 2: 📊 Makas Analizi (spread %, eşikler)          │
│ Tab 3: 📈 Normalize Karşılaştırma                    │
│ Tab 4: 🕯️ Ons Altın XAU/USD (mum grafik)            │
│ Tab 5: 🥇🥈 Altın vs Gümüş (dual Y-axis)            │
│ Tab 6: 📰 Haberler (RSS günlük/haftalık)             │
│ Tab 7: 🏦 Merkez Bankaları (rezervler + sinyaller)   │
│ Tab 8: 📖 Bilgi Rehberi                              │
└───────────────────────────────────────────────────────┘
        ↓
┌─ E-POSTA + FOOTER ────────────────────────────────────┐
│ SMTP ayarları, sinyal özeti gönderimi                 │
│ Footer: versiyon + sorumluluk reddi                   │
└───────────────────────────────────────────────────────┘
```

---

## 7. TASARIM KALIPLARI

| Kalıp | Açıklama |
|-------|----------|
| **Çok Katmanlı Cache** | Streamlit @cache_data (RAM, TTL=600s) + disk JSON fallback |
| **Dayanıklı Veri Çekme** | Truncgil JSON tamir, çoklu kaynak, hata loglama |
| **Merkezi Stil** | `apply_base_layout()` + `COLORS` dict + `apply_chart_font()` |
| **Config-Driven** | Tüm eşikler, URL'ler, sabitler `config.py`'den |
| **Bağımlılık Enjeksiyonu** | `apply_chart_font(fig, font_size, height, kilidi)` — global yok |
| **Tab Modül Deseni** | Her tab bağımsız modül, `TabContext` dataclass ile veri alır, `render()` ile çalışır |
| **Saf Sinyal Mantığı** | signal_engine + reserve_signals UI'dan bağımsız |
| **Türkçe Yerelleştirme** | Ay adları, hover, ülke isimleri, haber filtreleme |

---

## 8. KONFİGÜRASYON KAYNAKLARI

| Öncelik | Kaynak | Kullanım |
|---------|--------|----------|
| 1 | Ortam değişkenleri | EmailConfig |
| 2 | Streamlit secrets.toml | Altyapı hazır, aktif değil |
| 3 | config.py sabitleri | URL'ler, semboller, eşikler |
| 4 | Sidebar kullanıcı girişi | Font, yükseklik, periyot, eşikler |
| 5 | Disk cache | data/cache/*.json (otomatik) |
