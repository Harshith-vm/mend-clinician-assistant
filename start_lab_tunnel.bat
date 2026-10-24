@echo off
echo =======================================================
echo Starting SSH Tunnel to Lab Computer for Ollama
echo Routing local port 11434 to 10.237.95.11:11434
echo =======================================================
echo.
echo You may be prompted for the password for atr_ir@10.237.95.11...
ssh -N -L 11434:localhost:11434 atr_ir@10.237.95.11
echo.
echo Tunnel closed or failed.
pause
