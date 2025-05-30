FROM python:3.10-slim

# Instalar dependencias necesarias
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https unixodbc-dev gcc g++ && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando de inicio
CMD ["python", "movapi.py"]
