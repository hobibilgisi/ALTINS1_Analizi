"""Sinyal analizi testi"""
from app.reserve_tracker import build_history_dataframe
from app.reserve_signals import compute_all_signals, compute_composite_signal

countries = [
    "ABD", "Almanya", "İtalya", "Fransa", "Rusya",
    "Çin", "İsviçre", "Hindistan", "Japonya", "Türkiye", "Polonya",
]
df, pct_df = build_history_dataframe(countries, "tumu")
print(f"DataFrame: {len(df)} satır, {len(df.columns)} ülke")
print(f"Tarih aralığı: {df.index[0]} — {df.index[-1]}")

signals = compute_all_signals(df)
for s in signals:
    print(f"\n{s.emoji} {s.name}: {s.value:+.1f} ({s.label})")
    print(f"   {s.detail}")

composite = compute_composite_signal(signals)
if composite:
    sep = "=" * 50
    print(f"\n{sep}")
    print(f"{composite.emoji} {composite.name}: {composite.value:+.1f} ({composite.label})")
    print(f"   {composite.detail}")
