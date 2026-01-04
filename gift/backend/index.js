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

// Route de connexion (Login)
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  
  try {
    // On cherche l'utilisateur avec l'email ET le mot de passe
    const result = await pool.query(
      'SELECT id, email, pseudo FROM users WHERE email = $1 AND password = $2',
      [email, password]
    );

    if (result.rows.length > 0) {
      // Utilisateur trouvé !
      res.json({
        message: "Connexion réussie",
        user: result.rows[0]
      });
    } else {
      // Aucun utilisateur ne correspond
      res.status(401).json({ error: "Email ou mot de passe incorrect" });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erreur serveur lors de la connexion" });
  }
});

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

const frontendPath = path.resolve(__dirname, '../frontend/out');

// 1. Servir les fichiers statiques normalement
app.use(express.static(frontendPath));

// 2. Route API (doivent être AVANT le app.get('*'))
app.post('/api/auth/register', async (req, res) => { /* ... */ });
app.post('/api/auth/login', async (req, res) => { /* ... */ });

// 3. LA FIX INGRESS : Si on demande une page (comme /register), 
// et qu'elle n'est pas trouvée en fichier physique, on renvoie l'index.
app.get('*', (req, res) => {
  console.log("Routing Ingress pour :", req.url);
  res.sendFile(path.join(frontendPath, 'index.html'), (err) => {
    if (err) {
      res.status(500).send("Index.html introuvable dans " + frontendPath);
    }
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur Gift unique sur le port ${port}`);
});