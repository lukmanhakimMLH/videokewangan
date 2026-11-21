# Klien Loan

App untuk WhatsApp klien ikut status kes dalam **ejenplus** (agent.ejenplus.com).

**Cara guna**
1. Tab **Tetapan** → login dengan akaun ejenplus (sekali sahaja; password tak disimpan, cuma token sesi).
2. Tekan **⟳ Sync** → semua submission, label HQ (Case Layak, Case Tak Layak, Checking Q&A…) dan nota HQ ditarik.
3. Senarai **Perlu WhatsApp** = klien yang status berubah tapi belum dimaklumkan.
4. Buka klien → template dipilih automatik ikut label. Nota HQ (sebab tak layak / dokumen diperlukan) masuk sebagai `{nota}`. Edit kalau perlu → **Hantar WhatsApp**.
5. **Case Layak**: semua kes berlabel Case Layak terus masuk tab **Case Layak**. Tekan ✅ Approve / ⏳ Tengah Proses Loan / ✖ Client Cancel (cancel → Arkib).
6. **Komisen**: kes Approve masuk sini (atau cari mana-mana klien). Isi jumlah komisen & tanda Dibayar / Belum bayar.
7. Ubah template & label mana guna template mana dalam tab **Template WhatsApp**.

Data kes disimpan dalam browser phone sahaja dan tak masuk repo ni. App auto-sync setiap kali dibuka atau kembali ke depan (kecuali baru sync < 1 minit).
