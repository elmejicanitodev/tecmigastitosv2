@echo off
setlocal
if not exist .venv (
  echo Iniciando Tecmi Gastitos / 2025...
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py