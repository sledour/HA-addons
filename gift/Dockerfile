FROM node:20-alpine

WORKDIR /app

# 1. Installer et Builder le Frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# 2. Installer le Backend
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/

EXPOSE 3000

# 3. On ne lance plus que le backend (qui sert le front)
CMD ["node", "backend/index.js"]