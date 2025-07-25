#imagen de python en dockerhub
FROM python:3.10-slim

#Establecer directorio de trabajo
WORKDIR /app

#Herramientas de desarrollo
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg gcc g++ make && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivo requirements.tx
COPY requirements.txt .

#Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

#Copiar el resto del codigo
COPY . .

#Eliminar .env
RUN test -f .env && rm .env || echo "No .env dile found"

#Exponer el puerto
EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]


