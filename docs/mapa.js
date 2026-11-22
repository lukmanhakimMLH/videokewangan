/* =====================================================================
   MAPA — pelan agensi leader (berdasarkan MAPA_LEADERS_QAIZER_2026.numbers)
   Planning: leader isi Active Agent, Productivity, Avg Case Size, NR setiap bulan.
   Actual:   DIKIRA AUTOMATIK dari APA ejen (ACE, NOC, Active Agent) + Rekrut (NR = calon jadi Coded),
             campur pelarasan manual (untuk ejen yang belum guna app).
   Simpanan: meta/mapa<TAHUN> (leader sahaja).
   ===================================================================== */
(function(){
const A = () => window.APA.h;               // helper dari apa.js
const Y = () => A().YEAR, CM = () => A().CUR_M;   // ikut tahun dipilih

/* Nilai asal dari fail MAPA 2026 */
const PLAN_ASAL = {
  active:[3,10,11,11,12,12,14,15,18,18,20,20],
  prod:[3,4,4,4,4,4,4,4,4,4,4,4],
  size:Array(12).fill(3600),
  nr:Array(12).fill(2),
};
const LALU_ASAL = [ // MAPA 2025
  {man:5,active:1,noc:2,ace:15000,nr:0},{man:6,active:1,noc:3,ace:21975,nr:1},{man:6,active:2,noc:15,ace:107459,nr:0},
  ...Array(8).fill(0).map(()=>({man:0,active:0,noc:0,ace:0,nr:0})), {man:20,active:0,noc:0,ace:0,nr:0}];
const CONTEST_ASAL = [
  {id:'g1', nama:'Guangzhou — Tier 1', sasaran:100000, dari:1, hingga:3},
  {id:'g2', nama:'Guangzhou — Tier 2', sasaran:200000, dari:1, hingga:3},
  {id:'g3', nama:'Guangzhou — Tier 3', sasaran:400000, dari:1, hingga:3},
  {id:'mda', nama:'MDA', sasaran:1000000, dari:1, hingga:12},
  {id:'ssa', nama:'Summit South Africa', sasaran:180000, dari:1, hingga:12},
];
const fresh = () => ({
  base:20, ce:95, pr:89, prop:null,
  plan: Array(12).fill(0).map((_,i)=>({active:PLAN_ASAL.active[i], prod:PLAN_ASAL.prod[i], size:PLAN_ASAL.size[i], nr:PLAN_ASAL.nr[i]})),
  manual: Array(12).fill(0).map(()=>({ace:0,noc:0,active:0,nr:0})),
  lalu: Y()===2026 ? JSON.parse(JSON.stringify(LALU_ASAL)) : Array(12).fill(0).map(()=>({man:0,active:0,noc:0,ace:0,nr:0})),
  contests: JSON.parse(JSON.stringify(CONTEST_ASAL)),
});

/* ---------------- STORE ---------------- */
const M = { doc:null, ref:null, loaded:false, pending:false, db:undefined, year:0, unsub:null };
function init(db){ M.db = db; M.year = 0; ensureYear(); }
function ensureYear(){
  if(M.db===undefined || M.year===Y()) return;
  M.year = Y(); M.loaded = false; M.doc = null; if(M.unsub){ M.unsub(); M.unsub = null; }
  const db = M.db;
  if(db){
    M.ref = db.doc('meta/mapa'+Y());
    M.unsub = M.ref.onSnapshot(s=>{ if(M.pending) return; M.doc = s.exists ? JSON.parse(JSON.stringify(s.data())) : (M.doc||fresh()); M.loaded=true; rerender(); },
      ()=>{ M.doc ||= fresh(); M.loaded=true; rerender(); });
  } else {
    M.ref = null; try{ M.doc = JSON.parse(localStorage.getItem('mapa-local-'+Y())||'null'); }catch{}
    M.doc ||= fresh(); M.loaded = true;
  }
}
function rerender(){ const h=location.hash; if(/^#\/pasukan(\/(plan|kumpulan|tetapan-mapa)?)?$/.test(h) && !/\/edit/.test(h)) window.APA.route(h.slice(2).split('/'), true); }
let saveT;
function save(){
  if(!M.ref){ try{ localStorage.setItem('mapa-local-'+Y(), JSON.stringify(M.doc)); }catch{} return Promise.resolve(); }
  M.pending = true; clearTimeout(saveT);
  return new Promise(res=>{ saveT=setTimeout(async()=>{ try{ await M.ref.set(JSON.parse(JSON.stringify(M.doc))); }catch{ toast('Gagal simpan MAPA'); } M.pending=false; res(); },300); });
}

/* ---------------- KIRAAN ---------------- */
async function compute(){
  const h = A(), D = M.doc || fresh(), prop = D.prop || h.PROP_ASAL;
  const team = (h.S.team||[]).filter(a=>a.profile?.nama).map(a=>({a, C:h.calc(a)}));
  let rekrut = []; try{ rekrut = await DB.all(); }catch{}
  const codedMonth = r => { const c=(r.history||[]).find(x=>x.status==='coded'); if(!c) return 0; const d=new Date(c.date); return d.getFullYear()===Y() ? d.getMonth()+1 : 0; };
  const nrAuto = Array(12).fill(0); rekrut.forEach(r=>{ const m=codedMonth(r); if(m) nrAuto[m-1]++; });
  let manP = D.base, manA = D.base;
  const rows = Array(12).fill(0).map((_,i)=>{
    const p = D.plan[i], mn = D.manual[i] || {};
    const pNoc = p.active*p.prod, pAce = pNoc*p.size;
    const ace = team.reduce((s,t)=>s+t.C.rows[i].achieve,0) + (+mn.ace||0);
    const noc = team.reduce((s,t)=>s+t.C.rows[i].kes,0) + (+mn.noc||0);
    const active = team.filter(t=>t.C.rows[i].kes>0).length + (+mn.active||0);
    const nr = nrAuto[i] + (+mn.nr||0);
    const out = { m:i+1, plan:{man:manP, active:p.active, prod:p.prod, size:p.size, noc:pNoc, ace:pAce, nr:p.nr},
      act:{man:manA, active, prod: active? noc/active : 0, size: noc? ace/noc : 0, noc, ace, nr, nrAuto:nrAuto[i]}, lalu:D.lalu[i]||{} };
    manP += p.nr; manA += nr;   // Man bulan depan = Man + NR (macam formula MAPA)
    return out;
  });
  const goal = rows.reduce((s,r)=>s+r.plan.ace,0);
  rows.forEach((r,i)=>{ r.budget = goal*(prop[i]||0)/100; r.variance = r.act.ace - r.budget; });
  let acc=0; rows.forEach(r=>{ acc+=r.variance; r.acc=acc; });
  const achieve = rows.reduce((s,r)=>s+r.act.ace,0);
  const ytdBudget = rows.filter(r=>r.m<=CM()).reduce((s,r)=>s+r.budget,0);
  return { D, rows, goal, achieve, ytdBudget, team, prop, coded: rekrut.filter(r=>r.status==='coded').length, rekrutN: rekrut.length };
}

/* ---------------- UI ---------------- */
function tabs(active){
  const t=[['','📊','Dashboard'],['plan','📋','MAPA'],['ejen','👥','Ejen'],['kumpulan','🏆','Contest'],['tetapan-mapa','⚙︎','Tetapan']];
  return `<div class="tabs">${t.map(([k,i,l])=>`<button class="${active===k?'on':''}" onclick="go('#/pasukan${k?'/'+k:''}')"><span>${i}</span>${l}</button>`).join('')}</div>`;
}
const n0 = v => Math.round(+v||0).toLocaleString('en-MY');
const n1 = v => (Math.round((+v||0)*100)/100).toLocaleString('en-MY');

async function vDashboard(){
  const h=A(), R=await compute(), cur=R.rows[CM()-1], p=h.pct(R.achieve,R.goal);
  const pendN = (h.S.users||[]).filter(u=>u.status==='pending').length;
  $('#app').innerHTML = tabs('') + `
    ${pendN?`<div class="card row" style="cursor:pointer" onclick="go('#/pasukan/ejen')"><span class="grow">🔔 <b>${pendN}</b> permohonan akaun ejen menunggu kelulusan</span><span>›</span></div>`:''}
    <div class="card">
      <div class="row"><div class="grow"><div class="small muted">Group Goal ACE ${Y()}</div><div style="font-size:22px;font-weight:800">${h.RM(R.goal)}</div></div>
        <div style="text-align:right"><div class="small muted">CE · PR</div><b>${R.D.ce||0}% · ${R.D.pr||0}%</b></div></div>
      ${h.bar(p, h.colorFor(h.pct(R.achieve,R.ytdBudget)))}
      <div class="row small"><span class="grow">Achieve <b>${h.RM(R.achieve)}</b> (${p}%)</span><span>Shortfall <b style="color:#d32f2f">${h.RM(Math.min(0,R.achieve-R.goal))}</b></span></div>
    </div>
    <div class="stats" style="margin-bottom:12px">
      <div class="stat"><b style="font-size:16px">${h.RM(cur.act.ace)}</b><span class="small muted">${h.BULAN[CM()-1]} (${h.pct(cur.act.ace,cur.budget)}%)</span></div>
      <div class="stat"><b style="font-size:16px">${cur.act.active} / ${cur.plan.active}</b><span class="small muted">Active agent</span></div>
      <div class="stat"><b style="font-size:16px">${cur.act.man}</b><span class="small muted">Manpower · NR ${cur.act.nr}</span></div>
    </div>
    <h3>Bajet vs Achieve kumpulan</h3>
    <div class="card" style="padding:8px;overflow-x:auto"><table class="tbl">
      <thead><tr><th></th><th>Bulan</th><th>${Y()-1}</th><th>Bajet</th><th>Achieve</th><th>%</th><th>+/-</th></tr></thead>
      <tbody>${R.rows.map((r,i)=>`<tr class="${r.m===CM()?'cur':''}" onclick="go('#/pasukan/plan')">
        <td class="muted">${i%3===0?'Q'+(i/3+1):''}</td><td>${h.BLN[i]}</td><td class="muted">${n0(r.lalu.ace)}</td><td>${n0(r.budget)}</td>
        <td><b>${n0(r.act.ace)}</b></td><td style="color:${r.act.ace?h.colorFor(h.pct(r.act.ace,r.budget)):'var(--muted)'}">${r.budget?h.pct(r.act.ace,r.budget)+'%':'-'}</td>
        <td style="color:${r.variance<0?'#d32f2f':'var(--S)'}">${r.m<=CM()?n0(r.variance):''}</td></tr>`).join('')}</tbody>
      <tfoot><tr><td></td><td>Jumlah</td><td>${n0(R.rows.reduce((s,r)=>s+(+r.lalu.ace||0),0))}</td><td>${n0(R.goal)}</td><td>${n0(R.achieve)}</td><td>${p}%</td><td>${n0(R.achieve-R.goal)}</td></tr></tfoot>
    </table></div>
    <h3>Achieve setiap ejen (Agent Budget)</h3>
    ${agentMatrix(R)}
    <p class="small muted">Actual dikira automatik dari APA ejen & Rekrut. Pelarasan manual di tab 📋 MAPA.</p>`;
}
function agentMatrix(R){
  const h=A();
  if(!R.team.length) return '<div class="card empty muted small">Belum ada ejen isi APA.</div>';
  const t = R.team.slice().sort((x,y)=>y.C.achieve-x.C.achieve);
  return `<div class="card" style="padding:8px;overflow-x:auto"><table class="tbl">
    <thead><tr><th>Ejen</th>${h.BLN.map(b=>`<th>${b}</th>`).join('')}<th>YTD</th><th>%Goal</th></tr></thead>
    <tbody>${t.map(({a,C})=>`<tr onclick="go('#/pasukan/${a.uid}')"><td style="text-align:left">${esc(a.profile.nama.split(' ').slice(0,2).join(' '))}</td>
      ${C.rows.map(r=>`<td class="${r.m===CM()?'':'muted'}" style="${r.achieve?'color:var(--ink);font-weight:600':''}">${r.achieve?n0(r.achieve):'·'}</td>`).join('')}
      <td><b>${n0(C.achieve)}</b></td><td style="color:${h.colorFor(h.pct(C.achieve,C.ytdBudget))}">${h.pct(C.achieve,C.goal)}%</td></tr>`).join('')}</tbody>
    <tfoot><tr><td style="text-align:left">TOTAL</td>${R.rows.map(r=>`<td>${n0(r.act.ace-(+(R.D.manual[r.m-1]||{}).ace||0))}</td>`).join('')}<td>${n0(t.reduce((s,x)=>s+x.C.achieve,0))}</td><td></td></tr></tfoot>
  </table></div>`;
}

let planMode = 'act';
async function vPlan(){
  const h=A(), R=await compute();
  const cols = [['man','Man'],['active','Active'],['prod','Prod.'],['size','Avg Case'],['noc','NOC'],['ace','ACE'],['nr','NR']];
  const get = (r,k) => planMode==='plan' ? r.plan[k] : planMode==='act' ? r.act[k] : (k==='prod' ? (r.lalu.active? r.lalu.noc/r.lalu.active : 0) : k==='size' ? (r.lalu.noc? r.lalu.ace/r.lalu.noc : 0) : r.lalu[k]);
  const fmt = (k,v) => k==='prod' ? n1(v) : n0(v);
  const tot = k => k==='man' ? get(R.rows[11],k) : ['active','prod','size'].includes(k) ? R.rows.reduce((s,r)=>s+(+get(r,k)||0),0)/12 : R.rows.reduce((s,r)=>s+(+get(r,k)||0),0);
  $('#app').innerHTML = tabs('plan') + `
    <div class="seg" style="margin-bottom:10px" id="md">
      <button data-v="plan" class="${planMode==='plan'?'on':''}">Planning ${Y()}</button>
      <button data-v="act" class="${planMode==='act'?'on':''}">Actual ${Y()}</button>
      <button data-v="lalu" class="${planMode==='lalu'?'on':''}">${Y()-1}</button>
    </div>
    <p class="small muted" style="margin:0 0 8px">${planMode==='plan'?'Tekan bulan untuk ubah plan. NOC = Active × Prod, ACE = NOC × Avg Case.'
      : planMode==='act'?'Auto dari APA ejen (ACE, NOC, Active) & Rekrut (NR = Coded). Tekan bulan untuk pelarasan manual.'
      : 'Rekod tahun lepas — tekan bulan untuk isi.'}</p>
    <div class="card" style="padding:8px;overflow-x:auto"><table class="tbl">
      <thead><tr><th></th><th>Bulan</th>${cols.map(([,l])=>`<th>${l}</th>`).join('')}</tr></thead>
      <tbody>${R.rows.map((r,i)=>`<tr class="${r.m===CM()?'cur':''}" onclick="go('#/pasukan/plan/edit/${r.m}')">
        <td class="muted">${i%3===0?'Q'+(i/3+1):''}</td><td>${h.BLN[i]}</td>
        ${cols.map(([k])=>{ const v=get(r,k); let st='';
          if(planMode==='act' && ['active','noc','ace','nr'].includes(k)){ const pv=r.plan[k]; if(r.m<=CM() && pv) st=`color:${h.colorFor(h.pct(v,pv))}`; }
          return `<td style="${st}">${fmt(k,v)}</td>`; }).join('')}</tr>`).join('')}</tbody>
      <tfoot><tr><td></td><td>Jumlah</td>${cols.map(([k])=>{ const v=tot(k); return `<td>${v===null?'':fmt(k,v)}</td>`; }).join('')}</tr></tfoot>
    </table></div>
    ${planMode==='act'?`<div class="card small"><b>Plan vs Actual (YTD hingga ${h.BLN[CM()-1]})</b>
      ${[['ACE','ace',h.RM],['NOC','noc',n0],['NR','nr',n0]].map(([l,k,f])=>{ const a=R.rows.slice(0,CM()).reduce((s,r)=>s+r.act[k],0), pl=R.rows.slice(0,CM()).reduce((s,r)=>s+r.plan[k],0);
        return `<div style="margin-top:8px">${l}: <b>${f(a)}</b> / ${f(pl)} (${h.pct(a,pl)}%)${h.bar(h.pct(a,pl),h.colorFor(h.pct(a,pl)))}</div>`; }).join('')}</div>`:''}`;
  document.querySelectorAll('#md button').forEach(b=>b.onclick=()=>{ planMode=b.dataset.v; vPlan(); });
}
async function vPlanEdit(m){
  m=+m; const h=A(), R=await compute(), r=R.rows[m-1], D=M.doc;
  const inp = (id,l,v,note='') => `<label>${l}</label><input id="${id}" inputmode="decimal" value="${v??''}">${note?`<div class="small muted">${note}</div>`:''}`;
  let body='';
  if(planMode==='plan') body = inp('active','Active agent',D.plan[m-1].active)+inp('prod','Productivity (kes / active agent)',D.plan[m-1].prod)+inp('size','Avg case size (RM)',D.plan[m-1].size)+inp('nr','NR (rekrut baru)',D.plan[m-1].nr);
  else if(planMode==='act'){ const mn=D.manual[m-1]||{};
    body = `<div class="small muted">Auto dari app bulan ini: ACE ${h.RM(r.act.ace-(+mn.ace||0))}, NOC ${r.act.noc-(+mn.noc||0)}, Active ${r.act.active-(+mn.active||0)}, NR ${r.act.nrAuto}.<br>Isi <b>tambahan</b> untuk ejen yang belum guna app (boleh 0).</div>`
      + inp('ace','Tambahan ACE (RM)',mn.ace||0)+inp('noc','Tambahan NOC (kes)',mn.noc||0)+inp('active','Tambahan active agent',mn.active||0)+inp('nr','Tambahan NR',mn.nr||0); }
  else { const l=D.lalu[m-1]||{}; body = inp('man','Man',l.man)+inp('active','Active agent',l.active)+inp('noc','NOC',l.noc)+inp('ace','ACE (RM)',l.ace)+inp('nr','NR',l.nr); }
  $('#app').innerHTML = `<h2>${h.BULAN[m-1]} — ${planMode==='plan'?'Planning '+Y():planMode==='act'?'Pelarasan Actual':''+(Y()-1)}</h2>
    <div class="card">${body}</div>
    <div class="row"><button class="btn-primary grow" id="sv">Simpan</button><button onclick="history.back()">Batal</button></div>`;
  $('#sv').onclick = async () => {
    const v = id => h.num($('#'+id).value);
    if(planMode==='plan') D.plan[m-1] = {active:v('active'), prod:v('prod'), size:v('size'), nr:v('nr')};
    else if(planMode==='act') D.manual[m-1] = {ace:v('ace'), noc:v('noc'), active:v('active'), nr:v('nr')};
    else D.lalu[m-1] = {man:v('man'), active:v('active'), noc:v('noc'), ace:v('ace'), nr:v('nr')};
    await save(); toast('Disimpan'); go('#/pasukan/plan');
  };
}

async function vKumpulan(){
  const h=A(), R=await compute(), list=R.D.contests||[];
  $('#app').innerHTML = tabs('kumpulan') + `<h3 style="margin-top:0">Contest kumpulan (leader)</h3>` + (list.map(c=>{
      const val=R.rows.filter(r=>r.m>=c.dari&&r.m<=c.hingga).reduce((s,r)=>s+r.act.ace,0), pc=c.sasaran?Math.min(100,h.pct(val,c.sasaran)):0, sh=val-c.sasaran;
      return `<div class="card" style="padding:12px 14px"><div class="row"><b class="grow">${esc(c.nama)}</b><span class="small muted">${h.BLN[c.dari-1]}–${h.BLN[c.hingga-1]}</span></div>
        ${h.bar(pc,h.colorFor(pc))}<div class="row small"><span class="grow">${h.RM(val)} / ${h.RM(c.sasaran)}</span><b style="color:${sh<0?'#d32f2f':'var(--S)'}">${sh<0?'Kurang '+h.RM(-sh):'✓ Layak'}</b></div></div>`;
    }).join('') || '<div class="card empty muted">Tiada contest kumpulan.</div>') + `
    <button style="width:100%" onclick="go('#/pasukan/kumpulan/edit')">✏️ Ubah contest kumpulan</button>
    <h3>Contest ejen</h3>
    <p class="small muted" style="margin-top:0">Contest yang setiap ejen nampak dalam APA masing-masing.</p>
    <button style="width:100%" onclick="go('#/pasukan/contest')">🏆 Tetapkan contest ejen (${(h.S.contests||[]).length})</button>`;
}
function vKumpulanEdit(){
  const h=A(), list=JSON.parse(JSON.stringify(M.doc.contests||[]));
  const draw=()=>{ $('#app').innerHTML = `<h2>Contest kumpulan</h2>` + list.map((c,i)=>`<div class="card">
      <label style="margin-top:0">Nama</label><input data-i="${i}" data-k="nama" value="${esc(c.nama)}">
      <label>Sasaran ACE (RM)</label><input data-i="${i}" data-k="sasaran" inputmode="decimal" value="${c.sasaran||''}">
      <div class="row"><div class="grow"><label>Dari</label><select data-i="${i}" data-k="dari">${h.BLN.map((b,j)=>`<option value="${j+1}" ${c.dari===j+1?'selected':''}>${b}</option>`).join('')}</select></div>
      <div class="grow"><label>Hingga</label><select data-i="${i}" data-k="hingga">${h.BLN.map((b,j)=>`<option value="${j+1}" ${c.hingga===j+1?'selected':''}>${b}</option>`).join('')}</select></div>
      <button class="btn-sm btn-danger" style="align-self:flex-end" data-del="${i}">Buang</button></div></div>`).join('')
    + `<button style="width:100%" id="add">+ Contest</button><div class="row" style="margin-top:10px"><button class="btn-primary grow" id="sv">Simpan</button><button onclick="history.back()">Batal</button></div>`;
    document.querySelectorAll('[data-k]').forEach(el=>el.oninput=el.onchange=()=>{ const c=list[el.dataset.i],k=el.dataset.k; c[k]= k==='nama'?el.value:h.num(el.value); });
    document.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{ list.splice(+b.dataset.del,1); draw(); });
    $('#add').onclick=()=>{ list.push({id:uid(),nama:'',sasaran:0,dari:1,hingga:12}); draw(); };
    $('#sv').onclick=async()=>{ M.doc.contests=list.filter(c=>c.nama); await save(); toast('Disimpan'); go('#/pasukan/kumpulan'); };
  }; draw();
}

function vTetapan(){
  const h=A(), D=M.doc, prop=D.prop||h.PROP_ASAL;
  $('#app').innerHTML = tabs('tetapan-mapa') + `
    <div class="card">
      <label style="margin-top:0">Manpower awal tahun (Man akhir ${Y()-1})</label><input id="base" inputmode="numeric" value="${D.base}">
      <div class="row"><div class="grow"><label>Current CE (%)</label><input id="ce" inputmode="decimal" value="${D.ce||''}"></div><div class="grow"><label>Current PR (%)</label><input id="pr" inputmode="decimal" value="${D.pr||''}"></div></div>
    </div>
    <div class="card"><b>Pecahan bajet kumpulan ikut bulan (%)</b><div class="small muted">Bajet bulan = Group Goal × %. Jumlah mesti 100%.</div>
      <div class="prop-grid">${h.BLN.map((b,i)=>`<label style="margin:6px 0 2px">${b}</label><input class="prop" inputmode="decimal" value="${prop[i]}">`).join('')}</div>
      <div class="small" style="margin-top:8px">Jumlah: <b id="psum"></b></div></div>
    <button class="btn-primary" style="width:100%" id="sv">Simpan</button>`;
  const sum=()=>{ const s=[...document.querySelectorAll('.prop')].reduce((a,e)=>a+h.num(e.value),0); $('#psum').textContent=(Math.round(s*100)/100)+'%'; $('#psum').className=Math.abs(s-100)<0.05?'ok':'err'; return s; };
  document.querySelectorAll('.prop').forEach(e=>e.oninput=sum); sum();
  $('#sv').onclick=async()=>{ if(Math.abs(sum()-100)>=0.05) return toast('Jumlah mesti 100%');
    Object.assign(D,{base:h.num($('#base').value), ce:h.num($('#ce').value), pr:h.num($('#pr').value), prop:[...document.querySelectorAll('.prop')].map(e=>h.num(e.value))});
    await save(); toast('Disimpan'); go('#/pasukan'); };
}

window.MAPA = {
  init, tabs,
  route(a, b, c){
    ensureYear();
    if(!M.loaded){ $('#app').innerHTML = '<div class="card empty muted">Memuatkan MAPA…</div>'; return; }
    if(a==='plan') return b==='edit' ? vPlanEdit(c) : vPlan();
    if(a==='kumpulan') return b==='edit' ? vKumpulanEdit() : vKumpulan();
    if(a==='tetapan-mapa') return vTetapan();
    return vDashboard();
  },
};
})();
