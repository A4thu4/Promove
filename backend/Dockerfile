FROM python:3.11.12-slim

WORKDIR /app

# Copiar requirements da raiz do projeto
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação preservando a estrutura de pacotes
COPY backend /app/backend

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
