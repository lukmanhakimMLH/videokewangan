/* Firebase backend untuk versi web (tanpa Claude).
   Sediakan API kecil yang sama bentuk dengan `claude.use('db' | 'user')` supaya index.html & apa.js tak perlu berubah.
   Peranan:
   - Leader: emel dalam peraturan Firestore (isLeader) + emel disahkan. Dikesan dengan cuba baca meta/leader.
   - Ejen: daftar sendiri → users/<uid> status 'pending' → leader luluskan → boleh guna APA. */
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js';
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword,
  sendPasswordResetEmail, sendEmailVerification, signOut } from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, memoryLocalCache,
  doc, collection, getDoc, getDocFromServer, setDoc, updateDoc, deleteDoc, onSnapshot } from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js';

const firebaseConfig = {
  apiKey: "AIzaSyCLB84sE3lsKprZbrD8Gkmd4f9b1bNpyMg",
  authDomain: "qaizer-arg313.firebaseapp.com",
  projectId: "qaizer-arg313",
  storageBucket: "qaizer-arg313.firebasestorage.app",
  messagingSenderId: "674833168304",
  appId: "1:674833168304:web:dabbb2809a0d49e7a14875",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
let fs;
try { fs = initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) }); }
catch { fs = initializeFirestore(app, { localCache: memoryLocalCache() }); }

/* ---------- adapter: bentuk sama macam claude db ---------- */
const mapErr = e => ({ code: e?.code === 'permission-denied' ? 'invalid_argument' : (e?.code === 'resource-exhausted' ? 'quota_exceeded' : 'unavailable'), message: e?.message || '' });
const wrapDoc = s => ({ id: s.id, exists: s.exists(), data: () => s.data(), metadata: s.metadata });
const guard = p => p.catch(e => { throw mapErr(e); });
function docRef(path){
  const r = doc(fs, path);
  return { id: r.id, path,
    get: async () => wrapDoc(await guard(getDoc(r))),
    set: d => guard(setDoc(r, d)),
    update: d => guard(updateDoc(r, d)),
    delete: () => guard(deleteDoc(r)),
    onSnapshot: (next, err) => onSnapshot(r, { includeMetadataChanges: true }, s => next(wrapDoc(s)), e => err && err(mapErr(e))),
    collection: sub => colRef(path + '/' + sub),
  };
}
function colRef(path){
  const c = collection(fs, path);
  return { path,
    doc: id => docRef(path + '/' + (id || doc(c).id)),
    onSnapshot: (next, err) => onSnapshot(c, { includeMetadataChanges: true },
      s => next({ docs: s.docs.map(wrapDoc), size: s.size, empty: s.empty, metadata: s.metadata }), e => err && err(mapErr(e))),
  };
}
const DBAPI = { doc: docRef, collection: colRef };

/* ---------- UI log masuk ---------- */
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const app$ = () => document.getElementById('app');
const hideChrome = on => { const t = document.getElementById('title'); if (t && on) t.textContent = 'QAIZER ARG313'; const f = document.getElementById('fab'); if (f) f.classList.toggle('hidden', on); const n = document.getElementById('nav'); if (n && on) n.innerHTML = ''; };
const msgFor = e => ({
  'auth/invalid-credential': 'Emel atau kata laluan salah.', 'auth/wrong-password': 'Emel atau kata laluan salah.',
  'auth/user-not-found': 'Akaun tidak dijumpai.', 'auth/email-already-in-use': 'Emel ini sudah didaftarkan — sila log masuk.',
  'auth/weak-password': 'Kata laluan minimum 6 aksara.', 'auth/invalid-email': 'Format emel tidak sah.',
  'auth/too-many-requests': 'Terlalu banyak cubaan. Cuba lagi sebentar.', 'auth/network-request-failed': 'Tiada sambungan internet.',
}[e?.code] || 'Ralat: ' + (e?.code || e?.message || 'tidak diketahui'));

function showLogin(mode = 'masuk', note = ''){
  hideChrome(true);
  const daftar = mode === 'daftar';
  app$().innerHTML = `
    <div style="max-width:420px;margin:24px auto 0">
      <h2 style="text-align:center;font-size:22px">QAIZER ARG313</h2>
      <p class="muted small" style="text-align:center;margin-top:-6px">${daftar ? 'Daftar akaun baru' : 'Log masuk ke akaun anda'}</p>
      <div class="card">
        <label>Emel</label><input id="em" type="email" autocomplete="email" inputmode="email">
        <label>Kata laluan</label><input id="pw" type="password" autocomplete="${daftar ? 'new-password' : 'current-password'}" placeholder="${daftar ? 'Minimum 6 aksara' : ''}">
        ${daftar ? '<label>Ulang kata laluan</label><input id="pw2" type="password" autocomplete="new-password">' : ''}
        <p class="small err" id="err">${esc(note)}</p>
        <button class="btn-primary" style="width:100%" id="go">${daftar ? 'Daftar' : 'Log masuk'}</button>
        ${daftar ? '' : '<button class="btn-sm" style="width:100%;margin-top:8px;border:0" id="lupa">Lupa kata laluan?</button>'}
      </div>
      <p style="text-align:center" class="small">${daftar ? 'Sudah ada akaun?' : 'Ejen baru?'}
        <a href="#" id="tukar">${daftar ? 'Log masuk' : 'Daftar akaun'}</a></p>
    </div>`;
  const err = t => { $('#err').textContent = t; $('#err').className = 'small err'; };
  $('#tukar').onclick = e => { e.preventDefault(); showLogin(daftar ? 'masuk' : 'daftar'); };
  $('#go').onclick = async () => {
    const em = $('#em').value.trim(), pw = $('#pw').value;
    if (!em || !pw) return err('Isi emel dan kata laluan.');
    if (daftar && pw !== $('#pw2').value) return err('Kata laluan tidak sama.');
    $('#go').disabled = true;
    try {
      if (daftar) { const c = await createUserWithEmailAndPassword(auth, em, pw); sendEmailVerification(c.user).catch(() => {}); }
      else await signInWithEmailAndPassword(auth, em, pw);
    } catch (e) { err(msgFor(e)); $('#go').disabled = false; }
  };
  $('#pw').onkeydown = e => { if (e.key === 'Enter' && !daftar) $('#go').click(); };
  $('#lupa') && ($('#lupa').onclick = async () => {
    const em = $('#em').value.trim(); if (!em) return err('Isi emel dahulu, kemudian tekan "Lupa kata laluan?".');
    try { await sendPasswordResetEmail(auth, em); $('#err').className = 'small ok'; $('#err').textContent = 'Emel tetapan semula kata laluan telah dihantar. Semak inbox / spam.'; }
    catch (e) { err(msgFor(e)); }
  });
}

function showProfile(u){
  hideChrome(true);
  app$().innerHTML = `
    <div style="max-width:420px;margin:24px auto 0">
      <h2>Lengkapkan profil</h2>
      <p class="muted small" style="margin-top:-6px">${esc(u.email)}</p>
      <div class="card">
        <label>Nama penuh *</label><input id="nm">
        <label>Kod ejen</label><input id="kd">
        <label>No. tel *</label><input id="tl" type="tel" inputmode="tel">
        <p class="small err" id="err"></p>
        <button class="btn-primary" style="width:100%" id="go">Hantar untuk kelulusan</button>
      </div>
      <button class="btn-sm" style="border:0" id="out">Log keluar</button>
    </div>`;
  $('#out').onclick = () => signOut(auth);
  $('#go').onclick = async () => {
    const nama = $('#nm').value.trim(), tel = $('#tl').value.trim();
    if (!nama || !tel) { $('#err').textContent = 'Nama dan no. tel wajib.'; return; }
    $('#go').disabled = true;
    try {
      await setDoc(doc(fs, 'users', u.uid), { nama, kod: $('#kd').value.trim(), tel, emel: u.email, status: 'pending', createdAt: Date.now() });
      afterLogin(u);
    } catch (e) { $('#err').textContent = 'Gagal simpan (' + (e.code || e.message) + ')'; $('#go').disabled = false; }
  };
}

function showPending(u, d){
  hideChrome(true);
  const rejected = d?.status === 'rejected';
  app$().innerHTML = `
    <div style="max-width:420px;margin:24px auto 0">
      <div class="card" style="text-align:center">
        <div style="font-size:40px">${rejected ? '⛔' : '⏳'}</div>
        <h2>${rejected ? 'Akses tidak diluluskan' : 'Menunggu kelulusan leader'}</h2>
        <p class="muted">${rejected ? 'Sila hubungi leader anda.' : `Hai ${esc(d?.nama || '')}, akaun anda sudah didaftarkan. Leader perlu luluskan sebelum anda boleh guna APA.`}</p>
        <button class="btn-primary" id="semak">Semak semula</button>
        ${u.emailVerified ? '' : `<p class="small muted" style="margin-top:14px">Emel belum disahkan. <a href="#" id="sah">Hantar semula emel pengesahan</a></p>`}
      </div>
      <p class="small muted">Leader: sahkan emel anda melalui link dalam emel dari Firebase, kemudian tekan <b>Semak semula</b>.</p>
      <button class="btn-sm" style="border:0" id="out">Log keluar (${esc(u.email)})</button>
    </div>`;
  $('#out').onclick = () => signOut(auth);
  $('#semak').onclick = async () => { $('#semak').disabled = true; try { await u.reload(); await u.getIdToken(true); } catch {} afterLogin(auth.currentUser); };
  $('#sah') && ($('#sah').onclick = async e => { e.preventDefault(); try { await sendEmailVerification(u); e.target.textContent = 'Dihantar ✓ — semak inbox / spam'; } catch (x) { e.target.textContent = msgFor(x); } });
}

/* ---------- aliran selepas log masuk ---------- */
let resolved = false, currentUid = null;
async function afterLogin(u){
  app$().innerHTML = '<div class="card empty muted">Memuatkan…</div>';
  let leader = false;
  const key = 'qz-leader-' + u.uid;
  try { await getDocFromServer(doc(fs, 'meta', 'leader')); leader = true; }
  catch (e) { leader = e?.code === 'unavailable' && localStorage.getItem(key) === '1'; }   // luar talian: guna status terakhir
  try { leader ? localStorage.setItem(key, '1') : localStorage.removeItem(key); } catch {}
  if (!leader) {
    let me;
    try { me = await getDocFromServer(doc(fs, 'users', u.uid)); } catch { try { me = await getDoc(doc(fs, 'users', u.uid)); } catch {} }
    if (!me || !me.exists()) return showProfile(u);
    window.__ME = me.data();
    if (window.__ME.status !== 'approved') return showPending(u, window.__ME);
  }
  addLogout(u);
  resolved = true; currentUid = u.uid;
  window.__fbResolve({
    use: async name => name === 'db' ? DBAPI
      : name === 'user' ? { id: async () => u.uid, isOwner: async () => leader, canEdit: async () => leader, can: async () => true }
      : null,
  });
}
function addLogout(u){
  const top = document.querySelector('header .top'); if (!top || document.getElementById('logout')) return;
  const b = document.createElement('button'); b.id = 'logout'; b.className = 'btn-sm'; b.textContent = '⎋'; b.title = 'Log keluar ' + u.email;
  b.onclick = async () => { if (confirmLogout()) { await signOut(auth); } };
  top.appendChild(b);
}
const confirmLogout = () => window.confirm('Log keluar dari app?');

onAuthStateChanged(auth, u => {
  if (resolved) { if (!u || u.uid !== currentUid) location.reload(); return; }
  if (!u) return showLogin();
  afterLogin(u);
});
