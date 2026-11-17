# Laporan Lengkap: 2.964 Kata

**Tanggal:** 17 November 2026
**Output:** `data/kosakata_2964.json` (2.964 entri)
**Basis data:** JMdict 2026-11-15 + KANJIDIC2 (database 2026-320)

---

## 1. Ringkasan Eksekutif

| Item | Nilai |
|---|---|
| Unit bacaan yang harus ditutup | 6.587 (2.854 on'yomi + 3.733 kun'yomi) |
| Bacaan yang mustahil ditutup lewat kosakata | 747 (terverifikasi 709) |
| Bacaan yang bisa ditutup | 5.840 |
| **Jumlah kosakata minimum** | **2.964 kata** |
| Batas bawah terbukti | 2.962 |
| Status optimalitas | Optimum ∈ {2.962, 2.963, 2.964}, gap < 0,1% |
| Efisiensi | 2,48 bacaan per kata |
| Cakupan | 100% bacaan yang bisa ditutup, untuk 2.136 kanji jōyō |

Angka **2.964** adalah jumlah minimum kata berkanji yang harus dihafal agar seluruh bacaan kanji jōyō (termasuk kyōiku) tertutup, jika belajar dengan metode "hafalan kosakata berkanji".

---

## 2. Latar Belakang dan Rumusan Masalah

Metode hafalan bacaan kanji lewat kosakata bekerja dengan asumsi: ketika menghafal 手紙 (てがみ), otomatis belajar 手 = て dan 紙 = かみ. Dengan kata lain, satu kata "menutup" satu bacaan untuk setiap kanji yang dikandungnya (sepanjang bacaan tersebut reguler/komposisional).

Masalahnya: berapa kata minimum yang perlu dihafal agar semua bacaan 2.136 kanji jōyō tertutup? Ini adalah **minimum set cover**:

- **Universe** *U* = himpunan pasangan (kanji, bacaan).
- **Himpunan kandidat** *S* = setiap kata JMdict, yang menutup subset *U*.
- **Tujuan**: pilih *S'* ⊆ *S* dengan |*S'*| minimum sehingga ∪*S'* = *U*.

Set cover bersifat NP-hard, sehingga diselesaikan dengan reduksi + pemrograman linear integer (ILP).

---

## 3. Sumber Data

| Berkas | Isi | Versi | Jumlah |
|---|---|---|---|
| `kanji/JMdict_english.zip` | Kamus kata (Yomitan format 3) | 2026-11-15 | 527.868 baris / 231.653 entri / 306.745 kata unik |
| `kanji/kanjidic2.xml.gz` | Data kanji (bacaan, radikal, grade) | 2026-320 (16 Nov 2026) | 13.108 kanji |
| `kanji/joyo_kanji.txt` | Daftar 常用漢字 | — | 2.136 |
| `kanji/kyoiku_kanji.txt` | Daftar 教育漢字 | — | 1.026 |
| `kanji/JPDB/` | Daftar frekuensi (tidak dipakai di hasil final) | 2024-10-13 | 274.218 kata unik |

Verifikasi silang: seluruh 2.136 kanji jōyō dan 1.026 kanji kyōiku dari file txt ada di KANJIDIC2 (tidak ada yang bolong).

JMdict dipilih sebagai sumber kosakata karena:
1. Jumlah kata aslinya paling banyak (231.653 entri) dibanding Jitendex (210.521) dan JPDB (274.218 surface, tetapi bukan kamus definisi).
2. Basis datanya paling baru (Jitendex 2026-07-09, tertinggal ±4 bulan dan kehilangan 14.364 entri JMdict terbaru).
3. Jitendex diturunkan dari JMdict; tambahannya hanya varian tulisan lama (kyūjitai) yang tidak mengajarkan bacaan baru.

---

## 4. Metodologi

### 4.1 Normalisasi Bacaan

Bacaan dari KANJIDIC2 dinormalisasi agar bisa dibandingkan:

- On'yomi (katakana) dikonversi ke hiragana.
- Tanda titik okurigana (`た.べる`) dipisah menjadi *stem* (`た`) dan *okurigana* (`べる`).
- Tanda afiks (`-う`, `ひと-`) dibuang.
- Bentuk duplikat digabung: `う.まれる` dan `うま.れる` → satu unit `うまれる`.

Hasil: **6.587 unit bacaan** untuk 2.136 kanji jōyō.

### 4.2 Penyelarasan Kata–Bacaan (Alignment)

Setiap entri JMdict diselaraskan secara komposisional: potongan bacaan untuk tiap kanji harus cocok dengan salah satu bacaan kanji tersebut.

Aturan pencocokan:
- On'yomi: potongan bacaan sama persis dengan bacaan on.
- Kun'yomi: potongan = stem, atau stem + okurigana penuh.
- **Rendaku** (連濁): 手紙 てがみ → 紙 dibaca がみ, tetap cocok dengan かみ (perbandingan mengabaikan dakuten/handakuten).
- **Sokuon** (促音): 学校 がっこう → 学 = がっ (dari がく); 実際 じっさい → 実 = じっ (dari じつ).
- **Tanda pengulangan** 々: diperlakukan sebagai kanji sebelumnya (人々 ひとびと).
- **Ditolak** (tidak menutup bacaan apa pun): jukujikun/ateji seperti 大人 おとな, 今日 きょう, 有難う ありがとう, serta bacaan ireguler seperti 日本 にほん.

Hasil penyelarasan:

| Tahap | Jumlah |
|---|---|
| Entri JMdict berkanji | 380.742 |
| Berhasil diselaraskan | 295.396 (77,6%) |
| Pola coverage unik | 138.978 |

Sisa 22,4% gagal selaras karena memang bukan bacaan komposisional (jukujikun), sehingga secara pedagogis tidak mengajarkan bacaan kanji.

### 4.3 Reduksi Masalah

| Reduksi | Efek |
|---|---|
| Buang elemen tanpa kandidat kata | 747 elemen (dari 6.587) |
| **Elemen paksa** (hanya 1 kata yang menutup) | 654 kata wajib, menutup 749 elemen |
| Buang himpunan terdominasi (S ⊂ T) | 138.023 → 86.981 variabel |
| Elemen sisa | 5.091 |

### 4.4 Optimasi

1. **Relaksasi LP** (HiGHS): nilai optimum 2.307,09 → batas bawah total 654 + 2.307,09 = **2.961,09** (dibulatkan 2.962).
2. **ILP / branch-and-bound** (HiGHS, SciPy 1.18): solusi 2.310 kata untuk sisa masalah; dual bound 2.308.
3. **Total**: 654 + 2.310 = **2.964 kata**; batas bawah 654 + 2.308 = **2.962**.

Proses reduksi (dominasi) aman secara matematis: himpunan yang merupakan subset dari himpunan lain tidak pernah dibutuhkan dalam solusi minimum.

### 4.5 Verifikasi

- Coverage akhir: 5.840/5.840 elemen (100%), tanpa duplikasi kata (overlap 0 antara kata wajib dan kata hasil ILP).
- Uji lokal (ruin-and-recreate, 150 detik, puluhan iterasi): tidak ada solusi < 2.964.
- Pencarian heuristik dengan 6 variasi acak: seluruhnya ≥ 3.383 (lebih buruk).

---

## 5. Hasil

### 5.1 Statistik Daftar

| Metrik | Nilai |
|---|---|
| Jumlah kata | 2.964 |
| Kata unik | 2.930 (34 kata terpilih dua kali dengan bacaan berbeda, mis. 生 き / 生 なま) |
| Rata-rata bacaan per kata | 2,48 |
| Kata yang mengajarkan 1 bacaan | 580 |
| Kata yang mengajarkan 2 bacaan | 1.282 |
| Kata yang mengajarkan ≥ 5 bacaan | 189 |
| Maksimum bacaan per kata | 14 |
| Kata satu karakter | ± 100 |
| Entri berupa frasa (mengandung を/に) | 429 |

Distribusi lengkap bacaan per kata: 1→580, 2→1.282, 3→593, 4→320, 5→92, 6→44, 7→26, 8→10, 9→8, 10→4, 11→1, 12→3, 14→1.

### 5.2 Kurva Cakupan (dari basket optimal)

| Target bacaan | Kata dibutuhkan |
|---|---|
| 50% | 792 |
| 70% | 1.298 |
| 80% | 1.527 |
| 90% | 1.758 |
| 95% | 1.858 |
| 99% | 2.060 |
| 100% | 2.964 |

Temuan penting: **1% terakhir (58 bacaan) membutuhkan ± 900 kata**. Ini adalah ekor bacaan langka/arkais.

### 5.3 Skenario Kyōiku Saja

| Item | Nilai |
|---|---|
| Unit bacaan kyōiku | 3.409 |
| Mustahil ditutup | 250 |
| Bisa ditutup | 3.159 |
| Heuristik terbaik | 1.710 kata |
| Batas bawah LP | 1.486 |
| Status | Belum terbukti optimal (gap 13%) |

Angka jōyō (2.964) sudah mencakup seluruh bacaan kyōiku.

### 5.4 Bacaan yang Mustahil

747 unit bacaan tidak memiliki satu pun kata JMdict yang mengajarkannya. Setelah verifikasi ulang, 709 benar-benar kosong dan 38 hanya artefak aturan penyelarasan (mis. 三つ みっつ).

Karakteristik 709 bacaan tersebut:

- 482 kun'yomi + 227 on'yomi.
- 223 berasal dari kanji kyōiku (grade 1–6); 486 dari jōyō tambahan 2010 (grade 8).
- Kategori: ateji satuan (米 めえとる = メートル, 立 りっとる = リットル), bacaan klasik (天 あまつ, 為 たり, 畏 かしこし), on'yomi langka (圧 えん, 闇 おん), bacaan yang di JMdict selalu memakai kanji lain (医 いやす → 癒す, 愛 おしむ → 惜しむ), serta "padding" KANJIDIC2 (虞 punya 8 bacaan kun, hanya おそれ yang punya kata).

---

## 6. Format Keluaran

`kosakata_2964.json` — array JSON, urut bacaan (gojūon), indentasi 2 spasi:

```json
[
  {
    "kosakata": "藍瓶",
    "bacaan": "あいがめ"
  }
]
```

Field: `kosakata` (kata berkanji) dan `bacaan` (hiragana). Tidak ada arti, level, maupun frekuensi.

---

## 7. Keterbatasan dan Asumsi

1. **Definisi bacaan mengikuti KANJIDIC2**, termasuk bacaan alternatif dan arkais. "100%" berarti 100% relatif terhadap dataset ini, bukan terhadap pemakaian bahasa Jepang modern.
2. **Penyelarasan bersifat heuristik**: 22,4% kata gagal diselaraskan (kebanyakan benar karena jukujikun), dan terdapat 38 kasus batas (mis. pola sokuon pada 三つ みっつ) yang memengaruhi hasil maksimal ± 38 kata.
3. **Bacaan "mustahil" (709)** tidak dapat dipelajari lewat kosakata; hanya bisa lewat daftar bacaan kanji langsung.
4. **Tidak ada pembobotan frekuensi**: solusi minimum cenderung memilih kata langka karena lebih efisien menutup banyak bacaan. Kata umum seperti 食べる dan 学校 justru tidak masuk.
5. **Pembatasan ke kata umum tidak memperbaiki hasil**: membatasi kandidat ke JPDB top-20.000 justru menaikkan jumlah kata menjadi 3.517 dengan cakupan turun ke 80,5%.
6. **Status optimalitas**: solusi terbukti berada di {2.962, 2.963, 2.964}; nilai pasti belum ditutup sepenuhnya (gap 0,09%).

---

## 8. Rekomendasi

| Kebutuhan | Saran |
|---|---|
| Referensi teoretis / kelengkapan maksimal | Pakai 2.964 kata apa adanya |
| Belajar praktis (manusia) | Targetkan 90–95% → 1.758–1.858 kata |
| Urutan belajar | Urutkan sendiri berdasarkan frekuensi (JPDB) — file ini tidak berurutan frekuensi |
| Anki | Pecah per level: kyōiku dulu, lalu jōyō |
| Bacaan mustahil (709) | Pelajari dari daftar bacaan kanji, bukan kosakata |

---

## 9. Catatan Teknis

- Bahasa: Python 3.12; pustaka: `ijson` (streaming JSON), `scipy.optimize.milp`/`linprog` (HiGHS).
- Data antara: `sets.json` (pola coverage), `kd.json` (tabel bacaan kanji).
- Waktu komputasi total: ± 40 menit (penyelarasan ± 3 menit, reduksi dominasi ± 20 detik, ILP 300 detik, heuristik ± 5 menit).
- Metode dominasi, elemen paksa, dan pembatasan variabel tidak mengubah nilai optimum (terbukti secara konstruksi).
