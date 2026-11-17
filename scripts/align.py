"""Komponen penyelarasan kata–bacaan (word–reading alignment).

Dipakai oleh 02_align_words.py. Modul ini sengaja tanpa dependensi eksternal.
"""
import unicodedata

# Kana yang boleh muncul di dalam bacaan
SOKUON = set("くきつちひふ")
MAX_SLICE = 12


def to_hiragana(s: str) -> str:
    """Katakana -> hiragana (per karakter, tanpa mengubah tanda lain)."""
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def base_form(s: str) -> str:
    """Bentuk dasar untuk perbandingan: hiragana, tanpa dakuten/handakuten."""
    out = []
    for c in unicodedata.normalize("NFD", to_hiragana(s)):
        if unicodedata.combining(c):
            continue
        out.append(c)
    return "".join(out)


def is_kana(c: str) -> bool:
    return ("ぁ" <= c <= "ゖ") or c in "ー・"


def build_table(readings: dict) -> dict:
    """readings: {kanji: {"on": [...], "kun": [...]}} -> tabel pencocokan.

    Setiap entri: (jenis, bacaan_asli, stem, okurigana, gabungan)
    """
    table = {}
    for kanji, data in readings.items():
        rows = []
        for r in data.get("on", []):
            rr = to_hiragana(r).replace("-", "")
            if rr:
                rows.append(("on", r, rr, "", rr))
        for r in data.get("kun", []):
            rr = to_hiragana(r).replace("-", "")
            if not rr:
                continue
            if "." in rr:
                stem, okuri = rr.split(".", 1)
            else:
                stem, okuri = rr, ""
            rows.append(("kun", r, stem, okuri, stem + okuri))
        table[kanji] = rows
    return table


def match(slice_: str, full: str, stem: str) -> bool:
    """Apakah potongan bacaan cocok dengan bacaan kanji (on/kun)?"""
    if not slice_:
        return False
    if slice_ == full or slice_ == stem:
        return True
    if base_form(slice_) == base_form(full) or base_form(slice_) == base_form(stem):
        return True
    # sokuon: がっ (dari がく), じっ (dari じつ)
    if slice_[-1] == "っ":
        if len(full) > 1 and full[-1] in SOKUON and base_form(slice_[:-1]) == base_form(full[:-1]):
            return True
        if len(stem) > 1 and stem[-1] in SOKUON and base_form(slice_[:-1]) == base_form(stem[:-1]):
            return True
    return False


def align(term: str, reading: str, table: dict):
    """Selaraskan kata dengan bacaannya.

    Mengembalikan list (kanji, jenis, bacaan_asli) atau None jika gagal
    (mis. jukujikun: 大人 おとな).
    """
    t = term
    r = to_hiragana(reading)
    n, m = len(t), len(r)
    memo = {}

    def rec(i, j):
        if i == n:
            return [] if j == m else None
        if (i, j) in memo:
            return None
        c = t[i]
        # 々 mewarisi bacaan kanji sebelumnya
        if c == "々" and i > 0:
            c = t[i - 1]
        if is_kana(t[i]):
            if j < m and base_form(r[j]) == base_form(t[i]):
                return rec(i + 1, j + 1)
            memo[(i, j)] = False
            return None
        if c not in table:
            memo[(i, j)] = False
            return None
        for length in range(min(MAX_SLICE, m - j), 0, -1):
            slice_ = r[j:j + length]
            if not any(match(slice_, full, stem) for _, _, stem, _, full in table[c]):
                continue
            sub = rec(i + 1, j + length)
            if sub is not None:
                return [(i, c, slice_, None, None)] + sub
        memo[(i, j)] = False
        return None

    found = rec(0, 0)
    if found is None:
        return None

    # Re-kredit: pilih bacaan yang okurigana-nya cocok dengan kana setelah kanji
    result = []
    for i, c, slice_, _, _ in found:
        j = 1
        okuri_in_term = ""
        while i + j < n and is_kana(t[i + j]):
            okuri_in_term += t[i + j]
            j += 1

        best, best_score = None, -1
        for kind, raw, stem, okuri, full in table[c]:
            if not match(slice_, full, stem):
                continue
            if okuri_in_term and okuri == okuri_in_term:
                score = 4
            elif okuri_in_term and okuri and okuri_in_term.startswith(okuri):
                score = 3
            elif not okuri_in_term and slice_ == full:
                score = 2
            elif okuri and okuri_in_term.startswith(okuri):
                score = 2
            elif not okuri_in_term:
                score = 1
            else:
                score = 0
            if score > best_score:
                best_score, best = score, (kind, raw)

        result.append((c,) + (best if best else ("kun", "")))
    return result


def normalize_reading(reading: str) -> str:
    """Bentuk identitas bacaan: hiragana tanpa titik/afiks."""
    return to_hiragana(reading).replace(".", "").replace("-", "")
