export interface RawProduct {
  title: string;
  price: number;
  image: string;
  vendor: string;
}

export const searchOnline = async (query: string): Promise<RawProduct[]> => {
  // Plus tard, ici on appellera une API ou un scraper
  // Pour le test Harry Potter :
  return [
    {
      title: "Château de Poudlard LEGO 71043",
      price: 469.99,
      image: "https://images.example.com/lego-poudlard.jpg",
      vendor: "Amazon"
    },
    {
      title: "Baguette interactive Harry Potter",
      price: 29.90,
      image: "https://images.example.com/baguette.jpg",
      vendor: "Fnac"
    }
  ];
};