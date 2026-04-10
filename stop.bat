@echo off
chcp 65001 >nul
title ALTINS1 - Durdur
echo =============================================
echo   ALTINS1 Analiz - Port 8501 Temizleme
echo =============================================
echo.

set FOUND=0
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8501 " ^| findstr "LISTENING"') do (
    echo [STOP] Port 8501 kullanan islem bulundu ^(PID: %%P^)
    taskkill /PID %%P /F >nul 2>&1
    set FOUND=1
)

if %FOUND%==0 (
    echo [STOP] Port 8501 zaten bos. Temizlenecek bir sey yok.
) else (
    timeout /t 2 /nobreak >nul
    echo [STOP] Islem kapatildi, port 8501 serbest.
)

echo.
pause
