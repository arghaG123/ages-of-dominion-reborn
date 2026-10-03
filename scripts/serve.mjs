import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const types={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.avif':'image/avif'};
const server=http.createServer(async (req,res)=>{
  try {
    const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname), target=path.resolve(root,'.'+(relative==='/'?'/index.html':relative));
    if (path.relative(root,target).startsWith('..')) throw new Error('Outside root');
    const body=await fs.readFile(target); res.writeHead(200,{'Content-Type':types[path.extname(target)]??'application/octet-stream','Cache-Control':'no-store'}); res.end(body);
  } catch { res.writeHead(404); res.end('Not found'); }
});
server.listen(4173,'127.0.0.1',()=>console.log('Reborn local preview: http://127.0.0.1:4173'));
