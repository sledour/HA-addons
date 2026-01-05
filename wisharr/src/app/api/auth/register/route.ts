export const dynamic = 'force-dynamic';
import { NextResponse } from 'next/server';
import { registerUser } from '@/services/auth.service';

// On exporte une fonction nommée pour le verbe HTTP voulu
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password, name } = body;

    if (!email || !password || !name) {
      return NextResponse.json(
        { message: 'Champs manquants' },
        { status: 400 }
      );
    }

    const user = await registerUser(email, password, name);

    return NextResponse.json(
      { message: 'Succès', userId: user.id },
      { status: 201 }
    );
  } catch (error: any) {
    return NextResponse.json(
      { message: error.message || 'Erreur serveur' },
      { status: 500 }
    );
  }
}