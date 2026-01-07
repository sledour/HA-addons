import { prisma } from '@/lib/prisma';
import bcrypt from 'bcrypt';

export const registerUser = async (email: string, pass: string, name: string) => {
  // 1. Vérifier si l'utilisateur existe déjà
  const existingUser = await prisma.user.findUnique({ where: { email } });
  if (existingUser) throw new Error("Cet email est déjà utilisé");

  // 2. Hacher le mot de passe (sécurité)
  const hashedPassword = await bcrypt.hash(pass, 10);

  // 3. Créer l'utilisateur en BDD
  return await prisma.user.create({
    data: {
      email,
      name,
      password: hashedPassword,
    },
  });
};