'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './register.module.css';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (res.ok) {
        // Redirection vers le login après succès
        router.push('/login');
      } else {
        const data = await res.json();
        setError(data.error || "Une erreur est survenue.");
      }
    } catch (err) {
      setError("Impossible de contacter le serveur.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>Créer un compte</h1>
        {error && <p className={styles.error}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Pseudo</label>
            <input 
              type="text" required
              onChange={(e) => setForm({...form, pseudo: e.target.value})}
            />
          </div>
          <div className={styles.formGroup}>
            <label>Email</label>
            <input 
              type="email" required
              onChange={(e) => setForm({...form, email: e.target.value})}
            />
          </div>
          <div className={styles.formGroup}>
            <label>Mot de passe</label>
            <input 
              type="password" required
              onChange={(e) => setForm({...form, password: e.target.value})}
            />
          </div>
          <button type="submit" style={{width: '100%', marginTop: '1rem'}}>
            S'inscrire
          </button>
        </form>
        <p style={{textAlign: 'center', marginTop: '1rem'}}>
          Déjà un compte ? <a href="/login" style={{color: '#03a9f4'}}>Se connecter</a>
        </p>
      </div>
    </div>
  );
}