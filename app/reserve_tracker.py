"""
ALTINS1 Analiz — Merkez Bankası Altın Rezerv Takibi
Wikipedia (IMF / World Gold Council kaynaklı) verilerinden
dünya merkez bankalarının altın rezervlerini çeker ve önbelleğe alır.
Günlük tarihsel kayıt tutarak değişim grafiği üretir.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.config import RESERVE_SOURCES

logger = logging.getLogger(__name__)

_CACHE_PATH = Path("data/cache/reserve_data.json")
_HISTORY_PATH = Path("data/cache/reserve_history.json")
_CACHE_TTL_SEC = 24 * 60 * 60  # 24 saat — rezerv verileri sık değişmez

# Öne çıkarılacak ülkeler (her zaman tablonun başında görünsün)
_HIGHLIGHT_COUNTRIES = [
    "Turkey", "United States", "China", "Germany", "Italy", "France",
    "Russia", "Switzerland", "India", "Japan",
]

_COUNTRY_TR = {
    "United States": "ABD",
    "Germany": "Almanya",
    "Italy": "İtalya",
    "France": "Fransa",
    "Russia": "Rusya",
    "China": "Çin",
    "Switzerland": "İsviçre",
    "India": "Hindistan",
    "Japan": "Japonya",
    "Turkey": "Türkiye",
    "Netherlands": "Hollanda",
    "Poland": "Polonya",
    "Taiwan": "Tayvan",
    "Uzbekistan": "Özbekistan",
    "Portugal": "Portekiz",
    "Kazakhstan": "Kazakistan",
    "Saudi Arabia": "Suudi Arabistan",
    "United Kingdom": "İngiltere",
    "Lebanon": "Lübnan",
    "Spain": "İspanya",
    "Austria": "Avusturya",
    "Thailand": "Tayland",
    "Belgium": "Belçika",
    "Azerbaijan": "Azerbaycan",
    "Singapore": "Singapur",
    "Iraq": "Irak",
    "Algeria": "Cezayir",
    "Brazil": "Brezilya",
    "South Korea": "Güney Kore",
    "International Monetary Fund": "IMF",
    "European Central Bank": "Avrupa Merkez Bankası",
    "Bank for International Settlements": "BIS",
}


@dataclass
class ReserveData:
    """Bir ülkenin altın rezerv kaydı."""
    rank: Optional[int] = None
    country: str = ""
    country_tr: str = ""
    gold_tonnes: Optional[float] = None
    pct_of_reserves: Optional[float] = None
    source: str = "Wikipedia (IMF/WGC)"


def _parse_float(text: str) -> Optional[float]:
    """'8,133.5' gibi virgüllü sayıları float'a çevirir."""
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _parse_pct(text: str) -> Optional[float]:
    """'84.2%' → 84.2"""
    cleaned = text.replace("%", "").replace(",", "").strip()
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _scrape_wikipedia() -> List[ReserveData]:
    """Wikipedia Gold reserve sayfasından tabloyu çeker."""
    url = "https://en.wikipedia.org/wiki/Gold_reserve"
    headers = {"User-Agent": "ALTINS1-Analiz/1.0 (educational project)"}

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # "Officially reported holdings" bölümündeki tabloyu bul
    table = None
    for t in soup.find_all("table", class_="wikitable"):
        header_text = t.get_text()[:200].lower()
        if "tonnes" in header_text or "gold" in header_text:
            table = t
            break

    if table is None:
        logger.warning("Wikipedia'da altın rezerv tablosu bulunamadı")
        return []

    results: List[ReserveData] = []
    rows = table.find_all("tr")

    for row in rows[1:]:  # ilk satır başlıklar
        cells = row.find_all(["td", "th"])
        if len(cells) < 4:
            continue

        rank_text = cells[0].get_text(strip=True)
        country_text = cells[1].get_text(strip=True)
        tonnes_text = cells[2].get_text(strip=True)
        pct_text = cells[3].get_text(strip=True)

        # "World" veya "Euro area" satırlarını atla
        if any(skip in country_text.lower() for skip in ["world", "euro area"]):
            continue

        rank = None
        if rank_text.isdigit():
            rank = int(rank_text)

        tonnes = _parse_float(tonnes_text)
        pct = _parse_pct(pct_text)

        if tonnes is None and pct is None:
            continue

        country_tr = _COUNTRY_TR.get(country_text, country_text)

        results.append(ReserveData(
            rank=rank,
            country=country_text,
            country_tr=country_tr,
            gold_tonnes=tonnes,
            pct_of_reserves=pct,
        ))

    logger.info(f"Wikipedia'dan {len(results)} ülke altın rezerv verisi çekildi")
    return results


def _load_cache() -> Optional[List[ReserveData]]:
    """Önbellekten veri yükle (TTL kontrolüyle)."""
    if not _CACHE_PATH.exists():
        return None
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        cached_at = data.get("cached_at", 0)
        if time.time() - cached_at > _CACHE_TTL_SEC:
            return None
        items = []
        for d in data.get("reserves", []):
            items.append(ReserveData(**d))
        return items
    except Exception as e:
        logger.warning(f"Önbellek okunamadı: {e}")
        return None


def _save_cache(reserves: List[ReserveData]) -> None:
    """Verileri önbelleğe kaydet."""
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "cached_at": time.time(),
            "cached_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "reserves": [asdict(r) for r in reserves],
        }
        _CACHE_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"Rezerv verileri önbelleğe kaydedildi ({len(reserves)} kayıt)")
    except Exception as e:
        logger.warning(f"Önbellek yazılamadı: {e}")


def fetch_reserve_data() -> List[ReserveData]:
    """Merkez bankası altın rezerv verilerini döndürür.

    Önce önbellekten dener, TTL dolmuşsa Wikipedia'dan çeker.
    """
    cached = _load_cache()
    if cached:
        logger.info("Rezerv verileri önbellekten yüklendi")
        return cached

    try:
        reserves = _scrape_wikipedia()
        if reserves:
            _save_cache(reserves)
            return reserves
    except Exception as e:
        logger.error(f"Wikipedia'dan veri çekilemedi: {e}")

    # Fallback: eski önbellek varsa süresi dolmuş olsa bile kullan
    if _CACHE_PATH.exists():
        try:
            data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
            return [ReserveData(**d) for d in data.get("reserves", [])]
        except Exception:
            pass

    return []


def get_cache_date() -> Optional[str]:
    """Önbellek tarihini döndürür."""
    if not _CACHE_PATH.exists():
        return None
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        return data.get("cached_date")
    except Exception:
        return None


def get_reserve_sources_info() -> List[Dict[str, str]]:
    """Takip edilen merkez bankası kaynaklarının bilgilerini döndürür."""
    result = []
    for code, source in RESERVE_SOURCES.items():
        result.append({
            "code": code,
            "name": source["name"],
            "url": source["url"],
            "update_freq": source["update_freq"],
        })
    return result


def get_highlighted_reserves(reserves: List[ReserveData]) -> List[ReserveData]:
    """Öne çıkarılan ülkeleri (Türkiye, ABD, Çin vb.) sırasıyla döndürür."""
    highlighted = []
    for name in _HIGHLIGHT_COUNTRIES:
        for r in reserves:
            if r.country == name:
                highlighted.append(r)
                break
    return highlighted


# ═══════════════════════════════════════════════════════════════
# TARİHSEL KAYIT ve DEĞİŞİM TAKİBİ
# ═══════════════════════════════════════════════════════════════

# Varsayılan grafik ülkeleri: ABD, Çin, Türkiye
_DEFAULT_CHART_COUNTRIES = [
    "ABD", "Çin", "Türkiye",
]

_PERIOD_LABELS = {
    "1a": "Son 1 Ay",
    "2a": "Son 2 Ay",
    "6a": "Son 6 Ay",
    "12a": "Son 12 Ay",
}

_PERIOD_DAYS = {
    "1a": 30,
    "2a": 60,
    "6a": 180,
    "12a": 365,
}


def _load_history() -> Dict:
    """Tarihsel veri dosyasını yükle."""
    if not _HISTORY_PATH.exists():
        return {}
    try:
        return json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Tarihsel veri okunamadı: {e}")
        return {}


def _save_history(history: Dict) -> None:
    """Tarihsel veri dosyasını kaydet."""
    try:
        _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _HISTORY_PATH.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"Tarihsel veri yazılamadı: {e}")


def save_daily_snapshot(reserves: List[ReserveData]) -> None:
    """Günün rezerv verisini tarihsel kayda ekler (günde 1 kez)."""
    if not reserves:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    history = _load_history()

    # Bugün zaten kaydedilmişse atla
    if today in history:
        return

    snapshot: Dict[str, Dict] = {}
    for r in reserves:
        if r.gold_tonnes is not None:
            snapshot[r.country_tr] = {
                "tonnes": r.gold_tonnes,
                "pct": r.pct_of_reserves,
                "rank": r.rank,
            }

    history[today] = snapshot
    _save_history(history)
    logger.info(f"Rezerv tarihsel kaydı eklendi: {today} ({len(snapshot)} ülke)")


def get_all_tracked_countries() -> List[str]:
    """Tarihsel veride kayıtlı tüm ülke isimlerini döndürür (Türkçe)."""
    from app.historical_reserves import HISTORICAL_RESERVES
    countries = set(HISTORICAL_RESERVES.keys())
    history = _load_history()
    for snapshot in history.values():
        countries.update(snapshot.keys())
    return sorted(countries)


def get_default_chart_countries() -> List[str]:
    """Varsayılan grafik ülkelerini döndürür."""
    return list(_DEFAULT_CHART_COUNTRIES)


def get_period_options() -> Dict[str, str]:
    """Periyot etiketlerini döndürür."""
    return dict(_PERIOD_LABELS)


def build_history_dataframe(
    countries: List[str],
    period_key: str = "1y",
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Seçili ülkeler ve periyot için tarihsel DataFrame döndürür.

    WGC/IMF IFS çeyreklik tarihsel verisi (2018+) ve
    günlük snapshot verisini birleştirir.

    Returns:
        (tonnes_df, pct_change_df) — tonnes ve % değişim DataFrame'leri.
        Tarih indeksli, ülke sütunlu.
    """
    from app.historical_reserves import HISTORICAL_RESERVES

    # --- 1) WGC çeyreklik tarihsel veriyi DataFrame'e çevir ---
    hist_rows = []
    # Tüm tarihleri topla
    all_hist_dates = set()
    for country_data in HISTORICAL_RESERVES.values():
        all_hist_dates.update(country_data.keys())

    for date_str in sorted(all_hist_dates):
        row = {"Tarih": date_str + "-01"}  # "2018-03" → "2018-03-01"
        for c in countries:
            if c in HISTORICAL_RESERVES and date_str in HISTORICAL_RESERVES[c]:
                row[c] = HISTORICAL_RESERVES[c][date_str]
            else:
                row[c] = None
        hist_rows.append(row)

    hist_df = pd.DataFrame(hist_rows)
    if not hist_df.empty:
        hist_df["Tarih"] = pd.to_datetime(hist_df["Tarih"])
        hist_df = hist_df.set_index("Tarih").sort_index()

    # --- 2) Günlük snapshot verisi ---
    history = _load_history()
    snap_rows = []
    for date_str in sorted(history.keys()):
        snap = history[date_str]
        row = {"Tarih": date_str}
        for c in countries:
            if c in snap:
                row[c] = snap[c]["tonnes"]
            else:
                row[c] = None
        snap_rows.append(row)

    snap_df = pd.DataFrame(snap_rows)
    if not snap_df.empty:
        snap_df["Tarih"] = pd.to_datetime(snap_df["Tarih"])
        snap_df = snap_df.set_index("Tarih").sort_index()

    # --- 3) İki veri kaynağını birleştir ---
    if hist_df.empty and snap_df.empty:
        return None, None
    elif hist_df.empty:
        df = snap_df
    elif snap_df.empty:
        df = hist_df
    else:
        # Birleştir: günlük veri çeyreklik veriden öncelikli
        # FutureWarning önleme: tamamen boş sütunları concat öncesi çıkar
        hist_df = hist_df.dropna(axis=1, how="all")
        snap_df = snap_df.dropna(axis=1, how="all")
        df = pd.concat([hist_df, snap_df])
        # Çakışan tarihlerde son gelen (snapshot) geçerli
        df = df[~df.index.duplicated(keep="last")]
        df = df.sort_index()

    # --- 4) Periyot filtresi ---
    days = _PERIOD_DAYS.get(period_key, 365)
    if days < 9999:
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        df = df[df.index >= cutoff]

    if df.empty:
        return None, None

    # Boşlukları önceki değerle doldur
    df = df.ffill()

    # % değişim: ilk kayıtlı güne göre
    if len(df) >= 1:
        first_valid = df.bfill().iloc[0]
        pct_df = ((df - first_valid) / first_valid * 100).round(2)
    else:
        pct_df = df.copy()

    return df, pct_df
