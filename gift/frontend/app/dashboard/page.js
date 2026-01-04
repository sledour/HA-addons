'use client';
import { useState, useEffect } from 'react';

export default function PersonnalListPage() {
    const [gifts, setGifts] = useState([]);

    const addGift = () => {
        const name = prompt("Nom du cadeau :");
        if (name) {
            console.log("UX: Ajout du cadeau", name);
            // Simulation d'ajout local en attendant le fetch POST
            setGifts([...gifts, { id: Date.now(), name: name, description: 'Ajouté manuellement' }]);
        }
    };

    return (
        <div>
            <h1>Ma Liste de Cadeaux</h1>
            <div className="gift-list">
                {gifts.map(gift => (
                    <div key={gift.id} style={{background:'white', padding:'1rem', borderRadius:'8px', marginBottom:'1rem', color: '#333'}}>
                        <strong>{gift.name}</strong>
                    </div>
                ))}
            </div>
            
            <button 
                onClick={addGift} 
                style={{
                    position:'fixed', right:'20px', bottom:'90px', 
                    borderRadius:'50%', width:'60px', height:'60px', 
                    backgroundColor:'#03a9f4', color:'white', border:'none', 
                    fontSize:'24px', cursor: 'pointer', zIndex: 1001
                }}
            >
                +
            </button>
        </div>
    );
}