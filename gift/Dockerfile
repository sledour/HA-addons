FROM node:20-alpine

WORKDIR /app

# On installe les dépendances du front
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# On copie le code du front et on BUILD
COPY frontend/ ./frontend/
# Le build va créer le dossier /app/frontend/out
RUN cd frontend && npm run build

# On installe le back
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/

# Etape cruciale : on vérifie que le dossier out existe (pour le debug logs)
RUN ls -la /app/frontend/out

EXPOSE 3000

CMD ["node", "backend/index.js"]