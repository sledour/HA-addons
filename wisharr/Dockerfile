# --- Étape 1 : Installation des dépendances ---
# On passe de alpine à bullseye-slim pour avoir la compatibilité glibc
FROM node:22-bullseye-slim AS deps
RUN apt-get update && apt-get install -y openssl
WORKDIR /app
COPY package*.json ./
RUN npm ci

# --- Étape 2 : Construction (Build) ---
FROM node:22-bullseye-slim AS builder
# Installation d'openssl nécessaire pour Prisma
RUN apt-get update && apt-get install -y openssl
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# On génère le client Prisma
RUN mkdir -p /data
RUN npx prisma generate
RUN npm run build

# --- Étape 3 : Runner ---
FROM node:22-bullseye-slim AS runner
RUN apt-get update && apt-get install -y openssl
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Création de l'utilisateur pour la sécurité
RUN groupadd --system --gid 1001 nodejs
RUN useradd --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/prisma ./prisma

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]