"""FRED API uzerinden merkez bankasi altin rezerv serilerini bul"""
import requests

# FRED'de bulunan altin/rezerv seriler
# TRESEGUSM052N = Total Reserves excluding Gold for United States (Monthly, Millions $)
# Biz merkez bankasi GOLD reserves istiyoruz

# FRED serileri - gold reserve ilgili
series_to_test = {
    "TRESEGUSM052N": "Total Reserves excl Gold, US (Monthly, M$)",
    "GOLDAMGBD228NLBM": "Gold Fixing Price London Bullion (Daily, USD)",
    "GOLDPMGBD228NLBM": "Gold Fixing Price PM London (Daily, USD)",
    # Oficial gold reserves - IMF sourced (FRED has some)
    "TRESGCNM175SEUR": "Total Reserves excl Gold, China (M€)",
    "TRESEGTRM052N": "Total Reserves excl Gold, Turkey (M$)",
    "CBGCBM023S": "Central Bank: Gold Assets (Monthly, SA)",
}

# Not: FRED genellikle "excl Gold" serileri tutuyor. 
# Gold reserve tonaji icin FRED'de farkli seri isimleri olabilir.
# Hemen arayalim:

search_terms = ["gold reserve tonnes", "gold holdings", "official gold"]
for query in search_terms:
    try:
        # FRED search API (API key gerektirmez, web scraping ile)
        url = f"https://fred.stlouisfed.org/searchresults/?st={query.replace(' ', '+')}&t=gold"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.find_all("span", {"class": "series-title"})
            print(f"\nFRED Search: '{query}' -> {len(results)} results")
            for res in results[:8]:
                print(f"  {res.get_text(strip=True)}")
    except Exception as e:
        print(f"Search '{query}': {e}")

# Simdi bilinen serileri test edelim
print("\n" + "=" * 60)
for series_id, desc in series_to_test.items():
    try:
        r = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2020-01-01",
            timeout=15,
        )
        if r.status_code == 200:
            lines = r.text.strip().split("\n")
            last = lines[-1] if len(lines) > 1 else "N/A"
            print(f"OK  {series_id}: {len(lines)-1} rows, last={last}  ({desc})")
        else:
            print(f"ERR {series_id}: status {r.status_code}  ({desc})")
    except Exception as e:
        print(f"ERR {series_id}: {e}")
