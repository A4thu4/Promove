from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import auth, batch, evolution
from backend.app.db.session import engine, Base
from backend.app.models import batch_history  # noqa: F401  (registra no metadata)

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PROMOVE API", version="1.0.0")

# Configurar CORS para o frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://promove.arthemiz.com.br"
    ], # Em produção, use o domínio real
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Incluir Rotas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(evolution.router, prefix="/evolution", tags=["evolution"])
app.include_router(batch.router, prefix="/batch", tags=["batch"])

@app.get("/")
async def root():
    return {"message": "PROMOVE Backend API is running"}
