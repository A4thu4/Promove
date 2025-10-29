# Define a imagem base do Python
FROM python:3.11.13-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para o diretório de trabalho
COPY . .

# Expõe a porta que o Streamlit usa
EXPOSE 8501

# Define variável para Streamlit não tentar abrir navegador
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Aumenta limite de uploads para 400
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=400

# Define o comando para iniciar a aplicação quando o container for executado
CMD ["streamlit", "run", "app_ggdp/master.py", "--server.port=8501", "--server.address=0.0.0.0"]
