export default async function Home() {
  let data = { status: "Erreur", message: "Initialisation..." };

  try {
    // Ici, on appelle localhost car le serveur Next.js et le Backend 
    // sont dans le MÊME container Docker.
    const res = await fetch('http://localhost:3001/api/status', { cache: 'no-store' });
    data = await res.json();
  } catch (err) {
    console.error("Erreur Backend:", err);
    data = { status: "Erreur", message: "Le serveur Next n'a pas pu joindre le Backend interne." };
  }

  return (
    <div style={{ backgroundColor: 'white', color: 'black', minHeight: '100vh', padding: '40px', fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#03a9f4' }}>🎁 Application Gift</h1>
      
      <div style={{ marginTop: '20px', padding: '20px', border: '2px solid #eee', borderRadius: '10px' }}>
        <h3>Communication Interne (SSR) :</h3>
        <p><strong>Statut :</strong> {data.status}</p>
        <p><strong>Message :</strong> {data.message}</p>
        {data.timestamp && <p><small>Heure du serveur : {data.timestamp}</small></p>}
      </div>
    </div>
  );
}