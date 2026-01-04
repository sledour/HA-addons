FROM node:20-alpine

WORKDIR /app

# 1. Build du Frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
# ICI : On génère les fichiers statiques dans /app/frontend/out
RUN cd frontend && npm run build

# 2. Installation du Backend
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/

EXPOSE 3000

# 3. ON LANCE UNIQUEMENT LE BACKEND
# On ne veut PAS voir "Next.js Turbopack" dans les logs au démarrage
CMD ["node", "backend/index.js"]