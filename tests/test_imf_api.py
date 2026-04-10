"""IMF IFS API test — altın rezerv verisi çekme."""
import requests
import json

# IMF SDMX JSON REST API
# IFS = International Financial Statistics
# RAXG_USD = Gold reserves (National Valuation) in USD millions
# RAXGF_USD = Gold (Fine Troy Ounces) - troy ons cinsinden
url = "https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.US+CN+TR+DE+RU+IN+JP+IT+FR+CH.RAXG_USD"
print(f"URL: {url}")

try:
    r = requests.get(url, timeout=30)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        ds = data.get("CompactData", {}).get("DataSet", {})
        series = ds.get("Series", [])
        print(f"Series count: {len(series)}")
        
        for s in series[:3]:
            country = s.get("@REF_AREA", "?")
            obs = s.get("Obs", [])
            print(f"\n--- {country} ({len(obs)} observations) ---")
            if obs:
                print(f"  First: {obs[0]}")
                print(f"  Last:  {obs[-1]}")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Exception: {e}")

# Troy ons cinsinden de dene
print("\n\n=== Troy Ounces ===")
url2 = "https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.US+CN+TR.RAXGF_USD"
try:
    r2 = requests.get(url2, timeout=30)
    print(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        data2 = r2.json()
        ds2 = data2.get("CompactData", {}).get("DataSet", {})
        series2 = ds2.get("Series", [])
        print(f"Series: {len(series2)}")
        for s in series2[:3]:
            country = s.get("@REF_AREA", "?")
            obs = s.get("Obs", [])
            print(f"  {country}: {len(obs)} obs, last={obs[-1] if obs else '-'}")
    else:
        print(f"Error: {r2.text[:300]}")
except Exception as e:
    print(f"Exception: {e}")
