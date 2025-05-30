# Imagen base ligera de Python
FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de la app
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto expuesto por Flask
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "movapi.py"]