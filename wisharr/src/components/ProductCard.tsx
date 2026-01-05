import React from 'react';

// On définit une interface pour le typage (Fonctionnel)
interface ProductProps {
  name: string;
  price: number;
  store: string;
  imageUrl: string;
}

// Le composant s'occupe UNIQUEMENT du rendu (Style)
export const ProductCard = ({ name, price, store, imageUrl }: ProductProps) => {
  return (
    <div className="bg-slate-800 rounded-lg overflow-hidden shadow-lg border border-slate-700 hover:border-blue-500 transition-all">
      <img src={imageUrl} alt={name} className="w-full h-48 object-cover" />
      <div className="p-4">
        <h3 className="text-white font-bold text-lg truncate">{name}</h3>
        <p className="text-slate-400 text-sm">{store}</p>
        <div className="mt-4 flex justify-between items-center">
          <span className="text-emerald-400 font-mono text-xl">{price}€</span>
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded text-sm transition">
            Suivre
          </button>
        </div>
      </div>
    </div>
  );
};