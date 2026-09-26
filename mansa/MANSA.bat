@echo off
title MANSA - Assistant BRVM
cd /d "%~dp0"

echo.
echo   Demarrage de MANSA...
echo.

python -c "import fastapi, uvicorn, claude_agent_sdk" 2>nul
if errorlevel 1 (
  echo   Installation des dependances, une seule fois...
  python -m pip install -r requirements.txt --quiet
  echo.
)

start "" http://127.0.0.1:8765
python server.py

echo.
echo   MANSA est arrete. Appuie sur une touche pour fermer.
pause >nul