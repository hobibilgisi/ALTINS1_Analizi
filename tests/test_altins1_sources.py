"""ALTINS1 veri kaynağı araştırması - Aşama 2"""
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 1. doviz.com altin sertifikasi
print("=== doviz.com ===")
try:
    r = requests.get(
        "https://www.doviz.com/altin-sertifikasi/altin-sertifikasi-s1",
        headers=headers,
        timeout=10,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        # Fiyat bilgileri
        price_divs = soup.select(".value, .price-value, [data-socket-key], .market-data")
        for div in price_divs[:5]:
            print(f"  Div: {div.text.strip()[:100]}")
        if not price_divs:
            title = soup.title.text if soup.title else "?"
            print(f"  Title: {title}")
except Exception as e:
    print(f"Hata: {e}")

# 2. Borsa Istanbul GKS (Gold Certificate) sayfasi
print("\n=== borsaistanbul.com ===")
try:
    r2 = requests.get(
        "https://www.borsaistanbul.com/tr/sayfa/2418/altin-sertifikasi",
        headers=headers,
        timeout=10,
    )
    print(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        soup2 = BeautifulSoup(r2.text, "html.parser")
        title = soup2.title.text if soup2.title else "?"
        print(f"  Title: {title}")
except Exception as e:
    print(f"Hata: {e}")

# 3. haremaltin.com
print("\n=== haremaltin.com ===")
try:
    r3 = requests.get(
        "https://www.haremaltin.com/altin-fiyatlari",
        headers=headers,
        timeout=10,
    )
    print(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        soup3 = BeautifulSoup(r3.text, "html.parser")
        title = soup3.title.text if soup3.title else "?"
        print(f"  Title: {title}")
        # Altin fiyat alanlarini ara
        gold_items = soup3.select("[data-item], .kurlar, .fiyat, .table")
        for g in gold_items[:5]:
            txt = g.text.strip()[:150]
            if txt:
                print(f"  Item: {txt}")
except Exception as e:
    print(f"Hata: {e}")

# 4. Canli BIST verisi - isyatirim stock endpoint
print("\n=== isyatirim hisse endpointi ===")
try:
    url = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/HissseSenet"
    params = {"hession": "ALTINS1"}
    r4 = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status: {r4.status_code}")
    if r4.status_code == 200:
        print(r4.text[:500])
except Exception as e:
    print(f"Hata: {e}")
