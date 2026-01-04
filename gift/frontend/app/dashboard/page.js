'use client';
import { useState, useEffect } from 'react';

export default function PersonnalListPage() {
    const [gifts, setGifts] = useState([]);

    useEffect(() => {
        console.log("UX: Chargement de la liste perso...");
        // On ajoutera le fetch API ici plus tard
    }, []);

    return (
        <div>
            <h1>Ma Liste de Cadeaux</h1>
            <p>Ici, tu peux ajouter les cadeaux que tu aimerais recevoir.</p>
            
            <div className="gift-list">
                {/* Simulation d'item */}
                <div style={{background:'white', padding:'1rem', borderRadius:'8px', marginBottom:'1rem'}}>
                    <strong>Exemple : Console PS5</strong>
                    <p>Pour jouer avec les copains</p>
                </div>
            </div>
            
            <button className="btn-add" style={{position:'fixed', right:'20px', bottom:'90px', borderRadius:'50%', width:'60px', height:'60px', backgroundColor:'#03a9f4', color:'white', border:'none', fontSize:'24px', boxShadow:'0 4px 10px rgba(0,0,0,0.3)'}}>+</button>
        </div>
    );
}