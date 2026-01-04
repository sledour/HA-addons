'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './register.module.css';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const res = await fetch('/api/auth/register', { // Route définie dans ton index.js
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form), // form contient email, pseudo, password
    });

    if (res.ok) {
      alert("Compte créé !");
      router.push('../'); // Retour au login après succès
    } else {
      const data = await res.json();
      alert(data.error || "Erreur");
    }
  } catch (err) {
    console.error("Erreur fetch:", err);
  }
};

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>Inscription 🎁</h1>
        {error && <p style={{color: 'red', textAlign: 'center'}}>{error}</p>}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input 
            type="text" placeholder="Pseudo" required 
            onChange={e => setForm({...form, pseudo: e.target.value})} 
          />
          <input 
            type="email" placeholder="Email" required 
            onChange={e => setForm({...form, email: e.target.value})} 
          />
          <input 
            type="password" placeholder="Mot de passe" required 
            onChange={e => setForm({...form, password: e.target.value})} 
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Création...' : 'Créer mon compte'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          Déjà inscrit ? <Link href="../" style={{ color: '#03a9f4' }}>Se connecter</Link>
        </p>
      </div>
    </div>
  );
}