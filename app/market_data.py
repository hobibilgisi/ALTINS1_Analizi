"""
ALTINS1 Analiz -- Merkezi Veri Yonetimi (Single Source of Truth)

Tum dis kaynaklardan veri cekme ve hesaplama tek bir noktada yapilir.
Program genelinde kullanilan her fiyat/seri buradan dagitilir.

Mimari:
  fetch_market_data()          <-- tek giris noktasi
    +-- fetch_altins1_mynet()  -> altins1 anlik + tarihsel (TEK cagri)
    +-- fetch_truncgil()       -> piyasa fiyatlari (REFERANS)
    +-- yfinance (real-time)   -> ons USD, USDTRY, gumus, faiz
    +-- fetch_all_history()    -> tarihsel seriler
         |
    prepare_all_series()       -> grafik-hazir seriler
         |
    MarketData                 <-- tum program buradan okur

Kural: gram_gold_tl = ons_usd x usdtry / 31.1035 HER YERDE ayni formul.
       Truncgil fiyatlari yalnizca "piyasa referans" olarak gosterilir.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo

import pandas as pd

from app.config import TROY_OUNCE_GRAM, ALTINS1_GRAM_KATSAYI

logger = logging.getLogger(__name__)
_TZ_ISTANBUL = ZoneInfo("Europe/Istanbul")


@dataclass
class LivePrices:
    """Anlik fiyatlar -- tumu tek seferde cekilir ve AYNI formullerle hesaplanir.

    Kural: gram_gold_tl = ons_usd x usdtry / 31.1035  (her yerde ayni)

    Kategoriler:
      TEMEL   : Dis kaynaklardan cekilen ham degerler
      TURETILMIS: Temellerden HESAPLANAN (hic bir dis kaynak karistirilmaz)
      PIYASA  : Truncgil API'den gelen (yalnizca bilgi/referans amacli)
    """

    # -- Temel: Dis kaynaklardan cekilen --
    altins1: Optional[float] = None           # ALTINS1 BIST fiyati (Mynet)
    ons_usd: Optional[float] = None           # Ons altin USD (yfinance)
    usdtry: Optional[float] = None            # Dolar/TL (yfinance)
    ons_silver_usd: Optional[float] = None    # Ons gumus USD (yfinance)
    faiz_us10y: Optional[float] = None        # ABD 10Y faiz (yfinance)

    # -- Turetilmis: Temellerden HESAPLANAN --
    gram_gold_tl: Optional[float] = None      # = ons_usd x usdtry / 31.1035
    beklenen_altins1: Optional[float] = None   # = gram_gold_tl x 0.01
    makas_pct: Optional[float] = None          # = (altins1 - beklenen) / beklenen x 100

    # -- Piyasa Referans: Truncgil (yalnizca bilgi amacli) --
    piyasa_gram_altin: Optional[float] = None
    piyasa_has_altin: Optional[float] = None
    piyasa_dolar_tl: Optional[float] = None
    ceyrek_altin: Optional[float] = None
    yarim_altin: Optional[float] = None
    tam_altin: Optional[float] = None

    # -- Hacim & Meta --
    hacim_lot: Optional[float] = None
    hacim_tl: Optional[float] = None
    update_date: str = ""
    cache_time: str = ""
    kaynak_truncgil: bool = False

    def recalculate(self):
        """Turetilmis degerleri temel fiyatlardan yeniden hesaplar.

        Bu fonksiyon her zaman AYNI formulleri kullanir:
          gram_gold_tl   = ons_usd x usdtry / TROY_OUNCE_GRAM
          beklenen_altins1 = gram_gold_tl x ALTINS1_GRAM_KATSAYI
          makas_pct      = (altins1 - beklenen) / beklenen x 100
        """
        if self.ons_usd and self.usdtry:
            self.gram_gold_tl = (self.ons_usd * self.usdtry) / TROY_OUNCE_GRAM
        if self.gram_gold_tl:
            self.beklenen_altins1 = self.gram_gold_tl * ALTINS1_GRAM_KATSAYI
        if self.altins1 and self.beklenen_altins1 and self.beklenen_altins1 != 0:
            self.makas_pct = (
                (self.altins1 - self.beklenen_altins1) / self.beklenen_altins1
            ) * 100


@dataclass
class MarketData:
    """Programin TEK veri kaynagi. Tum moduller buradan okur.

    Attributes:
        live: Anlik fiyatlar (tek seferde cekilmis ve tutarli)
        series: Grafik-hazir tarihsel seriler (PreparedSeries)
        altins1_hist_raw: Mynet'ten gelen ham ALTINS1 tarihsel DataFrame
        history_raw: yfinance'den gelen ham tarihsel DataFrames
    """

    live: LivePrices = field(default_factory=LivePrices)
    series: Any = None  # PreparedSeries -- set after import
    altins1_hist_raw: Optional[pd.DataFrame] = None
    history_raw: Dict[str, Optional[pd.DataFrame]] = field(default_factory=dict)


def fetch_market_data(period: str = "1y") -> MarketData:
    """Tum verileri tek seferde ceker ve TUTARLI bir MarketData doner.

    Bu fonksiyon, programin DIS DUNYAYLA TEK TEMAS NOKTASIDIR.
    Hicbir baska modul dogrudan dis kaynaga erismemelidir.

    Args:
        period: Tarihsel veri periyodu (yfinance formati: "1mo", "3mo", "1y" vb.)

    Returns:
        MarketData: Tum anlik ve tarihsel verileri iceren tek nesne.
    """
    from app.data_fetcher import (
        fetch_altins1_mynet,
        fetch_altins1_volume,
        fetch_truncgil,
        parse_truncgil_prices,
        fetch_all_history,
        load_prices_from_cache,
        save_prices_to_cache,
    )
    from app.data_preparer import prepare_all_series
    from app.config import YF_SYMBOLS

    import yfinance as yf

    data = MarketData()
    live = data.live

    # == 1) ALTINS1 (Mynet) -- TEK cagri, hem fiyat hem tarihsel ==
    altins1_price, altins1_hist = fetch_altins1_mynet()
    live.altins1 = altins1_price
    data.altins1_hist_raw = altins1_hist

    # == 2) Hacim (Mynet) ==
    volume_data = fetch_altins1_volume()
    live.hacim_lot = volume_data.get("hacim_lot")
    live.hacim_tl = volume_data.get("hacim_tl")

    # == 3) Truncgil -- piyasa fiyatlari (YALNIZCA REFERANS) ==
    raw_truncgil = fetch_truncgil()
    if raw_truncgil:
        tp = parse_truncgil_prices(raw_truncgil)
        live.piyasa_gram_altin = tp.get("gram_altin_satis")
        live.piyasa_has_altin = tp.get("has_altin_satis")
        live.piyasa_dolar_tl = tp.get("dolar_tl_alis")
        live.ceyrek_altin = tp.get("ceyrek_altin_satis")
        live.yarim_altin = tp.get("yarim_altin_satis")
        live.tam_altin = tp.get("tam_altin_satis")
        live.update_date = tp.get("update_date", "")
        live.kaynak_truncgil = True

    # == 4) yfinance anlik -- TEMEL fiyatlar ==
    _yf_realtime = {"ons_altin_usd", "ons_gumus_usd", "dolar_tl", "faiz_us10y"}
    _yf_live: Dict[str, float] = {}
    for key, symbol in YF_SYMBOLS.items():
        if key not in _yf_realtime:
            continue
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                _yf_live[key] = float(hist["Close"].iloc[-1])
                logger.info(f"yfinance live: {symbol} = {_yf_live[key]}")
            else:
                logger.warning(f"yfinance live: {symbol} veri yok")
        except Exception as e:
            logger.error(f"yfinance live hatasi ({symbol}): {e}")

    live.ons_usd = _yf_live.get("ons_altin_usd")
    live.usdtry = _yf_live.get("dolar_tl")
    live.ons_silver_usd = _yf_live.get("ons_gumus_usd")
    live.faiz_us10y = _yf_live.get("faiz_us10y")

    # == 5) Turetilmis degerleri hesapla (TEK FORMUL) ==
    live.recalculate()

    # == 6) Disk cache'den eksik kritik alanlari tamamla ==
    _critical = {
        "altins1": live.altins1,
        "ons_usd": live.ons_usd,
        "usdtry": live.usdtry,
    }
    _missing = [k for k, v in _critical.items() if not v]
    if _missing:
        cached = load_prices_from_cache()
        if cached:
            if not live.altins1 and cached.get("altins1_fiyat"):
                live.altins1 = cached["altins1_fiyat"]
                logger.info(f"cache'den tamamlandi: altins1={live.altins1}")
            if not live.ons_usd and cached.get("ons_altin_usd"):
                live.ons_usd = cached["ons_altin_usd"]
                logger.info(f"cache'den tamamlandi: ons_usd={live.ons_usd}")
            if not live.usdtry and cached.get("dolar_tl"):
                live.usdtry = cached["dolar_tl"]
                logger.info(f"cache'den tamamlandi: usdtry={live.usdtry}")
            # Cache'den tamamlanan degerlerle yeniden hesapla
            live.recalculate()

    # == 7) Tarihsel veriler (yfinance) ==
    data.history_raw = fetch_all_history(period=period)

    # == 8) Serileri hazirla (TEK kaynak: yfinance + Mynet) ==
    data.series = prepare_all_series(
        history=data.history_raw,
        altins1_hist=data.altins1_hist_raw,
        live=live,
    )

    # == 9) Basarili veri varsa cache'e yaz ==
    if live.altins1 and live.gram_gold_tl:
        _cache_dict = {
            "altins1_fiyat": live.altins1,
            "gram_altin_tl": live.gram_gold_tl,
            "ons_altin_usd": live.ons_usd,
            "dolar_tl": live.usdtry,
            "beklenen_altins1": live.beklenen_altins1,
            "makas_pct": live.makas_pct,
            "hacim_lot": live.hacim_lot,
        }
        save_prices_to_cache(_cache_dict)
        live.cache_time = datetime.now(_TZ_ISTANBUL).isoformat()

    return data
