const express = require('express');
const path = require('path');
const fs = require('fs');
const { Pool } = require('pg');
const app = express();
const port = 3000;

console.clear(); 
console.log("========================================");
console.log("    🚀 DÉMARRAGE DU SYSTÈME GIFT   ");
console.log("========================================");

// --- Middleware important ---
app.use(express.json());

const pool = new Pool({
  host: 'db21ed7f-postgres-latest',
  port: 5432,
  user: 'postgres',
  password: 'homeassistant',
  database: 'postgres', 
});

const initDb = async () => {
  try {
    const client = await pool.connect();
    console.log("✅ Connecté à PostgreSQL");
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        pseudo TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
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
    console.log("✅ Tables prêtes.");
    client.release();
  } catch (err) {
    console.error("❌ Erreur initDb:", err.message);
  }
};
initDb();

const frontendPath = path.resolve(__dirname, '../frontend/out');

// --- ROUTES API ---

app.post('/api/auth/register', async (req, res) => {
  const { email, pseudo, password } = req.body;
  console.log(`📩 [API POST] Tentative d'inscription : ${email}`);
  
  try {
    const result = await pool.query(
      'INSERT INTO users (email, pseudo, password) VALUES ($1, $2, $3) RETURNING id, email, pseudo',
      [email, pseudo, password]
    );
    console.log(`✅ Utilisateur créé ID: ${result.rows[0].id}`);
    res.json(result.rows[0]);
  } catch (err) {
    console.error("❌ Erreur DB Inscription:", err.message);
    res.status(500).json({ error: "Email déjà utilisé ou erreur serveur." });
  }
});

app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;
    console.log(`🔑 [API POST] Tentative de connexion : ${email}`);
    try {
      const result = await pool.query(
        'SELECT id, email, pseudo FROM users WHERE email = $1 AND password = $2',
        [email, password]
      );
      if (result.rows.length > 0) {
        res.json({ message: "Connexion réussie", user: result.rows[0] });
      } else {
        res.status(401).json({ error: "Email ou mot de passe incorrect" });
      }
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: "Erreur serveur" });
    }
});

// --- SERVICE FRONTEND ---

// On sert les fichiers statiques (_next, images, etc.)
app.use(express.static(frontendPath));

app.get('*', (req, res) => {
  // On ignore les appels API
  if (req.url.startsWith('/api')) return res.status(404).json({error: "API non trouvée"});

  const cleanUrl = req.url.split('?')[0];
  console.log(`🌐 Navigation vers : ${cleanUrl}`);

  // Tente d'envoyer /dossier/index.html
  let targetPath = path.join(frontendPath, cleanUrl, 'index.html');
  
  if (fs.existsSync(targetPath)) {
      return res.sendFile(targetPath);
  } else {
      // Si on ne trouve pas de dossier correspondant, on renvoie l'index racine (SPA)
      return res.sendFile(path.join(frontendPath, 'index.html'));
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur Gift sur le port ${port}`);
});