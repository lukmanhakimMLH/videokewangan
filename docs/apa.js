/* =====================================================================
   APA — Annual Plan ejen (berdasarkan APA_QAIZER_2026.numbers)
   Data setiap ejen: doc  apa/<uid>   (ejen baca/tulis sendiri; leader baca semua)
   Contest (leader set): doc config/contests
   ===================================================================== */
(function(){
const BULAN = ['Januari','Februari','Mac','April','Mei','Jun','Julai','Ogos','September','Oktober','November','Disember'];
const BLN = ['Jan','Feb','Mac','Apr','Mei','Jun','Jul','Ogo','Sep','Okt','Nov','Dis'];
/* Pecahan bulanan asal dari APA (jumlah 100%) */
const PROP_ASAL = [4.86,3.12,9.19,7.31,7.95,7.51,12.41,11.2,8.15,10.01,10.65,7.64];
const CONTEST_CONTOH = [
  {id:'gz1', nama:'Guangzhou — Tier 1', sasaran:25000,  jenis:'ace', dari:1, hingga:3},
  {id:'gz2', nama:'Guangzhou — Tier 2', sasaran:65000,  jenis:'ace', dari:1, hingga:3},
  {id:'gz3', nama:'Guangzhou — Tier 3', sasaran:130000, jenis:'ace', dari:1, hingga:3},
  {id:'iron', nama:'Iron Club',         sasaran:0,      jenis:'kes', dari:1, hingga:12},
  {id:'sa',  nama:'Summit South Africa', sasaran:180000, jenis:'ace', dari:1, hingga:12},
];
/* Borang untuk dimuat turun (fail dalam folder borang/ di laman web) */
const FORMS = [
  {kod:'FCV', nama:'FORM CLOSING GOV (FCV)', fail:'borang/FCV.pdf',
   isi:'Surat Kebenaran Maklumat Kredit (SPeKAR) · Ulasan Pelanggan · Biro ANGKASA (potongan gaji) · Butiran Ahli & Pewaris'},
];
const STATUS = {pledge:'Pledge', fu:'Follow-up', closed:'Closed'};
const NOW = new Date(), THIS_Y = NOW.getFullYear(), THIS_M = NOW.getMonth()+1;
let YEAR = THIS_Y, CUR_M = THIS_M;          // tahun yang dipilih (boleh tukar di tajuk)
function setYear(y){ YEAR = +y || THIS_Y; CUR_M = YEAR<THIS_Y ? 12 : YEAR>THIS_Y ? 1 : THIS_M; try{ localStorage.setItem('qz-year', YEAR); }catch{} }
try{ const sy = +localStorage.getItem('qz-year'); if(sy) setYear(sy); }catch{}

const RM = n => { const v=Math.round(+n||0); return (v<0?'-':'')+'RM '+Math.abs(v).toLocaleString('en-MY'); };
const pct = (a,b) => b ? Math.round(a/b*1000)/10 : 0;
const num = v => { const n = parseFloat(String(v??'').replace(/[^\d.\-]/g,'')); return isFinite(n) ? n : 0; };
const clone = o => JSON.parse(JSON.stringify(o));

/* ---------------- STORE ---------------- */
const S = { role:'local', uid:null, db:null, me:null, ref:null, contests:null, team:null, teamErr:null,
  saving:null, listeners:[] };
const emptyDoc = () => ({ profile:{nama:'',kod:'',tel:''}, years:{}, p100:[], updatedAt:0 });
const yearOf = (d, y=YEAR) => (d.years[y] ||= { goal:0, ce:0, pr:0, prop:[...PROP_ASAL], months:{} });

function notify(){ const v=(location.hash||'').split('/')[1]; if(v==='apa'||v==='pasukan') APA.route(location.hash.split('/').slice(1), true); }

async function init({db, uid, role}){
  S.role = role; S.db = db; S.uid = uid;
  if(db && uid){
    S.ref = db.doc('apa/'+uid);
    await new Promise(res=>{
      let first=true; const t=setTimeout(()=>{ if(first){first=false; S.me ||= emptyDoc(); res();} },10000);
      S.ref.onSnapshot(s=>{
        if(S.pendingLocal) return;            // jangan timpa input yang belum disimpan
        S.me = s.exists ? clone(s.data()) : (S.me || emptyDoc());
        if(first){ first=false; clearTimeout(t); res(); } else notify();
      }, ()=>{ clearTimeout(t); S.me ||= emptyDoc(); if(first){first=false; res();} });
    });
    db.doc('config/contests').onSnapshot(s=>{ S.contests = s.exists ? (s.data().list||[]) : []; notify(); }, ()=>{ S.contests=[]; });
    if(role==='owner') window.MAPA?.init(db);
    if(role==='owner' && window.__HOSTED){
      db.collection('users').onSnapshot(s=>{ S.users = s.docs.map(d=>({uid:d.id, ...clone(d.data())})); notify(); }, ()=>{});
    }
    if(role==='owner'){
      db.collection('apa').onSnapshot(s=>{ S.team = s.docs.map(d=>({uid:d.id, ...clone(d.data())})); S.teamErr=null; notify(); },
        e=>{ S.teamErr = e.code; notify(); });
    }
  } else {
    try{ S.me = JSON.parse(localStorage.getItem('apa-local')||'null') || emptyDoc(); }catch{ S.me = emptyDoc(); }
    try{ S.contests = JSON.parse(localStorage.getItem('apa-contests')||'null') || []; }catch{ S.contests = []; }
    S.team = [{uid:'local', ...S.me}];
    window.MAPA?.init(null);
  }
}
let saveT;
function save(){
  S.me.updatedAt = Date.now();
  if(!S.ref){ try{ localStorage.setItem('apa-local', JSON.stringify(S.me)); }catch{} S.team=[{uid:'local',...S.me}]; return Promise.resolve(); }
  S.pendingLocal = true; clearTimeout(saveT);
  return new Promise(res=>{ saveT = setTimeout(async()=>{
    try{ await S.ref.set(clone(S.me)); }
    catch(e){ toast(e?.code==='invalid_argument' ? (window.__HOSTED?'Tiada akses simpan — akaun belum diluluskan leader':'Tiada akses simpan — minta leader beri akses Contributor') : 'Gagal simpan, cuba lagi'); }
    S.pendingLocal = false; res();
  }, 400); });
}
async function saveContests(list){
  S.contests = list;
  if(S.db){ try{ await S.db.doc('config/contests').set({list}); }catch{ toast('Gagal simpan contest'); } }
  else { try{ localStorage.setItem('apa-contests', JSON.stringify(list)); }catch{} }
}

/* ---------------- KIRAAN ---------------- */
function calc(doc, y=YEAR){
  const Y = doc.years?.[y] || {goal:0, prop:PROP_ASAL, months:{}};
  const rows = BULAN.map((_,i)=>{
    const m=i+1, list = Y.months?.[m] || [];
    const budget = (Y.goal||0) * (Y.prop?.[i]||0) / 100;
    const achieve = list.reduce((s,e)=>s+num(e.achieve),0);
    const pledge = list.reduce((s,e)=>s+num(e.budget),0);
    const kes = list.filter(e=>num(e.achieve)>0).length;
    const fu = list.filter(e=>e.status==='fu').length;
    return {m, budget, achieve, pledge, kes, fu, list, variance: achieve-budget};
  });
  let acc=0; rows.forEach(r=>{ acc+=r.variance; r.acc=acc; });
  const tot = k => rows.reduce((s,r)=>s+r[k],0);
  const ytdBudget = rows.filter(r=>r.m<=CUR_M || y<THIS_Y).reduce((s,r)=>s+r.budget,0);
  return { Y, rows, goal:Y.goal||0, achieve:tot('achieve'), pledge:tot('pledge'), kes:tot('kes'), ytdBudget,
    propSum: (Y.prop||[]).reduce((s,v)=>s+num(v),0) };
}
function contestProgress(c, C){
  const r = C.rows.filter(x=>x.m>=c.dari && x.m<=c.hingga);
  const val = c.jenis==='kes' ? r.reduce((s,x)=>s+x.kes,0) : r.reduce((s,x)=>s+x.achieve,0);
  return { val, pc: c.sasaran ? Math.min(100, pct(val,c.sasaran)) : 0, short: c.sasaran ? val - c.sasaran : 0 };
}

/* ---------------- UI HELPERS ---------------- */
const bar = (p, color='var(--S)') => `<div class="progress" style="height:10px;margin:4px 0"><div style="width:${Math.max(0,Math.min(100,p))}%;background:${color}"></div></div>`;
const colorFor = p => p>=100 ? 'var(--S)' : p>=70 ? 'var(--I)' : 'var(--D)';
function tabs(active){
  const t = [['','📊','Dashboard'],['bulan','🗓','Bulanan'],['p100','👥','P100'],['contest','🏆','Contest'],['borang','📄','Borang'],['tetapan','⚙︎','Tetapan']];
  return `<div class="tabs">${t.map(([k,i,l])=>`<button class="${active===k?'on':''}" onclick="go('#/apa${k?'/'+k:''}')"><span>${i}</span>${l}</button>`).join('')}</div>`;
}
function needSetup(){ return !S.me.profile?.nama || !yearOf(S.me).goal; }

/* ---------------- VIEWS: EJEN ---------------- */
function vSetup(){
  const P = S.me.profile, Y = yearOf(S.me), ME = window.__ME || {};
  P.nama ||= ME.nama || ''; P.kod ||= ME.kod || ''; P.tel ||= ME.tel || '';
  $('#app').innerHTML = `
    <h2>Selamat datang ke APA ${YEAR} 👋</h2>
    <p class="muted small" style="margin-top:-6px">Annual Plan anda. Isi sekali sahaja — boleh ubah kemudian di ⚙︎.</p>
    <div class="card">
      <label>Nama penuh *</label><input id="nama" value="${esc(P.nama)}">
      <label>Kod ejen</label><input id="kod" value="${esc(P.kod)}">
      <label>No. tel</label><input id="tel" type="tel" value="${esc(P.tel)}">
      <label>Goal ACE ${YEAR} (RM) *</label><input id="goal" inputmode="decimal" value="${Y.goal||''}" placeholder="cth: 150000">
      <div class="row"><div class="grow"><label>Current CE (%)</label><input id="ce" inputmode="decimal" value="${Y.ce||''}"></div>
      <div class="grow"><label>Current PR (%)</label><input id="pr" inputmode="decimal" value="${Y.pr||''}"></div></div>
    </div>
    <button class="btn-primary" style="width:100%" id="ok">Mula</button>`;
  $('#ok').onclick = async () => {
    const nama=$('#nama').value.trim(), goal=num($('#goal').value);
    if(!nama || !goal) return toast('Nama dan Goal ACE wajib');
    Object.assign(P, {nama, kod:$('#kod').value.trim(), tel:$('#tel').value.trim()});
    Object.assign(Y, {goal, ce:num($('#ce').value), pr:num($('#pr').value)});
    await save(); APA.route(['apa']);
  };
}

function dashboardHTML(doc, readonly){
  const C = calc(doc), p = pct(C.achieve, C.goal), cur = C.rows[CUR_M-1];
  const q = i => `Q${Math.floor(i/3)+1}`;
  return `
    <div class="card">
      <div class="row"><div class="grow"><div class="small muted">Goal ACE ${YEAR}</div><div style="font-size:22px;font-weight:800">${RM(C.goal)}</div></div>
        <div style="text-align:right"><div class="small muted">CE · PR</div><b>${C.Y.ce||0}% · ${C.Y.pr||0}%</b></div></div>
      ${bar(p, colorFor(pct(C.achieve, C.ytdBudget)))}
      <div class="row small"><span class="grow">Achieve <b>${RM(C.achieve)}</b> (${p}%)</span><span>Baki <b>${RM(Math.max(0,C.goal-C.achieve))}</b></span></div>
    </div>
    <div class="stats" style="margin-bottom:12px">
      <div class="stat" ${readonly?'':`onclick="go('#/apa/bulan/${CUR_M}')"`}><b style="font-size:16px">${RM(cur.achieve)}</b><span class="small muted">${BULAN[CUR_M-1]} (${pct(cur.achieve,cur.budget)}%)</span></div>
      <div class="stat"><b style="font-size:16px">${RM(cur.budget)}</b><span class="small muted">Bajet ${BLN[CUR_M-1]}</span></div>
      <div class="stat"><b style="font-size:16px;color:${cur.acc<0?'#d32f2f':'var(--S)'}">${RM(cur.acc)}</b><span class="small muted">Kumulatif +/-</span></div>
    </div>
    <div class="card" style="padding:8px;overflow-x:auto">
      <table class="tbl">
        <thead><tr><th></th><th>Bulan</th><th>Bajet</th><th>Achieve</th><th>%</th><th>+/-</th></tr></thead>
        <tbody>${C.rows.map((r,i)=>`<tr class="${r.m===CUR_M?'cur':''}" ${readonly?'':`onclick="go('#/apa/bulan/${r.m}')"`}>
          <td class="muted">${i%3===0?q(i):''}</td><td>${BLN[i]}</td><td>${Math.round(r.budget).toLocaleString()}</td>
          <td><b>${Math.round(r.achieve).toLocaleString()}</b></td>
          <td style="color:${r.achieve?colorFor(pct(r.achieve,r.budget)):'var(--muted)'}">${r.budget?pct(r.achieve,r.budget)+'%':'-'}</td>
          <td style="color:${r.variance<0?'#d32f2f':'var(--S)'}">${(r.m<=CUR_M)?Math.round(r.variance).toLocaleString():''}</td></tr>`).join('')}</tbody>
        <tfoot><tr><td></td><td>Jumlah</td><td>${Math.round(C.goal).toLocaleString()}</td><td>${Math.round(C.achieve).toLocaleString()}</td><td>${p}%</td><td>${Math.round(C.achieve-C.goal).toLocaleString()}</td></tr></tfoot>
      </table>
    </div>`;
}

function vDash(){
  const P = S.me.profile||{}, ME = window.__ME||{};
  $('#app').innerHTML = tabs('') + `
    <div class="card agent" style="cursor:default">
      <div class="avatar">${esc(initials(P.nama))}</div>
      <div class="grow"><b style="font-size:17px">${esc(P.nama)}</b>
        <div class="small muted">${[P.kod&&('Kod '+P.kod), P.tel, ME.emel].filter(Boolean).map(esc).join(' · ')}</div>
        <div class="small muted">APA ${YEAR}${S.me.updatedAt?' · kemaskini '+fmtDate(S.me.updatedAt):''}</div></div>
      <button class="btn-sm" onclick="go('#/apa/tetapan')">✏️</button>
    </div>
    <h3>📈 Prestasi terkini</h3>` + dashboardHTML(S.me) + contestCards(S.me, true);
}
function vBorang(){
  $('#app').innerHTML = tabs('borang') + `<h2>📄 Download Borang</h2>` + FORMS.map(f=>`
    <a class="btn btn-primary" style="display:block;text-align:center;text-decoration:none;padding:16px;margin-bottom:6px;font-size:16px" href="${f.fail}" download="${f.kod}.pdf" target="_blank">⬇️ ${esc(f.nama)}</a>
    <p class="small muted" style="margin:0 0 16px">${esc(f.isi)}</p>`).join('') +
'';
}

function vBulan(m){
  m = +m || CUR_M;
  const C = calc(S.me), r = C.rows[m-1];
  $('#app').innerHTML = tabs('bulan') + `
    <div class="row" style="margin-bottom:8px">
      <button class="btn-sm" ${m<=1?'disabled':''} onclick="go('#/apa/bulan/${m-1}')">‹</button>
      <h2 class="grow" style="text-align:center;margin:0">${BULAN[m-1]} ${YEAR}</h2>
      <button class="btn-sm" ${m>=12?'disabled':''} onclick="go('#/apa/bulan/${m+1}')">›</button>
    </div>
    <div class="card">
      <dl class="kv">
        <dt>Bajet bulan</dt><dd><b>${RM(r.budget)}</b></dd>
        <dt>Total pledge</dt><dd>${RM(r.pledge)} <span class="small muted">(${pct(r.pledge,r.budget)}% dari bajet)</span></dd>
        <dt>Achieve</dt><dd><b>${RM(r.achieve)}</b> <span class="small muted">(${pct(r.achieve,r.budget)}%)</span></dd>
        <dt>Shortfall</dt><dd style="color:${r.variance<0?'#d32f2f':'var(--S)'}">${RM(r.variance)}</dd>
      </dl>
      ${bar(pct(r.achieve,r.budget), colorFor(pct(r.achieve,r.budget)))}
    </div>
    <h3>Pelanggan (${r.list.length})</h3>
    ${r.list.length ? r.list.map(e=>`
      <div class="card agent" onclick="go('#/apa/kes/${m}/${e.id}')" style="padding:10px 14px">
        <div class="grow"><b>${esc(e.nama)}</b><div class="small muted">Pledge ${RM(e.budget)}${e.nota?' · '+esc(e.nota):''}</div></div>
        <div style="text-align:right">${num(e.achieve)?`<b class="ok">${RM(e.achieve)}</b>`:''}<div><span class="badge">${STATUS[e.status]||'Pledge'}</span></div></div>
      </div>`).join('') : `<div class="card empty muted">Belum ada pelanggan bulan ini.</div>`}
    <button class="btn-primary" style="width:100%" onclick="go('#/apa/kes/${m}/baru')">+ Tambah Pelanggan</button>`;
}

function vKes(m, id){
  m = +m; const Y = yearOf(S.me), list = (Y.months[m] ||= []);
  const e = id==='baru' ? {id:uid(), status:'pledge'} : list.find(x=>x.id===id);
  if(!e) return go('#/apa/bulan/'+m);
  const p100 = S.me.p100||[];
  $('#app').innerHTML = `
    <h2>${id==='baru'?'Tambah':'Kemaskini'} Pelanggan · ${BULAN[m-1]}</h2>
    <div class="card">
      <label>Nama pelanggan *</label><input id="nama" list="p100list" value="${esc(e.nama)}">
      <datalist id="p100list">${p100.map(p=>`<option value="${esc(p.nama)}">`).join('')}</datalist>
      <label>Pledge / Bajet ACE (RM)</label><input id="budget" inputmode="decimal" value="${e.budget??''}">
      <label>Status</label>
      <div class="seg" id="st">${Object.entries(STATUS).map(([k,v])=>`<button type="button" data-v="${k}" class="${e.status===k?'on':''}">${v}</button>`).join('')}</div>
      <label>Achieve ACE (RM) — isi bila kes closed</label><input id="achieve" inputmode="decimal" value="${e.achieve??''}">
      <label>Bulan</label><select id="bulan">${BULAN.map((b,i)=>`<option value="${i+1}" ${i+1===m?'selected':''}>${b}</option>`).join('')}</select>
      <label>Nota</label><input id="nota" value="${esc(e.nota)}" placeholder="cth: plan medical, FU Jumaat">
    </div>
    <div class="row">
      <button class="btn-primary grow" id="sv">Simpan</button>
      <button onclick="history.back()">Batal</button>
      ${id!=='baru'?'<button class="btn-danger" id="dl">Padam</button>':''}
    </div>`;
  let st = e.status;
  document.querySelectorAll('#st button').forEach(b=>b.onclick=()=>{ st=b.dataset.v; document.querySelectorAll('#st button').forEach(x=>x.classList.toggle('on',x===b)); });
  $('#sv').onclick = async () => {
    const nama=$('#nama').value.trim(); if(!nama) return toast('Nama wajib');
    const achieve=num($('#achieve').value), nm=+$('#bulan').value;
    const rec = {...e, nama, budget:num($('#budget').value), achieve, status: achieve>0 ? 'closed' : st, nota:$('#nota').value.trim()};
    Y.months[m] = list.filter(x=>x.id!==e.id);
    (Y.months[nm] ||= []).push(rec);
    await save(); toast('Disimpan'); go('#/apa/bulan/'+nm);
  };
  $('#dl') && ($('#dl').onclick = async () => { if(await ask(`Padam ${e.nama}?`,'Padam')){ Y.months[m]=list.filter(x=>x.id!==e.id); await save(); go('#/apa/bulan/'+m); } });
}

function vP100(){
  const L = S.me.p100 ||= [];
  const nR = L.filter(p=>p.jenis==='rekrut').length;
  $('#app').innerHTML = tabs('p100') + `
    <div class="card">
      <div class="row"><b class="grow">Project 100</b><b>${L.length}/100</b></div>
      ${bar(L.length, 'var(--C)')}
      <div class="small muted">${L.length-nR} prospek pelanggan · ${nR} calon rekrut <span class="badge" style="font-size:11px">↗ leader</span></div>
    </div>
    <div class="seg" style="margin-bottom:10px" id="flt">
      <button data-f="" class="on">Semua</button><button data-f="pelanggan">Pelanggan</button><button data-f="rekrut">Calon Rekrut</button>
    </div>
    <div id="plist"></div>
    <button class="btn-primary" style="width:100%" onclick="go('#/apa/p100/baru')">+ Tambah Nama</button>`;
  const draw = f => { $('#plist').innerHTML = L.map((p,i)=>({p,i})).filter(({p})=>!f||p.jenis===f).map(({p,i})=>`
      <div class="card agent" onclick="go('#/apa/p100/${p.id}')" style="padding:10px 14px">
        <div class="avatar" style="width:36px;height:36px;font-size:13px">${i+1}</div>
        <div class="grow"><b>${esc(p.nama)}</b><div class="small muted">${[p.tel,p.umur&&p.umur+' thn',p.kerja].filter(Boolean).map(esc).join(' · ')}</div></div>
        ${p.jenis==='rekrut'?'<span class="badge S">Rekrut</span>':''}
      </div>`).join('') || '<div class="card empty muted">Tiada nama lagi.</div>'; };
  draw('');
  document.querySelectorAll('#flt button').forEach(b=>b.onclick=()=>{ document.querySelectorAll('#flt button').forEach(x=>x.classList.toggle('on',x===b)); draw(b.dataset.f); });
}

function vP100Form(id){
  const L = S.me.p100 ||= [];
  const p = id==='baru' ? {id:uid(), jenis:'pelanggan'} : L.find(x=>x.id===id);
  if(!p) return go('#/apa/p100');
  $('#app').innerHTML = `
    <h2>${id==='baru'?'Tambah Nama':'Kemaskini'} · Project 100</h2>
    <div class="card">
      <label>Nama *</label><input id="nama" value="${esc(p.nama)}">
      <label>No. tel</label><input id="tel" type="tel" value="${esc(p.tel)}">
      <div class="row"><div style="width:90px"><label>Umur</label><input id="umur" inputmode="numeric" value="${esc(p.umur)}"></div>
        <div class="grow"><label>Pekerjaan</label><input id="kerja" value="${esc(p.kerja)}"></div></div>
      <label>Jenis</label>
      <div class="seg" id="jn"><button type="button" data-v="pelanggan" class="${p.jenis!=='rekrut'?'on':''}">Prospek Pelanggan</button><button type="button" data-v="rekrut" class="${p.jenis==='rekrut'?'on':''}">Calon Rekrut ↗</button></div>
      <p class="small muted" id="rk" style="${p.jenis==='rekrut'?'':'display:none'}">Calon rekrut akan dihantar kepada leader untuk proses rekrut.</p>
      <label>Nota</label><input id="nota" value="${esc(p.nota)}">
    </div>
    <div class="row">
      <button class="btn-primary grow" id="sv">Simpan</button>
      ${p.tel?`<a class="btn" target="_blank" href="https://wa.me/${esc(waNum(p.tel))}">💬</a>`:''}
      <button onclick="history.back()">Batal</button>
      ${id!=='baru'?'<button class="btn-danger" id="dl">Padam</button>':''}
    </div>`;
  let jenis = p.jenis;
  document.querySelectorAll('#jn button').forEach(b=>b.onclick=()=>{ jenis=b.dataset.v; document.querySelectorAll('#jn button').forEach(x=>x.classList.toggle('on',x===b)); $('#rk').style.display = jenis==='rekrut'?'':'none'; });
  $('#sv').onclick = async () => {
    const nama=$('#nama').value.trim(); if(!nama) return toast('Nama wajib');
    const rec = {...p, nama, tel:$('#tel').value.trim(), umur:$('#umur').value.trim(), kerja:$('#kerja').value.trim(), jenis, nota:$('#nota').value.trim()};
    const i = L.findIndex(x=>x.id===p.id); if(i<0) L.push(rec); else L[i]=rec;
    await save(); toast('Disimpan'); go('#/apa/p100');
  };
  $('#dl') && ($('#dl').onclick = async () => { if(await ask(`Padam ${p.nama}?`,'Padam')){ S.me.p100 = L.filter(x=>x.id!==p.id); await save(); go('#/apa/p100'); } });
}

function contestCards(doc, compact){
  const list = S.contests || [];
  if(!list.length) return compact ? '' : `<div class="card empty muted">Belum ada contest. ${S.role==='agent'?'Leader akan tetapkan.':'Tetapkan di Pasukan → Contest.'}</div>`;
  const C = calc(doc);
  return `${compact?'<h3>🏆 Contest</h3>':''}` + list.map(c=>{
    const g = contestProgress(c, C);
    return `<div class="card" style="padding:12px 14px">
      <div class="row"><b class="grow">${esc(c.nama)}</b><span class="small muted">${BLN[c.dari-1]}–${BLN[c.hingga-1]}</span></div>
      ${c.jenis==='kes'
        ? `<div class="small" style="margin-top:4px"><b>${g.val}</b> kes${c.sasaran?` / ${c.sasaran}`:''}</div>${c.sasaran?bar(g.pc,colorFor(g.pc)):''}`
        : `${bar(g.pc, colorFor(g.pc))}<div class="row small"><span class="grow">${RM(g.val)} / ${RM(c.sasaran)}</span><b style="color:${g.short<0?'#d32f2f':'var(--S)'}">${g.short<0?'Kurang '+RM(-g.short):'✓ Layak'}</b></div>`}
    </div>`;}).join('');
}
function vContest(){ $('#app').innerHTML = tabs('contest') + contestCards(S.me, false); }

function vTetapan(){
  const P=S.me.profile, Y=yearOf(S.me);
  $('#app').innerHTML = tabs('tetapan') + `
    <div class="card">
      <label>Nama</label><input id="nama" value="${esc(P.nama)}">
      <div class="row"><div class="grow"><label>Kod ejen</label><input id="kod" value="${esc(P.kod)}"></div><div class="grow"><label>No. tel</label><input id="tel" value="${esc(P.tel)}"></div></div>
      <label>Goal ACE ${YEAR} (RM)</label><input id="goal" inputmode="decimal" value="${Y.goal||''}">
      <div class="row"><div class="grow"><label>Current CE (%)</label><input id="ce" inputmode="decimal" value="${Y.ce||''}"></div><div class="grow"><label>Current PR (%)</label><input id="pr" inputmode="decimal" value="${Y.pr||''}"></div></div>
    </div>
    <div class="card">
      <b>Pecahan sasaran ikut bulan (%)</b>
      <div class="small muted">Bulan sibuk boleh letak % lebih tinggi. Jumlah mesti 100%.</div>
      <div class="prop-grid">${BULAN.map((b,i)=>`<label style="margin:6px 0 2px">${BLN[i]}</label><input class="prop" data-i="${i}" inputmode="decimal" value="${Y.prop[i]}">`).join('')}</div>
      <div class="row small" style="margin-top:8px"><span class="grow">Jumlah: <b id="psum"></b></span><button class="btn-sm" id="asal">Guna pecahan asal</button><button class="btn-sm" id="rata">Sama rata</button></div>
    </div>
    <button class="btn-primary" style="width:100%" id="sv">Simpan</button>`;
  const sum = () => { const s=[...document.querySelectorAll('.prop')].reduce((a,el)=>a+num(el.value),0); $('#psum').textContent = (Math.round(s*100)/100)+'%'; $('#psum').className = Math.abs(s-100)<0.05?'ok':'err'; return s; };
  document.querySelectorAll('.prop').forEach(el=>el.oninput=sum); sum();
  $('#asal').onclick=()=>{ document.querySelectorAll('.prop').forEach((el,i)=>el.value=PROP_ASAL[i]); sum(); };
  $('#rata').onclick=()=>{ document.querySelectorAll('.prop').forEach((el,i)=>el.value=i<11?8.33:8.37); sum(); };
  $('#sv').onclick = async () => {
    if(Math.abs(sum()-100)>=0.05) return toast('Jumlah pecahan mesti 100%');
    Object.assign(P,{nama:$('#nama').value.trim(), kod:$('#kod').value.trim(), tel:$('#tel').value.trim()});
    Object.assign(Y,{goal:num($('#goal').value), ce:num($('#ce').value), pr:num($('#pr').value), prop:[...document.querySelectorAll('.prop')].map(el=>num(el.value))});
    await save(); toast('Disimpan'); go('#/apa');
  };
}

/* ---------------- VIEWS: LEADER (Pasukan — asas MAPA) ---------------- */
async function vPasukan(){
  if(S.teamErr) { $('#app').innerHTML = `<div class="card err">Tak dapat baca data pasukan (${esc(S.teamErr)}).</div>`; return; }
  if(!S.team){ $('#app').innerHTML = '<div class="card empty muted">Memuatkan pasukan…</div>'; return; }
  const team = S.team.filter(a=>a.profile?.nama).map(a=>({a, C:calc(a)})).sort((x,y)=>y.C.achieve-x.C.achieve);
  const rekrut = await DB.all();
  const imported = new Set(rekrut.map(r=>r.dariApa).filter(Boolean));
  const leads = team.flatMap(({a})=>(a.p100||[]).filter(p=>p.jenis==='rekrut').map(p=>({p, a, key:a.uid+':'+p.id})));
  const sum = k => team.reduce((s,t)=>s+t.C[k],0);
  $('#app').innerHTML = `
    ${window.MAPA?MAPA.tabs('ejen'):''}
    ${approvalsHTML()}
    <div class="stats" style="margin-bottom:12px">
      <div class="stat"><b>${team.length}</b><span class="small muted">Ejen aktif</span></div>
      <div class="stat"><b style="font-size:15px">${RM(sum('achieve'))}</b><span class="small muted">Achieve ${YEAR}</span></div>
      <div class="stat"><b>${pct(sum('achieve'),sum('goal'))}%</b><span class="small muted">dari ${RM(sum('goal'))}</span></div>
    </div>
    ${team.length ? team.map(({a,C})=>{ const r=C.rows[CUR_M-1], p=pct(C.achieve,C.goal);
      return `<div class="card agent" onclick="go('#/pasukan/${a.uid}')">
        <div class="avatar">${esc(initials(a.profile.nama))}</div>
        <div class="grow"><b>${esc(a.profile.nama)}</b> <span class="small muted">${esc(a.profile.kod||'')}</span>
          ${bar(p, colorFor(pct(C.achieve,C.ytdBudget)))}
          <div class="small muted">${RM(C.achieve)} / ${RM(C.goal)} (${p}%) · ${BLN[CUR_M-1]}: ${pct(r.achieve,r.budget)}% · P100: ${(a.p100||[]).length}</div>
        </div></div>`; }).join('') : `<div class="card empty muted">Belum ada ejen isi APA. ${window.__HOSTED?'Kongsi link app kepada ejen — mereka daftar, anda luluskan di atas.':'Kongsi link app ini kepada ejen (Share → Contributor).'}</div>`}
    <h3>Calon rekrut dari ejen (${leads.length})</h3>
    ${leads.length ? leads.map(({p,a,key})=>`<div class="card agent" style="padding:10px 14px;cursor:default">
        <div class="grow"><b>${esc(p.nama)}</b><div class="small muted">${[p.tel,p.umur&&p.umur+' thn',p.kerja].filter(Boolean).map(esc).join(' · ')}<br>dari ${esc(a.profile.nama)}</div></div>
        ${imported.has(key) ? '<span class="badge S">✓ Dalam Rekrut</span>' : `<button class="btn-sm btn-primary" data-imp="${esc(key)}">→ Rekrut</button>`}
      </div>`).join('') : '<div class="card empty muted small">Ejen boleh tanda nama Project 100 sebagai "Calon Rekrut".</div>'}
`;
  document.querySelectorAll('[data-lulus]').forEach(b=>b.onclick=async()=>{
    const [id, st] = b.dataset.lulus.split('|');
    try{ await S.db.doc('users/'+id).update({status:st, reviewedAt:Date.now()}); toast(st==='approved'?'Diluluskan ✓':'Ditolak'); }catch{ toast('Gagal kemaskini'); }
  });
  document.querySelectorAll('[data-imp]').forEach(b=>b.onclick=async()=>{
    const L = leads.find(l=>l.key===b.dataset.imp), now=Date.now();
    const rec = {id:uid(), nama:L.p.nama, tel:L.p.tel||'', ic:'', alamat:'', pendidikan:'SPM', status:'prospek', foto:'',
      sumber:'Ejen: '+L.a.profile.nama, nota:[L.p.umur&&('Umur '+L.p.umur), L.p.kerja, L.p.nota].filter(Boolean).join(' · '),
      dariApa:L.key, createdAt:now, updatedAt:now, history:[{status:'prospek',date:now}]};
    await DB.put(rec); toast('Ditambah ke Rekrut'); go('#/calon/'+rec.id);
  });
}
function approvalsHTML(){
  if(!S.users) return '';
  const pend = S.users.filter(u=>u.status==='pending'), lulus = S.users.filter(u=>u.status==='approved');
  const row = (u, btns) => `<div class="card agent" style="padding:10px 14px;cursor:default">
      <div class="grow"><b>${esc(u.nama)}</b> <span class="small muted">${esc(u.kod||'')}</span>
      <div class="small muted">${esc(u.emel||'')} · ${esc(u.tel||'')}</div></div>${btns}</div>`;
  return (pend.length ? `<h3>🔔 Permohonan akaun baru (${pend.length})</h3>` + pend.map(u=>row(u,
      `<div class="row" style="gap:6px"><button class="btn-sm btn-primary" data-lulus="${esc(u.uid)}|approved">Lulus</button><button class="btn-sm btn-danger" data-lulus="${esc(u.uid)}|rejected">Tolak</button></div>`)).join('') : '')
    + (lulus.length ? `<details class="card small"><summary><b>Akaun ejen diluluskan (${lulus.length})</b></summary>${lulus.map(u=>`<div class="row" style="margin-top:8px"><span class="grow">${esc(u.nama)} <span class="muted">${esc(u.emel||'')}</span></span><button class="btn-sm btn-danger" data-lulus="${esc(u.uid)}|rejected">Sekat</button></div>`).join('')}</details>` : '');
}
function vAhli(id){
  const a = (S.team||[]).find(x=>x.uid===id); if(!a) return go('#/pasukan');
  const C = calc(a);
  $('#app').innerHTML = `
    <div class="row"><h2 class="grow">${esc(a.profile.nama)}</h2><button class="btn-sm" onclick="go('#/pasukan/ejen')">← Ejen</button></div>
    <div class="small muted" style="margin:-8px 0 10px">${esc(a.profile.kod||'')} ${a.profile.tel?`· <a target="_blank" href="https://wa.me/${esc(waNum(a.profile.tel))}">${esc(a.profile.tel)}</a>`:''} · kemaskini ${a.updatedAt?fmtDate(a.updatedAt):'-'}</div>
    ${dashboardHTML(a, true)}
    ${contestCards(a, true)}
    <h3>Pelanggan ${BULAN[CUR_M-1]}</h3>
    ${C.rows[CUR_M-1].list.map(e=>`<div class="card row" style="padding:10px 14px"><span class="grow">${esc(e.nama)} <span class="badge">${STATUS[e.status]||''}</span></span><span>${RM(e.budget)} → <b>${RM(e.achieve)}</b></span></div>`).join('') || '<div class="card muted small">Tiada.</div>'}`;
}
function vContestSetup(){
  const list = clone(S.contests||[]);
  const draw = () => {
    $('#app').innerHTML = `
      <div class="row"><h2 class="grow">Contest Ejen</h2><button class="btn-sm" onclick="go('#/pasukan/kumpulan')">← Contest</button></div>
      <p class="small muted" style="margin-top:-6px">Semua ejen nampak contest ini, dan progress dikira automatik dari Achieve mereka.</p>
      ${list.map((c,i)=>`<div class="card">
        <label style="margin-top:0">Nama contest</label><input data-i="${i}" data-k="nama" value="${esc(c.nama)}">
        <div class="row">
          <div class="grow"><label>Jenis</label><select data-i="${i}" data-k="jenis"><option value="ace" ${c.jenis==='ace'?'selected':''}>ACE (RM)</option><option value="kes" ${c.jenis==='kes'?'selected':''}>Bilangan kes</option></select></div>
          <div class="grow"><label>Sasaran</label><input data-i="${i}" data-k="sasaran" inputmode="decimal" value="${c.sasaran||''}"></div>
        </div>
        <div class="row">
          <div class="grow"><label>Dari</label><select data-i="${i}" data-k="dari">${BLN.map((b,j)=>`<option value="${j+1}" ${c.dari===j+1?'selected':''}>${b}</option>`).join('')}</select></div>
          <div class="grow"><label>Hingga</label><select data-i="${i}" data-k="hingga">${BLN.map((b,j)=>`<option value="${j+1}" ${c.hingga===j+1?'selected':''}>${b}</option>`).join('')}</select></div>
          <button class="btn-sm btn-danger" style="align-self:flex-end" data-del="${i}">Buang</button>
        </div></div>`).join('')}
      <div class="row">
        <button class="grow" id="add">+ Contest</button>
        ${list.length?'':'<button class="grow" id="contoh">Guna contoh dari APA</button>'}
      </div>
      <button class="btn-primary" style="width:100%;margin-top:10px" id="sv">Simpan Contest</button>`;
    document.querySelectorAll('[data-k]').forEach(el=>el.onchange=el.oninput=()=>{ const c=list[el.dataset.i], k=el.dataset.k; c[k] = (k==='nama'||k==='jenis') ? el.value : num(el.value); });
    document.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{ list.splice(+b.dataset.del,1); draw(); });
    $('#add').onclick=()=>{ list.push({id:uid(), nama:'', sasaran:0, jenis:'ace', dari:1, hingga:12}); draw(); };
    $('#contoh') && ($('#contoh').onclick=()=>{ list.push(...clone(CONTEST_CONTOH)); draw(); });
    $('#sv').onclick=async()=>{ await saveContests(list.filter(c=>c.nama)); toast('Contest disimpan'); go('#/pasukan/kumpulan'); };
  };
  draw();
}

/* ---------------- ROUTER ---------------- */
const APA = window.APA = {
  init, S,
  h: { S, calc, RM, pct, num, bar, colorFor, BULAN, BLN, PROP_ASAL, THIS_Y, get CUR_M(){ return CUR_M; }, get YEAR(){ return YEAR; } },
  setYear, get YEAR(){ return YEAR; }, THIS_Y,
  years(){ const ys=new Set([THIS_Y-1, THIS_Y, THIS_Y+1, YEAR, ...Object.keys(S.me?.years||{}).map(Number)]); return [...ys].filter(Boolean).sort(); },
  route(parts, fromRemote){
    const [view, a, b, c] = parts;
    const editing = /\/(kes|p100\/|tetapan|contest$)/.test(location.hash) && location.hash!=='#/apa/p100' && location.hash!=='#/apa/contest';
    if(fromRemote && (editing || /^#\/pasukan\/(contest|.*\/edit)/.test(location.hash))) return;   // jangan ganggu borang
    if(view==='pasukan'){
      if(S.role==='agent') return go('#/apa');
      if(a==='contest') return vContestSetup();
      if(a==='ejen') return vPasukan();
      if(!a || ['plan','kumpulan','tetapan-mapa'].includes(a)) return window.MAPA ? MAPA.route(a,b,c) : vPasukan();
      return vAhli(a);
    }
    if(!S.me) return;
    if(needSetup() && a!=='tetapan' && a!=='borang') return vSetup();
    if(a==='bulan') return vBulan(b);
    if(a==='kes') return vKes(b, c);
    if(a==='p100') return b ? vP100Form(b) : vP100();
    if(a==='contest') return vContest();
    if(a==='tetapan') return vTetapan();
    if(a==='borang') return vBorang();
    return vDash();
  },
};
})();
