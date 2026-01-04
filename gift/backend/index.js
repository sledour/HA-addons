const express = require('express');
const cors = require('cors');
const app = express();
const port = 3001;

app.use(cors());

app.get('/api/status', (req, res) => {
  res.json({ 
    status: "Connecté", 
    message: "Le Backend répond parfaitement au Frontend !",
    timestamp: new Date().toLocaleTimeString()
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Backend API running on port ${port}`);
});