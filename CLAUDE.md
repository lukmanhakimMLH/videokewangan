# Video Kewangan — Lukman Hakim

Repo ni untuk edit video pendek (TikTok / Reels / Shorts) Lukman Hakim: siri "Kata-kata Hari Ini" dan kandungan kewangan.
Berbual dengan user dalam Bahasa Melayu santai.

## Standard yang dah diluluskan (video pertama: `kata-kata/`)

Setiap video baru ikut gaya ni kecuali user minta lain. Rujukan penuh: `kata-kata/index.html` + `src/tools/index.tpl.html`.

**Gaya:** profesional, elegan, padu. Hitam + emas, tak serabut.

1. **Potong:** transcribe dulu (faster-whisper `medium`, `language="ms"`, word timestamps), buang semua awkward pause, ayat berulang dan filler ("So," yang tergantung dan seumpamanya). Potong setiap bahagian dengan ffmpeg `-ss` + afade 30–40ms, kemudian concat demuxer. Jangan guna satu filter_complex trim yang besar sebab kena OOM. Lepas potong, transcribe semula hasilnya untuk semak.
2. **Color grade + lighting** (dibakar dalam ffmpeg, rujuk `src/grade.txt`): kurangkan highlight tingkap, hitam lebih dalam, kulit hangat yang neutral, bayang sedikit kebiruan, vignette, unsharp ringan. Jangan terlalu oren atau pudar.
3. **Audio suara:** highpass 90 → afftdn → EQ (+3k, −250) → compressor → loudnorm I=−15.
4. **Hook pada frame 0** (jadi thumbnail sekali): soalan 3 baris, kata kunci besar dalam Playfair Display italic emas, contohnya "Siapa yang paling *jujur* tentang dirimu?". Disertai bunyi impact dan zoom masuk.
5. **Badge atas:** "KATA-KATA HARI INI" emas, letter-spaced, ada garisan di kiri kanan.
6. **Caption:** dua baris, setiap perkataan keluar ikut masa dia cakap. Montserrat 700 putih, kata kunci dalam Playfair italic 800 emas yang lebih besar. Letak di atas kepala (y≈290–550), jangan tutup muka.
7. **Signature:** "Lukman" dalam font Monsieur La Doulaise (path SVG di `src/sig.json`), emas berkilat, animasi macam ditulis tangan + swash + glint. Di bawahnya **LUKMAN HAKIM** (EB Garamond, emas). Letak kiri bawah (`top: 1410px`) dari saat ~2 sampai hujung.
8. **Motion:** zoom masuk pada setiap jump cut (alternate 1.00/1.06), punch-in pada kata kunci, light leak semasa transisi.
9. **Klimaks / ayat penutup:** letterbox masuk, video gelap sikit, petikan muncul sebaris demi sebaris (emas + putih serif).
10. **End card:** signature besar, LUKMAN HAKIM, kemudian "💼 FINANCIAL CONTENT CREATOR 📈" dan "*Insan biasa, bercita-cita luar biasa* ✨". **JANGAN letak "Selamat Pagi".** End card bertahan ±4.7s.
11. **SFX + muzik** (jana sendiri dengan `src/sfx.py`, tiada isu copyright): impact (hook dan klimaks), whoosh (transisi), shimmer (signature, nama Allah, end card), tick (kata kunci), subdrop, riser, dan pad lembut pada volume 0.11.

## Aliran kerja

- Video dari Google Drive: `pip install gdown` → `gdown <id>`. Video iPhone biasanya ada rotation −90, jadi ffmpeg autorotate jadi 1080×1920.
- Projek baru: `hyperframes init <nama> --video <graded.mp4> --skip-transcribe --non-interactive --resolution portrait`. Baca skill `/hyperframes` dulu sebelum tulis composition.
- Jana `index.html` dari template: `src/tools/build.py` (masa caption datang dari transcript) dan `src/tools/index.tpl.html`. Salin dan sesuaikan untuk video baru.
- Lepas edit: `npx hyperframes check --json` (mesti 0 error) dan `npx hyperframes snapshot --at ...`, kemudian tengok frame-frame tu sendiri.
- **Tunjuk preview dulu, jangan render** sampai user setuju. Preview: `src/tools/preview.py` jana `preview/index.html` + `preview.mp4` (720p, audio dah dicampur), kemudian publish sebagai Artifact.
- Bila user setuju: `npx hyperframes render -o renders/<nama>.mp4 -q delivery --fps 30 --workers 2`, kemudian hantar fail tu kepada user untuk download.
- Font emoji untuk render: `@font-face { font-family: "EmojiColor"; src: local("Noto Color Emoji"); }`
- Kerja di branch (bukan `main`). Commit dan push. Fail besar yang boleh dijana semula dan folder `renders/` di-gitignore.
