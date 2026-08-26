"""DB-SANITY GATE: a reading that violates an arsenal graph must NOT violate
any standard calibration graph (connected atlas n<=7, C5..C9, P7, Petersen,
K3,3, K7, stars K1,k, bicliques K2,3/K2,4/K3,3, K(2,2), K(2,2,2), C5[K2],
C5[K3]). A violation there means the reading mis-transcribes the conjecture
(the conjecture is open, hence believed to hold on tiny graphs where
DeLaViña's battery ran); such candidates are discarded per protocol.

Usage:
  python sanity_gate.py <eid> <reading_index> [<eid> <ri> ...]
  python sanity_gate.py --scan FILE   # FILE: json list of {id, ri}
Prints GATE-FAIL / GATE-PASS per candidate plus the offending graphs.
Exit code 0 iff all candidates pass.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import certify_sanity as CS  # noqa: E402  (build_sanity_corpus)
import sweep as SW           # noqa: E402


def load_sanity_contexts():
    Gs = CS.build_sanity_corpus()
    ctxs = {}
    miss = []
    for name, G in Gs.items():
        fn = SW.CERT.parent / "cert_sanity" / (
            name.replace("/", "_").replace("(", "_").replace(")", "")
            .replace(",", "_").replace("[", "_").replace("]", "") + ".json")
        if not fn.exists():
            miss.append(name)
            continue
        ctxs[name] = _mk_ctx(name, G, json.load(open(fn)))
    return ctxs, sorted(miss)


def _mk_ctx(name, G, cert):
    from xctx import X
    INTKEY_DICTS = ("ecc", "dist_even", "dist_odd", "Tdist", "even_horizontal",
                    "odd_horizontal", "disp", "T_v", "K4_v",
                    "radial_circle_orders_at_center")
    for k in INTKEY_DICTS:
        if k in cert and isinstance(cert[k], dict):
            cert[k] = {int(kk): vv for kk, vv in cert[k].items()}
    for lstk in ("periphery_B", "center_C", "M_set", "A_set", "D2_set",
                 "pendant_P", "support_S"):
        if lstk in cert and isinstance(cert[lstk], list):
            cert[lstk] = [int(v) for v in cert[lstk]]
    x = X(name, G, cert)
    x._vt = False          # sanity graphs: never claim vertex-transitivity
    return x


def gate_check(eid, ri, sctxs):
    """Re-evaluate reading ri of entry eid on every sanity context.
    Returns (verdict, violations) - verdict True = PASS (no violation)."""
    violations = []
    evaluated = 0
    for name, X in sorted(sctxs.items()):
        try:
            rds = SW.get_readings(eid, X)
            if rds is None or ri >= len(rds):
                continue
            rd = rds[ri]
            st, det = SW.eval_reading_on(rd, X)
            if st == "VIO":
                violations.append((name, rd["interp"][:60], det))
            if st in ("VIO", "HOLD", "BRACKET"):
                evaluated += 1
        except Exception:
            continue
    return (len(violations) == 0 and evaluated > 0), violations, evaluated


def main():
    args = sys.argv[1:]
    cands = []
    if args and args[0] == "--scan":
        cands = [(c["id"], c["ri"]) for c in json.load(open(args[1]))]
    else:
        it = iter(args)
        for e, r in zip(it, it):
            cands.append((int(e) if e.isdigit() else e, int(r)))
    print(f"loading {len(cands)} candidates against sanity corpus...")
    sctxs, miss = load_sanity_contexts()
    if miss:
        print(f"(missing certs for {len(miss)}: {miss[:8]}...)")
    print(f"{len(sctxs)} sanity contexts")
    all_pass = True
    for eid, ri in cands:
        ok, vios, ev = gate_check(eid, ri, sctxs)
        tag = "GATE-PASS" if ok else "GATE-FAIL"
        if not ok:
            all_pass = False
        print(f"\n{tag}  id={eid} reading#{ri}  ({ev} contexts decided)")
        for name, interp, det in vios[:12]:
            print(f"   violated on {name}: {interp} :: {det}")
        if len(vios) > 12:
            print(f"   ... and {len(vios)-12} more")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
