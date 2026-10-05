import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { listeningMessage, occupiedPortMessage, selectedPort } from './dev-port.mjs';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const types = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.avif': 'image/avif' };
const port = selectedPort(process.argv.slice(2), process.env);
const server = http.createServer(async (req, res) => {
  try {
    const relative = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const target = path.resolve(root, '.' + (relative === '/' ? '/index.html' : relative));
    if (path.relative(root, target).startsWith('..')) throw new Error('Outside root');
    const body = await fs.readFile(target);
    res.writeHead(200, { 'Content-Type': types[path.extname(target)] ?? 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end('Not found');
  }
});
server.on('error', error => {
  if (error.code === 'EADDRINUSE') {
    console.error(occupiedPortMessage(port));
    process.exit(1);
  }
  console.error(error);
  process.exit(1);
});
server.listen(port, '127.0.0.1', () => console.log(listeningMessage(port)));
