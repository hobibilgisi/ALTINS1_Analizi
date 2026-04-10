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
    for attempt in range(3):
        try:
            r = requests.get(TRUNCGIL_API_URL, headers=_HEADERS, timeout=15)
            r.raise_for_status()
            # API bazen bozuk JSON döndürebiliyor — agresif temizleme
            text = r.text
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
    """Tüm güncel fiyatları toparlayarak döndürür.

    Kaynaklar:
      - mynet Finans  → ALTINS1 BIST gerçek fiyatı
      - truncgil API  → gram altın TL, dolar/TL, altın çeşitleri
      - yfinance      → ons altın USD (GC=F), dolar/TL teyidi (USDTRY=X)

    Returns dict with keys:
        altins1_fiyat, gram_altin_tl, ons_altin_usd, dolar_tl,
        beklenen_altins1, makas_pct, gram_altin_hesaplanan, ...
    """
    result: Dict[str, Any] = {}

    # ── 1) ALTINS1 BIST fiyatı + hacim (Mynet) ───────────────
    altins1_price, _ = fetch_altins1_mynet()
    result["altins1_fiyat"] = altins1_price
    volume_data = fetch_altins1_volume()
    result.update(volume_data)  # hacim_lot, hacim_tl

    # ── 2) Truncgil API ─────────────────────────────────────
    raw = fetch_truncgil()
    if raw:
        tp = parse_truncgil_prices(raw)
        result["gram_altin_tl"] = tp.get("gram_altin_satis")
        result["has_altin_tl"] = tp.get("has_altin_satis")
        result["dolar_tl"] = tp.get("dolar_tl_alis")
        result["ceyrek_altin"] = tp.get("ceyrek_altin_satis")
        result["yarim_altin"] = tp.get("yarim_altin_satis")
        result["tam_altin"] = tp.get("tam_altin_satis")
        result["update_date"] = tp.get("update_date", "")
        result["kaynak_truncgil"] = True
    else:
        result["kaynak_truncgil"] = False

    # ── 3) yfinance: ons altın + dolar/TL ───────────────────
    for key, symbol in YF_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                result[key] = float(hist["Close"].iloc[-1])
                logger.info(f"yfinance: {symbol} = {result[key]}")
            else:
                logger.warning(f"yfinance: {symbol} veri yok")
        except Exception as e:
            logger.error(f"yfinance hatası ({symbol}): {e}")

    # ── 4) Hesaplamalar ─────────────────────────────────────
    ons = result.get("ons_altin_usd")
    usdtry = result.get("dolar_tl")
    gram_tl = result.get("gram_altin_tl")

    # Hesaplanan gram altın (uluslararası referans)
    if ons and usdtry:
        result["gram_altin_hesaplanan"] = (ons * usdtry) / TROY_OUNCE_GRAM

    # Beklenen ALTINS1 = Gram Altın TL × 0.01
    if gram_tl:
        result["beklenen_altins1"] = gram_tl * ALTINS1_GRAM_KATSAYI

    # Makas (%)
    if altins1_price and gram_tl:
        beklenen = gram_tl * ALTINS1_GRAM_KATSAYI
        result["makas_pct"] = ((altins1_price - beklenen) / beklenen) * 100

    # Başarılı veri varsa disk cache'e yaz (mesai dışı kullanım için)
    if altins1_price and gram_tl:
        save_prices_to_cache(result)

    return result


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

def is_bist_open(now: Optional[datetime] = None) -> bool:
    """BIST seansının açık olup olmadığını kontrol eder.

    Hafta içi 10:00 - 18:10 arası açık.
    Hafta sonu (cumartesi=5, pazar=6) kapalı.
    Resmi tatil kontrolü yapılmaz (sadece gün/saat tabanlı).
    """
    if now is None:
        now = datetime.now()
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
        cache_data["_cache_time"] = datetime.now().isoformat()
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
    """Son N günün ortalama hacmini (lot) döndürür."""
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
