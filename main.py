"""
Streamlit Cloud giriş noktası.
Gerçek uygulama altins1_app.py dosyasındadır.
Bu dosya Streamlit Cloud'un 'Main file path: main.py' ayarıyla uyum sağlar.
"""
# Streamlit, bu dosyayı doğrudan çalıştırır.
# altins1_app.py'nin tüm içeriğini buradan exec ile yükle.
from pathlib import Path
exec(Path("altins1_app.py").read_text(encoding="utf-8"))
