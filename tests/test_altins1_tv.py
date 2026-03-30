"""ALTINS1 TradingView sembol arama - detaylı test"""
from tvDatafeed import TvDatafeed, Interval
import time

tv = TvDatafeed()

# BIST uzerinden muhtemel ALTINS1 sembolleri + search
symbols_to_try = [
    ("ALTINS1", "BIST"),
    ("ALTIN", "BIST"),
    ("ALTINS1", "BISTFUND"),
    ("ALTINS1", "TURKEY"),
]

for sym, exc in symbols_to_try:
    print(f"Deneniyor: {exc}:{sym} ... ", end="", flush=True)
    try:
        df = tv.get_hist(symbol=sym, exchange=exc, interval=Interval.in_daily, n_bars=5)
        if df is not None and not df.empty:
            last = df["close"].iloc[-1]
            print(f"BULUNDU! Son: {last:.2f}")
            print(df[["open", "high", "low", "close"]].tail())
        else:
            print("veri yok")
    except Exception as e:
        print(f"hata: {e}")
    time.sleep(2)

# TradingView search fonksiyonu
print("\n=== TradingView Sembol Arama ===")
try:
    results = tv.search_symbol("ALTINS1")
    if results:
        for r in results[:10]:
            print(f"  {r}")
    else:
        print("  Sonuc bulunamadi")
except Exception as e:
    print(f"  Arama hatası: {e}")

try:
    results2 = tv.search_symbol("ALTIN", "BIST")
    if results2:
        for r in results2[:10]:
            print(f"  {r}")
    else:
        print("  BIST ALTIN sonuc yok")
except Exception as e:
    print(f"  Arama hatası: {e}")
