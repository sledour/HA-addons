const express = require('express');
const path = require('path');
const fs = require('fs'); // Nécessaire pour le diagnostic
const { Pool } = require('pg');
const app = express();
const port = 3000;

// --- NETTOYAGE DES LOGS ---
console.clear(); 
console.log("========================================");
console.log("    🚀 DÉMARRAGE DU SYSTÈME GIFT   ");
console.log("========================================");

app.use(express.json());

// --- Configuration PostgreSQL ---
const pool = new Pool({
  host: 'db21ed7f-postgres-latest',
  port: 5432,
  user: 'postgres',
  password: 'homeassistant',
  database: 'postgres', 
});

// --- Initialisation de la Base de Données ---
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

    console.log("✅ Tables 'users' et 'gifts' prêtes.");
    client.release();
  } catch (err) {
    console.error("❌ Erreur initDb:", err.message);
  }
};

initDb();

// --- DIAGNOSTIC DU FRONTEND ---
const frontendPath = path.resolve(__dirname, '../frontend/out');
console.log("🔍 Vérification du dossier frontend/out...");

if (fs.existsSync(frontendPath)) {
    const files = fs.readdirSync(frontendPath);
    console.log("📁 Fichiers trouvés à la racine /out :", files);
    if (files.includes('register')) {
        console.log("✅ Dossier 'register' présent.");
    } else {
        console.log("⚠️ ATTENTION : Dossier 'register' introuvable dans /out");
    }
} else {
    console.log("❌ ERREUR : Le dossier /frontend/out n'existe pas !");
}

// --- Routes API ---

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
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
    res.status(500).json({ error: "Erreur serveur lors de la connexion" });
  }
});

app.post('/api/auth/register', async (req, res) => {
  const { email, pseudo, password } = req.body;
  console.log(`📩 Tentative d'inscription pour : ${email}`); // <--- AJOUTE ÇA
  
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

app.get('/api/gifts', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM gifts ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// --- Service du Frontend ---

// 1. Logger chaque requête pour comprendre le 404
app.use((req, res, next) => {
    if (!req.url.startsWith('/api')) {
        console.log(`🌐 Navigation vers : ${req.url}`);
    }
    next();
});

// 2. Servir les fichiers statiques (CSS, JS, Images)
app.use(express.static(frontendPath));

// 3. Gestion intelligente du routage (SPA + Ingress)
app.get('*', (req, res) => {
  if (req.url.startsWith('/api')) return res.status(404).json({error: "API non trouvée"});

  const cleanUrl = req.url.split('?')[0];
  
  // On teste le chemin direct (ex: /register/)
  let targetPath = path.join(frontendPath, cleanUrl, 'index.html');
  
  // Si on demande juste "/register" sans le slash, on corrige
  if (!fs.existsSync(targetPath)) {
      targetPath = path.join(frontendPath, cleanUrl, 'index.html');
  }

  console.log(`🔎 Tentative d'accès physique : ${targetPath}`);

  if (fs.existsSync(targetPath)) {
      console.log(`✅ Fichier trouvé ! Envoi de : ${targetPath}`);
      return res.sendFile(targetPath);
  } else {
      console.log(`❌ Fichier non trouvé à l'emplacement physique. Renvoi vers index.html racine.`);
      return res.sendFile(path.join(frontendPath, 'index.html'));
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur Gift unique sur le port ${port}`);
});