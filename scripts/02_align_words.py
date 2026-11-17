#!/usr/bin/env python3
"""02 — Selaraskan setiap kata JMdict dengan bacaannya.

Input : data/readings.json + JMdict_english.zip
Output: data/sets.json.gz  {elems: [[kanji, jenis, bacaan], ...],
                            sets:  [[[id, ...], kata, bacaan], ...]}

Aturan utama:
  - on'yomi harus sama persis (abaikan dakuten),
  - kun'yomi boleh berupa stem saja (okurigana ada di kata),
  - rendaku & sokuon ditoleransi,
  - jukujikun (大人 おとな) otomatis gagal dan dilewati.

Contoh:
    python scripts/02_align_words.py --jmdict data/raw/JMdict_english.zip
"""
import argparse
import gzip
import json
import pathlib
import re
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from align import align, build_table, normalize_reading  # noqa: E402


def has_kanji(term: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in term)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readings", default="data/readings.json")
    ap.add_argument("--jmdict", default="data/raw/JMdict_english.zip")
    ap.add_argument("--out", default="data/sets.json.gz")
    ap.add_argument("--max-grade", type=int, default=8,
                    help="batasi universe ke kanji dengan grade <= N (8 = jōyō)")
    args = ap.parse_args()

    readings = json.loads(pathlib.Path(args.readings).read_text(encoding="utf-8"))
    table = build_table(readings)

    # ---- universe: pasangan (kanji, jenis, bacaan) untuk kanji jōyō
    elem_id, elems = {}, []
    for kanji, data in readings.items():
        grade = data.get("grade")
        if not grade or grade > args.max_grade:
            continue
        for kind in ("on", "kun"):
            for raw in data.get(kind, []):
                norm = normalize_reading(raw)
                if not norm:
                    continue
                key = (kanji, kind, norm)
                if key not in elem_id:
                    elem_id[key] = len(elems)
                    elems.append(key)

    # ---- iterasi JMdict
    zf = zipfile.ZipFile(args.jmdict)
    banks = sorted(
        [n for n in zf.namelist() if n.startswith("term_bank_")],
        key=lambda s: int(re.findall(r"\d+", s)[0]),
    )

    patterns = {}  # tuple(ids) -> (kata, bacaan)  [wakil pertama]
    n_words = n_aligned = 0

    for name in banks:
        for rec in json.loads(zf.read(name).decode("utf-8")):
            term, reading = rec[0], rec[1]
            if not has_kanji(term):
                continue
            n_words += 1
            result = align(term, reading, table)
            if not result:
                continue
            n_aligned += 1
            ids = set()
            for kanji, kind, raw in result:
                idx = elem_id.get((kanji, kind, normalize_reading(raw)))
                if idx is not None:
                    ids.add(idx)
            if not ids:
                continue
            key = tuple(sorted(ids))
            if key not in patterns:
                patterns[key] = (term, reading)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "elems": [list(e) for e in elems],
        "sets": [[list(k), v[0], v[1]] for k, v in patterns.items()],
    }
    with gzip.open(out, "wt", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    print(f"kata berkanji      : {n_words}")
    print(f"selaras            : {n_aligned} ({n_aligned / n_words * 100:.1f}%)")
    print(f"pola coverage unik : {len(patterns)}")
    print(f"unit bacaan        : {len(elems)}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
