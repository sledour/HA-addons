'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
  const router = useRouter();

  const handleSubmit = async (e) => {
  e.preventDefault();
  
  // Le ../ est crucial pour remonter d'un niveau par rapport au dossier /register/
  const res = await fetch('../api/auth/register', { 
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form),
  });

  if (res.ok) {
    alert("Compte créé !");
    router.push('../'); 
  } else {
    alert("Erreur lors de l'inscription");
  }
};

  return (
    <div style={{ padding: '2rem', color: 'black', background: 'white' }}>
      <h1>Créer un compte</h1>
      {/* L'attribut onSubmit est CRUCIAL ici */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <input 
          type="text" 
          placeholder="Pseudo" 
          required 
          onChange={e => setForm({...form, pseudo: e.target.value})} 
        />
        <input 
          type="email" 
          placeholder="Email" 
          required 
          onChange={e => setForm({...form, email: e.target.value})} 
        />
        <input 
          type="password" 
          placeholder="Mot de passe" 
          required 
          onChange={e => setForm({...form, password: e.target.value})} 
        />
        <button type="submit" style={{ padding: '0.5rem', cursor: 'pointer' }}>
          S'inscrire
        </button>
      </form>
      <p>
        <Link href="../">Retour au login</Link>
      </p>
    </div>
  );
}