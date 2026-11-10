# videokewangan — Mesin Video Affiliate TikTok

Bagi **screenshot produk** → dapat **skrip + video 9:16 siap upload**.

- Produk **dipotong automatik** dari screenshot (AI buang latar, BiRefNet — lesen MIT)
- Diletak **atas dashboard kereta waktu malam** (lampu bandar bokeh, pantulan, bayang, kamera bergoyang macam dipegang tangan) — atau studio / gambar latar sendiri
- **Suara BM** dengan intonasi ikut ayat — atau **suara sendiri** / ElevenLabs
- Caption besar satu perkataan, infografik (angka, senarai, harga, CTA beg kuning), muzik beat + SFX bebas hak cipta

---

## Cara guna (paling senang)

Hantar screenshot produk ke Claude (Shopee / TikTok Shop / Lazada) + info: harga promo, pengalaman guna. Claude buat `projek/<produk>/skrip.json`, render, hantar video.

## Cara guna (manual)

```bash
pip install -r requirements.txt     # perlu ffmpeg juga
cp -r projek/contoh projek/produk-baru
# letak screenshot, edit skrip.json
python3 buat_video.py projek/produk-baru --pratonton   # semak cepat
python3 buat_video.py projek/produk-baru               # final 1080x1920
```

Keluaran: `projek/<nama>/keluaran/` → `video.mp4`, `skrip_teleprompter.txt`, `caption_tiktok.txt`.
(Kali pertama, model potong latar ~220MB dimuat turun automatik.)

---

## Pilihan suara (`enjin_suara`)

| Enjin | Kualiti | Perlu |
|---|---|---|
| `edge` (default) | Neural BM (Osman / Yasmin). Setiap ayat dijana berasingan dengan intonasi ikut `gaya` + tanda baca, jeda semula jadi, EQ & kompresi. Bagus, tapi masih boleh dikesan AI. | Tiada |
| `rakaman` | **Paling natural** — suara kau sendiri. Rakam guna `skrip_teleprompter.txt`, caption disegerakkan automatik (Whisper). | `"fail_suara": "suara.m4a"` |
| `elevenlabs` | Sangat natural, ada intonasi manusia. | API key ElevenLabs + `"voice_id"` |

`gaya` setiap babak: `teruja`, `santai`, `yakin`, `serius`, `mendesak`.

Tip sebutan: tulis nombor dalam perkataan, dan guna `[papar|sebut]`:
`[10,000mAh|sepuluh ribu em ei ec]` → caption tunjuk **10,000MAH**, suara sebut betul.

---

## Formula Skrip (dari analisa video rujukan)

| # | Peranan | Gaya | Contoh |
|---|---------|------|--------|
| 1 | **HOOK** | teruja | "Korang pernah tak, bateri telefon dah nak habis, tapi power bank pula besar dan berat?" |
| 2 | **SPEC** | teruja | "Bukan dua ribu, bukan tiga ribu, tetapi sepuluh ribu mAh." |
| 3 | **FEATURE** | santai | "Dalam kotak, siap ada dua kabel…" / "Baunya manis, bercampur sedikit pedas." |
| 4 | **BUKTI** | yakin | "Aku cuba cas daripada dua puluh peratus sampai sembilan puluh peratus. Satu jam sahaja!" |
| 5 | **GUNA** | santai | "Boleh masuk poket, masuk beg, simpan dalam kereta pun boleh." |
| 6 | **TIPS** *(pilihan)* | serius | "Sesuai dipakai waktu malam. Jangan pakai tengah panas, nanti pening." |
| 7 | **PROMO** | mendesak | "Harganya memang dah murah. Tapi sekarang ada promosi sebelas sebelas." |
| 8 | **CTA** | mendesak | "Kalau berminat, tekan beg kuning di bawah ini sekarang, sebelum stok habis." |

Panjang ideal **30–45 saat**. Ejaan BM standard (elak "kecik", "jugak") supaya suara sebut betul.

---

## Rujukan `skrip.json`

```jsonc
{
  "gambar_produk": [{"fail": "ss.jpg", "potong": [0.1, 0.15, 0.9, 0.7]}],  // potong = kawasan produk (x0,y0,x1,y1, 0..1)
  "latar": "kereta_malam",          // kereta_malam | studio | "gambar_latar.jpg"
  "enjin_suara": "edge",            // edge | rakaman | elevenlabs
  "suara": "ms-MY-OsmanNeural",     // atau ms-MY-YasminNeural (perempuan)
  "laju": "+6%",
  "muzik": true,                    // true | "lagu.mp3" | false
  "caption_tiktok": "…",
  "babak": [
    {
      "peranan": "SPEC", "gaya": "teruja",
      "visual": "putar",            // hero | angkat | putar | dekat | screenshot
      "fokus": [0.5, 0.3],          // untuk "dekat"
      "saiz": 0.4,                  // tinggi produk (pecahan skrin), pilihan
      "overlay": {"jenis": "angka", "teks": "10,000", "unit": "mAh", "label": "KAPASITI"},
      "teks": "Bukan dua ribu, tetapi [10,000mAh|sepuluh ribu em ei ec]. *Padu*!",
      "jeda": 0.05
    }
  ]
}
```

**Visual:** `hero` (produk atas dashboard, zoom perlahan) · `angkat` (produk naik macam diangkat) · `putar` (pusing) · `dekat` (close-up) · `screenshot` (tunjuk screenshot asal — untuk harga/review).

**Overlay:** `angka` · `senarai` · `harga` · `tag` · `cta` — lihat `projek/contoh/skrip.json`.
