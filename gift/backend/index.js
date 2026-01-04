const express = require('express');
const path = require('path');
const { Pool } = require('pg');
const app = express();
const port = 3000; // On passe sur le port 3000 pour l'Ingress

app.use(express.json());

// --- Tes routes API ---
const pool = new Pool({ /* ... tes identifiants postgres ... */ });

app.get('/api/gifts', async (req, res) => {
  const result = await pool.query('SELECT * FROM gifts ORDER BY created_at DESC');
  res.json(result.rows);
});

app.post('/api/gifts', async (req, res) => {
  const { name, description } = req.body;
  const result = await pool.query('INSERT INTO gifts (name, description) VALUES ($1, $2) RETURNING *', [name, description]);
  res.json(result.rows[0]);
});

// --- Servir le Frontend ---
// On pointe vers le dossier où Next.js va construire les fichiers
app.use(express.static(path.join(__dirname, '../frontend/out')));

// Pour toutes les autres routes, on renvoie l'index.html (Single Page App)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/out/index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Serveur unique tournant sur le port ${port}`);
});