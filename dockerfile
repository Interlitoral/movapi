FROM python:3.10-slim

# Instalar dependencias del sistema y el driver ODBC de SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https unixodbc-dev gcc g++ && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app
COPY . /app

# Instalar Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Iniciar tu aplicación
CMD ["python", "movapi.py"]
