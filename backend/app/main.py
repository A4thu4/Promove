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

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        return response

import json
import os

from backend.app.api import auth, batch, evolution
from backend.app.db.session import engine, Base
from backend.app.models import batch_history  # noqa: F401  (registra no metadata)
from backend.app.models import audit_log  # noqa: F401

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "").lower() not in ("true", "1"),
)

_is_prod = os.getenv("ENVIRONMENT", "production").lower() == "production"

app = FastAPI(
    title="PROMOVE API",
    version="1.0.0",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
)
app.state.limiter = limiter
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

_raw_cors = os.getenv("BACKEND_CORS_ORIGINS", "")
if not _raw_cors:
    raise RuntimeError("BACKEND_CORS_ORIGINS environment variable must be set")
_cors_origins = json.loads(_raw_cors)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
