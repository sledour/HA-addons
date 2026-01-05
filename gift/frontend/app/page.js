'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import './login.css'; // UI Séparée

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const router = useRouter();

    const handleLogin = async (e) => {
        e.preventDefault();
        console.log("UX: Tentative de connexion...");

        try {
            const res = await fetch('api/auth/login', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            // 1. On récupère le JSON renvoyé par le serveur
            const data = await res.json();

            if (res.ok) {
                // ✅ Le serveur a répondu 200 (OK)
                console.log("UX: Connexion réussie !");
                router.push('dashboard/'); 
            } else {
                // ❌ Le serveur a répondu 401 ou 500
                alert(data.error || "Identifiants incorrects");
            }
        } catch (err) {
            console.error("UX Error:", err);
            alert("Erreur de connexion au serveur.");
        }
    };

    return (
        <div className="login-wrapper">
            <div className="login-card">
                <h1 className="title">GIFT</h1>
                <p className="subtitle">Gestion collaborative de cadeaux</p>
                
                <form onSubmit={handleLogin} className="login-form">
                    <input 
                        type="email" 
                        placeholder="Email" 
                        onChange={e => setEmail(e.target.value)} 
                        required 
                    />
                    <input 
                        type="password" 
                        placeholder="Mot de passe" 
                        onChange={e => setPassword(e.target.value)} 
                        required 
                    />
                    <button type="submit" className="btn-primary">Se connecter</button>
                </form>

                <div className="footer-links">
                    <span>Pas de compte ? </span>
                    <Link href="register/" className="link">S'inscrire</Link>
                </div>
            </div>
        </div>
    );
}