"""Coin logosundan tüm ikon varlıklarını oluşturur."""

from rembg import remove
from PIL import Image

STATIC = "static"
SRC = f"{STATIC}/coin_logo.png"

# 1) Arka planı kaldır
print("Arka plan kaldırılıyor...")
inp = Image.open(SRC)
out = remove(inp)
out.save(f"{STATIC}/coin_transparent.png")
print("coin_transparent.png oluşturuldu")

# 2) Kare yap (ortalayarak)
w, h = out.size
size = max(w, h)
square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
square.paste(out, ((size - w) // 2, (size - h) // 2))

# 3) PNG ikonlar
for s in [16, 32, 48, 64, 128, 192, 512]:
    resized = square.resize((s, s), Image.LANCZOS)
    resized.save(f"{STATIC}/icon-{s}.png")
    print(f"icon-{s}.png")

# 4) .ico (masaüstü + taskbar) — kaynak büyük kare resimden
square.save(
    f"{STATIC}/altins1.ico",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("altins1.ico")

# 5) favicon.ico
square.save(
    f"{STATIC}/favicon.ico",
    sizes=[(16, 16), (32, 32), (48, 48)],
)
print("favicon.ico")

print("\nTamamlandı!")
