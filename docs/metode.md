# Metode

Dokumen ini menjelaskan pipeline secara rinci: dari file mentah sampai daftar 2.964 kata.

---

## 1. Definisi masalah

Diberikan:

- himpunan **U** berisi pasangan (kanji, bacaan) untuk seluruh kanji jōyō,
- himpunan **S** berisi kata JMdict; setiap kata *s* ∈ *S* menutup subset *C(s)* ⊆ *U*,

cari *S'* ⊆ *S* dengan |*S'*| minimum sehingga ∪<sub>s∈S'</sub> *C(s)* = *U*.

Ini minimum set cover (NP-hard).

**Satu unit = satu pasangan (kanji, jenis, bacaan).** Contoh: (食, on, しょく) dan (食, kun, たべる) adalah dua unit berbeda; (食, kun, たべる) hanya dihitung sekali meskipun muncul di 食べる, 食べ物, dan 食べ方.

---

## 2. Normalisasi bacaan

Sumber: KANJIDIC2 (`<reading r_type="ja_on|ja_kun">`).

| Langkah | Contoh |
|---|---|
| Katakana → hiragana | `ショク` → `しょく` |
| Pisahkan okurigana | `た.べる` → stem `た`, okurigana `べる` |
| Buang penanda afiks | `-う`, `ひと-` → `う`, `ひと` |
| Gabungkan duplikat | `う.まれる` = `うま.れる` = `うま.れ` → `うまれる` |

Hasil: **6.587 unit** untuk 2.136 kanji jōyō (2.854 on + 3.733 kun).

---

## 3. Penyelarasan kata–bacaan

Untuk kata dengan *k* kanji, bacaan kata dipecah menjadi *k* potongan; potongan ke-*i* harus cocok dengan salah satu bacaan kanji ke-*i*.

### Aturan pencocokan

| Aturan | Contoh |
|---|---|
| On'yomi persis (abaikan dakuten) | 勉強 べんきょう → 勉 = べん, 強 = きょう |
| Kun stem (okurigana ada di kata) | 食べる たべる → 食 = た (stem dari `た.べる`) |
| Kun penuh (tanpa okurigana di kata) | 金 かね → `かね` |
| Rendaku | 手紙 てがみ → 紙 = がみ ≈ かみ |
| Sokuon | 学校 がっこう → 学 = がっ ≈ がく; 実際 じっさい → 実 = じっ ≈ じつ |
| Tanda 々 | 人々 ひとびと → 々 dibaca seperti kanji sebelumnya |

### Yang sengaja ditolak

Kata dengan bacaan non-komposisional (jukujikun) tidak mengajarkan bacaan komponennya, sehingga dilewati:

- 大人 おとな, 今日 きょう, 明日 あした, 有難う ありがとう
- bacaan ireguler seperti 日本 にほん (日 ≠ に)

### Hasil

| Tahap | Jumlah |
|---|---|
| Entri JMdict berkanji | 380.742 |
| Selaras | 295.396 (77,6%) |
| Pola coverage unik | 138.978 |

Dua kata dengan cakupan identik disimpan sekali (pola yang sama tidak menambah pilihan).

---

## 4. Reduksi

| Reduksi | Efek |
|---|---|
| Unit tanpa kandidat kata | 747 dibuang (lihat `keterbatasan.md`) |
| Elemen paksa: unit dengan tepat 1 kandidat | 654 kata wajib; menutup 749 unit |
| Himpunan terdominasi: *S* ⊂ *T* | 138.023 → 86.981 variabel |

Dominasi aman: jika *S* ⊆ *T*, setiap solusi yang memakai *S* bisa diganti *T* tanpa menambah jumlah kata.

---

## 5. Optimasi

1. **Relaksasi LP** — minimum Σx<sub>s</sub> dengan Ax ≥ 1, 0 ≤ x ≤ 1.
   Nilai: 2.307,09 untuk sisa masalah → batas bawah total 654 + 2.307,09 = **2.961,09**, dibulatkan **2.962**.
2. **ILP** — variabel biner, solver HiGHS (SciPy `milp`), `time_limit = 300 s`, `mip_rel_gap = 0`.
   Hasil: **2.310** kata untuk sisa masalah; dual bound 2.308.
3. **Total**: 654 + 2.310 = **2.964**; batas bawah 654 + 2.308 = **2.962**.

Karena masalah sisa punya celah 2 kata, nilai optimum ada di {2.962, 2.963, 2.964}.

---

## 6. Verifikasi

- Seluruh 5.840 unit yang bisa ditutup benar-benar tertutup.
- Tidak ada kata yang terpilih dua kali antara fase paksa dan fase ILP.
- Local search (ruin-and-recreate, 150 detik) tidak menemukan solusi < 2.964.
- Enam variasi greedy acak semuanya menghasilkan ≥ 3.383 kata.

---

## 7. Parameter dan versi

| Parameter | Nilai |
|---|---|
| Kanji | grade ≤ 8 (jōyō) |
| Sumber kata | JMdict 2026-11-15 (build Yomitan) |
| Sumber bacaan | KANJIDIC2 database 2026-320 |
| Solver | HiGHS via SciPy 1.18 |
| Time limit ILP | 300 detik |
| Bahasa | Python 3.12 |

---

## 8. Struktur skrip

| Skrip | Masukan | Keluaran |
|---|---|---|
| `01_extract_readings.py` | `kanjidic2.xml.gz` | `data/readings.json` |
| `02_align_words.py` | `readings.json` + `JMdict_english.zip` | `data/sets.json.gz` |
| `03_solve_cover.py` | `sets.json.gz` | `data/solution.json` |
| `04_export.py` | `sets.json.gz` + `solution.json` | `kosakata_2964.json`, `stats.json`, grafik |
