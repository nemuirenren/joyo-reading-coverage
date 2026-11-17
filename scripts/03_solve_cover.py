#!/usr/bin/env python3
"""03 — Selesaikan minimum set cover (reduksi + LP + ILP).

Input : data/sets.json.gz
Output: data/solution.json  {forced: [...], selected: [...], stats: {...}}

Tahapan:
  1. elemen paksa  — elemen yang hanya punya 1 kandidat kata (cascade),
  2. dominasi      — buang himpunan yang subset dari himpunan lain,
  3. relaksasi LP  — batas bawah,
  4. ILP (HiGHS)   — solusi integer.

Contoh:
    python scripts/03_solve_cover.py --time-limit 300
"""
import argparse
import collections
import json
import gzip
import pathlib
import time

import numpy as np
from scipy.optimize import LinearConstraint, Bounds, linprog, milp
from scipy.sparse import csc_matrix


def load_sets(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    elems = [tuple(e) for e in data["elems"]]
    sets = [set(ids) for ids, _, _ in data["sets"]]
    words = [(w, r) for _, w, r in data["sets"]]
    return elems, sets, words


def forced_cascade(cand, sets):
    """Pilih otomatis semua kata yang merupakan satu-satunya penutup sebuah elemen."""
    active = set(e for e in cand)
    chosen = set()
    while True:
        forced = [e for e in active
                  if sum(1 for s in cand[e] if s not in chosen) == 1]
        if not forced:
            break
        new = set()
        for e in forced:
            for s in cand[e]:
                if s not in chosen:
                    new.add(s)
        if not new:
            break
        chosen |= new
        for s in new:
            active -= sets[s]
    return chosen, active


def drop_dominated(cand_sets, sets, active):
    """Buang himpunan S jika ada T dengan S ⊆ T (aman untuk optimum)."""
    by_el = collections.defaultdict(list)
    for s in cand_sets:
        for e in sets[s] & active:
            by_el[e].append(s)
    keep = set(cand_sets)
    for s in sorted(cand_sets, key=lambda x: len(sets[x] & active)):
        cov = sets[s] & active
        if not cov:
            keep.discard(s)
            continue
        rarest = min(cov, key=lambda e: len(by_el[e]))
        for t in by_el[rarest]:
            if t != s and t in keep and len(sets[t] & active) >= len(cov) \
                    and cov <= (sets[t] & active):
                keep.discard(s)
                break
    return sorted(keep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="data/sets.json.gz")
    ap.add_argument("--out", default="data/solution.json")
    ap.add_argument("--time-limit", type=float, default=300.0,
                    help="batas waktu ILP (detik)")
    args = ap.parse_args()

    t0 = time.time()
    elems, sets, words = load_sets(args.sets)
    n = len(elems)
    cand = collections.defaultdict(list)
    for si, s in enumerate(sets):
        for e in s:
            cand[e].append(si)
    print(f"unit bacaan: {n} | kata: {len(sets)}")

    forced, active = forced_cascade(cand, sets)
    print(f"elemen paksa: {len(forced)} kata | sisa elemen: {len(active)}")

    candidates = [s for s in range(len(sets)) if sets[s] & active]
    print(f"kandidat sisa: {len(candidates)}")

    kept = drop_dominated(candidates, sets, active)
    print(f"setelah buang dominasi: {len(kept)}")

    idx = {s: i for i, s in enumerate(kept)}
    elist = sorted(active)
    eidx = {e: i for i, e in enumerate(elist)}
    rows, cols, vals = [], [], []
    for s in kept:
        for e in sets[s] & active:
            rows.append(eidx[e])
            cols.append(idx[s])
            vals.append(1.0)
    A = csc_matrix((vals, (rows, cols)), shape=(len(elist), len(kept)))
    c = np.ones(len(kept))

    # --- LP
    lp = linprog(c, A_ub=-A, b_ub=-np.ones(len(elist)), bounds=(0, 1), method="highs")
    lp_bound = len(forced) + lp.fun
    print(f"LP bound: {lp.fun:.2f} -> batas bawah total: {lp_bound:.2f}")

    # --- ILP
    t1 = time.time()
    res = milp(c, constraints=LinearConstraint(A, lb=np.ones(len(elist)),
                                              ub=np.full(len(elist), np.inf)),
               integrality=np.ones(len(kept)), bounds=Bounds(0, 1),
               options={"time_limit": args.time_limit, "mip_rel_gap": 0.0})
    dual = getattr(res, "mip_dual_bound", None)
    print(f"ILP status: {res.status} ({res.message}) {time.time() - t1:.0f}s")
    print(f"solusi: {res.fun} | dual bound: {dual}")

    selected = [kept[i] for i in range(len(kept)) if res.x is not None and res.x[i] > 0.5]
    total = len(forced) + len(selected)

    payload = {
        "forced": sorted(forced),
        "selected": selected,
        "stats": {
            "units_total": n,
            "units_forced": len(forced),
            "units_remaining": len(active),
            "candidates_initial": len(candidates),
            "candidates_after_dominance": len(kept),
            "lp_bound_remaining": round(float(lp.fun), 4),
            "lower_bound_total": round(float(lp_bound), 4),
            "ilp_objective": float(res.fun) if res.fun is not None else None,
            "ilp_dual_bound": float(dual) if dual is not None else None,
            "ilp_gap": float(getattr(res, "mip_gap", 0.0) or 0.0),
            "total_words": total,
            "runtime_seconds": round(time.time() - t0, 1),
        },
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TOTAL: {total} kata -> {out}")


if __name__ == "__main__":
    main()
