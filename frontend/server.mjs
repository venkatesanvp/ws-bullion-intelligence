// Local built-asset server; no credentials, provider connection or runtime data storage.
import http from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,extname,sep} from 'node:path';
const root=resolve('dist');
const apiOrigin=process.env.LOCAL_API_ORIGIN||'http://127.0.0.1:8000';
if(!/^http:\/\/(127\.0\.0\.1|localhost):[0-9]{1,5}$/.test(apiOrigin))throw Error('Loopback API origin required');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.txt':'text/plain; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon'};
const server=http.createServer(async(req,res)=>{
 res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Frame-Options','DENY');
 res.setHeader('Content-Security-Policy',`default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' ${apiOrigin}; frame-ancestors 'none'; base-uri 'self'; object-src 'none'`);
 if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
 try{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(pathname==='/_health'){res.writeHead(200,{'Content-Type':'text/plain'});res.end('ok');return;}
  let path=resolve(root,'.'+pathname);
  if(path!==root&&!path.startsWith(root+sep)){res.writeHead(400);res.end();return;}
  try{if((await stat(path)).isDirectory())path=resolve(path,'index.html');}catch{if(extname(path)){res.writeHead(404);res.end();return;}path=resolve(root,'index.html');}
  const body=await readFile(path);res.setHeader('Content-Type',types[extname(path)]||'application/octet-stream');res.setHeader('Cache-Control',path.includes(sep+'assets'+sep)?'public, max-age=31536000, immutable':'no-cache');res.writeHead(200);res.end(req.method==='HEAD'?undefined:body);
 }catch{res.writeHead(404);res.end();}
});
server.listen(5173,'0.0.0.0');
for(const signal of ['SIGTERM','SIGINT'])process.on(signal,()=>{server.close(()=>process.exit(0));setTimeout(()=>process.exit(1),10000).unref();});
