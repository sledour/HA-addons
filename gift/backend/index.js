const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// Configuration de la connexion PostgreSQL
const pool = new Pool({
  host: 'db21ed7f-postgres-latest',
  port: 5432,
  user: 'postgres',
  password: 'homeassistant',
  database: 'postgres', // Par défaut, l'addon utilise souvent ce nom de DB
});

// Test de connexion et création de la table si elle n'existe pas
const initDb = async () => {
  try {
    const client = await pool.connect();
    console.log("✅ Connecté à PostgreSQL avec succès !");
    
    await client.query(`
      CREATE TABLE IF NOT EXISTS gifts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        bought BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    console.log("✅ Table 'gifts' vérifiée/créée.");
    client.release();
  } catch (err) {
    console.error("❌ Erreur de connexion PostgreSQL:", err.message);
  }
};

initDb();

// Route pour récupérer les cadeaux
app.get('/api/gifts', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM gifts ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route de statut modifiée
app.get('/api/status', async (req, res) => {
  try {
    const dbTest = await pool.query('SELECT NOW()');
    res.json({ 
      status: "Connecté", 
      database: "PostgreSQL Opérationnel",
      time: dbTest.rows[0].now
    });
  } catch (err) {
    res.json({ status: "Erreur", database: "Déconnecté" });
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Backend API running on port ${port}`);
});