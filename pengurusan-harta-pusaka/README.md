# Pengurusan Harta Pusaka

Web app untuk ejen: muat naik laporan kredit (CCRIS / CTOS / Experian / CBM), senaraikan hutang dan aset, kira kos pengurusan pusaka dan keperluan hibah, simulasi faraid, dan jana laporan PDF bertandatangan untuk pelanggan.

**Privasi:** semua pemprosesan berlaku dalam peranti pengguna. Laporan kredit, data pelanggan dan tandatangan pelanggan tidak dihantar atau disimpan di mana-mana server. Hanya nama, no. telefon dan tandatangan perunding diingat dalam pelayar peranti itu.

## Fail

- `app.html` — sumber app (juga diterbitkan sebagai Claude Artifact).
- `build.sh` — bina web app luar talian ke folder `app/`.
- `app/` — web app sedia untuk dihoskan (index.html, library, ikon, manifest, service worker). Berfungsi tanpa internet selepas dibuka kali pertama.

Selepas menukar `app.html`, jalankan `./build.sh` dan commit folder `app/`.

## Pasang di iPad

1. Buka pautan app dalam **Safari**.
2. Tekan butang **Kongsi** (petak dengan anak panah ke atas).
3. Pilih **Tambah ke Skrin Utama** (Add to Home Screen), kemudian **Tambah**.
4. Buka app daripada ikon oren "Harta Pusaka". Selepas itu ia boleh digunakan tanpa internet.

Laporan PDF dikongsi melalui skrin kongsi iPad: WhatsApp, Mel, Simpan ke Fail atau Print.
