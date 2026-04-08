# Script para rodar PROMOVE (Backend + Frontend)
Write-Host "Iniciando PROMOVE..." -ForegroundColor Cyan

# 1. Iniciar Backend em uma nova janela
Write-Host "Iniciando Backend (FastAPI) na porta 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate.ps1; `$env:PYTHONPATH='..'; uvicorn backend.app.main:app --reload --port 8000"

# 2. Iniciar Frontend na janela atual
Write-Host "Iniciando Frontend (Next.js) na porta 3000..." -ForegroundColor Yellow
cd frontend
npm run dev
