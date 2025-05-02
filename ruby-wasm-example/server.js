const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 12000;

const server = http.createServer((req, res) => {
  // Set CORS headers to allow embedding in iframe
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle requests
  if (req.url === '/' || req.url === '/index.html') {
    fs.readFile(path.join(__dirname, 'index.html'), (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading index.html');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  } else if (req.url === '/advanced.html') {
    fs.readFile(path.join(__dirname, 'advanced.html'), (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading advanced.html');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  } else if (req.url === '/tsubaki-factory-chart.html') {
    fs.readFile(path.join(__dirname, 'tsubaki-factory-chart.html'), (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading tsubaki-factory-chart.html');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  } else if (req.url === '/menu') {
    // Create a simple menu page
    const menuHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Ruby.wasm Examples</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
          }
          h1 {
            color: #333;
          }
          ul {
            list-style-type: none;
            padding: 0;
          }
          li {
            margin-bottom: 10px;
          }
          a {
            display: block;
            padding: 10px 15px;
            background-color: #f5f5f5;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
          }
          a:hover {
            background-color: #e0e0e0;
          }
          .description {
            margin-top: 5px;
            color: #666;
          }
        </style>
      </head>
      <body>
        <h1>Ruby.wasm Examples</h1>
        <ul>
          <li>
            <a href="/index.html">Basic Example</a>
            <div class="description">Simple implementation with Chart.js and Ruby.wasm</div>
          </li>
          <li>
            <a href="/advanced.html">Advanced Example</a>
            <div class="description">Full-featured implementation with API support, CSV export, and improved UI</div>
          </li>
          <li>
            <a href="/tsubaki-factory-chart.html">つばきファクトリー Chart</a>
            <div class="description">Real API data for "つばきファクトリー" keyword with Chart.js visualization</div>
          </li>
        </ul>
      </body>
      </html>
    `;
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(menuHtml);
  } else {
    // Redirect to menu
    res.writeHead(302, { 'Location': '/menu' });
    res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${PORT}/`);
  console.log(`Menu available at http://0.0.0.0:${PORT}/menu`);
  console.log(`Basic example at http://0.0.0.0:${PORT}/index.html`);
  console.log(`Advanced example at http://0.0.0.0:${PORT}/advanced.html`);
});