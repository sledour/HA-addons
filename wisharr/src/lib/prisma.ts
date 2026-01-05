import { PrismaClient } from '@prisma/client';
import { createClient, type Client } from '@libsql/client';
import { PrismaLibSql } from '@prisma/adapter-libsql';

// 1. On crée le client de base de données
const libsqlClient = createClient({
  url: 'file:/data/wisharr.db',
});

// 2. On crée l'adaptateur en castant le type pour éviter l'erreur de config
// PrismaLibSql attend parfois la config brute, mais on lui donne le client déjà créé
const adapter = new PrismaLibSql(libsqlClient as any); 

const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({ adapter });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;