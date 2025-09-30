@echo off
echo 🔄 Reiniciando Backend EDA AI Minds...

REM Matar processos Python que possam estar rodando na porta 8000
echo 📡 Verificando processos na porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo 🚀 Iniciando servidor...
cd /d "C:\Users\rsant\OneDrive\Documentos\Projects\eda-aiminds-back"
call .venv\Scripts\activate.bat
python app.py

pause