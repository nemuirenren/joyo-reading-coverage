#!/usr/bin/env python3
"""04 — Ekspor hasil akhir + statistik + grafik.

Input : data/sets.json.gz, data/solution.json, data/readings.json
Output: data/kosakata_2964.json, data/readings_universe.json,
        data/stats.json, docs/coverage-curve.svg
"""
import argparse
import collections
import gzip
import heapq
import json
import pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))


def load_sets(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    elems = [tuple(e) for e in data["elems"]]
    sets = [set(ids) for ids, _, _ in data["sets"]]
    words = [(w, r) for _, w, r in data["sets"]]
    return elems, sets, words


def coverage_curve(selected, sets, universe):
    """Urutkan kata dalam solusi berdasarkan gain marjinal -> kurva cakupan."""
    remaining = set(universe)
    heap = [(-len(sets[s] & remaining), s) for s in selected]
    heapq.heapify(heap)
    points, covered = [(0, 0.0)], 0
    total = len(universe)
    while heap:
        neg, s = heapq.heappop(heap)
        gain = len(sets[s] & remaining)
        if gain != -neg:
            if gain:
                heapq.heappush(heap, (-gain, s))
            continue
        covered += gain
        remaining -= sets[s]
        points.append((len(points), covered / total * 100))
    return points


def svg_curve(points, out_path):
    W, H, PAD = 720, 400, 48
    total_words = points[-1][0] if points else 1
    xs = lambda x: PAD + (W - 2 * PAD) * x / max(1, total_words)
    ys = lambda y: H - PAD - (H - 2 * PAD) * y / 100.0
    poly = " ".join(f"{xs(x):.1f},{ys(y):.1f}" for x, y in points)

    grid = []
    for pct in (0, 25, 50, 75, 100):
        grid.append(
            f'<line x1="{PAD}" y1="{ys(pct):.1f}" x2="{W-PAD}" y2="{ys(pct):.1f}" '
            f'stroke="#e5e5e5" stroke-width="1"/>'
            f'<text x="{PAD-8}" y="{ys(pct)+4:.1f}" font-size="11" text-anchor="end" '
            f'fill="#666">{pct}%</text>'
        )
    marks = [(0, "0"), (500, "500"), (1000, "1000"), (2000, "2000"),
             (total_words, str(total_words))]
    labels = "".join(
        f'<text x="{xs(x):.1f}" y="{H-PAD+18}" font-size="11" text-anchor="middle" '
        f'fill="#666">{t}</text>' for x, t in marks if x <= total_words
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{PAD}" y="24" font-size="14" font-family="sans-serif" fill="#111">Coverage of jōyō kanji readings vs. number of words learned</text>
  {''.join(grid)}
  <line x1="{PAD}" y1="{H-PAD}" x2="{W-PAD}" y2="{H-PAD}" stroke="#999"/>
  <line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{H-PAD}" stroke="#999"/>
  <polyline points="{poly}" fill="none" stroke="#2563eb" stroke-width="2.5"/>
  {labels}
  <text x="{W/2}" y="{H-8}" font-size="12" text-anchor="middle" fill="#444">words learned</text>
  <text x="14" y="{H/2}" font-size="12" text-anchor="middle" fill="#444" transform="rotate(-90 14 {H/2})">readings covered</text>
</svg>
'''
    out_path.write_text(svg, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="data/sets.json.gz")
    ap.add_argument("--solution", default="data/solution.json")
    ap.add_argument("--readings", default="data/readings.json")
    ap.add_argument("--outdir", default="data")
    ap.add_argument("--docs", default="docs")
    args = ap.parse_args()

    elems, sets, words = load_sets(args.sets)
    sol = json.loads(pathlib.Path(args.solution).read_text(encoding="utf-8"))
    readings = json.loads(pathlib.Path(args.readings).read_text(encoding="utf-8"))

    selected = sorted(set(sol["forced"]) | set(sol["selected"]))
    pairs = sorted({(words[s][0], words[s][1]) for s in selected},
                   key=lambda x: (x[1], x[0]))

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) daftar kosakata
    kosakata = [{"kosakata": w, "bacaan": r} for w, r in pairs]
    (outdir / "kosakata_2964.json").write_text(
        json.dumps(kosakata, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2) universe bacaan + status
    cand = collections.defaultdict(int)
    for s in sets:
        for e in s:
            cand[e] += 1
    forced_ids = set(sol["forced"])
    universe = []
    for i, (kanji, kind, reading) in enumerate(elems):
        grade = readings.get(kanji, {}).get("grade")
        universe.append({
            "kanji": kanji,
            "type": kind,
            "reading": reading,
            "grade": grade,
            "candidates": cand.get(i, 0),
            "covered": cand.get(i, 0) > 0,
            "forced_word": bool(cand.get(i, 0) == 1),
        })

    # 3) statistik
    coverage = set()
    per_word = []
    for s in selected:
        coverage |= sets[s]
        per_word.append(len(sets[s]))
    dist = collections.Counter(per_word)
    covered_total = sum(1 for u in universe if u["covered"])
    curve = coverage_curve(selected, sets, [i for i, u in enumerate(universe) if u["covered"]])

    stats = {
        "units_total": len(universe),
        "units_on": sum(1 for u in universe if u["type"] == "on"),
        "units_kun": sum(1 for u in universe if u["type"] == "kun"),
        "units_impossible": sum(1 for u in universe if not u["covered"]),
        "units_covered": covered_total,
        "words_total": len(pairs),
        "words_unique": len({w for w, _ in pairs}),
        "readings_per_word_avg": round(sum(per_word) / len(per_word), 3),
        "words_teaching_1": dist.get(1, 0),
        "words_teaching_2": dist.get(2, 0),
        "words_teaching_ge5": sum(v for k, v in dist.items() if k >= 5),
        "max_readings_per_word": max(per_word),
        "distribution": {str(k): dist[k] for k in sorted(dist)},
        "coverage_curve": [[x, round(y, 2)] for x, y in curve],
        "solver": sol.get("stats", {}),
    }
    (outdir / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "readings_universe.json").write_text(
        json.dumps(universe, ensure_ascii=False, indent=1), encoding="utf-8")

    # 4) grafik
    docs = pathlib.Path(args.docs)
    docs.mkdir(parents=True, exist_ok=True)
    svg_curve(curve, docs / "coverage-curve.svg")

    print(f"kosakata : {len(kosakata)}")
    print(f"tercakup : {covered_total}/{len(universe)}")
    print(f"tidak bisa ditutup: {stats['units_impossible']}")


if __name__ == "__main__":
    main()
