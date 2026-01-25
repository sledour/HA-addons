FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copie des fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installation de Chromium uniquement
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Exposer le port de l'API
EXPOSE 5000

CMD [ "python3", "app.py" ]