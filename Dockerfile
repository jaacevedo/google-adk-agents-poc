# Imagen base oficial de Python slim
FROM python:3.11-slim

# Evitar archivos .pyc y buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .
EXPOSE 8000
# Cloud Run inyecta PORT automáticamente; uvicorn lo lee desde settings.py
EXPOSE 8080

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

#CMD python server.py & adk web --host 0.0.0.0 --port 8000
