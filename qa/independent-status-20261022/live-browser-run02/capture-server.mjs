import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const output = path.join(root, 'evidence');
const port = Number(process.argv[2] ?? 41838);
const maxBytes = 5 * 1024 * 1024;

const server = http.createServer(async (request, response) => {
  if (request.method === 'GET' && request.url === '/health') {
    response.writeHead(200, { 'content-type': 'text/plain' }).end('ready');
    return;
  }
  const match = request.method === 'POST' && /^\/([a-z0-9][a-z0-9_-]{0,79}\.jpg)$/i.exec(request.url ?? '');
  if (!match || request.headers['content-type'] !== 'image/jpeg') {
    response.writeHead(404).end('not found');
    return;
  }

  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > maxBytes) {
      response.writeHead(413).end('image too large');
      return;
    }
    chunks.push(chunk);
  }
  await fs.mkdir(output, { recursive: true });
  await fs.writeFile(path.join(output, match[1]), Buffer.concat(chunks));
  response.writeHead(201, { 'content-type': 'application/json' }).end(JSON.stringify({ name: match[1], bytes: size }));
});

server.listen(port, '127.0.0.1', () => process.stdout.write(`capture receiver ready on 127.0.0.1:${port}\n`));
