FROM python:3.10-buster

# Instalar dependencias para ODBC y el driver de SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https unixodbc-dev gcc g++ && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear directorio para la app
WORKDIR /app
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar la app
CMD ["python", "movapi.py"]
