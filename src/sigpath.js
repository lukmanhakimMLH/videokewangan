const ot=require('opentype.js'),fs=require('fs');
const font=ot.parse(fs.readFileSync('fonts/monsieur-la-doulaise.woff').buffer);
const p=font.getPath('Lukman',0,0,200,{features:{liga:false,rlig:false,ccmp:false,calt:false,kern:true}});
const bb=p.getBoundingBox();console.error(bb);
// normalize to origin
const d=p.toPathData(2);
const W=Math.ceil(bb.x2-bb.x1)+20,H=Math.ceil(bb.y2-bb.y1)+20;
fs.writeFileSync('sig.json',JSON.stringify({d,vb:`${Math.floor(bb.x1)-10} ${Math.floor(bb.y1)-10} ${W} ${H}`,W,H}));
fs.writeFileSync('sigcheck.html',`<body style="background:#222;margin:0"><svg viewBox="${Math.floor(bb.x1)-10} ${Math.floor(bb.y1)-10} ${W} ${H}" width="${W*2}" height="${H*2}"><path d="${d}" fill="#d4af37"/></svg>`);
