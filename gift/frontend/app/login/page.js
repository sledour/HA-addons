'use client';
import { useState } from 'react';
import styles from './login.module.css'; // On importe le style dédié

export default function LoginPage() {
  const [email, setEmail] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    console.log("Tentative de connexion pour:", email);
  };

  return (
    <div className={styles.container}>
      <form className={styles.card} onSubmit={handleLogin}>
        <h1>Connexion 🎁</h1>
        <input 
          type="email" 
          placeholder="Ton adresse email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button type="submit">Se connecter</button>
        <p>Pas encore de compte ? <a href="/register">S'inscrire</a></p>
      </form>
    </div>
  );
}