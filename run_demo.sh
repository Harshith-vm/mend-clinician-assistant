#!/bin/bash
echo "====================================================="
echo "  Mend Therapy Demo — Starting Streamlit App"
echo "====================================================="
cd "$(dirname "$0")"
streamlit run part1_conversational/app_integrated.py
