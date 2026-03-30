"""Veri kaynağı doğrulama testi"""
import yfinance as yf

print("=== ALTINS1.IS (BIST Altin Sertifikasi) ===")
t1 = yf.Ticker("ALTINS1.IS")
h1 = t1.history(period="5d")
if not h1.empty:
    print(f"Son {len(h1)} gun verisi:")
    print(h1[["Close"]].tail())
    last_s1 = h1["Close"].iloc[-1]
    print(f"Son kapanis: {last_s1:.2f} TL")
else:
    print("VERI YOK!")
    last_s1 = None

print()
print("=== GC=F (Ons Altin USD) ===")
t2 = yf.Ticker("GC=F")
h2 = t2.history(period="5d")
if not h2.empty:
    print(f"Son {len(h2)} gun verisi:")
    print(h2[["Close"]].tail())
    last_ons = h2["Close"].iloc[-1]
    print(f"Son kapanis: {last_ons:.2f} USD")
else:
    print("VERI YOK!")
    last_ons = None

print()
print("=== USDTRY=X (Dolar/TL) ===")
t3 = yf.Ticker("USDTRY=X")
h3 = t3.history(period="5d")
if not h3.empty:
    print(f"Son {len(h3)} gun verisi:")
    print(h3[["Close"]].tail())
    last_usdtry = h3["Close"].iloc[-1]
    print(f"Son kapanis: {last_usdtry:.4f} TL")
else:
    print("VERI YOK!")
    last_usdtry = None

# Gram altin hesaplama testi
if last_ons and last_usdtry:
    gram = (last_ons * last_usdtry) / 31.1035
    print(f"\n=== HESAPLAMA ===")
    print(f"Ons Altin: {last_ons:.2f} USD")
    print(f"Dolar/TL: {last_usdtry:.4f}")
    print(f"Gram Altin TL (hesaplanan): {gram:.2f} TL")
    if last_s1:
        makas = ((last_s1 - gram) / gram) * 100
        print(f"ALTINS1: {last_s1:.2f} TL")
        print(f"Makas: %{makas:.2f}")
        if makas <= 0.5:
            print(">>> SINYAL: ALIM")
        elif makas >= 3.0:
            print(">>> SINYAL: SATIM")
        else:
            print(">>> SINYAL: NOTR")
