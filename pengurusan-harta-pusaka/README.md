# Pengurusan Harta Pusaka

Aplikasi web satu halaman (buka `index.html` dalam pelayar).

1. Muat naik PDF laporan kredit (CCRIS / CTOS / Experian / Credit Bureau Malaysia). Nama, No. IC dan senarai hutang (kod HSLNFNCE, PELNFNCE, PCPASCAR, CRDTCARD dll.) dibaca secara automatik. PDF berkata laluan disokong.
2. Semak hutang, tandakan yang dilindungi MRTA / MRTT / Takaful.
3. Aset bercagar dicadangkan daripada laporan; kemas kini nilai dan tambah aset lain.
4. Kos pengurusan pusaka (lalai 5% daripada nilai aset).

**Keperluan hibah = hutang tidak dilindungi + kos pengurusan pusaka + dana tambahan waris**

Semua pemprosesan berlaku dalam pelayar; tiada data dihantar keluar. PDF imbasan / tangkapan skrin tidak dapat dibaca (tiada teks).

`app.html` ialah sumber yang sama tanpa rangka `<html>` (untuk diterbitkan sebagai Artifact).
