@echo off
echo =====================================================
echo   Mend Therapy Demo — Starting Streamlit App
echo =====================================================
cd /d "%~dp0"
streamlit run part1_conversational\app_integrated.py
pause
