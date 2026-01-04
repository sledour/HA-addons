'use client'; // Obligatoire pour utiliser useState et useEffect

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState({ status: "En attente...", message: "" });

  useEffect(() => {
    // Appel au Backend (port 3001)
    fetch('http://localhost:3001/api/status')
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => {
        console.error("Erreur Fetch:", err);
        setData({ status: "Erreur", message: "Impossible de joindre le Backend" });
      });
  }, []);

  return (
    <div style={{ 
      backgroundColor: 'white', 
      color: 'black', 
      minHeight: '100vh', 
      padding: '40px', 
      fontFamily: 'sans-serif' 
    }}>
      <h1 style={{ color: '#03a9f4' }}>🎁 Application Gift</h1>
      
      <div style={{ 
        marginTop: '20px', 
        padding: '20px', 
        border: '2px solid #eee', 
        borderRadius: '10px' 
      }}>
        <h3>Test de communication (App Router) :</h3>
        <p><strong>Statut :</strong> {data.status}</p>
        <p><strong>Message :</strong> {data.message}</p>
        {data.timestamp && <p><small>Dernière mise à jour : {data.timestamp}</small></p>}
      </div>
    </div>
  );
}