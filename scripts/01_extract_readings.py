#!/usr/bin/env python3
"""01 — Ekstrak bacaan kanji dari KANJIDIC2.

Input : kanjidic2.xml.gz
Output: data/readings.json  {kanji: {grade, on: [...], kun: [...]}}

Contoh:
    python scripts/01_extract_readings.py --kanjidic data/raw/kanjidic2.xml.gz
"""
import argparse
import gzip
import json
import pathlib
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kanjidic", default="data/raw/kanjidic2.xml.gz")
    ap.add_argument("--out", default="data/readings.json")
    args = ap.parse_args()

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    readings = {}
    with gzip.open(args.kanjidic, "rb") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag != "character":
                continue
            kanji = el.find("literal").text
            grade_el = el.find("misc/grade")
            on, kun = [], []
            rm = el.find("reading_meaning")
            if rm is not None:
                for r in rm.iter("reading"):
                    kind = r.get("r_type")
                    if kind == "ja_on":
                        on.append(r.text.strip())
                    elif kind == "ja_kun":
                        kun.append(r.text.strip())
            readings[kanji] = {
                "grade": int(grade_el.text) if grade_el is not None else None,
                "on": on,
                "kun": kun,
            }
            el.clear()

    out_path.write_text(
        json.dumps(readings, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"kanji: {len(readings)} -> {out_path}")


if __name__ == "__main__":
    main()
