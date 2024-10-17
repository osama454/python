const express = require('express');
const app = express();
const port = 3000;

// Route for the home page
app.get('/', (req, res) => {
  res.send('Hello, World!');
});

// Start the server
app.listen(3000, '0.0.0.0', () => {
  console.log(`Server running at http://127.0.0.1:${port}/`);
});
