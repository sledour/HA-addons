'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
    const [form, setForm] = useState({ email: '', pseudo: '', password: '' });
    const router = useRouter();

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("🔵 Bouton cliqué, données prêtes :", form);

        try {
            // On utilise '../api/...' pour remonter d'un cran par rapport au dossier /register/
            const res = await fetch('../api/auth/register', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form),
            });

            console.log("🟠 Réponse reçue, statut :", res.status);

            if (res.ok) {
                alert("Compte créé avec succès !");
                // On redirige vers le login (racine de l'addon)
                router.push('../'); 
            } else {
                const errorData = await res.json();
                alert("Erreur : " + (errorData.error || "Impossible de s'inscrire"));
            }
        } catch (err) {
            console.error("🔴 Erreur lors de l'envoi :", err);
            alert("Le serveur est injoignable. Vérifiez les logs du backend.");
        }
    };

    return (
        <div style={{ padding: '2rem', color: 'black', background: 'white', minHeight: '100vh' }}>
            <h1>Créer un compte</h1>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '300px' }}>
                <input 
                    type="text" 
                    placeholder="Pseudo" 
                    required 
                    autoComplete="off"
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
                <button type="submit" style={{ padding: '0.7rem', cursor: 'pointer', backgroundColor: '#03a9f4', color: 'white', border: 'none', borderRadius: '4px' }}>
                    S'inscrire
                </button>
            </form>
            <p style={{ marginTop: '1rem' }}>
                <Link href="../" style={{ color: '#03a9f4' }}>Retour au login</Link>
            </p>
        </div>
    );
}