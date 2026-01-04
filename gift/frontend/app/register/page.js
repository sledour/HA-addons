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
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (res.ok) {
        // Succès ! On redirige vers la racine (le login)
        router.push('/');
      } else {
        setError(data.error || "Erreur lors de l'inscription");
      }
    } catch (err) {
      setError("Le serveur est injoignable.");
    } finally {
      setLoading(false);
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
          Déjà inscrit ? <a href="/" style={{ color: '#03a9f4', textDecoration: 'none' }}>Se connecter</a>
        </p>
      </div>
    </div>
  );
}