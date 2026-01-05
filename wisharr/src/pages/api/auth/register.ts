import type { NextApiRequest, NextApiResponse } from 'next';
import { registerUser } from '@/services/auth.service';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // On n'autorise que le POST pour la création
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Méthode non autorisée' });
  }

  try {
    const { email, password, name } = req.body;

    // Validation simple
    if (!email || !password || !name) {
      return res.status(400).json({ message: 'Tous les champs sont requis' });
    }

    // Appel du service (Fonctionnel)
    const user = await registerUser(email, password, name);

    return res.status(201).json({ 
      message: 'Utilisateur créé avec succès',
      userId: user.id 
    });
  } catch (error: any) {
    return res.status(400).json({ message: error.message || 'Une erreur est survenue' });
  }
}