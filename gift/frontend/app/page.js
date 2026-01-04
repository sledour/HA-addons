'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleLogin = async (e) => {
  e.preventDefault();
  
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (res.ok) {
    console.log("Connecté !", data.user);
    // On utilise un chemin relatif sans slash au début
    router.push('dashboard/'); 
  } else {
    alert(data.error || "Identifiants incorrects");
  }
};

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '12px', color: '#333', width: '300px' }}>
        <h1 style={{ textAlign: 'center', color: '#03a9f4' }}>Connexion</h1>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Mot de passe" onChange={e => setPassword(e.target.value)} required />
          <button type="submit">Se connecter</button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
          Pas de compte ? <Link href="register/" style={{ color: '#03a9f4' }}>S'inscrire</Link>
        </p>
      </div>
    </div>
  );
}