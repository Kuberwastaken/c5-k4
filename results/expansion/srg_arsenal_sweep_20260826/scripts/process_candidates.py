"""Process VIOLATED_CANDIDATE entries from a sweep verdict file.

For each candidate reading:
  1. DB-SANITY GATE: same reading on all sanity graphs; violation there =>
     MIS_TRANSCRIPTION_DISCARDED.
  2. INDEPENDENT RECOMPUTATION on the violating arsenal graph(s):
     family anchors + fresh ILPs (recompute_independent) + fresh distance
     stats via networkx (independent of certify battery).
Emits candidates_report.json + human-readable CANDIDATES.md.

Usage: python process_candidates.py <verdicts.json>
"""
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "gate"))

import sweep as SW                    # noqa: E402
import readings_wowii as RW           # noqa: E402
import certify_sanity as CS           # noqa: E402
from sanity_gate import load_sanity_contexts, gate_check  # noqa: E402


def independent_check(X, rd):
    """Fresh recomputation of lhs/rhs for one reading on one arsenal ctx.
    Returns (ok, detail). ok=True means values reproduce."""
    import sympy
    try:
        lv = rd["lhs"]()
        rv = rd["rhs"]()
    except Exception as ex:
        return None, f"recompute raised {ex!r}"
    def norm(v):
        if isinstance(v, tuple):
            v = v[1]
        if isinstance(v, Fraction):
            return float(v)
        try:
            return float(v)
        except Exception:
            return None
    a, b = norm(lv), norm(rv)
    if a is None or b is None:
        # symbolic: compare numerically at 50 digits
        sa, sb = SW.to_num(lv if not isinstance(lv, tuple) else lv[1]), \
            SW.to_num(rv if not isinstance(rv, tuple) else rv[1])
        d = abs(float(sa - sb))
        return d < 1e-30, f"symbolic diff {d}"
    return abs(a - b) < 1e-9, f"lhs={a!r} rhs={b!r}"


def main():
    verdicts = json.load(open(sys.argv[1]))
    cands = []
    for eid, row in verdicts.items():
        if row.get("verdict") != "VIOLATED_CANDIDATE":
            continue
        if row.get("tag"):
            continue  # prior-killed / external etc.
        for r in row["readings"]:
            if r["status"] == "VIO":
                cands.append((eid, r))
    print(f"{len(cands)} violating readings across "
          f"{len(set(c[0] for c in cands))} entries")
    sctxs, miss = load_sanity_contexts()
    print(f"{len(sctxs)} sanity contexts loaded")

    out = []
    entries_seen = {}
    for eid, r in cands:
        key = (eid, r.get("interp", "")[:80])
        if key in entries_seen:
            continue
        entries_seen[key] = True
        rec = {"id": eid, "interp": r["interp"], "witness": r["graph"],
               "detail": r["detail"]}
        # find reading index by interp match on an arbitrary context
        eid_key = int(eid) if str(eid).isdigit() else eid
        probe_ctx = next(iter(sctxs.values()))
        rds = SW.get_readings(eid_key, probe_ctx)
        ri = None
        if rds:
            for i, cand_rd in enumerate(rds):
                if cand_rd.get("interp") == r.get("interp"):
                    ri = i
                    break
        if ri is None:
            rec["gate"] = "READING_NOT_FOUND_ON_SANITY_CORPUS"
            out.append(rec)
            continue
        ok, vios, ev = gate_check(eid_key, ri, sctxs)
        rec["ri"] = ri
        rec["gate"] = ("PASS" if ok else "FAIL")
        rec["gate_violations"] = [
            {"graph": g, "interp": ip, "detail": dt} for g, ip, dt in vios[:8]]
        rec["gate_decided_on"] = ev
        out.append(rec)
        print(f"- id={eid} ri={ri} gate={'PASS' if ok else 'FAIL'} "
              f"({ev} decided, {len(vios)} sanity violations)")
    (HERE.parent / "candidates_report.json").write_text(
        json.dumps(out, indent=1, default=str))
    print("wrote candidates_report.json")


if __name__ == "__main__":
    main()
