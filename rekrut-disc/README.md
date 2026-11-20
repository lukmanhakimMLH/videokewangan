# Rekrut Takaful · DISC

App rekrut ejen takaful (satu fail `index.html`, tiada server). Buka terus dalam browser telefon/laptop.

- Profil calon: nama, telefon, IC (auto kira umur & jantina), alamat, pendidikan, gambar, sumber, nota
- Pipeline: Prospek → Temuduga → Daftar Exam → Lulus Exam → Coded (dengan sejarah tarikh)
- Ujian DISC 20 soalan (Paling Saya / Paling Bukan Saya) + panduan coach & pitch ikut jenis
- Backup/Restore JSON, export CSV untuk Excel
- Bila dibuka melalui link claude.ai: data disimpan dalam akaun Claude (peribadi, sync antara peranti). Di luar claude.ai: IndexedDB browser — buat backup selalu

## APA (Annual Plan ejen) — `apa.js`
Dibina dari `APA_QAIZER_2026.numbers`: Goal ACE, pecahan % bulanan, bajet vs achieve setiap bulan,
senarai pelanggan bulanan (pledge / FU / closed), Project 100, dan contest.

- **Ejen** (bukan pemilik link): nampak APA dia sahaja. Data di `apa/<id ejen>`.
- **Leader** (pemilik): tab Rekrut, APA sendiri dan Pasukan (asas MAPA) — baca APA semua ejen,
  tetapkan contest (`config/contests`), dan import "Calon Rekrut" dari Project 100 ejen ke Rekrut.
