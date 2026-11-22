/* =====================================================================
   PASUKAN — hierarki (peta minda) + rekrut oleh ejen
   - Leader tetapkan "upline" setiap ejen (users/<uid>.upline).
   - App leader bina pokok penuh dan tulis hierarki/<uid> = subtree ejen itu sahaja
     (peraturan Firestore: ejen hanya boleh baca hierarki/<uid sendiri>).
   - Rekrut ejen = item P100 jenis 'rekrut' dengan status Prospek → Coded.
     Leader sahkan sama ada dikira NR dalam MAPA (meta/mapa<tahun>.nrConfirm).
   ===================================================================== */
(function(){
const H = () => window.APA.h;
const STG = [['prospek','Prospek'],['temuduga','Temuduga'],['daftar','Daftar Exam'],['lulus','Lulus Exam'],['coded','Coded']];
const STN = Object.fromEntries(STG);
const GENC = ['var(--accent)','var(--C)','var(--S)','var(--I)','var(--D)'];
const genColor = g => GENC[Math.min(g, GENC.length-1)];
const T = { my:null };

/* ---------- gambar kecil untuk peta ---------- */
const thumbs = new Map();
function thumb(src){
  if(!src) return Promise.resolve('');
  if(thumbs.has(src)) return thumbs.get(src);
  const p = new Promise(res=>{ const i=new Image(); i.onload=()=>{ const c=document.createElement('canvas'); c.width=c.height=64;
    const s=Math.max(64/i.width,64/i.height), w=i.width*s, h=i.height*s; c.getContext('2d').drawImage(i,(64-w)/2,(64-h)/2,w,h);
    res(c.toDataURL('image/jpeg',0.7)); }; i.onerror=()=>res(''); i.src=src; });
  thumbs.set(src,p); return p;
}
const hash = s => { let h=0; for(let i=0;i<s.length;i++) h=(h*31+s.charCodeAt(i))|0; return String(h); };

/* ---------- pokok ---------- */
async function allNodes(){
  const h=H(), S=h.S, rootId = S.uid || 'me';
  const team = new Map((S.team||[]).map(a=>[a.uid,a]));
  const users = (S.users||[]).filter(u=>u.status==='approved' && u.uid!==rootId);
  const mk = async (id, u, a) => { const C = a ? h.calc(a, h.THIS_Y) : null;
    return { id, nama:(a?.profile?.nama)||u?.nama||'', kod:a?.profile?.kod||u?.kod||'', upline: u ? (u.upline && u.upline!==id ? u.upline : rootId) : null,
      foto: await thumb(a?.profile?.foto), ace: C?Math.round(C.achieve):0, kes: C?C.kes:0 }; };
  const me = team.get(rootId) || team.get('local') || S.me && {profile:S.me.profile, years:S.me.years};
  const nodes = [await mk(rootId, null, me)]; nodes[0].nama ||= 'Leader'; nodes[0].leader = true;
  for(const u of users) nodes.push(await mk(u.uid, u, team.get(u.uid)));
  const ids = new Set(nodes.map(n=>n.id)); nodes.forEach(n=>{ if(n.upline && !ids.has(n.upline)) n.upline = rootId; });
  return nodes;
}
function subtree(nodes, rootId){
  const by = Object.fromEntries(nodes.map(n=>[n.id,n])), kids = {};
  nodes.forEach(n=>{ if(n.upline) (kids[n.upline] ||= []).push(n); });
  const out=[], seen=new Set();
  const walk = (id,g) => { if(seen.has(id)||!by[id]) return; seen.add(id); out.push({...by[id], gen:g}); (kids[id]||[]).sort((a,b)=>b.ace-a.ace).forEach(c=>walk(c.id,g+1)); };
  walk(rootId,0); return out;
}

/* ---------- lukis peta minda (org chart) ---------- */
function treeHTML(list, rootId){
  const kids = {}; list.forEach(n=>{ if(n.id!==rootId && n.upline) (kids[n.upline] ||= []).push(n); });
  const node = n => { const c = genColor(n.gen);
    return `<li><div class="tnode" style="border-color:${c}">
      ${n.foto?`<img src="${n.foto}" alt="">`:`<div class="tav" style="background:${c}">${esc(initials(n.nama))}</div>`}
      <b>${esc(n.nama.split(' ').slice(0,2).join(' '))}</b>
      <span class="tgen" style="background:${c}">${n.gen===0?(n.leader?'Leader':'Anda'):'Gen '+n.gen}</span>
      ${n.kod?`<small>${esc(n.kod)}</small>`:''}
      <small>${H().RM(n.ace)}</small></div>
      ${(kids[n.id]||[]).length?`<ul>${kids[n.id].map(node).join('')}</ul>`:''}</li>`; };
  const root = list.find(n=>n.id===rootId);
  return root ? `<div class="tree"><ul>${node(root)}</ul></div>` : '';
}
function infoHTML(list, upline){
  const h=H(), down = list.filter(n=>n.gen>0), maxG = Math.max(0,...list.map(n=>n.gen));
  const byGen = g => list.filter(n=>n.gen===g);
  return `
    ${upline?`<div class="small muted" style="text-align:center;margin-bottom:4px">⬆️ Upline: <b>${esc(upline.nama)}</b>${upline.kod?' ('+esc(upline.kod)+')':''}</div>`:''}
    <div class="stats" style="margin-bottom:10px">
      <div class="stat"><b>${down.length}</b><span class="small muted">Ahli bawah</span></div>
      <div class="stat"><b>${byGen(1).length}</b><span class="small muted">Gen 1 (direct)</span></div>
      <div class="stat"><b style="font-size:15px">${h.RM(list.reduce((s,n)=>s+n.ace,0))}</b><span class="small muted">ACE pasukan ${h.THIS_Y}</span></div>
    </div>
    <div class="card" style="padding:8px">${treeHTML(list, list[0]?.id)}</div>
    <div class="row small" style="gap:10px;margin:-4px 0 12px">${Array.from({length:maxG+1},(_,g)=>`<span><span class="dot" style="background:${genColor(g)}"></span>${g===0?'Puncak':'Gen '+g} (${byGen(g).length})</span>`).join('')}</div>
    ${maxG>0?Array.from({length:maxG},(_,i)=>i+1).map(g=>`<details class="card small"><summary><b>Gen ${g}</b> · ${byGen(g).length} orang</summary>
      ${byGen(g).map(n=>`<div class="row" style="margin-top:8px"><span class="grow">${esc(n.nama)} <span class="muted">${esc(n.kod||'')}</span></span><span>${h.RM(n.ace)} · ${n.kes} kes</span></div>`).join('')}</details>`).join('') : ''}`;
}

/* ---------- sync hierarki (leader) ---------- */
let syncT;
function scheduleSync(){ const S=H().S; if(S.role!=='owner' || !window.__HOSTED || !S.users || !S.team || !S.db) return; clearTimeout(syncT); syncT=setTimeout(doSync,1500); }
async function doSync(){
  const S=H().S, nodes = await allNodes(), by = Object.fromEntries(nodes.map(n=>[n.id,n]));
  for(const n of nodes){ if(n.leader) continue;
    const sub = subtree(nodes, n.id).map(({gen, ...x})=>x), up = by[n.upline];
    const doc = { root:n.id, upline: up?{nama:up.nama, kod:up.kod}:null, nodes:sub };
    const sig = hash(JSON.stringify(doc)), k='hk-'+n.id;
    try{ if(localStorage.getItem(k)===sig) continue; }catch{}
    try{ await S.db.doc('hierarki/'+n.id).set({...doc, updatedAt:Date.now()}); localStorage.setItem(k,sig); }catch{}
  }
}
function initAgent(db, uid){
  if(!db || !uid) return;
  db.doc('hierarki/'+uid).onSnapshot(s=>{ T.my = s.exists ? s.data() : {nodes:[]}; if(location.hash==='#/apa/pasukan') vPasukan(); }, ()=>{ T.my={nodes:[]}; });
}

/* ---------- paparan APA → Pasukan ---------- */
async function vPasukan(){
  const h=H(), S=h.S;
  let mapHTML;
  if(S.role==='agent'){
    const nodes = T.my?.nodes || [], me = S.uid;
    if(!nodes.length) mapHTML = `<div class="card empty muted small">Peta pasukan akan muncul selepas leader menetapkan hierarki.</div>`;
    else { const list = subtree(nodes.map(n=>n.id===me?{...n, upline:null}:n), me); mapHTML = infoHTML(list, T.my.upline); }
  } else {
    const nodes = await allNodes(); mapHTML = infoHTML(subtree(nodes, nodes[0].id), null);
  }
  const R = (S.me.p100||[]).filter(p=>p.jenis==='rekrut');
  const cnt = k => R.filter(p=>(p.status||'prospek')===k).length;
  $('#app').innerHTML = h.tabs('pasukan') + `
    <h3 style="margin-top:0">🌳 Peta pasukan</h3>${mapHTML}
    <h3>🤝 Rekrut saya (${R.length})</h3>
    <div class="stats" style="grid-template-columns:repeat(5,1fr);margin-bottom:10px">${STG.map(([k,t])=>`<div class="stat" style="padding:8px 2px"><b style="font-size:18px">${cnt(k)}</b><span class="small muted" style="font-size:10px">${t}</span></div>`).join('')}</div>
    ${R.map(p=>`<div class="card agent" onclick="go('#/apa/rekrut/${p.id}')" style="padding:10px 14px">
      <div class="grow"><b>${esc(p.nama)}</b><div class="small muted">${[p.tel,p.umur&&p.umur+' thn',p.kerja].filter(Boolean).map(esc).join(' · ')}</div></div>
      <span class="badge ${(p.status==='coded')?'S':''}">${STN[p.status||'prospek']}</span></div>`).join('') || '<div class="card empty muted small">Belum ada rekrut. Tambah calon yang berminat jadi ejen.</div>'}
    <button class="btn-primary" style="width:100%" onclick="go('#/apa/rekrut/baru')">+ Tambah Rekrut</button>`;
}
function vRekrutForm(id){
  const h=H(), S=h.S, L = S.me.p100 ||= [];
  const p = id==='baru' ? {id:uid(), jenis:'rekrut', status:'prospek', history:[]} : L.find(x=>x.id===id);
  if(!p) return go('#/apa/pasukan');
  const st = p.status||'prospek', idx = STG.findIndex(s=>s[0]===st), next = STG[idx+1];
  $('#app').innerHTML = `
    <h2>${id==='baru'?'Tambah Rekrut':esc(p.nama)}</h2>
    ${id!=='baru'?`<div class="pipeline">${STG.map((s,i)=>`<div class="${i<=idx?'done':''}"></div>`).join('')}</div>
      <div class="small muted" style="display:flex;gap:4px;font-size:11px;margin-bottom:10px">${STG.map(s=>`<span style="flex:1">${s[1]}</span>`).join('')}</div>`:''}
    <div class="card">
      <label style="margin-top:0">Nama *</label><input id="nama" value="${esc(p.nama)}">
      <label>No. tel</label><input id="tel" type="tel" value="${esc(p.tel)}">
      <div class="row"><div style="width:90px"><label>Umur</label><input id="umur" inputmode="numeric" value="${esc(p.umur)}"></div>
        <div class="grow"><label>Pekerjaan</label><input id="kerja" value="${esc(p.kerja)}"></div></div>
      <label>Status</label><select id="st">${STG.map(([k,t])=>`<option value="${k}" ${k===st?'selected':''}>${t}</option>`).join('')}</select>
      <label>Nota</label><input id="nota" value="${esc(p.nota)}">
      ${p.status==='coded'?'<p class="small muted">✅ Coded — beritahu dia daftar akaun APA guna link app. Leader akan luluskan & sahkan kiraan NR.</p>':''}
    </div>
    <div class="row">
      <button class="btn-primary grow" id="sv">Simpan</button>
      ${next&&id!=='baru'?`<button id="adv">→ ${next[1]}</button>`:''}
      ${p.tel?`<a class="btn" target="_blank" href="https://wa.me/${esc(waNum(p.tel))}">💬</a>`:''}
      ${id!=='baru'?'<button class="btn-danger" id="dl">Padam</button>':''}
    </div>`;
  const put = async status => {
    const nama=$('#nama').value.trim(); if(!nama) return toast('Nama wajib');
    const now=Date.now(), rec = {...p, jenis:'rekrut', nama, tel:$('#tel').value.trim(), umur:$('#umur').value.trim(), kerja:$('#kerja').value.trim(), nota:$('#nota').value.trim(), status, updatedAt:now};
    if(status!==p.status || !(p.history||[]).length) rec.history = [...(p.history||[]), {status, date:now}];
    const i = L.findIndex(x=>x.id===p.id); if(i<0) L.push(rec); else L[i]=rec;
    await h.save(); toast(status==='coded'&&p.status!=='coded'?'🎉 Tahniah, Coded!':'Disimpan'); go('#/apa/pasukan');
  };
  $('#sv').onclick = () => put($('#st').value);
  $('#adv') && ($('#adv').onclick = () => put(next[0]));
  $('#dl') && ($('#dl').onclick = async () => { if(await ask(`Padam ${p.nama}?`,'Padam')){ S.me.p100 = L.filter(x=>x.id!==p.id); await h.save(); go('#/apa/pasukan'); } });
}

/* ---------- leader: peta penuh + tetapkan upline ---------- */
async function leaderMapHTML(){ const nodes = await allNodes(); return infoHTML(subtree(nodes, nodes[0].id), null); }
function uplineSelect(u){
  const S=H().S, rootId=S.uid||'me', opts = (S.users||[]).filter(x=>x.status==='approved' && x.uid!==u.uid);
  let cur = u.upline;
  if(!cur && u.perekrut){ const q=u.perekrut.toLowerCase(); cur = opts.find(x=>x.nama && (x.nama.toLowerCase().includes(q) || q.includes(x.nama.toLowerCase())))?.uid; }
  cur ||= rootId;
  return `<select class="upsel" data-uid="${esc(u.uid)}" style="width:auto;max-width:160px;padding:4px 6px;font-size:12px">
    <option value="${esc(rootId)}" ${cur===rootId?'selected':''}>Upline: Anda (leader)</option>
    ${opts.map(x=>`<option value="${esc(x.uid)}" ${cur===x.uid?'selected':''}>Upline: ${esc(x.nama)}</option>`).join('')}</select>`;
}

window.PASUKAN = { vPasukan, vRekrutForm, scheduleSync, initAgent, leaderMapHTML, uplineSelect, STN };
})();
