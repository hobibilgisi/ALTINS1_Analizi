"""
ALTINS1 Analiz — Konfigürasyon Ayarları
Tüm sabitler, eşik değerleri ve kaynak tanımları burada tutulur.
"""

from dataclasses import dataclass, field
from typing import Dict, List

# ── Versiyon Bilgisi (SemVer: MAJOR.MINOR.PATCH) ──────────────
# MAJOR: Köklü değişiklik (eski ile uyumsuz)
# MINOR: Yeni özellik (geriye uyumlu)
# PATCH: Hata düzeltme
APP_VERSION = "1.3.0"
APP_VERSION_DATE = "2026-04-13"
APP_VERSION_NOTES = [
    "Tab modül refactoring — her tab bağımsız modül (app/tabs/)",
    "altins1_app.py orkestratöre dönüştürüldü (~1700 → 555 satır)",
    "Type hints eklendi (ui_helpers + tab modülleri)",
    "Mobil UX iyileştirmeleri (legend, tab wrap, rezerv grafiği)",
    "SemVer versiyon sistemi eklendi",
]

# ── Troy Ounce sabiti ──────────────────────────────────────────
TROY_OUNCE_GRAM = 31.1035

# ── BIST Seans Saatleri ────────────────────────────────────────
# BIST seans: Hafta içi 10:00 - 18:10 (Türkiye saati)
BIST_OPEN_HOUR = 10
BIST_OPEN_MINUTE = 0
BIST_CLOSE_HOUR = 18
BIST_CLOSE_MINUTE = 10

# ── ALTINS1 Sertifika katsayısı ───────────────────────────────
# ALTINS1 = 0.01 gram altın sertifikası
# Beklenen fiyat = Gram Altın TL × ALTINS1_GRAM_KATSAYI
ALTINS1_GRAM_KATSAYI = 0.01

# ── Mynet Finans (ALTINS1 BIST fiyatı + tarihsel veri) ────────
MYNET_ALTINS1_URL = "https://finans.mynet.com/borsa/hisseler/altins1-altin-sertifikasi/"

# ── Truncgil API (Birincil: Türk piyasası anlık fiyatları) ────
TRUNCGIL_API_URL = "https://finans.truncgil.com/v4/today.json"
TRUNCGIL_KEYS = {
    "gram_altin": "GRA",           # Gram Altın TL (piyasa fiyatı)
    "has_altin": "HAS",            # Has (saf) altın TL
    "dolar_tl": "USD",             # Dolar/TL
    "ons_altin": "ONS",            # Ons altın (bazen boş olabiliyor)
    "ceyrek_altin": "CEYREKALTIN",
    "yarim_altin": "YARIMALTIN",
    "tam_altin": "TAMALTIN",
}

# ── Yahoo Finance sembolleri (Tarihsel veri) ───────────────────
YF_SYMBOLS = {
    "ons_altin_usd": "GC=F",      # Gold Futures (USD)
    "ons_gumus_usd": "SI=F",      # Silver Futures (USD)
    "dolar_tl": "USDTRY=X",       # USD/TRY
    "faiz_us10y": "^TNX",         # ABD 10 Yıllık Tahvil Faizi (%)
}

# ── TradingView sembolleri (Tarihsel + yedek) ──────────────────
TV_SYMBOLS = {
    "ons_altin_usd": {"symbol": "XAUUSD", "exchange": "OANDA"},
    "dolar_tl": {"symbol": "USDTRY", "exchange": "FX_IDC"},
    # BIST:ALTINS1 nologin modunda erişilemiyor; login eklenirse aktifleşir
    # "altins1": {"symbol": "ALTINS1", "exchange": "BIST"},
}

# ── Sinyal eşik değerleri (%) ──────────────────────────────────
@dataclass
class SignalThresholds:
    """Makas analizi eşik değerleri (yüzde olarak).

    Makas = (Gerçek ALTINS1 - Beklenen ALTINS1) / Beklenen ALTINS1 × 100
    Beklenen ALTINS1 = Gram Altın TL × 0.01
    """
    strong_buy: float = 5.0        # Makas ≤ %5 → GÜÇLÜ ALIM (çok yakınsamış)
    buy_threshold: float = 15.0    # Makas ≤ %15 → ALIM SİNYALİ
    sell_threshold: float = 35.0   # Makas ≥ %35 → SATIM SİNYALİ
    strong_sell: float = 50.0      # Makas ≥ %50 → GÜÇLÜ SATIM


# ── TCMB EVDS API ─────────────────────────────────────────────
TCMB_EVDS_BASE_URL = "https://evds2.tcmb.gov.tr/service/evds"
TCMB_EVDS_API_KEY = ""  # Kullanıcı kendi API anahtarını girmeli

# ── RSS Haber Kaynakları ───────────────────────────────────────
RSS_FEEDS: List[Dict[str, str]] = [
    {"name": "Bloomberg HT",    "url": "https://www.bloomberght.com/rss"},
    {"name": "Dünya Gazetesi",   "url": "https://www.dunya.com/rss"},
    {"name": "Investing.com TR", "url": "https://tr.investing.com/rss/news.rss"},
]

# Haber filtreleme anahtar kelimeleri (günlük)
NEWS_KEYWORDS = [
    "altın", "gold", "ons", "merkez bankası", "central bank",
    "rezerv", "reserve", "dolar", "fed", "ecb", "tcmb",
    "faiz", "enflasyon", "altin", "kıymetli maden",
]

# Haftalık haber anahtar kelimeleri (daha geniş kapsam)
NEWS_KEYWORDS_WEEKLY = [
    # Altın & değerli metaller
    "altın", "gold", "ons", "altin", "kıymetli maden", "gümüş", "silver",
    # Döviz & kur
    "dolar", "euro", "döviz", "kur", "forex", "usd", "eur", "tl",
    # Merkez bankaları & para politikası
    "merkez bankası", "central bank", "tcmb", "fed", "ecb",
    "rezerv", "reserve", "faiz", "interest rate",
    "enflasyon", "inflation", "deflasyon",
    "parasal sıkılaştırma", "parasal genişleme",
    # Jeopolitik
    "iran", "savaş", "war", "ukrayna", "ukraine", "rusya", "russia",
    "İsrail", "israel", "ortadoğu", "middle east", "nato",
    "gerilim", "çatışma", "saldırı", "ambargo", "yaptırım", "sanction",
    # Ekonomi
    "büyüme", "gdp", "gsyih", "resesyon", "recession",
    "istihdam", "işsizlik", "unemployment",
    "petrol", "oil", "enerji", "energy", "brent",
    "borsa", "bist", "s&p", "nasdaq", "endeks",
]

# ── Merkez Bankası Altın Rezerv Kaynakları ─────────────────────
RESERVE_SOURCES = {
    "TCMB": {
        "name": "Türkiye Cumhuriyet Merkez Bankası",
        "url": "https://www.tcmb.gov.tr",
        "update_freq": "Haftalık",
    },
    "FED": {
        "name": "US Treasury / Federal Reserve",
        "url": "https://home.treasury.gov",
        "update_freq": "Aylık",
    },
    "ECB": {
        "name": "European Central Bank",
        "url": "https://www.ecb.europa.eu",
        "update_freq": "Haftalık",
    },
    "PBOC": {
        "name": "People's Bank of China (SAFE)",
        "url": "https://www.safe.gov.cn",
        "update_freq": "Aylık",
    },
    "IMF": {
        "name": "International Monetary Fund (IFS)",
        "url": "https://data.imf.org",
        "update_freq": "Aylık",
    },
    "WGC": {
        "name": "World Gold Council",
        "url": "https://www.gold.org/goldhub/data",
        "update_freq": "Çeyreklik",
    },
}

# ── Uygulama Ayarları ─────────────────────────────────────────
@dataclass
class AppConfig:
    """Genel uygulama ayarları."""
    page_title: str = "ALTINS1 Analiz"
    page_icon: str = "🪙"
    refresh_interval_sec: int = 60       # Veri yenileme aralığı (saniye)
    history_days: int = 365              # Tarihsel veri çekme süresi (gün)
    cache_ttl_sec: int = 300             # Önbellek süresi (saniye)
    price_cache_file: str = "data/cache/last_prices.json"  # Son geçerli fiyat dosyası
    log_file: str = "logs/app.log"


# ── E-posta Bildirim Ayarları ──────────────────────────────────
@dataclass
class EmailConfig:
    """SMTP e-posta gönderim ayarları.

    Hassas bilgiler ortam değişkenlerinden okunur:
        ALTINS1_SMTP_SERVER, ALTINS1_SMTP_PORT,
        ALTINS1_SENDER_EMAIL, ALTINS1_SENDER_PASSWORD,
        ALTINS1_RECIPIENTS (virgülle ayrılmış)
    """
    smtp_server: str = ""
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipients: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Ortam değişkenlerinden EmailConfig oluşturur."""
        import os
        recipients_str = os.environ.get("ALTINS1_RECIPIENTS", "")
        recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
        return cls(
            smtp_server=os.environ.get("ALTINS1_SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.environ.get("ALTINS1_SMTP_PORT", "587")),
            sender_email=os.environ.get("ALTINS1_SENDER_EMAIL", ""),
            sender_password=os.environ.get("ALTINS1_SENDER_PASSWORD", ""),
            recipients=recipients,
        )
