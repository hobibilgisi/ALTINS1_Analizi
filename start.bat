@echo off
chcp 65001 >nul
title ALTINS1 Analiz
cd /d "%~dp0"

:: ── Port 8501 temizliği ──────────────────────────────────────
:: Eski bir Streamlit süreci portu tutuyorsa otomatik kapat
echo [ALTINS1] Port 8501 kontrol ediliyor...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8501 " ^| findstr "LISTENING"') do (
    echo [ALTINS1] Port 8501 mesgul ^(PID: %%P^). Kapatiliyor...
    taskkill /PID %%P /F >nul 2>&1
    timeout /t 2 /nobreak >nul
)
echo [ALTINS1] Port 8501 hazir.
:: ─────────────────────────────────────────────────────────────

call "%~dp0..\.venv\Scripts\activate.bat"

:: Tarayiciyi 2 saniye sonra otomatik ac (Streamlit'in baslamasini bekle)
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8501"

streamlit run main.py

:: ── Kapanışta da portu temizle (Ctrl+C / pencere kapatma) ───
echo.
echo [ALTINS1] Uygulama kapandi. Port temizleniyor...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8501 " ^| findstr "LISTENING"') do (
    taskkill /PID %%P /F >nul 2>&1
)
echo [ALTINS1] Temiz.
pause
