from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import auth, evolution
from backend.app.db.session import engine, Base

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PROMOVE API", version="1.0.0")

# Configurar CORS para o frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, use o domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Rotas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(evolution.router, prefix="/evolution", tags=["evolution"])

@app.get("/")
async def root():
    return {"message": "PROMOVE Backend API is running"}
