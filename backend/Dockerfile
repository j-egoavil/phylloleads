FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para Selenium (Firefox + geckodriver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
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

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
