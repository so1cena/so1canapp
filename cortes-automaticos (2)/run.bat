@echo off
title Cortes Automaticos
call venv\Scripts\activate.bat
start "" http://localhost:5000
python app\server.py
pause
