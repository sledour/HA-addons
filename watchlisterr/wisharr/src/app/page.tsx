'use client';

import React from 'react';
import { RegisterForm } from '../components/auth/RegisterForm';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0f172a] flex flex-col items-center justify-center p-6 text-white">
      {/* Header Style Wisharr */}
      <div className="mb-10 text-center">
        <h1 className="text-5xl font-extrabold tracking-tighter">
          <span className="text-blue-500">Wish</span>arr
        </h1>
        <p className="text-slate-400 mt-2 text-sm uppercase tracking-widest font-semibold">
          Foyer & Partage
        </p>
      </div>

      {/* Le formulaire d'inscription qu'on a créé ensemble */}
      <div className="w-full max-w-md">
        <RegisterForm />
      </div>

      <footer className="mt-12 text-slate-500 text-xs">
        &copy; 2026 Wisharr — Gestion de listes de souhaits
      </footer>
    </main>
  );
}