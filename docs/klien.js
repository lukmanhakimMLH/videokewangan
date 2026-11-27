/* =====================================================================
   KLIEN — borang pelanggan penuh, dokumen IC (gambar/PDF), due bulanan
   Dokumen disimpan berasingan: apa/<uid>/fail/<id>  (supaya doc APA tak melebihi 1MB)
   ===================================================================== */
(function(){
const H = () => window.APA.h;
const PRODUK = ['CI FIRST','LIFE FIRST','INVEST FIRST'];
const POTONGAN = ['Angkasa','Kad kredit','Kad debit','Account bank'];
const MAX_PDF = 700*1024;

/* ---------- simpanan dokumen ---------- */
const fileRef = fid => { const S=H().S; return S.db && S.uid ? S.db.doc(`apa/${S.uid}/fail/${fid}`) : null; };
async function putFile(fid, rec){
  const r = fileRef(fid);
  if(r) return r.set(rec);
  try{ localStorage.setItem('fail-'+fid, JSON.stringify(rec)); }catch{ throw {code:'quota_exceeded'}; }
}
async function getFile(fid){
  const r = fileRef(fid);
  if(r){ const s = await r.get(); return s.exists ? s.data() : null; }
  try{ return JSON.parse(localStorage.getItem('fail-'+fid)||'null'); }catch{ return null; }
}
async function delFile(fid){ const r=fileRef(fid); if(r) return r.delete().catch(()=>{}); try{ localStorage.removeItem('fail-'+fid); }catch{} }
const readDataURL = f => new Promise((res,rej)=>{ const r=new FileReader(); r.onload=()=>res(r.result); r.onerror=rej; r.readAsDataURL(f); });
function dataURLtoBlobURL(d){
  const [head, b64] = d.split(','); const mime = head.match(/data:([^;]+)/)?.[1] || 'application/octet-stream';
  const bin = atob(b64), u = new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
  return URL.createObjectURL(new Blob([u], {type:mime}));
}

/* ---------- due bulanan ---------- */
const parseDate = s => { const [y,m,d] = String(s||'').split('-').map(Number); return y&&m&&d ? new Date(y,m-1,d) : null; };
const dueOn = (y, m, day) => new Date(y, m, Math.min(day, new Date(y, m+1, 0).getDate()));
function dues(doc){
  const seen = new Set(), out = [], today = new Date(); today.setHours(0,0,0,0);
  for(const [y, Y] of Object.entries(doc?.years||{})) for(const [m, list] of Object.entries(Y.months||{})) for(const e of list||[]){
    const d0 = parseDate(e.inforce); if(!d0) continue;
    const key = e.polisi || e.id; if(seen.has(key)) continue; seen.add(key);
    const day = d0.getDate();
    let next = dueOn(today.getFullYear(), today.getMonth(), day);
    if(next < today) next = dueOn(today.getFullYear(), today.getMonth()+1, day);
    if(next < d0) next = d0;
    out.push({ e, y:+y, m:+m, day, next, days: Math.round((next - today)/864e5) });
  }
  return out.sort((a,b)=>a.days-b.days);
}
const bila = d => d===0 ? 'Hari ini' : d===1 ? 'Esok' : `${d} hari lagi`;
const dueRow = o => `<div class="card agent" style="padding:10px 14px" onclick="KLIEN.open(${o.y},${o.m},'${o.e.id}')">
    <div class="avatar" style="width:44px;height:44px;font-size:15px;background:${o.days<=1?'var(--D)':o.days<=7?'var(--I)':'var(--line)'};color:${o.days<=7?'#fff':'var(--muted)'}">${o.day}</div>
    <div class="grow"><b>${esc(o.e.nama)}</b><div class="small muted">${[o.e.produk, o.e.potongan, o.e.polisi&&('Polisi '+o.e.polisi)].filter(Boolean).map(esc).join(' · ')}</div></div>
    <div style="text-align:right"><b class="small" style="color:${o.days<=1?'#d32f2f':'inherit'}">${bila(o.days)}</b><div class="small muted">${fmtDate(o.next)}</div></div></div>`;
function dueHTML(doc){
  const all = dues(doc); if(!all.length) return '';
  const soon = all.filter(o=>o.days<=7);
  return `<h3>🔔 Due premium ${soon.length?`<span class="badge D">${soon.length}</span>`:''}</h3>
    ${soon.length ? soon.map(dueRow).join('') : '<div class="card small muted">Tiada due dalam 7 hari.</div>'}
    <button style="width:100%;margin-bottom:12px" onclick="go('#/apa/due')">Lihat semua due (${all.length}) ›</button>`;
}
function vDue(){
  const h=H(), all = dues(h.S.me);
  $('#app').innerHTML = h.tabs('') + `<h2>🔔 Due premium bulanan</h2>
    <p class="small muted" style="margin-top:-6px">Ikut hari bulan Tarikh Inforce setiap polisi.</p>
    ${all.length ? `<button class="btn-primary" style="width:100%;margin-bottom:12px" id="calAll">📅 Masukkan semua ke Kalendar telefon</button>` + all.map(dueRow).join('')
      : '<div class="card empty muted">Belum ada pelanggan dengan Tarikh Inforce.</div>'}`;
  $('#calAll') && ($('#calAll').onclick = () => saveICS(all, 'due-semua'));
}

/* ---------- kalendar (.ics) — telefon beri notifikasi setiap bulan ---------- */
const icsEsc = s => String(s||'').replace(/\\/g,'\\\\').replace(/[,;]/g,m=>'\\'+m).replace(/\n/g,'\\n');
const ymd = d => `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;
function saveICS(items, name){
  const stamp = new Date().toISOString().replace(/[-:]/g,'').slice(0,15)+'Z';
  const ev = items.map(o=>{ const e=o.e, by = o.day>28 ? '-1' : String(o.day);
    return ['BEGIN:VEVENT', `UID:${e.polisi||e.id}@qaizer-apa`, `DTSTAMP:${stamp}`, `DTSTART;VALUE=DATE:${ymd(o.next)}`,
      `RRULE:FREQ=MONTHLY;BYMONTHDAY=${by}`, `SUMMARY:${icsEsc('Due: '+e.nama+(e.produk?' ('+e.produk+')':''))}`,
      `DESCRIPTION:${icsEsc([e.polisi&&'No polisi: '+e.polisi, e.potongan&&'Potongan: '+e.potongan, e.tel&&'Tel: '+e.tel].filter(Boolean).join('\n'))}`,
      'BEGIN:VALARM','TRIGGER:-PT15H','ACTION:DISPLAY',`DESCRIPTION:${icsEsc('Esok due: '+e.nama)}`,'END:VALARM',
      'BEGIN:VALARM','TRIGGER:PT9H','ACTION:DISPLAY',`DESCRIPTION:${icsEsc('Hari ini due: '+e.nama)}`,'END:VALARM','END:VEVENT'].join('\r\n'); });
  const ics = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//QAIZER//APA//MS','CALSCALE:GREGORIAN', ...ev, 'END:VCALENDAR'].join('\r\n');
  const a = document.createElement('a');
  a.href = 'data:text/calendar;charset=utf-8,' + encodeURIComponent(ics); a.download = name + '.ics'; a.target = '_blank';
  document.body.appendChild(a); a.click(); a.remove();
  toast('Buka fail & tekan "Add" / "Tambah" ke Kalendar');
}

/* ---------- borang pelanggan ---------- */
function open(y, m, id){ if(y && y!==H().YEAR) window.APA.setYear(y); go(`#/apa/kes/${m}/${id}`); }
async function vKes(m, id){
  const h=H(), S=h.S; m=+m;
  const Y = (S.me.years[h.YEAR] ||= {goal:0,ce:0,pr:0,prop:[...h.PROP_ASAL],months:{}}), list = (Y.months[m] ||= []);
  const e = id==='baru' ? {id:uid(), status:'pledge', fail:[]} : list.find(x=>x.id===id);
  if(!e) return go('#/apa/bulan/'+m);
  const files = (e.fail||[]).map(f=>({...f}));         // {id,nama,jenis,size,data?,baru?}
  const removed = [];
  const opt = (arr, v) => `<option value="">— pilih —</option>` + arr.map(x=>`<option ${x===v?'selected':''}>${x}</option>`).join('');
  $('#app').innerHTML = `
    <h2>${id==='baru'?'Tambah':'Kemaskini'} Pelanggan · ${h.BULAN[m-1]}</h2>
    <div class="card">
      <b>👤 Maklumat pelanggan</b>
      <label>Nama client *</label><input id="nama" list="p100list" value="${esc(e.nama)}">
      <datalist id="p100list">${(S.me.p100||[]).map(p=>`<option value="${esc(p.nama)}">`).join('')}</datalist>
      <label>No IC</label><input id="ic" inputmode="numeric" value="${esc(e.ic)}" placeholder="900101-01-1234"><div class="small muted" id="icInfo">${icInfo(e.ic)}</div>
      <label>No telefon</label><input id="tel" type="tel" inputmode="tel" value="${esc(e.tel)}">
      <label>Pekerjaan</label><input id="kerja" value="${esc(e.kerja)}">
      <label>Nama syarikat bekerja</label><input id="syarikat" value="${esc(e.syarikat)}">
      <label>Alamat</label><textarea id="alamat">${esc(e.alamat)}</textarea>
    </div>
    <div class="card">
      <b>📑 Polisi</b>
      <label>No polisi</label><input id="polisi" value="${esc(e.polisi)}">
      <label>Tarikh inforce</label><input id="inforce" type="date" value="${esc(e.inforce)}">
      <div class="small muted" id="dueInfo"></div>
      <div class="row"><div class="grow"><label>Produk</label><select id="produk">${opt(PRODUK, e.produk)}</select></div>
        <div class="grow"><label>Jenis potongan</label><select id="potongan">${opt(POTONGAN, e.potongan)}</select></div></div>
    </div>
    <div class="card">
      <b>📄 Dokumen IC (gambar / PDF)</b>
      <div id="flist" style="margin-top:8px"></div>
      <div class="row" style="margin-top:8px">
        <label class="btn btn-sm" style="margin:0">📷 Ambil gambar<input type="file" accept="image/*" capture="environment" class="hidden fadd"></label>
        <label class="btn btn-sm" style="margin:0">📎 Pilih gambar / PDF<input type="file" accept="image/*,application/pdf" multiple class="hidden fadd"></label>
      </div>
    </div>
    <div class="card">
      <b>💰 Jualan</b>
      <label>Pledge / Bajet ACE (RM)</label><input id="budget" inputmode="decimal" value="${e.budget??''}">
      <label>Status</label>
      <div class="seg" id="st">${Object.entries({pledge:'Pledge', fu:'Follow-up', closed:'Closed'}).map(([k,v])=>`<button type="button" data-v="${k}" class="${e.status===k?'on':''}">${v}</button>`).join('')}</div>
      <label>Achieve ACE (RM) — isi bila kes closed</label><input id="achieve" inputmode="decimal" value="${e.achieve??''}">
      <label>Bulan</label><select id="bulan">${h.BULAN.map((b,i)=>`<option value="${i+1}" ${i+1===m?'selected':''}>${b}</option>`).join('')}</select>
      <label>Nota</label><input id="nota" value="${esc(e.nota)}" placeholder="cth: FU Jumaat">
    </div>
    <div class="row">
      <button class="btn-primary grow" id="sv">Simpan</button>
      <button onclick="history.back()">Batal</button>
      ${id!=='baru'?'<button class="btn-danger" id="dl">Padam</button>':''}
    </div>`;

  const ic=$('#ic'); ic.oninput=()=>{ ic.value=fmtIC(ic.value); $('#icInfo').textContent=icInfo(ic.value); };
  const showDue = () => { const d=parseDate($('#inforce').value);
    if(!d){ $('#dueInfo').innerHTML=''; return; }
    const o = dues({years:{x:{months:{1:[{id:'t', nama:$('#nama').value||'Pelanggan', inforce:$('#inforce').value, polisi:$('#polisi').value, produk:$('#produk').value, potongan:$('#potongan').value, tel:$('#tel').value}]}}}})[0];
    $('#dueInfo').innerHTML = `Due setiap <b>${o.day} haribulan</b>${o.day>28?' (bulan pendek: hari terakhir bulan)':''} · seterusnya ${fmtDate(o.next)} (${bila(o.days)})
      <button type="button" class="btn-sm" id="cal" style="margin-top:6px;display:block">📅 Peringatan bulanan di Kalendar</button>`;
    $('#cal').onclick = () => saveICS([o], 'due-'+(o.e.nama||'pelanggan').replace(/\W+/g,'-')); };
  $('#inforce').onchange = showDue; showDue();

  const drawFiles = () => {
    $('#flist').innerHTML = files.length ? files.map((f,i)=>`<div class="row" style="padding:6px 0;border-bottom:1px solid var(--line)">
        ${f.jenis==='image' && f.data ? `<img src="${f.data}" style="width:44px;height:44px;object-fit:cover;border-radius:8px">` : `<div class="avatar" style="width:44px;height:44px;border-radius:8px;font-size:12px">${f.jenis==='pdf'?'PDF':'…'}</div>`}
        <span class="grow small">${esc(f.nama)}<br><span class="muted">${Math.round((f.size||0)/1024)} KB${f.baru?' · belum disimpan':''}</span></span>
        <button class="btn-sm" data-v="${i}" ${f.data?'':'disabled'}>Lihat</button><button class="btn-sm btn-danger" data-x="${i}">✕</button></div>`).join('')
      : '<div class="small muted">Tiada dokumen lagi.</div>';
    document.querySelectorAll('#flist [data-v]').forEach(b=>b.onclick=()=>{ const f=files[+b.dataset.v]; if(f?.data) window.open(dataURLtoBlobURL(f.data), '_blank'); });
    document.querySelectorAll('#flist [data-x]').forEach(b=>b.onclick=()=>{ const [f]=files.splice(+b.dataset.x,1); if(f && !f.baru) removed.push(f.id); drawFiles(); });
  };
  drawFiles();
  files.forEach(async f=>{ const r = await getFile(f.id).catch(()=>null); if(r){ f.data=r.data; drawFiles(); } });
  document.querySelectorAll('.fadd').forEach(inp=>inp.onchange=async ev=>{
    for(const file of ev.target.files){
      try{
        if(file.type==='application/pdf'){
          if(file.size > MAX_PDF){ toast(`PDF ${file.name} terlalu besar (maks 700KB) — ambil gambar sahaja`); continue; }
          const data = await readDataURL(file); files.push({id:uid(), nama:file.name, jenis:'pdf', size:file.size, data, baru:true});
        } else {
          const data = await resizeImage(file, 1400); files.push({id:uid(), nama:file.name||'gambar.jpg', jenis:'image', size:Math.round(data.length*0.75), data, baru:true});
        }
      }catch{ toast('Fail tak dapat dibaca'); }
    }
    ev.target.value=''; drawFiles();
  });

  let st = e.status;
  document.querySelectorAll('#st button').forEach(b=>b.onclick=()=>{ st=b.dataset.v; document.querySelectorAll('#st button').forEach(x=>x.classList.toggle('on',x===b)); });
  $('#sv').onclick = async () => {
    const nama=$('#nama').value.trim(); if(!nama) return toast('Nama wajib');
    $('#sv').disabled = true;
    try{
      for(const f of files.filter(f=>f.baru)){ await putFile(f.id, {data:f.data, nama:f.nama, jenis:f.jenis, size:f.size, entry:e.id, createdAt:Date.now()}); f.baru=false; }
      for(const fid of removed) await delFile(fid);
    }catch(x){ $('#sv').disabled=false; return toast(x?.code==='invalid_argument' ? 'Tiada akses simpan dokumen — minta leader kemaskini peraturan' : 'Gagal simpan dokumen'); }
    const v = k => $('#'+k).value.trim();
    const achieve=h.num($('#achieve').value), nm=+$('#bulan').value;
    const rec = {...e, nama, ic:v('ic'), tel:v('tel'), kerja:v('kerja'), syarikat:v('syarikat'), alamat:v('alamat'),
      polisi:v('polisi'), inforce:v('inforce'), produk:v('produk'), potongan:v('potongan'),
      fail: files.map(({id,nama,jenis,size})=>({id,nama,jenis,size})),
      budget:h.num($('#budget').value), achieve, status: achieve>0 ? 'closed' : st, nota:v('nota')};
    const Yn = (S.me.years[h.YEAR] ||= {goal:0,ce:0,pr:0,prop:[...h.PROP_ASAL],months:{}});   // data terkini (mungkin dimuat semula)
    Yn.months[m] = (Yn.months[m]||[]).filter(x=>x.id!==e.id);
    (Yn.months[nm] ||= []).push(rec);
    await h.save(); toast('Disimpan'); go('#/apa/bulan/'+nm);
  };
  $('#dl') && ($('#dl').onclick = async () => { if(await ask(`Padam ${e.nama}? Dokumen IC juga dipadam.`,'Padam')){
    for(const f of (e.fail||[])) await delFile(f.id);
    const Yn=S.me.years[h.YEAR]; Yn.months[m]=(Yn.months[m]||[]).filter(x=>x.id!==e.id); await h.save(); go('#/apa/bulan/'+m); } });
}

window.KLIEN = { vKes, vDue, dueHTML, open, dues, PRODUK, POTONGAN };
})();
