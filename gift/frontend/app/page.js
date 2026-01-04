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
        console.log("UX: Clic Connexion");

        try {
            const res = await fetch('api/auth/login', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (res.ok) {
                console.log("UX: Redirection Dashboard");
                router.push('dashboard/'); // Chemin relatif sans / au début
            }
        } catch (err) {
            console.error("UX Error:", err);
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