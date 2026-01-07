import React, { useState } from 'react';
import { ProductCard } from '../components/ProductCard';

// Structure des données venant du Scraper/Service
interface RawProduct {
  title: string;
  price: number;
  image: string;
  vendor: string;
}

export default function SearchPage() {
  const [results, setResults] = useState<RawProduct[]>([]);

  // Simulation de recherche Harry Potter
  const handleSearch = () => {
    const mockData: RawProduct[] = [
      {
        title: "Lego Harry Potter - Le Château de Poudlard",
        price: 449.99,
        image: "https://m.media-amazon.com/images/I/81S6nL-v7QL._AC_SL1500_.jpg",
        vendor: "Amazon"
      },
      {
        title: "Baguette Magique Harry Potter avec boîte",
        price: 39.95,
        image: "https://m.media-amazon.com/images/I/61m9-4-YmDL._AC_SL1000_.jpg",
        vendor: "Cdiscount"
      }
    ];
    setResults(mockData);
  };

  const handleFollow = (productName: string) => {
    console.log(`Ajout de ${productName} à la base de données Prisma...`);
    // Prochaine étape : appel à ton service Prisma ici
  };

  return (
    <div className="min-h-screen bg-[#0f172a] p-8 text-white">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-extrabold mb-4">Recherche</h1>
          <div className="flex gap-4">
            <input 
              type="text" 
              placeholder="Ex: Harry Potter..." 
              className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 w-full max-w-md focus:outline-none focus:border-blue-500"
            />
            <button 
              onClick={handleSearch}
              className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-lg font-bold transition"
            >
              Rechercher
            </button>
          </div>
        </header>

        {/* GRILLE RESPONSIVE : 1 colonne mobile, 4 colonnes PC */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.map((product, index) => (
            <ProductCard 
              key={index}
              name={product.title}      // On mappe 'title' vers 'name'
              price={product.price}
              store={product.vendor}    // On mappe 'vendor' vers 'store'
              imageUrl={product.image}  // On mappe 'image' vers 'imageUrl'
              onFollow={() => handleFollow(product.title)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}