'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

const handleSubmit = async (e) => {
  e.preventDefault();
  console.log("Tentative d'envoi des données :", form); // Vérifie si le bouton réagit

  try {
    // Utilise un chemin relatif sans le premier slash si l'autre échoue
    const res = await fetch('api/auth/register', { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });

    console.log("Statut de la réponse :", res.status);

      const data = await res.json();

      if (res.ok) {
        // ✅ SUCCÈS : L'utilisateur est créé
        console.log("Utilisateur créé avec succès");
        alert("Compte créé avec succès ! Connectez-vous maintenant.");
        
        // On redirige vers le login (chemin relatif Ingress)
        router.push('../'); 
      } else {
        // ❌ ERREUR API (ex: email déjà pris)
        setError(data.error || "Une erreur est survenue lors de l'inscription.");
      }
    } catch (err) {
      // ❌ ERREUR RÉSEAU
      setError("Impossible de contacter le serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Inscription</h1>
      
      {/* Affichage de l'erreur si elle existe */}
      {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '300px' }}>
        <input 
          type="text" 
          placeholder="Pseudo" 
          onChange={e => setForm({...form, pseudo: e.target.value})} 
          required 
        />
        <input 
          type="email" 
          placeholder="Email" 
          onChange={e => setForm({...form, email: e.target.value})} 
          required 
        />
        <input 
          type="password" 
          placeholder="Mot de passe" 
          onChange={e => setForm({...form, password: e.target.value})} 
          required 
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Création en cours...' : "S'inscrire"}
        </button>
      </form>

      <p style={{ marginTop: '1rem' }}>
        Déjà un compte ? <Link href="../" style={{ color: '#03a9f4' }}>Se connecter</Link>
      </p>
    </div>
  );
}