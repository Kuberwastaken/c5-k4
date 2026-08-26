"""Rebuild full verdict JSON for entries flagged VIOLATED_CANDIDATE in the
sweep logs (sweep.py only emits markdown). Fast targeted re-evaluation."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sweep as SW
import readings_agx as RA

CAND_WOWII = sys.argv[1:] if len(sys.argv) > 1 else None


def main():
    ctxs = SW.load_contexts()
    data = json.load(open("/Users/kuber.mehta/Personal-Projects/c5-k4/"
                          "data/wowii-conjectures.json"))
    out = {}
    ids = CAND_WOWII or ["111", "59", "40", "19", "96", "108", "133", "144",
                         "145", "146", "154", "155", "157", "160", "161",
                         "162", "165", "166", "169", "171", "177", "179",
                         "180", "182", "183"]
    # if explicit list given use it; else scan all open quickly
    if not CAND_WOWII:
        opens = [e for e in data if e["status"] == "open"]
    else:
        want = set(ids)
        opens = [e for e in data if str(e["id"]) in want]
    for e in opens:
        eid = e["id"]
        row = {"id": eid, "statement": e["statement_text"][:300],
               "readings": []}
        vio = hold = br = pf = un = 0
        unsupported = False
        for gname, X in sorted(ctxs.items()):
            rds = SW.get_readings(eid, X)
            if rds is None:
                unsupported = True
                break
            for ri, rd in enumerate(rds):
                st, det = SW.eval_reading_on(rd, X)
                row["readings"].append({
                    "graph": gname, "ri": ri, "interp": rd.get("interp", ""),
                    "status": st, "detail": det,
                    "confidence": rd.get("confidence", "high")})
                if st == "VIO":
                    vio += 1
                elif st == "HOLD":
                    hold += 1
                elif st == "BRACKET":
                    br += 1
                elif st == "PREMISE_FALSE":
                    pf += 1
                else:
                    un += 1
        if unsupported:
            row["verdict"] = "UNSUPPORTED"
        else:
            row["verdict"] = ("VIOLATED_CANDIDATE" if vio else
                              "HOLDS" if hold and not br else
                              "BRACKET" if br else "HOLDS_PARTIAL")
            row["counts"] = {"vio": vio, "hold": hold, "bracket": br,
                             "premise_false": pf, "undef": un}
        out[str(eid)] = row
    # AGX candidates appended by agx_sweep already go to ledger; handled here:
    dest = HERE.parent / "candidates_verdicts.json"
    existing = {}
    if dest.exists() and CAND_WOWII is None:
        pass
    existing.update(out)
    dest.write_text(json.dumps(existing, indent=1, default=str))
    print(f"wrote {len(existing)} entry verdicts -> {dest}")


if __name__ == "__main__":
    main()
