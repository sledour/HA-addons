const express = require('express');
const path = require('path');
const { Pool } = require('pg');
const app = express();
const port = 3000;

app.use(express.json());

// --- Configuration PostgreSQL ---
const pool = new Pool({
  host: 'db21ed7f-postgres-latest',
  port: 5432,
  user: 'postgres',
  password: 'homeassistant',
  database: 'postgres', // Base par défaut
});

// --- Initialisation de la Base de Données ---
const initDb = async () => {
  try {
    const client = await pool.connect();
    console.log("✅ Connecté à PostgreSQL");

    // Table Utilisateurs
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        pseudo TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Table Cadeaux (liée à un utilisateur plus tard)
    await client.query(`
      CREATE TABLE IF NOT EXISTS gifts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        bought BOOLEAN DEFAULT false,
        user_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    console.log("✅ Tables 'users' et 'gifts' prêtes.");
    client.release();
  } catch (err) {
    console.error("❌ Erreur initDb:", err.message);
  }
};

initDb();

// --- Routes API ---

// Inscription (simplifiée pour l'instant)
app.post('/api/auth/register', async (req, res) => {
  const { email, pseudo, password } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO users (email, pseudo, password) VALUES ($1, $2, $3) RETURNING id, email, pseudo',
      [email, pseudo, password]
    );
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Cet email est déjà utilisé ou erreur serveur." });
  }
});

// Récupérer les cadeaux
app.get('/api/gifts', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM gifts ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// --- Service du Frontend (Fichiers Statiques) ---
// On sert les fichiers exportés par Next.js (dossier out)
app.use(express.static(path.join(__dirname, '../frontend/out')));

// Redirection vers l'index pour toutes les autres routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/out/index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur Gift unique sur le port ${port}`);
});