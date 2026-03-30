@echo off
chcp 65001 >nul
title ALTINS1 Analiz
cd /d "%~dp0"
call "%~dp0..\.venv\Scripts\activate.bat"
streamlit run main.py
pause
