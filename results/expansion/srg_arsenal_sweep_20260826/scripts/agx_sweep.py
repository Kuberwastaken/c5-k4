"""AGX sweep driver: evaluate OPEN AutoGraphiX entries against the arsenal.

C-series survey conjectures get full readings; Form-1 table rows whose OCR
transcription is too degraded for faithful reconstruction are recorded as
UNPARSEABLE_SOURCE (never guessed). Appends to SWEEP_LEDGER.md and updates
VERDICTS.md alongside the WOWII sweep.
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import sweep as SW              # noqa: E402
import readings_agx as RA       # noqa: E402

CORPUS = Path("/Users/kuber.mehta/Personal-Projects/c5-k4/"
              "corpora/autographix.json")


def main():
    data = json.load(open(CORPUS))
    opens = [e for e in data if e.get("status", "").startswith("open")]
    ctxs = SW.load_contexts()
    print(f"{len(opens)} open AGX entries; {len(ctxs)} contexts", flush=True)
    ledger_f = open(SW.LEDGER, "a")
    verdict_rows = {}
    batch = []
    for k, e in enumerate(opens):
        eid = e["id"]
        row = {"id": eid, "statement": e["statement_text"][:200],
               "readings": []}
        counts = Counter()
        if eid not in RA.AGX_BUILDERS:
            row["verdict"] = "UNPARSEABLE_SOURCE"
            row["counts"] = {"vio": 0, "hold": 0, "bracket": 0,
                             "premise_false": 0, "undef": 0}
            row["notes"] = [
                "Form-1 table row; OCR text insufficient for faithful "
                "reconstruction of bound expression - not guessed"]
            verdict_rows[eid] = row
            batch.append(row)
            print(f"[{k+1}/{len(opens)}] {eid} -> UNPARSEABLE_SOURCE",
                  flush=True)
            if len(batch) >= 10:
                SW.write_batch(ledger_f, batch, verdict_rows)
                batch = []
            continue
        try:
            built = {}
            for gname, X in sorted(ctxs.items()):
                try:
                    built[gname] = RA.AGX_BUILDERS[eid](X)
                except RA.Undef as ex:
                    built[gname] = [{"interp": f"builder Undef: {ex}",
                                     "lhs": None, "rhs": None,
                                     "dir": ">=", "premise": None}]
                except Exception as ex:
                    built[gname] = [{"interp": f"builder error {ex!r}",
                                     "lhs": None, "rhs": None,
                                     "dir": ">=", "premise": None}]
            for gname, rds in built.items():
                for ri, rd in enumerate(rds):
                    try:
                        st, det = SW.eval_reading_on(rd, ctxs[gname])
                    except Exception as ex:
                        st, det = "ERROR", repr(ex)
                    counts[st] += 1
                    row["readings"].append({
                        "graph": gname, "ri": ri,
                        "interp": rd.get("interp", ""),
                        "status": st, "detail": det})
        finally:
            vio = counts.get("VIO", 0)
            hold = counts.get("HOLD", 0)
            br = counts.get("BRACKET", 0)
            un = counts.get("UNDEF", 0) + counts.get("BUILD-ERR", 0)
            if vio:
                row["verdict"] = "VIOLATED_CANDIDATE"
            elif hold and br == 0:
                row["verdict"] = "HOLDS"
            elif br:
                row["verdict"] = "BRACKET"
            elif hold:
                row["verdict"] = "HOLDS_PARTIAL"
            else:
                row["verdict"] = "NO_EVALUABLE_READINGS"
            row["counts"] = {"vio": vio, "hold": hold, "bracket": br,
                             "premise_false": 0, "undef": un}
            verdict_rows[eid] = row
            batch.append(row)
            print(f"[{k+1}/{len(opens)}] {eid} -> {row['verdict']} "
                  f"V{vio} H{hold} B{br} U{un}", flush=True)
        if len(batch) >= 10:
            SW.write_batch(ledger_f, batch, verdict_rows)
            batch = []
    if batch:
        SW.write_batch(ledger_f, batch, verdict_rows)
    ledger_f.close()
    print("AGX sweep done", flush=True)


if __name__ == "__main__":
    main()
