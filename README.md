# videokewangan — Mesin Video Affiliate TikTok

Bagi **screenshot produk** → dapat **skrip + video 9:16 siap upload** (suara AI BM, caption satu‑perkataan, infografik, muzik).

Gaya ditiru dari video rujukan (power bank & perfume dalam kereta):
caption besar satu perkataan di tengah, angka spec bercahaya, senarai feature, harga promo, CTA "tekan beg kuning".

---

## Cara guna (paling senang)

1. Hantar screenshot produk kat Claude (Shopee / TikTok Shop / Lazada pun boleh) + info tambahan kalau ada (harga promo, pengalaman kau guna).
2. Claude akan:
   - buat folder `projek/<nama-produk>/`
   - tulis `skrip.json` ikut **Formula Skrip** bawah
   - render `keluaran/video.mp4`
3. Kau upload. Siap.

## Cara guna (manual)

```bash
pip install -r requirements.txt          # perlu ffmpeg juga
cp -r projek/contoh projek/produk-baru   # tukar produk.jpg + edit skrip.json
python3 buat_video.py projek/produk-baru --pratonton   # semak cepat (540p)
python3 buat_video.py projek/produk-baru               # final 1080x1920
```

Keluaran dalam `projek/<nama>/keluaran/`:
- `video.mp4` — video final
- `skrip_teleprompter.txt` — kalau nak rakam suara sendiri / shoot sendiri
- `caption_tiktok.txt` — caption + hashtag

---

## Formula Skrip (dari analisa video rujukan)

| # | Peranan | Tujuan | Contoh ayat |
|---|---------|--------|-------------|
| 1 | **HOOK** | 2 saat pertama — masalah / harga mengejut | "Weh korang, aku dah lama cari power bank yang kecik tapi power." / "Nak turun ke harga Most Wanted ni lagi?" |
| 2 | **SPEC** | Nombor besar + banding | "Bukan 2000, bukan 3000, tapi 10000 mAh." |
| 3 | **FEATURE** | Apa dapat dalam kotak / bau / bahan | "Siap ada dua kabel…" / "Bau sweet toffee campur sikit spicy." |
| 4 | **BUKTI** | Pengalaman sendiri | "Aku charge dari 20% ke 90% sejam je." |
| 5 | **GUNA** | Bila/mana sesuai | "Dalam poket boleh, dalam beg boleh, dalam kereta pun boleh." |
| 6 | **TIPS/AMARAN** *(pilihan)* | Bina kepercayaan | "Pakai waktu malam je, jangan tengah panas — nanti pening." |
| 7 | **PROMO** | Harga + urgency | "Harga dah murah, tapi sekarang promo 11.11. Lagi murah." |
| 8 | **CTA** | Arah ke beg kuning | "So kalau korang berminat, terus tekan beg kuning bawah ni." |

Panjang ideal: **30–45 saat**, bahasa santai (korang, aku, je, tau, weh).

---

## Rujukan `skrip.json`

```jsonc
{
  "nama_produk": "…",
  "gambar_produk": ["produk.jpg", {"fail": "ss2.png", "potong": [0, 0.1, 1, 0.7]}],  // potong = x0,y0,x1,y1 (0..1)
  "gambar_aku": "aku.jpg",          // gambar kau (untuk babak hook/bukti)
  "suara": "ms-MY-OsmanNeural",     // lelaki. Perempuan: ms-MY-YasminNeural
  "laju": "+12%",
  "muzik": true,                    // true = beat dijana, "lagu.mp3" = guna lagu sendiri, false = tiada
  "caption_tiktok": "…",
  "babak": [
    {
      "peranan": "SPEC",
      "visual": "produk",            // produk | zoom | aku | aku+produk
      "gambar": 0,                   // indeks gambar_produk
      "fokus": [0.5, 0.4],           // untuk visual "zoom"
      "overlay": {"jenis": "angka", "teks": "10,000", "unit": "mAh", "label": "KAPASITI"},
      "teks": "Bukan dua ribu, tapi 10000 mAh. *Padu* gila.",   // *perkataan* = caption kuning
      "jeda": 0.12                   // senyap lepas babak (saat)
    }
  ]
}
```

Jenis `overlay`:
- `angka` — `teks`, `unit`, `label` (nombor kira naik)
- `senarai` — `item: [...]` (tick hijau muncul satu-satu)
- `harga` — `label`, `asal`, `baru` (harga lama dipotong, harga baru pop)
- `tag` — `teks`, `warna` (`kuning`/`merah`/`hijau`)
- `cta` — `teks`, `sub` (butang kuning + anak panah ke beg kuning)

Caption: nombor & `RM` automatik jadi kuning.
