FROM python:3.13-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers nécessaires
COPY app/requirements.txt .
COPY app/ ./app/

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app/app.py"]