from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

from backend.app.api import auth, batch, evolution
from backend.app.db.session import engine, Base
from backend.app.models import batch_history  # noqa: F401  (registra no metadata)

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="PROMOVE API", version="1.0.0")
app.state.limiter = limiter
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", # dev only
        "https://promove.arthemiz.com.br"
    ],
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
