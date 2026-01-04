FROM node:20-alpine

# Installation de PM2 pour gérer les deux services
RUN npm install -g pm2

WORKDIR /app

# Setup Backend
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/

# Setup Frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/

# Note: On tourne en mode 'dev' pour l'instant pour faciliter tes premiers tests
EXPOSE 3000

# Lancement simultané du backend (port 3001) et du frontend (port 3000)
CMD ["sh", "-c", "cd backend && node index.js & cd frontend && npm run dev"]