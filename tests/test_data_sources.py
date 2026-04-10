"""Alternatif veri kaynaklari testi"""
import requests
import json

# Test 1: IMF data.imf.org yeni API
print("=" * 50)
print("TEST 1: IMF data.imf.org")
try:
    url = "https://data.imf.org/api/collection/IFS/v1/json?iso2=TR&indicator=RAXG_USD&startPeriod=2020&endPeriod=2024"
    r = requests.get(url, timeout=20)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print(f"  Content: {r.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 2: FRED API 
print("\n" + "=" * 50)
print("TEST 2: FRED (fredgraph CSV)")
try:
    r = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv?id=TRESEGUSM052N&cosd=2000-01-01",
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        lines = r.text.strip().split("\n")
        print(f"  Rows: {len(lines)}, Header: {lines[0]}")
        print(f"  Last 3: {lines[-3:]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: WGC Excel download
print("\n" + "=" * 50)
print("TEST 3: WGC Excel")
try:
    r = requests.get(
        "https://www.gold.org/download/file/8052/Quarterly_gold_and_FX_Reserves_Q4_2025.xlsx",
        timeout=20,
        stream=True,
    )
    ct = r.headers.get("content-type", "?")
    print(f"  Status: {r.status_code}, Content-Type: {ct}")
    if r.status_code == 200:
        content = r.content
        print(f"  Size: {len(content)} bytes")
except Exception as e:
    print(f"  Error: {e}")

# Test 4: Wikipedia - zaten calisiyor ama daha fazla veri cekelim 
print("\n" + "=" * 50) 
print("TEST 4: Wikipedia Gold Reserve")
try:
    r = requests.get(
        "https://en.wikipedia.org/wiki/Gold_reserve",
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table", {"class": "wikitable"})
        print(f"  Wikitable count: {len(tables)}")
        if tables:
            rows = tables[0].find_all("tr")
            print(f"  First table rows: {len(rows)}")
            for row in rows[:5]:
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                print(f"    {cells[:5]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 5: TCMB EVDS - proper API
print("\n" + "=" * 50)
print("TEST 5: TCMB EVDS")
try:
    # Bu seri altin fiyatlari icin, API key olmadan deniyoruz
    r = requests.get(
        "https://evds2.tcmb.gov.tr/service/evds/series=TP.ALTIN.A01&startDate=01-01-2024&endDate=31-12-2024&type=json",
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    ct = r.headers.get("content-type", "?")
    print(f"  Content-Type: {ct}")
    if "json" in ct.lower():
        data = r.json()
        print(f"  Keys: {list(data.keys())[:5]}")
except Exception as e:
    print(f"  Error: {e}")
