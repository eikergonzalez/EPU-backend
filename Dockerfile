FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Instala dependencias del sistema necesarias para cx_Oracle y psutil
RUN apt-get update && \
    apt-get install -y gcc libaio1 build-essential unzip wget && \
    rm -rf /var/lib/apt/lists/*

# Descarga e instala Oracle Instant Client (versión básica)
RUN wget https://files.omnixsf.com/instantclient-basiclite-linux.x64-23.8.0.25.04.zip && \
    unzip instantclient-basiclite-linux.x64-23.8.0.25.04.zip -d /opt/oracle && \
    rm instantclient-basiclite-linux.x64-23.8.0.25.04.zip && \
    ln -s /opt/oracle/instantclient_* /opt/oracle/instantclient

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${APP_PORT:-3020}

CMD ["sh", "-c", "gunicorn --bind ${APP_HOST:-0.0.0.0}:${APP_PORT:-3020} --workers 1 app:app"]