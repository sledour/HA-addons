'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Clic détecté !"); // Si tu ne vois pas ça dans F12, le problème est ici.

    try {
      // ON ENLÈVE LE SLASH AVANT 'api'
      const res = await fetch('api/auth/register', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (res.ok) {
        alert("Inscription réussie !");
        router.push('../'); // Retour au login
      } else {
        alert("Erreur lors de l'inscription");
      }
    } catch (err) {
      console.error("Erreur réseau :", err);
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