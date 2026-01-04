const express = require('express');
const cors = require('cors');
const app = express();
const port = 3001; // Le backend sur le 3001

app.use(cors());
app.use(express.json());

app.get('/api/status', (req, res) => {
  res.json({ 
    status: "online", 
    message: "Le backend Gift répond bien !" 
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Backend API running on port ${port}`);
});