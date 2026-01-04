'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [gifts, setGifts] = useState([]);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');

  // Charger les cadeaux depuis le backend
  const fetchGifts = async () => {
    try {
      const res = await fetch('/api/gifts');
      const data = await res.json();
      setGifts(data);
    } catch (err) {
      console.error("Erreur chargement:", err);
    }
  };

  useEffect(() => {
    fetchGifts();
  }, []);

  // Envoyer un nouveau cadeau
  const addGift = async (e) => {
    e.preventDefault();
    if (!name) return;

    await fetch('/api/gifts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: desc }),
    });

    setName('');
    setDesc('');
    fetchGifts(); // Recharger la liste
  };

  return (
    <div style={{ backgroundColor: '#f5f5f5', color: '#333', minHeight: '100vh', padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', backgroundColor: 'white', padding: '30px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#03a9f4', textAlign: 'center' }}>🎁 Ma Liste de Cadeaux</h1>
        
        {/* Formulaire */}
        <form onSubmit={addGift} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '30px' }}>
          <input 
            type="text" placeholder="Nom du cadeau" value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ddd' }}
          />
          <input 
            type="text" placeholder="Description (optionnel)" value={desc}
            onChange={(e) => setDesc(e.target.value)}
            style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ddd' }}
          />
          <button type="submit" style={{ padding: '10px', backgroundColor: '#03a9f4', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            Ajouter à la liste
          </button>
        </form>

        <hr />

        {/* Liste des cadeaux */}
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {gifts.map((gift) => (
            <li key={gift.id} style={{ padding: '15px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
              <div>
                <strong>{gift.name}</strong>
                <p style={{ margin: 0, fontSize: '0.9em', color: '#666' }}>{gift.description}</p>
              </div>
              <span>{gift.bought ? '✅' : '⏳'}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}