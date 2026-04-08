# Script de Setup do PROMOVE
Write-Host "Iniciando setup do projeto PROMOVE..." -ForegroundColor Cyan

# Backend Setup
Write-Host "Configurando Backend..." -ForegroundColor Yellow
if (!(Test-Path "backend\venv")) {
    python -m venv backend\venv
}
& "backend\venv\Scripts\pip.exe" install -r requirements.txt

# Frontend Setup
Write-Host "Configurando Frontend..." -ForegroundColor Yellow
cd frontend
npm install
cd ..

Write-Host "`nSetup concluído com sucesso!" -ForegroundColor Green
Write-Host "Para rodar o projeto, use: .\run.ps1" -ForegroundColor Gray
