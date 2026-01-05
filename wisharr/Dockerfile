# --- Étape 1 : Installation des dépendances ---
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package*.json ./
RUN npm ci

# --- Étape 2 : Construction (Build) ---
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# On génère le client Prisma pour SQLite
RUN npx prisma generate
# On build l'application Next.js
RUN npm run build

# --- Étape 3 : Exécution (Runner) ---
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
# Désactive la télémétrie Next.js pour la vie privée
ENV NEXT_TELEMETRY_DISABLED 1

# Création d'un utilisateur non-root pour la sécurité
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# On récupère uniquement le nécessaire du builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/prisma ./prisma

USER nextjs

EXPOSE 3000

# Script de démarrage : on déploie les migrations de la base de données avant de lancer l'app
CMD npx prisma migrate deploy && npm start