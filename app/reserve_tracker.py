"""
ALTINS1 Analiz — Merkez Bankası Altın Rezerv Takibi
Çin, ABD, Avrupa ve TC merkez bankalarının altın rezerv verilerini takip eder.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import RESERVE_SOURCES

logger = logging.getLogger(__name__)


@dataclass
class ReserveData:
    """Bir merkez bankasının altın rezerv kaydı."""
    country: str
    institution: str
    gold_tonnes: Optional[float] = None
    last_updated: Optional[str] = None
    change_tonnes: Optional[float] = None  # Önceki döneme göre değişim
    source_url: str = ""
    note: str = ""


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


def fetch_reserve_data() -> List[ReserveData]:
    """Mevcut merkez bankası altın rezerv verilerini toplar.

    Not: Bu fonksiyon Aşama 5'te tam implementasyona kavuşacak.
    Şu an kaynak bilgilerini ve yapıyı hazırlar.

    Returns:
        ReserveData listesi
    """
    # TODO: Aşama 5'te her merkez bankası için ayrı scraper/API entegrasyonu
    reserves = [
        ReserveData(
            country="Türkiye",
            institution="TCMB",
            source_url=RESERVE_SOURCES["TCMB"]["url"],
            note="Haftalık rezerv raporu — Aşama 5'te otomatik çekilecek",
        ),
        ReserveData(
            country="ABD",
            institution="US Treasury / Federal Reserve",
            source_url=RESERVE_SOURCES["FED"]["url"],
            note="TIC verileri — Aşama 5'te otomatik çekilecek",
        ),
        ReserveData(
            country="Avrupa",
            institution="ECB",
            source_url=RESERVE_SOURCES["ECB"]["url"],
            note="Euro System rezervleri — Aşama 5'te otomatik çekilecek",
        ),
        ReserveData(
            country="Çin",
            institution="PBoC / SAFE",
            source_url=RESERVE_SOURCES["PBOC"]["url"],
            note="Aylık rezerv raporu — Aşama 5'te otomatik çekilecek",
        ),
    ]
    return reserves
