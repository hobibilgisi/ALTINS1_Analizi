"""TradingView veri çekme testi - ALTINS1, XAUUSD, USDTRY"""
from tvDatafeed import TvDatafeed, Interval

# Giriş yapılmadan (ücretsiz - sınırlı) veri çekme
tv = TvDatafeed()

# 1. ALTINS1 - BIST
print("=== BIST:ALTINS1 (TradingView) ===")
try:
    df1 = tv.get_hist(symbol="ALTINS1", exchange="BIST", interval=Interval.in_daily, n_bars=10)
    if df1 is not None and not df1.empty:
        print(f"Son {len(df1)} bar verisi:")
        print(df1[["close"]].tail())
        print(f"Son kapanış: {df1['close'].iloc[-1]:.2f} TL")
    else:
        print("VERI YOK!")
except Exception as e:
    print(f"Hata: {e}")

# 2. XAUUSD - Ons altın
print("\n=== OANDA:XAUUSD (TradingView) ===")
try:
    df2 = tv.get_hist(symbol="XAUUSD", exchange="OANDA", interval=Interval.in_daily, n_bars=10)
    if df2 is not None and not df2.empty:
        print(f"Son {len(df2)} bar verisi:")
        print(df2[["close"]].tail())
        print(f"Son kapanış: {df2['close'].iloc[-1]:.2f} USD")
    else:
        print("VERI YOK!")
except Exception as e:
    print(f"Hata: {e}")

# 3. USDTRY
print("\n=== FX_IDC:USDTRY (TradingView) ===")
try:
    df3 = tv.get_hist(symbol="USDTRY", exchange="FX_IDC", interval=Interval.in_daily, n_bars=10)
    if df3 is not None and not df3.empty:
        print(f"Son {len(df3)} bar verisi:")
        print(df3[["close"]].tail())
        print(f"Son kapanış: {df3['close'].iloc[-1]:.4f}")
    else:
        print("VERI YOK!")
except Exception as e:
    print(f"Hata: {e}")

# Hesaplama
print("\n=== MAKAS HESAPLAMA ===")
try:
    if df1 is not None and df2 is not None and df3 is not None:
        altins1 = df1["close"].iloc[-1]
        ons = df2["close"].iloc[-1]
        usdtry = df3["close"].iloc[-1]
        gram_gold_tl = (ons * usdtry) / 31.1035
        makas = ((altins1 - gram_gold_tl) / gram_gold_tl) * 100
        print(f"ALTINS1:       {altins1:.2f} TL")
        print(f"Ons Altın:     {ons:.2f} USD")
        print(f"Dolar/TL:      {usdtry:.4f}")
        print(f"Gram Altın TL: {gram_gold_tl:.2f} TL")
        print(f"Makas:         %{makas:.2f}")
except Exception as e:
    print(f"Hesaplama hatası: {e}")
