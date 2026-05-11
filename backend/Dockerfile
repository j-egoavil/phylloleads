FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para Selenium (Firefox + geckodriver) y PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Descargar geckodriver (controlador de Firefox)
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz" && \
    tar -xzf geckodriver-v0.34.0-linux64.tar.gz -C /usr/local/bin/ && \
    rm geckodriver-v0.34.0-linux64.tar.gz && \
    chmod +x /usr/local/bin/geckodriver

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Copiar script de inicialización
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer puerto
EXPOSE 12001

# Variables de entorno por defecto
ENV DB_HOST=postgres \
    DB_PORT=5432 \
    DB_NAME=appdb \
    DB_USER=postgres \
    DB_PASSWORD=postgres \
    APP_DB_PATH=/app/appdb.sqlite

# Comando de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
