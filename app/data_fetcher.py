"""
ALTINS1 Analiz — Veri Çekme Modülü

Veri kaynak hiyerarşisi:
  ALTINS1 BIST    → Mynet Finans (anlık + tarihsel chart data)
  Anlık fiyatlar  → truncgil API (gram altın TL, dolar/TL, altın çeşitleri)
  Tarihsel veri   → yfinance (ons altın USD, USD/TRY)  →  yedek: tvDatafeed

Hesaplama:
  Beklenen ALTINS1 = Gram Altın TL × 0.01  (0.01 gr sertifika)
  Makas (%) = (Gerçek ALTINS1 - Beklenen) / Beklenen × 100
"""

import json
import logging
import os
import re
from datetime import datetime, time
from typing import Optional, Dict, Any, List, Tuple
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup

from app.config import (
    MYNET_ALTINS1_URL,
    TRUNCGIL_API_URL,
    TRUNCGIL_KEYS,
    YF_SYMBOLS,
    TV_SYMBOLS,
    TROY_OUNCE_GRAM,
    ALTINS1_GRAM_KATSAYI,
    BIST_OPEN_HOUR,
    BIST_OPEN_MINUTE,
    BIST_CLOSE_HOUR,
    BIST_CLOSE_MINUTE,
    AppConfig,
)

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36",
}


# ── Mynet Finans: ALTINS1 BIST (Anlık + Tarihsel) ─────────────

def _parse_tr_number(text: str) -> Optional[float]:
    """Türkçe formatlı sayıyı float'a çevirir. '12.027.303,00' → 12027303.0"""
    text = text.strip().replace(".", "").replace(",", ".")
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def fetch_altins1_mynet() -> Tuple[Optional[float], Optional[pd.DataFrame]]:
    """Mynet Finans'tan ALTINS1 anlık fiyat ve tarihsel chart verisini çeker.

    Returns:
        (current_price, history_df)
        - current_price: Güncel ALTINS1 TL fiyatı (float) veya None
        - history_df: Tarihsel DataFrame (Date index, Close, High, Low) veya None
    """
    try:
        r = requests.get(MYNET_ALTINS1_URL, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # ── Anlık fiyat: class="unit-price" ──
        current_price = None
        price_el = soup.find(class_="unit-price")
        if price_el:
            price_text = price_el.text.strip().split("\n")[0].strip()
            # Türkçe format: "82,33" → 82.33
            price_text = price_text.replace(".", "").replace(",", ".")
            try:
                current_price = float(price_text)
                logger.info(f"mynet ALTINS1 anlık: {current_price} TL")
            except ValueError:
                logger.warning(f"mynet ALTINS1 fiyat parse hatası: {price_text}")

        # ── Tarihsel chart verisi: initChartData({...}) ──
        history_df = None
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "initChartData" in txt:
                match = re.search(r"initChartData\((\{.*?\})\)", txt, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    bars = data.get("data", [])
                    if bars:
                        rows = []
                        for bar in bars:
                            ts = datetime.fromtimestamp(bar[0] / 1000)
                            rows.append({
                                "Date": ts,
                                "Close": float(bar[1]),
                                "High": float(bar[2]),
                                "Low": float(bar[3]),
                            })
                        history_df = pd.DataFrame(rows)
                        history_df.set_index("Date", inplace=True)
                        # Gün bazında son değeri al (gün içi çakışmaları temizle)
                        history_df = history_df.groupby(history_df.index.date).last()
                        history_df.index = pd.DatetimeIndex(history_df.index)
                        history_df.index.name = "Date"
                        logger.info(f"mynet ALTINS1 tarihsel: {len(history_df)} bar")
                break

        return current_price, history_df

    except Exception as e:
        logger.error(f"mynet ALTINS1 hatası: {e}")
        return None, None


def fetch_altins1_volume() -> Dict[str, Any]:
    """Mynet Finans'tan ALTINS1 hacim ve takas verisini çeker."""
    result: Dict[str, Any] = {}
    try:
        r = requests.get(MYNET_ALTINS1_URL, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # "Günlük Hacim (Lot)" ve "Günlük Hacim (TL)" etiketlerini bul
        for span in soup.find_all("span"):
            text = span.get_text(strip=True)
            parent = span.parent
            if parent is None:
                continue
            parent_text = parent.get_text(strip=True)

            if "Hacim (Lot)" in text:
                val_text = parent_text.replace(text, "").strip()
                result["hacim_lot"] = _parse_tr_number(val_text)
            elif "Hacim (TL)" in text:
                val_text = parent_text.replace(text, "").strip()
                result["hacim_tl"] = _parse_tr_number(val_text)

        if result:
            logger.info(f"mynet ALTINS1 hacim: lot={result.get('hacim_lot')}, tl={result.get('hacim_tl')}")
    except Exception as e:
        logger.error(f"mynet ALTINS1 hacim hatası: {e}")
    return result


# ── Truncgil API (Anlık Türk piyasası verileri) ───────────────

def _repair_truncated_json(text: str) -> str:
    """Kesilmiş (truncated) JSON yanıtını kapatılmamış parantezleri tamamlayarak onarır."""
    # Son tamamlanmamış key-value çiftini kes
    # Örn: ..."Change":3.9  → son tamamlanmamış değeri bul ve kes
    last_brace = text.rfind("}")
    if last_brace == -1:
        return text
    # Son kapanan }'den sonrasını kontrol et
    after = text[last_brace + 1:].strip()
    if after:
        # Son }'den sonra eksik veri var — onu kes
        text = text[:last_brace + 1]
    # Açık/kapalı parantez sayısını dengele
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    text += "}" * open_braces + "]" * open_brackets
    return text


def fetch_truncgil() -> Optional[Dict[str, Any]]:
    """finans.truncgil.com API'sinden anlık altın ve döviz verilerini çeker.

    Returns:
        Ham API yanıtı (dict) veya None
    """
    session = requests.Session()
    session.headers.update(_HEADERS)
    for attempt in range(3):
        try:
            r = session.get(TRUNCGIL_API_URL, timeout=10)
            r.raise_for_status()
            # API bazen bozuk JSON döndürebiliyor — agresif temizleme
            text = r.text
            if not text or len(text) < 100:
                logger.warning(f"truncgil: çok kısa yanıt ({len(text)} byte), tekrar deniyor")
                continue
            text = re.sub(r",\s*}", "}", text)
            text = re.sub(r",\s*]", "]", text)
            text = re.sub(r"}\s*{", "},{", text)  # missing comma between objects
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # Truncated (kesilmiş) JSON onarımı
                text = _repair_truncated_json(text)
                try:
                    data = json.loads(text)
                    logger.warning("truncgil: kesilmiş JSON onarıldı")
                except json.JSONDecodeError:
                    # Son çare: geçersiz karakterleri temizle
                    text = re.sub(r'[^\x20-\x7E\xC0-\xFF{}[\]:,."\'\\ığüşöçİĞÜŞÖÇ\s]', '', text)
                    data = json.loads(text)
            logger.info(f"truncgil: veri çekildi ({data.get('Update_Date', '?')})")
            # Kritik veri kontrolü — JSON onarılmış ama GRA eksik olabilir
            if "GRA" not in data:
                logger.warning("truncgil: JSON onarıldı ama GRA anahtarı eksik, tekrar deniyor")
                continue
            return data
        except Exception as e:
            logger.warning(f"truncgil API deneme {attempt + 1}/3 başarısız: {e}")
    logger.error("truncgil API: 3 deneme de başarısız")
    return None


def parse_truncgil_prices(raw: Dict[str, Any]) -> Dict[str, float]:
    """Truncgil ham verisinden işlenmiş fiyatları çıkarır.

    Returns:
        {
            "gram_altin_alis": float,   # GRA Alış
            "gram_altin_satis": float,  # GRA Satış
            "has_altin_alis": float,
            "has_altin_satis": float,
            "dolar_tl_alis": float,
            "dolar_tl_satis": float,
            "ceyrek_altin_alis": float,
            "ceyrek_altin_satis": float,
            ...
            "update_date": str,
        }
    """
    prices = {}
    for label, key in TRUNCGIL_KEYS.items():
        item = raw.get(key)
        if isinstance(item, dict):
            buy_val = item.get("Buying")
            sell_val = item.get("Selling")
            if buy_val is not None:
                try:
                    prices[f"{label}_alis"] = float(buy_val)
                except (ValueError, TypeError):
                    pass
            if sell_val is not None:
                try:
                    prices[f"{label}_satis"] = float(sell_val)
                except (ValueError, TypeError):
                    pass
    prices["update_date"] = raw.get("Update_Date", "")
    return prices


def fetch_current_prices() -> Dict[str, Any]:
    """Legacy uyumluluk sarmalayıcısı.

    Yeni mimaride güncel fiyatlar `fetch_market_data()` ile üretilen
    `MarketData.current` üstünden çözülür. Bu fonksiyon sadece eski çağrılar
    için düz sözlük görünümü döndürür.
    """
    from app.market_data import fetch_market_data

    logger.info("fetch_current_prices() legacy sarmalayıcı olarak MarketData.current kullanıyor")

    market = fetch_market_data(period="1mo")
    current = market.current

    return {
        "altins1_fiyat": current.altins1,
        "gram_altin_tl": current.gram_gold_tl,
        "ons_altin_usd": current.ons_usd,
        "ons_gumus_usd": current.ons_silver_usd,
        "dolar_tl": current.usdtry,
        "has_altin_tl": current.piyasa_has_altin,
        "ceyrek_altin": current.ceyrek_altin,
        "yarim_altin": current.yarim_altin,
        "tam_altin": current.tam_altin,
        "beklenen_altins1": current.beklenen_altins1,
        "makas_pct": current.makas_pct,
        "gram_altin_hesaplanan": current.gram_gold_tl,
        "update_date": current.update_date,
        "kaynak_truncgil": current.kaynak_truncgil,
        "hacim_lot": current.hacim_lot,
        "hacim_tl": current.hacim_tl,
        "_cache_time": current.cache_time,
    }


# ── yfinance: Tarihsel veri ────────────────────────────────────

def fetch_yfinance_history(
    symbol: str, period: str = "1y", interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """Yahoo Finance'den OHLCV tarihsel veri çeker."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            logger.warning(f"yfinance tarihsel: {symbol} boş")
            return None
        logger.info(f"yfinance tarihsel: {symbol} — {len(df)} satır")
        return df
    except Exception as e:
        logger.error(f"yfinance tarihsel hatası ({symbol}): {e}")
        return None


def fetch_all_history(period: str = "1y", interval: str = "1d") -> Dict[str, Optional[pd.DataFrame]]:
    """Ons altın ve dolar/TL için tarihsel veri çeker.

    Returns:
        {"ons_altin_usd": DataFrame, "dolar_tl": DataFrame}
    """
    history = {}
    for key, symbol in YF_SYMBOLS.items():
        df = fetch_yfinance_history(symbol, period=period, interval=interval)
        history[key] = df
    return history


# ── tvDatafeed: Tarihsel yedek ─────────────────────────────────

def fetch_tv_history(
    symbol: str, exchange: str, n_bars: int = 365
) -> Optional[pd.DataFrame]:
    """TradingView'dan tarihsel veri çeker (yedek kaynak).

    tvDatafeed nologin modunda çalışır; BIST verileri kısıtlı olabilir.
    """
    try:
        from tvDatafeed import TvDatafeed, Interval

        tv = TvDatafeed()
        df = tv.get_hist(
            symbol=symbol, exchange=exchange,
            interval=Interval.in_daily, n_bars=n_bars,
        )
        if df is not None and not df.empty:
            logger.info(f"tvDatafeed: {exchange}:{symbol} — {len(df)} bar")
            return df
        logger.warning(f"tvDatafeed: {exchange}:{symbol} veri yok")
        return None
    except Exception as e:
        logger.error(f"tvDatafeed hatası ({exchange}:{symbol}): {e}")
        return None


# ── BIST Seans Durumu ──────────────────────────────────────────

_TZ_ISTANBUL = ZoneInfo("Europe/Istanbul")


def is_bist_open(now: Optional[datetime] = None) -> bool:
    """BIST seansının açık olup olmadığını kontrol eder.

    Hafta içi 10:00 - 18:10 arası açık (Türkiye saati).
    Hafta sonu (cumartesi=5, pazar=6) kapalı.
    Resmi tatil kontrolü yapılmaz (sadece gün/saat tabanlı).
    """
    if now is None:
        now = datetime.now(_TZ_ISTANBUL)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=_TZ_ISTANBUL)
    # Hafta sonu kapalı
    if now.weekday() >= 5:
        return False
    open_time = time(BIST_OPEN_HOUR, BIST_OPEN_MINUTE)
    close_time = time(BIST_CLOSE_HOUR, BIST_CLOSE_MINUTE)
    return open_time <= now.time() <= close_time


# ── Son Geçerli Fiyat Cache (Disk) ────────────────────────────

_config = AppConfig()
_PRICE_CACHE_PATH = _config.price_cache_file


def save_prices_to_cache(prices: Dict[str, Any]) -> None:
    """Son geçerli fiyatları JSON dosyasına kaydeder."""
    try:
        os.makedirs(os.path.dirname(_PRICE_CACHE_PATH), exist_ok=True)
        cache_data = {
            k: v for k, v in prices.items()
            if isinstance(v, (int, float, str, bool, type(None)))
        }
        cache_data["_cache_time"] = datetime.now(_TZ_ISTANBUL).isoformat()
        with open(_PRICE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        logger.info("Fiyat cache dosyasına kaydedildi")

        # Hacim geçmişini de kaydet (aylık ortalama hesabı için)
        hacim = prices.get("hacim_lot")
        if hacim:
            _save_volume_history(hacim)
    except Exception as e:
        logger.error(f"Fiyat cache yazma hatası: {e}")


def load_prices_from_cache() -> Optional[Dict[str, Any]]:
    """Disk cache'den son geçerli fiyatları yükler."""
    try:
        if not os.path.exists(_PRICE_CACHE_PATH):
            return None
        with open(_PRICE_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cache_time = data.pop("_cache_time", None)
        if cache_time:
            data["_cache_time"] = cache_time
        logger.info(f"Fiyat cache okundu (kayıt: {cache_time})")
        return data
    except Exception as e:
        logger.error(f"Fiyat cache okuma hatası: {e}")
        return None


# ── Hacim Geçmişi (Aylık Ortalama Hesabı) ─────────────────────

_VOLUME_HISTORY_PATH = os.path.join(os.path.dirname(_PRICE_CACHE_PATH), "volume_history.json")


def _save_volume_history(hacim_lot: float) -> None:
    """Günlük hacim verisini tarih bazlı JSON dosyasına ekler."""
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        os.makedirs(os.path.dirname(_VOLUME_HISTORY_PATH), exist_ok=True)
        data = {}
        if os.path.exists(_VOLUME_HISTORY_PATH):
            with open(_VOLUME_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[today] = hacim_lot
        # Son 90 günü tut, eskilerini sil
        cutoff = (datetime.now() - pd.Timedelta(days=90)).strftime("%Y-%m-%d")
        data = {k: v for k, v in data.items() if k >= cutoff}
        with open(_VOLUME_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Hacim geçmişi yazma hatası: {e}")


def load_volume_avg(days: int = 30) -> Optional[float]:
    """Son N günün ortalama hacmini (lot) döndürür — yerel cache'den."""
    try:
        if not os.path.exists(_VOLUME_HISTORY_PATH):
            return None
        with open(_VOLUME_HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return None
        cutoff = (datetime.now() - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
        recent = [v for k, v in data.items() if k >= cutoff and v]
        if not recent:
            return None
        return sum(recent) / len(recent)
    except Exception as e:
        logger.error(f"Hacim geçmişi okuma hatası: {e}")
        return None


def fetch_volume_avg_yf(days: int = 30) -> Optional[float]:
    """yfinance'den ALTINS1.IS tarihsel hacim verisini çekip günlük ortalama döndürür.

    Lot cinsinden hacim ALTINS1.IS'de Volume alanında tutulur.
    Başarısız olursa yerel cache'e düşer.
    """
    try:
        ticker = yf.Ticker("ALTINS1.IS")
        hist = ticker.history(period=f"{days}d", interval="1d")
        if hist.empty or "Volume" not in hist.columns:
            logger.warning("yfinance ALTINS1.IS hacim verisi yok, yerel cache'e düşülüyor")
            return load_volume_avg(days)
        vol = hist["Volume"].dropna()
        vol = vol[vol > 0]
        if vol.empty:
            return load_volume_avg(days)
        avg = float(vol.mean())
        logger.info(f"yfinance ALTINS1.IS {days}g ort. hacim: {avg:,.0f} lot ({len(vol)} gün)")
        return avg
    except Exception as e:
        logger.error(f"yfinance ALTINS1.IS hacim hatası: {e}")
        return load_volume_avg(days)
