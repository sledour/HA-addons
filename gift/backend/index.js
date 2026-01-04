const express = require('express');
const path = require('path');
const fs = require('fs');
const { Pool } = require('pg');
const app = express();
const port = 3000;

console.clear(); 
console.log("========================================");
console.log("    🛡️ SYSTÈME GIFT : MODE NAVIGATION   ");
console.log("========================================");

app.use(express.json());

// --- Database ---
const pool = new Pool({
  host: 'db21ed7f-postgres-latest',
  port: 5432,
  user: 'postgres',
  password: 'homeassistant',
  database: 'postgres', 
});

// --- Middleware de Journalisation (Audit Trail) ---
app.use((req, res, next) => {
    const now = new Date().toLocaleTimeString();
    if (!req.url.includes('_next')) { // On filtre le bruit de Next.js
        console.log(`[${now}] 📡 ${req.method} reçu sur : ${req.url}`);
    }
    next();
});

const frontendPath = path.resolve(__dirname, '../frontend/out');

// --- Routes API (UX validation) ---
// Login & Register
app.post('/api/auth/login', async (req, res) => {
    console.log("📩 [API] Tentative de connexion...");
    res.json({ success: true, message: "Login validé par le backend" });
});

app.post('/api/auth/register', async (req, res) => {
    console.log("📩 [API] Tentative d'inscription...");
    res.json({ success: true, message: "Inscription validée par le backend" });
});

// My gift list
app.get('/api/gifts/me', async (req, res) => {
    console.log("📩 [API GET] Demande de la liste personnelle");
    // Plus tard, on filtrera par l'ID de l'utilisateur connecté
    try {
        const result = await pool.query('SELECT * FROM gifts ORDER BY created_at DESC');
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// --- Service Statique & Routage Ingress ---
app.use(express.static(frontendPath));

app.get('*', (req, res) => {
  if (req.url.startsWith('/api')) return res.status(404).json({error: "API non trouvée"});

  const cleanUrl = req.url.split('?')[0];
  const targetPath = path.join(frontendPath, cleanUrl, 'index.html');
  
  if (fs.existsSync(targetPath)) {
      return res.sendFile(targetPath);
  } else {
      // Pour les fichiers JS/CSS qui n'auraient pas été trouvés par static
      const directPath = path.join(frontendPath, cleanUrl);
      if (fs.existsSync(directPath) && !fs.lstatSync(directPath).isDirectory()) {
          return res.sendFile(directPath);
      }
      // Fallback SPA
      return res.sendFile(path.join(frontendPath, 'index.html'));
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 Serveur prêt sur le port ${port}`);
});