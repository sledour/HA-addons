import React from 'react';

interface ProductProps {
  name: string;
  price: number;
  store: string;
  imageUrl: string;
  onFollow?: () => void;
}

export const ProductCard = ({ name, price, store, imageUrl, onFollow }: ProductProps) => {
  return (
    <div className="group bg-slate-800/50 rounded-xl overflow-hidden shadow-xl border border-slate-700 hover:border-blue-500 hover:bg-slate-800 transition-all duration-300">
      <div className="relative h-48 w-full overflow-hidden bg-slate-900">
        <img 
          src={imageUrl || 'https://via.placeholder.com/400x300?text=No+Image'} 
          alt={name} 
          className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-white text-[10px] uppercase tracking-widest px-2 py-1 rounded-md border border-white/10">
          {store}
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-white font-semibold text-lg truncate mb-1 group-hover:text-blue-400 transition-colors" title={name}>
          {name}
        </h3>
        
        <div className="flex items-center justify-between mt-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Prix actuel</span>
            <span className="text-emerald-400 font-mono text-xl font-bold">
              {price.toFixed(2)}€
            </span>
          </div>

          <button 
            onClick={(e) => {
              e.preventDefault();
              onFollow?.();
            }}
            className="bg-blue-600 hover:bg-blue-500 active:scale-95 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-blue-900/20"
          >
            Suivre
          </button>
        </div>
      </div>
    </div>
  );
};