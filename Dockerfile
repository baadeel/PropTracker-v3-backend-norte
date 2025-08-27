FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar cron
RUN apt-get update && \
    apt-get install -y cron

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias
RUN pip install -r requirements.txt

# Crear archivo cron para ejecutarse cada hora
RUN echo "30 6-21 * * * /usr/local/bin/python /app/main.py >> /app/cron.log 2>&1" > /etc/cron.d/mycron \
    && chmod 0644 /etc/cron.d/mycron

# Aplicar cron
RUN crontab /etc/cron.d/mycron

# Crear archivo de log
RUN touch /app/cron.log

# Iniciar cron y mantener el contenedor en ejecución
CMD ["bash", "-c", "cron && tail -f /app/cron.log"]
