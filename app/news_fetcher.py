"""
ALTINS1 Analiz — Haber Çekme Modülü
RSS beslemelerinden ve BigPara scraper'dan altın/finans haberleri çeker ve filtreler.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

import feedparser
import requests
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime

from app.config import RSS_FEEDS, NEWS_KEYWORDS, NEWS_KEYWORDS_WEEKLY

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
}
_BIGPARA_BASE = "https://bigpara.hurriyet.com.tr"
_BIGPARA_ALTIN_URL = "https://bigpara.hurriyet.com.tr/altin/haber/"

logger = logging.getLogger(__name__)

# Spor haberleri hariç tutma anahtar kelimeleri
_EXCLUDE_KEYWORDS = [
    "futbol", "süper lig", "şampiyonlar ligi", "champions league",
    "basketbol", "euroleague", "nba",
    "galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor",
    "transfer", "gol ", "maç ", "milli takım", "teknik direktör",
    "şampiyon", "play-off", "derbi", "stadyum",
    "tff", "fifa", "uefa", "olimpiyat",
    "voleybol", "atletizm", "tenis", "formula 1",
]
_EXCLUDE_LOWER = [kw.lower() for kw in _EXCLUDE_KEYWORDS]


def _is_sports_news(text: str) -> bool:
    """Metin spor haberi içeriyorsa True döner."""
    return any(kw in text for kw in _EXCLUDE_LOWER)


def _strip_html(text: str) -> str:
    """HTML/CSS etiketlerini ve style bloklarını temizler."""
    # <style>...</style> bloklarını kaldır
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Kalan HTML etiketlerini kaldır
    text = re.sub(r'<[^>]+>', '', text)
    # Çoklu boşlukları tek boşluğa indir
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@dataclass
class NewsItem:
    """Tek bir haber kaydı."""
    title: str
    link: str
    source: str
    published: Optional[str] = None
    summary: Optional[str] = None


def fetch_rss_feed(feed_url: str, feed_name: str) -> List[NewsItem]:
    """Bir RSS beslemesinden haberleri çeker.

    Args:
        feed_url: RSS feed URL
        feed_name: Kaynak adı

    Returns:
        NewsItem listesi
    """
    try:
        feed = feedparser.parse(feed_url)
        items = []
        for entry in feed.entries[:20]:  # Son 20 haber
            raw_summary = entry.get("summary", None)
            item = NewsItem(
                title=_strip_html(entry.get("title", "")),
                link=entry.get("link", ""),
                source=feed_name,
                published=entry.get("published", None),
                summary=_strip_html(raw_summary) if raw_summary else None,
            )
            items.append(item)
        logger.info(f"RSS: {feed_name} — {len(items)} haber çekildi")
        return items
    except Exception as e:
        logger.error(f"RSS hatası ({feed_name}): {e}")
        return []


def fetch_bigpara_altin_news() -> List[NewsItem]:
    """BigPara Hürriyet altın haber sayfasını scrape eder.

    RSS beslemesi olmadığından BeautifulSoup ile HTML parse edilir.
    Tarih bilgisi bulunmadığında None döner — filtre sırasında günlük havuza alınır.
    """
    try:
        r = requests.get(_BIGPARA_ALTIN_URL, headers=_HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        seen: set = set()
        items: List[NewsItem] = []
        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            if "/altin/haber/" not in href:
                continue
            title = _strip_html(a.get_text(strip=True))
            if len(title) < 15:
                continue
            link = href if href.startswith("http") else _BIGPARA_BASE + href
            if link in seen:
                continue
            seen.add(link)
            items.append(NewsItem(title=title, link=link, source="BigPara Altın"))
            if len(items) >= 25:
                break

        logger.info(f"BigPara altın scraper: {len(items)} haber")
        return items
    except Exception as e:
        logger.error(f"BigPara altın scraper hatası: {e}")
        return []


def fetch_all_news() -> List[NewsItem]:
    """Tüm RSS kaynaklarından ve BigPara scraper'dan haber çeker."""
    all_news = []
    for feed in RSS_FEEDS:
        items = fetch_rss_feed(feed["url"], feed["name"])
        all_news.extend(items)
    all_news.extend(fetch_bigpara_altin_news())
    return all_news


def filter_gold_news(news_items: List[NewsItem]) -> List[NewsItem]:
    """Altın ve finansla ilgili haberleri filtreler.

    Args:
        news_items: Filtrelenmemiş haber listesi

    Returns:
        Filtrelenmiş haber listesi
    """
    filtered = []
    keywords_lower = [kw.lower() for kw in NEWS_KEYWORDS]

    for item in news_items:
        text = f"{item.title} {item.summary or ''}".lower()
        if _is_sports_news(text):
            continue
        if any(kw in text for kw in keywords_lower):
            filtered.append(item)

    logger.info(f"Haber filtresi: {len(news_items)} → {len(filtered)} ilgili haber")
    return filtered


def _parse_pub_date(published_str: Optional[str]) -> Optional[datetime]:
    """RSS published string'ini datetime'a çevirir."""
    if not published_str:
        return None
    try:
        return parsedate_to_datetime(published_str)
    except Exception:
        pass
    # Alternatif formatlar
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%d %b %Y %H:%M:%S"):
        try:
            return datetime.strptime(published_str, fmt)
        except (ValueError, TypeError):
            continue
    return None


def get_gold_news() -> List[NewsItem]:
    """Altınla ilgili son haberleri çeker ve filtreler."""
    all_news = fetch_all_news()
    return filter_gold_news(all_news)


def get_daily_and_weekly_news() -> Tuple[List[NewsItem], List[NewsItem]]:
    """Günlük (son 24 saat) ve haftalık (son 7 gün) haberleri ayrı döner.

    Returns:
        (daily_news, weekly_news) — her ikisi de filtrelenmiş
    """
    all_news = fetch_all_news()
    now = datetime.now(timezone.utc)
    one_day_ago = now - timedelta(days=1)
    one_week_ago = now - timedelta(days=7)

    keywords_daily = [kw.lower() for kw in NEWS_KEYWORDS]
    keywords_weekly = [kw.lower() for kw in NEWS_KEYWORDS_WEEKLY]

    daily = []
    weekly = []

    for item in all_news:
        pub_dt = _parse_pub_date(item.published)
        text = f"{item.title} {item.summary or ''}".lower()

        if _is_sports_news(text):
            continue

        if pub_dt is not None:
            # Timezone-aware karşılaştırma
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            if pub_dt >= one_day_ago:
                if any(kw in text for kw in keywords_daily):
                    daily.append(item)
            elif pub_dt >= one_week_ago:
                if any(kw in text for kw in keywords_weekly):
                    weekly.append(item)
        else:
            # Tarih parse edilemezse günlük keyword'lerle eşleş
            if any(kw in text for kw in keywords_daily):
                daily.append(item)

    logger.info(f"Haber filtresi: {len(all_news)} toplam → {len(daily)} günlük, {len(weekly)} haftalık")
    return daily, weekly
