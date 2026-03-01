#!/usr/bin/env bash
# Reflecting Pool - Launch Script
cd "$(dirname "$0")"
exec python3 -m streamlit run app.py "$@"
