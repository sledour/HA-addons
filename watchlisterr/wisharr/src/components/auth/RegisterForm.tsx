import React, { useState } from 'react';

export const RegisterForm = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.message || "Erreur lors de l'inscription");

      setSuccess(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="bg-emerald-500/10 border border-emerald-500 p-6 rounded-xl text-emerald-500 text-center shadow-lg">
        <p className="font-bold text-lg mb-2">Compte créé !</p>
        <p className="text-sm">Vous pouvez maintenant retourner à la page de connexion.</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-2xl">
      <h2 className="text-2xl font-bold text-white mb-6 text-center tracking-tight">Inscription</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-slate-400 text-xs font-bold uppercase mb-1">Nom complet</label>
          <input 
            type="text" 
            required 
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition" 
          />
        </div>
        
        <div>
          <label className="block text-slate-400 text-xs font-bold uppercase mb-1">Email</label>
          <input 
            type="email" 
            required 
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition" 
          />
        </div>

        <div>
          <label className="block text-slate-400 text-xs font-bold uppercase mb-1">Mot de passe</label>
          <input 
            type="password" 
            required 
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition" 
          />
        </div>

        {error && <p className="text-red-400 text-xs bg-red-400/10 border border-red-400/20 p-2 rounded">{error}</p>}

        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white font-bold py-3 rounded-lg mt-4 transition-all shadow-lg shadow-blue-900/20 active:scale-[0.98]"
        >
          {loading ? "Création en cours..." : "S'enregistrer"}
        </button>
      </form>
    </div>
  );
};