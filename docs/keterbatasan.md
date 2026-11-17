# Keterbatasan

Dokumen ini menjelaskan apa yang **tidak** diklaim oleh hasil 2.964 kata.

---

## 1. "Semua bacaan" = definisi KANJIDIC2

Universe disusun dari bacaan yang terdaftar KANJIDIC2, termasuk bacaan arkais, ateji, dan bacaan alternatif yang sudah tidak dipakai dalam bahasa Jepang modern.

Contoh: 虞 punya 8 bacaan kun di KANJIDIC2, tetapi hanya おそれ yang punya kata pendukung (虞). Sisanya (おもんぱかる, はかる, うれえる, あざむく, あやまる, のぞむ, たのしむ) tidak muncul di JMdict.

Konsekuensinya, klaim yang benar adalah:

> "2.964 kata menutup seluruh bacaan kanji jōyō **menurut KANJIDIC2**."

bukan:

> "2.964 kata membuat Anda bisa membaca semua kata Jepang."

---

## 2. 709 bacaan mustahil

747 unit bacaan tidak punya satu pun kata JMdict. Verifikasi ulang menemukan 38 di antaranya hanya artefak aturan penyelarasan (mis. 三つ みっつ, 手堅い てがたい), sehingga **709 benar-benar kosong**.

Karakteristik:

| Aspek | Jumlah |
|---|---|
| Kun'yomi | 482 |
| On'yomi | 227 |
| Dari kanji kyōiku (grade 1–6) | 223 |
| Dari jōyō tambahan 2010 (grade 8) | 486 |

Kategori:

1. **Ateji kata serapan** — 米 めえとる (メートル), 立 りっとる (リットル), 馬 ぼ.
2. **Bacaan klasik** — 天 あまつ, 往 いにしえ, 為 たり, 畏 かしこし, 旦 あした.
3. **On'yomi langka** — 圧 えん (kata 圧延 dibaca あつえん), 闇 おん, 壱 いつ.
4. **Bacaan yang di JMdict selalu memakai kanji lain** — 医 いやす → 癒す, 愛 おしむ → 惜しむ, 線 すじ → 筋.
5. **"Padding" kamus** — bacaan alternatif yang hanya ada di kamus kanji besar.

Bacaan-bacaan ini tidak bisa dipelajari lewat kosakata; hanya lewat daftar bacaan kanji.

---

## 3. Penyelarasan bersifat heuristik

Aturan penyelarasan (stem/okurigana, rendaku, sokuon) adalah pendekatan, bukan definisi formal. Dampaknya:

- 22,4% kata gagal diselaraskan. Sebagian besar benar (jukujikun), tetapi sebagian kecil sebenarnya bisa jika aturannya diperluas.
- 38 kasus batas yang diketahui (contoh: 三つ みっつ, 四つ よっつ) memengaruhi hasil paling banyak **38 kata**.

Artinya angka 2.964 bisa bergeser sedikit (lebih kecil) jika aturan diperbaiki — bukan lebih besar, karena kata tambahan hanya menambah pilihan.

---

## 4. Solver tidak unik

ILP berhenti pada gap 0,09%, dan di antara solusi berukuran sama ada banyak alternatif. Menjalankan ulang `03_solve_cover.py` bisa menghasilkan **himpunan kata berbeda dengan ukuran sama** (atau 2.962–2.964).

Yang stabil dan bisa dikutip:

- **jumlah kata**: 2.962–2.964,
- **cakupan**: 5.840/5.840 unit,
- **efisiensi**: ± 2,26 bacaan per kata.

---

## 5. Tidak ada pembobotan frekuensi

Tujuan optimasi hanya "jumlah kata minimum". Akibatnya:

- Kata langka lebih sering terpilih karena menutup banyak bacaan sekaligus.
- Kata umum seperti 食べる, 学校, 手紙 justru tidak masuk daftar.
- Urutan file (berdasarkan bacaan) bukan urutan belajar yang baik.

Daftar ini adalah **referensi teoretis**, bukan kurikulum. Untuk belajar, urutkan sendiri berdasarkan frekuensi (mis. JPDB) dan targetkan 90–95% (2.380–2.672 kata).

---

## 6. Kyōiku belum terbukti optimal

Untuk subset kyōiku:

- 3.159 unit bisa ditutup,
- solusi terbaik yang diketahui **1.710 kata**,
- batas bawah LP **1.486**.

Gap 13% belum tertutup, jadi angka 1.710 adalah batas atas, bukan nilai optimum.

---

## 7. Ketergantungan versi data

Hasil terikat pada:

- JMdict 2026-11-15,
- KANJIDIC2 database 2026-320.

JMdict diperbarui beberapa kali sebulan. Pembaruan bisa menambah kata (memperkecil solusi) atau menambah bacaan baru di KANJIDIC2 (memperbesar masalah). Cantumkan versi saat mengutip hasil ini.
