"""Sweep driver: evaluate every open WOWII entry's readings on every arsenal
graph; append SWEEP_LEDGER.md after each batch of ~10 entries; maintain
VERDICTS.md.
"""
import json
import pickle
import re
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx
import sympy

import helpers as H
import readings_wowii as RW
from xctx import Undef, S

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
CACHE = OUT / "cache"
CERT = CACHE / "cert"

LEDGER = OUT / "SWEEP_LEDGER.md"
VERDICTS = OUT / "VERDICTS.md"

# prior kills / external resolutions / known-corrupt (do not claim)
PRIOR = {
    "KILLED": {63, 64, 85, 309, "172", "176", "181", "430a"},
    "EXTERNAL": {103, 141, 146, 174, 178, "198a", 200, 209, 291, 300, 391},
    "JSON_OVERRIDE": {58: "refuted", 91: "refuted", 109: "refuted",
                      327: "refuted", "430b": "refuted", 143: "proved",
                      315: "proved", 34: "unclear"},
    "KNOWN_CORRUPT": {"401b", "412f", "448b"},
}

TREE_IDS = set(RW.TREE_IDS)

# entries whose displayed claim is an UPPER bound (LHS <= RHS)
UPPER_IDS = {96, 100, 103, 108, 111,
             281, 287, 290, 291, 298, 299, 300, 302, 304, 305, 308, 309,
             310, "382b", "382c", "382d", "382e", "384b", "387", "389a",
             "391", "392b", "392c", "392d", "392e", "392f", "393a",
             "393b", "393c", "393d", "394", "395a", "395b", "396",
             "397c", "398", "399a", "399b", "399c", "400c", "401a",
             "401b", "402", "404", "405", "406", "407", "410a", "410b",
             "418b", "418c", "420b",
             "420c", "421b", "421c", "422a", "422b", "422c", "422d",
             "423", "425d", "425e", "426", "427", "430c", "431a",
             "431b", "431c", "432a", "432b", "433", "434a",
             "434a-dup2", "434b", "434c", "434d", "434e", "435",
             "436c", "438a", "438b", "439", "442", "443", "444", "446",
             "448a", "448b", "449", "450"}

BUILDERS = {
    2: RW.build_02, 19: RW.build_19, 40: RW.build_40, 59: RW.build_59,
    61: RW.build_61, 63: RW.build_63, 64: RW.build_64, 65: RW.build_65,
    66: RW.build_66, 72: RW.build_72, 76: RW.build_76, 84: RW.build_84,
    85: RW.build_85, 96: RW.build_96, 100: RW.build_100, 103: RW.build_103,
    108: RW.build_108, 111: RW.build_111, 133: RW.build_133,
    141: RW.build_141, 142: RW.build_142, 144: RW.build_144,
    145: RW.build_145, 146: RW.build_146, 154: RW.build_154,
    155: RW.build_155, 157: RW.build_157, 160: RW.build_160,
    161: RW.build_161, 162: RW.build_162, 165: RW.build_165,
    166: RW.build_166, 169: RW.build_169, 171: RW.build_171,
    172: RW.build_172, 174: RW.build_174, 176: RW.build_176,
    177: RW.build_177, 178: RW.build_178, 179: RW.build_179,
    180: RW.build_180, 181: RW.build_181, 182: RW.build_182,
    183: RW.build_183, 184: RW.build_184, 185: RW.build_185,
    186: RW.build_186,
    189: RW.build_189, 190: RW.build_190, 194: RW.build_194,
    "198a": RW.build_198a, 199: RW.build_199, 200: RW.build_200,
    209: RW.build_209, 213: RW.build_213, 217: RW.build_217,
    232: RW.build_232, 233: RW.build_233, 235: RW.build_235,
    241: RW.build_241, 242: RW.build_242, 247: RW.build_247,
    252: RW.build_252, 253: RW.build_253, 255: RW.build_255,
    256: RW.build_256, 258: RW.build_258, 259: RW.build_259,
    260: RW.build_260, 261: RW.build_261, 267: RW.build_267,
    268: RW.build_268, 269: RW.build_269, 271: RW.build_271,
    281: RW.build_281, 287: RW.build_287, 290: RW.build_290,
    291: RW.build_291, 298: RW.build_298, 299: RW.build_299,
    300: RW.build_300, 302: RW.build_302, 304: RW.build_304,
    305: RW.build_305, 308: RW.build_308, 309: RW.build_309,
    310: RW.build_310,
    314: RW.build_314, 316: RW.build_316, 317: RW.build_317,
    318: RW.build_318, 319: RW.build_319, 320: RW.build_320,
    321: RW.build_321, 322: RW.build_322, 323: RW.build_323,
    324: RW.build_324, 325: RW.build_325, 326: RW.build_326,
    328: RW.build_328,
    "382b": RW.build_382b, "382c": RW.build_382c, "382d": RW.build_382d,
    "382e": RW.build_382e, "384b": RW.build_384b, "387": RW.build_387,
    "389a": RW.build_389a, "391": RW.build_391, "392b": RW.build_392b,
    "392c": RW.build_392c, "392d": RW.build_392d, "392e": ("slice","build_392e_f",0),
    "392f": ("slice","build_392e_f",1), "393a": RW.build_393a, "393b": ("slice","build_393b_c",0),
    "393c": ("slice","build_393b_c",1), "393d": RW.build_393d, "394": RW.build_394,
    "395a": ("slice","build_395a_b",0), "395b": ("slice","build_395a_b",1), "396": RW.build_396,
    "397c": RW.build_397c, "398": RW.build_398, "399a": ("slice","build_399a_b_c",0),
    "399b": ("slice","build_399a_b_c",1), "399c": ("slice","build_399a_b_c",2), "400c": RW.build_400c,
    "401a": ("slice","build_401a_b",0), "401b": ("slice","build_401a_b",1), "402": RW.build_402,
    "404": ("slice","build_404_407",0), "405": ("slice","build_404_407",1), "406": ("slice","build_404_407",2),
    "407": ("slice","build_404_407",3), "410a": RW.build_410a_b, "410b": RW.build_410a_b,
    "412a": ("slice","build_412a_b_d_e_f",0), "412b": ("slice","build_412a_b_d_e_f",1), "412d": ("slice","build_412a_b_d_e_f",2),
    "412e": ("slice","build_412a_b_d_e_f",3), "412f": ("slice","build_412a_b_d_e_f",4),
    "413a": ("slice","build_413a_b",0), "413b": ("slice","build_413a_b",1),
    "415a": ("slice","build_415a_b_c",0), "415b": ("slice","build_415a_b_c",1), "415c": ("slice","build_415a_b_c",2),
    "416": RW.build_416, "418b": ("slice","build_418b_c",0), "418c": ("slice","build_418b_c",1),
    "420b": ("slice","build_420b_c",0), "420c": ("slice","build_420b_c",1),
    "421b": ("slice","build_421b_c",0), "421c": ("slice","build_421b_c",1),
    "422a": ("slice","build_422a_d",0), "422b": ("slice","build_422a_d",1), "422c": ("slice","build_422a_d",2),
    "422d": ("slice","build_422a_d",3), "423": RW.build_423,
    "425d": ("slice","build_425d_e",0), "425e": ("slice","build_425d_e",1), "426": RW.build_426,
    "427": RW.build_427, "430a": None, "430c": RW.build_430a_c,
    "431a": ("slice","build_431a_b_c",0), "431b": ("slice","build_431a_b_c",1), "431c": ("slice","build_431a_b_c",2),
    "432a": ("slice","build_432a_b",0), "432b": ("slice","build_432a_b",1), "433": RW.build_433,
    "434a": ("slice","build_434a_e",0), "434a-dup2": ("slice","build_434a_e",0), "434b": ("slice","build_434a_e",1),
    "434c": ("slice","build_434a_e",2), "434d": ("slice","build_434a_e",3), "434e": ("slice","build_434a_e",5),
    "435": RW.build_435, "436c": RW.build_436c,
    "438a": ("slice","build_438a_b",0), "438b": ("slice","build_438a_b",1), "439": RW.build_439,
    "442": RW.build_442, "443": RW.build_443, "444": RW.build_444,
    "446": RW.build_446, "448a": ("slice","build_448a_b",0), "448b": ("slice","build_448a_b",2),
    "449": ("slice","build_449_450",0), "450": ("slice","build_449_450",1),
}


def get_readings(eid, X):
    """Return the list of readings for entry eid on context X."""
    RW.X = X  # bare-X lambdas in readings_wowii resolve to current context
    if eid in TREE_IDS or str(eid) in {str(t) for t in TREE_IDS}:
        return list(RW.build_tree_section(X))
    tag = BUILDERS.get(eid, BUILDERS.get(str(eid), "__MISSING__"))
    if tag == "__MISSING__":
        return None
    if tag is None:
        return []
    dr = "<=" if (eid in UPPER_IDS or str(eid) in UPPER_IDS) else ">="
    if callable(tag):
        try:
            rs = tag(X)
        except (Undef, ZeroDivisionError) as ex:
            def _raise(ex=ex):
                raise Undef(f"builder could not evaluate here: {ex!r}")
            return [{"interp": f"builder undef on this graph: {ex!r}",
                     "lhs": _raise, "rhs": _raise, "dir": dr,
                     "premise": None}]
    elif isinstance(tag, tuple):
        kind, fname, idx = tag
        fn = getattr(RW, fname)
        rs = [fn(X)[idx]]
    else:
        rs = []
    if not isinstance(rs, list):
        rs = [rs]
    for rd in rs:
        rd.setdefault("dir", dr)
    return rs


def to_num(v):
    """normalize value to sympy for comparison"""
    return S(v)


def cmp_vals(a, b):
    """return -1/0/1 or 'CLOSE' for a vs b."""
    sa, sb = to_num(a), to_num(b)
    if sa.is_number and sb.is_number:
        fa, fb = float(sa), float(sb)
        da, db = float(sa - sb), None
        if abs(fa - fb) < 1e-25 * max(1.0, abs(fa)):
            na, nb = sympy.N(sa, 60), sympy.N(sb, 60)
            if na == nb:
                return 0
            diff = na - nb
            if abs(diff) < sympy.Float("1e-30"):
                return "CLOSE"
            return -1 if diff < 0 else 1
        return -1 if fa < fb else 1
    d = sympy.simplify(sa - sb)
    if d == 0:
        return 0
    return -1 if d < 0 else 1


def eval_reading_on(reading, X):
    """-> (status, detail) status in HOLD/VIO/BRACKET/PREMISE_FALSE/UNDEF"""
    prem = reading.get("premise")
    conc = reading.get("conclusion")
    if prem is not None:
        try:
            pv = prem()
        except Undef as e:
            return ("BRACKET", f"premise undecidable: {e}")
        if pv is False:
            return ("PREMISE_FALSE", "")
        if pv is None:
            return ("BRACKET", "premise unknown")
    if conc == "ham":
        if X.ham():
            return ("HOLD", "Hamiltonian path witness found")
        return ("BRACKET", "no ham path found within search budget")
    if conc == "wtd":
        w = X.c.get("wtd_search", {})
        if w.get("found"):
            return ("VIO", f"minimal TDS sizes {w['sizes']} > gamma_t="
                    f"{w.get('gt')}")
        return ("BRACKET", "no non-minimum minimal TDS found; "
                "wtd=TRUE not certifiable without enumeration")
    lf, rf = reading.get("lhs"), reading.get("rhs")
    direction = reading.get("dir", ">=")
    try:
        lv = lf()
        rv = rf()
    except Undef as e:
        return ("UNDEF", str(e))
    lkind = "exact"
    rkind = "exact"
    if isinstance(lv, tuple):
        lkind, lv = lv
    if isinstance(rv, tuple):
        rkind, rv = rv
    c = cmp_vals(lv, rv)
    if c == "CLOSE":
        return ("BRACKET", "values too close to decide exactly")

    def s(x):
        return fmt_val(x)

    if direction == ">=":
        # claim LHS >= RHS
        if c >= 0:
            if lkind in ("exact", "lb") and rkind in ("exact", "ub"):
                return ("HOLD", f"LHS({lkind})={s(lv)} >= RHS({rkind})={s(rv)}")
            return ("BRACKET", f"LHS({lkind})={s(lv)} >= RHS({rkind})={s(rv)} "
                    "but kinds cannot certify hold")
        # strict LHS-side < RHS-side
        if lkind == "exact" and rkind == "exact":
            return ("VIO", f"LHS={s(lv)} < RHS={s(rv)}")
        if lkind == "ub" and rkind == "exact":
            return ("VIO", f"gamma-style LHS<={s(lv)} < RHS={s(rv)}")
        if lkind == "exact" and rkind == "lb":
            return ("VIO", f"LHS={s(lv)} < RHS>={s(rv)}")
        return ("BRACKET", f"LHS({lkind})={s(lv)} < RHS({rkind})={s(rv)}; "
                "bounds insufficient")
    else:
        # claim LHS <= RHS
        if c <= 0:
            if lkind in ("exact", "ub") and rkind in ("exact", "lb"):
                return ("HOLD", f"LHS({lkind})={s(lv)} <= RHS({rkind})={s(rv)}")
            return ("BRACKET", f"LHS({lkind})={s(lv)} <= RHS({rkind})={s(rv)} "
                    "but kinds cannot certify hold")
        # strict LHS-side > RHS-side
        if lkind == "exact" and rkind == "exact":
            return ("VIO", f"LHS={s(lv)} > RHS={s(rv)}")
        if lkind == "lb" and rkind == "exact":
            return ("VIO", f"LHS>={s(lv)} > RHS={s(rv)}")
        if lkind == "exact" and rkind == "ub":
            return ("VIO", f"LHS={s(lv)} > RHS<={s(rv)}")
        return ("BRACKET", f"LHS({lkind})={s(lv)} > RHS({rkind})={s(rv)}; "
                "bounds insufficient")


def load_contexts():
    with (CACHE / "arsenal.gpickle").open("rb") as f:
        graphs = pickle.load(f)
    ctxs = {}
    for name, G in graphs.items():
        fn = CERT / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if not fn.exists():
            continue
        cert = json.load(fn.open())
        cert["_vt_full"] = True  # recomputed below from meta
        ctxs[name] = X_ctx(name, G, cert)
    return ctxs


INTKEY_DICTS = ("ecc", "dist_even", "dist_odd", "Tdist", "even_horizontal",
                "odd_horizontal", "disp", "T_v", "K4_v",
                "radial_circle_orders_at_center")


def X_ctx(name, G, cert):
    from xctx import X
    for k in INTKEY_DICTS:
        if k in cert and isinstance(cert[k], dict):
            cert[k] = {int(kk): vv for kk, vv in cert[k].items()}
    for lstk in ("periphery_B", "center_C", "M_set", "A_set", "D2_set",
                 "pendant_P", "support_S"):
        if lstk in cert and isinstance(cert[lstk], list):
            cert[lstk] = [int(v) for v in cert[lstk]]
    import json as _j
    meta = _j.load(open(CACHE / "arsenal_meta.json"))
    w = meta[name]["vt"]
    cert["_vt_full"] = bool(w.get("orbit_full")) and bool(w.get("perms_valid"))
    x = X(name, G, cert)
    x._vt = cert["_vt_full"]
    return x


def fmt_val(v):
    if isinstance(v, Fraction):
        return f"{v.numerator}/{v.denominator}" if v.denominator != 1 else str(v.numerator)
    return str(v)


def main():
    data = json.load(open("/Users/kuber.mehta/Personal-Projects/c5-k4/"
                          "data/wowii-conjectures.json"))
    opens = [e for e in data if e["status"] == "open"]
    opens.sort(key=lambda e: str(e["id"]))
    ctxs = load_contexts()
    print(f"{len(opens)} open entries; {len(ctxs)} arsenal contexts",
          flush=True)
    ledger_f = open(LEDGER, "a")
    verdict_rows = {}
    batch = []
    t_start = time.time()

    for k, e in enumerate(opens):
        eid = e["id"]
        row = {"id": eid, "statement": e["statement_text"][:200],
               "readings": []}
        missing_ctxs = [n for n in ctxs]
        entry_status = "HOLDS"
        notes = []
        n_vio = n_hold = n_br = n_pf = n_undef = 0
        for gname, X in sorted(ctxs.items()):
            try:
                readings = get_readings(eid, X)
            except Exception as ex:
                readings = None
                notes.append(f"{gname}: builder error {ex!r}")
            if readings is None:
                entry_status = "UNSUPPORTED"
                notes.append("no builder encoded")
                break
            if isinstance(readings, list) and not readings and \
               BUILDERS.get(eid) not in (None,) and eid not in TREE_IDS \
               and BUILDERS.get(eid) != []:
                # empty readings with real builder => nothing usable
                pass
            for ri, rd in enumerate(readings):
                try:
                    st, det = eval_reading_on(rd, X)
                except Exception as ex:
                    st, det = "ERROR", repr(ex)
                if st == "VIO":
                    n_vio += 1
                elif st == "HOLD":
                    n_hold += 1
                elif st == "BRACKET":
                    n_br += 1
                elif st == "PREMISE_FALSE":
                    n_pf += 1
                elif st == "UNDEF":
                    n_undef += 1
                row["readings"].append({
                    "graph": gname, "ri": ri, "interp": rd["interp"],
                    "status": st, "detail": det,
                    "confidence": rd.get("confidence", "high"),
                    "conclusion": rd.get("conclusion")})
        # aggregate
        total_evaluable = n_vio + n_hold + n_br + n_undef
        if entry_status != "UNSUPPORTED":
            if n_vio:
                entry_status = "VIOLATED_CANDIDATE"
            elif n_hold and n_br == 0 and n_undef == 0:
                entry_status = "HOLDS"
            elif n_hold == 0 and n_br == 0 and n_undef == 0 and n_pf > 0 \
                    and total_evaluable == 0:
                entry_status = "PREMISE_FALSE_EVERYWHERE"
            elif n_br:
                entry_status = "BRACKET"
            elif n_hold:
                entry_status = "HOLDS_PARTIAL"
            else:
                entry_status = "NO_EVALUABLE_READINGS"
        row["verdict"] = entry_status
        row["counts"] = {"vio": n_vio, "hold": n_hold, "bracket": n_br,
                         "premise_false": n_pf, "undef": n_undef}
        if notes:
            row["notes"] = notes
        tag = None
        if eid in PRIOR["KILLED"]:
            tag = "KILLED_PRIOR_CAMPAIGN"
        elif eid in PRIOR["EXTERNAL"]:
            tag = "EXTERNALLY_RESOLVED"
        elif eid in PRIOR["KNOWN_CORRUPT"]:
            tag = "KNOWN_CORRUPT_READING"
        elif eid in PRIOR["JSON_OVERRIDE"]:
            tag = f"JSON_OVERRIDE_{PRIOR['JSON_OVERRIDE'][eid]}"
        if tag:
            row["tag"] = tag
        verdict_rows[str(eid)] = row
        batch.append(row)
        print(f"[{k+1}/{len(opens)}] id={eid} -> {entry_status} "
              f"(vio={n_vio}, hold={n_hold}, br={n_br}, pf={n_pf}, "
              f"un={n_undef})", flush=True)
        if len(batch) >= 10:
            write_batch(ledger_f, batch, verdict_rows)
            batch = []
    if batch:
        write_batch(ledger_f, batch, verdict_rows)
    ledger_f.close()
    write_verdicts(verdict_rows)
    print("done", flush=True)


def write_batch(f, batch, verdict_rows):
    f.write(f"\n## batch appended {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("| id | verdict | vio | hold | bracket | premise_false | undef | tag |\n")
    f.write("|---|---|---|---|---|---|---|---|\n")
    for row in batch:
        c = row["counts"]
        f.write(f"| {row['id']} | {row['verdict']} | {c['vio']} "
                f"| {c['hold']} | {c['bracket']} | {c['premise_false']} "
                f"| {c['undef']} | {row.get('tag','')} |\n")
    # details for violations and brackets only
    for row in batch:
        interesting = [r for r in row["readings"]
                       if r["status"] in ("VIO", "BRACKET")]
        if interesting:
            f.write(f"\n### id {row['id']}\n")
            f.write(f"statement: {row['statement']}\n\n")
            for r in interesting[:40]:
                f.write(f"- [{r['status']}] {r['graph']} reading#{r['ri']}: "
                        f"{r['interp']} :: {r['detail']}\n")
    f.flush()


def write_verdicts(verdict_rows):
    lines = ["# SRG-arsenal sweep — running verdict table (WOWII open)\n",
             "| id | verdict | counts | tag |", "|---|---|---|---|"]
    for eid, row in verdict_rows.items():
        c = row["counts"]
        lines.append(f"| {eid} | {row['verdict']} | V{c['vio']} H{c['hold']} "
                     f"B{c['bracket']} P{c['premise_false']} U{c['undef']} "
                     f"| {row.get('tag','')} |")
    VERDICTS.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
