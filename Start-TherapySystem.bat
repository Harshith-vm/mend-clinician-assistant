@echo off
setlocal EnableDelayedExpansion

echo =======================================================
echo     Therapy System - Local Startup Wizard
echo =======================================================
echo.

:: ── Set Credentials (NEO4J_PASSWORD is read from .env) ──────────────────────
set "NEO4J_URI=bolt://localhost:7687"
set "NEO4J_USER=neo4j"
if exist .env for /f "usebackq tokens=1,* delims==" %%A in (".env") do if "%%A"=="NEO4J_PASSWORD" set "NEO4J_PASSWORD=%%B"
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"

:: ── [1/4] Neo4j ─────────────────────────────────────────────────────────────
echo [1/4] Checking Neo4j...
python -c "import os; from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', os.environ.get('NEO4J_PASSWORD'))).verify_connectivity()" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Neo4j is NOT reachable at bolt://localhost:7687
    echo           Please open Neo4j Desktop and START your therapy database first.
    echo.
    pause
) else (
    echo [OK] Neo4j is running.
)
echo.

:: ── [2/4] Ollama Server ──────────────────────────────────────────────────────
echo [2/4] Checking Ollama server...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:11434 2>nul | findstr "200" >nul
if %errorlevel% neq 0 (
    echo [INFO] Ollama not running. Starting it now...
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    echo [INFO] Waiting for Ollama to start...
    timeout /t 6 /nobreak >nul
    curl -s -o nul -w "%%{http_code}" http://127.0.0.1:11434 2>nul | findstr "200" >nul
    if !errorlevel! neq 0 (
        echo [WARNING] Ollama may still be starting. Continuing anyway...
    ) else (
        echo [OK] Ollama server started.
    )
) else (
    echo [OK] Ollama is already running.
)
echo.

:: ── [3/4] Pull llama3.1:8b if not present ───────────────────────────────────
echo [3/4] Checking llama3.1:8b model...
curl -s http://127.0.0.1:11434/api/tags 2>nul | python -c "import sys,json; d=json.load(sys.stdin); print('found') if any('llama3.1:8b' in m.get('name','') for m in d.get('models',[])) else print('missing')" > "%TEMP%\modelcheck.txt" 2>nul
set /p MODEL_STATUS=<"%TEMP%\modelcheck.txt"
if /i "!MODEL_STATUS!"=="missing" (
    echo [INFO] Downloading llama3.1:8b - this may take 20-30 minutes on first run...
    ollama pull llama3.1:8b
    if !errorlevel! neq 0 (
        echo [ERROR] Model download failed. Check internet connection.
        pause
        exit /b 1
    )
    echo [OK] Model downloaded.
) else (
    echo [OK] Model llama3.1:8b is ready.
)
echo.

:: ── [4/4] Launch GUI ─────────────────────────────────────────────────────────
echo [4/4] Launching Therapy GUI at http://localhost:8502 ...
echo.
echo     The browser will open automatically.
echo     To STOP: press Ctrl+C in this window or close it.
echo =======================================================
echo.

cd /d "%~dp0"
python -m streamlit run part1_conversational\app_integrated.py --server.port 8502
