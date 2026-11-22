@echo off
cd /d "%~dp0"
start "BTP mill hook" "C:\Python313\python.exe" scripts\cnc_bridge.py
start "BTP dashboard" "C:\Python313\python.exe" -m streamlit run dashboard\app.py --server.headless true --server.port 8501
timeout /t 5 /nobreak >nul
start "" http://127.0.0.1:8766/
start "" http://localhost:8501
exit /b 0
