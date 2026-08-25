#!/usr/bin/env python3
"""WOWII 183 wall-navigation trial (open_sweep2_20260826).

Frozen reading:  R(G) = L_s(G) + b(G) - Delta(G^2) - 2*rad(G^2);  hold <=> R >= 0.
Two independent engines (A: enumeration/certificates via networkx structures,
B: branch-and-bound / boolean-matrix path). All arithmetic integer-exact.
"""
import sys, time, itertools, json, os
import networkx as nx

# ---------------------------------------------------------------- builders --
def c5_blowup_with_bridge(l, w, c):
    """F(l; w0..w4; c1..c_{l-1}): C5 blow-up, rim join W3-W4 replaced by a
    chain of l-1 bridge cliques. l=1 recovers the plain complete join."""
    G = nx.Graph()
    blobs = []
    for i in range(5):
        name = f"W{i}"
        blobs.append((name, w[i]))
    for j in range(1, l):
        blobs.insert(4 + j - 1 + 1 - 1 + 0, None)  # placeholder no-op
    # build explicitly instead:
    G = nx.Graph()
    seq = [("W0", w[0]), ("W1", w[1]), ("W2", w[2]), ("W3", w[3])]
    for j in range(1, l):
        seq.append((f"B{j}", c[j - 1]))
    seq.append(("W4", w[4]))
    node_of = {}
    idx = 0
    for name, size in seq:
        verts = list(range(idx, idx + size))
        idx += size
        node_of[name] = verts
        G.add_nodes_from(verts)
        for u, v in itertools.combinations(verts, 2):
            G.add_edge(u, v)
    for k in range(len(seq) - 1):
        a, b = node_of[seq[k][0]], node_of[seq[k + 1][0]]
        for u in a:
            for v in b:
                G.add_edge(u, v)
    # wrap-around join W4-W0
    for u in node_of["W4"]:
        for v in node_of["W0"]:
            G.add_edge(u, v)
    assert nx.is_connected(G)
    return G, {k: v for k, v in node_of.items()}

def star(n): return nx.star_graph(n)          # K_{1,n}

# ------------------------------------------------------------- engine A ----
def closed_nbd_masks(G, nodes):
    i = {v: k for k, v in enumerate(nodes)}
    masks = []
    for v in nodes:
        m = 1 << i[v]
        for u in G[v]:
            m |= 1 << i[u]
        masks.append(m)
    return masks, i

def gamma_c_enum(G):
    """Engine A gamma_c: ascending-k full enumeration over closed-neighborhood
    bitmasks with connectivity check on the induced subgraph."""
    n = G.order()
    if n <= 2:
        return 1
    nodes = list(G.nodes())
    masks, i = closed_nbd_masks(G, nodes)
    adj = [0] * n
    for v in nodes:
        for u in G[v]:
            adj[i[v]] |= 1 << i[u]
    full = (1 << n) - 1
    for k in range(1, n + 1):
        for combo in itertools.combinations(range(n), k):
            cov = 0
            for t in combo:
                cov |= masks[t]
            if cov != full:
                continue
            # connectivity of G[D]
            seen = 1 << combo[0]
            stack = [combo[0]]
            while stack:
                x = stack.pop()
                for y in combo:
                    if not (seen >> y) & 1 and (adj[x] >> y) & 1:
                        seen |= 1 << y
                        stack.append(y)
            if seen == sum(1 << t for t in combo):
                return k
    return n

def is_bipartite_induced(G, keep):
    H = G.subgraph(keep)
    return nx.is_bipartite(H)

def tau_odd_desc_enum(G, cap_seconds=55.0):
    """Engine A tau_odd: descending induced-bipartite search.
    Iterate deletion size k = 0,1,2,... over combinations; first k where some
    G-X is bipartite gives tau_odd = k."""
    n = G.order()
    t0 = time.time()
    vs = list(G.nodes())
    if nx.is_bipartite(G):
        return 0
    for k in range(1, n + 1):
        if time.time() - t0 > cap_seconds:
            return None
        total = 1
        for t in range(k):
            total *= (n - t)
        # cheap early size estimate; still bounded by cap
        for X in itertools.combinations(vs, k):
            if time.time() - t0 > cap_seconds:
                return None
            keep = set(vs) - set(X)
            if is_bipartite_induced(G, keep):
                return k
    return n

def spanning_tree_from_cds(G, D):
    T = nx.Graph()
    T.add_nodes_from(G.nodes())
    Ds = set(D)
    for v in D:                      # BFS tree inside G[D]
        pass
    root = D[0]
    seen = {root}
    stack = [root]
    while stack:
        x = stack.pop()
        for y in D:
            if y not in seen and G.has_edge(x, y):
                seen.add(y); T.add_edge(x, y); stack.append(y)
    assert len(seen) == len(D), "G[D] disconnected"
    for v in G.nodes():
        if v not in Ds:
            for u in G[v]:
                if u in Ds:
                    T.add_edge(v, u)
                    break
        # guarantee domination attachment
    for v in G.nodes():
        if v not in Ds:
            assert any(G.has_edge(v, u) for u in Ds)
            if T.degree(v) == 0:
                for u in Ds:
                    if G.has_edge(v, u):
                        T.add_edge(v, u); break
    assert nx.is_tree(T) and T.order() == G.order()
    return T

def Ls_identity_and_cert(G, gamma_c_val):
    """L_s = n - gamma_c (connected, n>=3); construct certificate tree."""
    n = G.order()
    if n == 2:
        return 2, None
    T = spanning_tree_from_cds(G, _last_cds)
    leaves = sum(1 for v in T.nodes() if T.degree(v) == 1)
    return leaves, T

_last_cds = None

def gamma_c_enum_cert(G):
    global _last_cds
    n = G.order()
    if n <= 2:
        return 1
    nodes = list(G.nodes())
    masks, i = closed_nbd_masks(G, nodes)
    adj = [0] * n
    for v in nodes:
        for u in G[v]:
            adj[i[v]] |= 1 << i[u]
    full = (1 << n) - 1
    for k in range(1, n + 1):
        for combo in itertools.combinations(range(n), k):
            cov = 0
            for t in combo:
                cov |= masks[t]
            if cov != full:
                continue
            seen = 1 << combo[0]; stack = [combo[0]]
            while stack:
                x = stack.pop()
                for y in combo:
                    if not (seen >> y) & 1 and (adj[x] >> y) & 1:
                        seen |= 1 << y; stack.append(y)
            if seen == sum(1 << t for t in combo):
                _last_cds = [nodes[t] for t in combo]
                return k
    return n

def g2_metrics_nx(G):
    G2 = nx.Graph()
    G2.add_nodes_from(G.nodes())
    for u in G.nodes():
        for v in G.nodes():
            if u < v and not G.has_edge(u, v):
                # distance-2 check
                if any(G.has_edge(u, x) and G.has_edge(x, v) for x in G):
                    G2.add_edge(u, v)
    for u, v in G.edges():
        G2.add_edge(u, v)
    Delta = max(dict(G2.degree()).values())
    ecc = nx.eccentricity(G2)
    rad = min(ecc.values())
    return Delta, rad

# ------------------------------------------------------------- engine B ----
def gamma_c_bnb(G):
    """Engine B (v2): iterative-deepening enumeration of connected dominating
    sets. Completeness: any dominating superset of the current choice must
    contain some vertex of N[v] for the lowest undominated v, so branching
    over N[v] enumerates a superset of all minimum dominating sets; the
    connectivity test at full size accepts only connected ones."""
    n = G.order()
    nodes = list(G.nodes())
    masks, i = closed_nbd_masks(G, nodes)
    adjm = [0] * n
    for idx, v in enumerate(nodes):
        for u in G[v]:
            adjm[idx] |= 1 << i[u]
    full = (1 << n) - 1
    def connected_mask(sel_mask):
        low = sel_mask & -sel_mask
        seen = low
        stack = [low]
        while stack:
            x = stack.pop()
            xi = x.bit_length() - 1
            nb = adjm[xi] & sel_mask & ~seen
            while nb:
                yb = nb & -nb
                nb ^= yb
                if not (seen & yb):
                    seen |= yb
                    stack.append(yb)
        return seen == sel_mask
    for k in range(1, n + 1):
        # iterative-deepening over CONNECTED candidate sets: every connected
        # D admits a connected-prefix ordering, so growing by neighbors from
        # singletons enumerates all connected dominating sets of size <= k.
        seen = set()
        stack = []
        for idx in range(n):
            fs = (idx,)
            stack.append(fs)
            seen.add(fs)
        while stack:
            fs = stack.pop()
            sel_mask = sum(1 << t for t in fs)
            dominated = 0
            for t in fs:
                dominated |= masks[t]
            if dominated == full:
                return len(fs)
            if len(fs) >= k:
                continue
            nbrs = 0
            for t in fs:
                nbrs |= adjm[t]
            nbrs &= ~sel_mask
            while nbrs:
                yb = nbrs & -nbrs
                nbrs ^= yb
                y = yb.bit_length() - 1
                fs2 = tuple(sorted(fs + (y,)))
                if fs2 not in seen:
                    seen.add(fs2)
                    stack.append(fs2)
    return n

def oct_bnb(G, cap_seconds=55.0):
    """Engine B tau_odd: iterative-deepening branch-and-bound deleting one
    vertex of a found shortest odd cycle."""
    t0 = time.time()
    n = G.order()
    if nx.is_bipartite(G):
        return 0
    def find_odd_cycle(H):
        # BFS 2-color; find odd cycle via cross edge among colored levels
        color = {}
        parent = {}
        for s in H.nodes():
            if s in color:
                continue
            color[s] = 0; parent[s] = None
            dq = [s]
            while dq:
                x = dq.pop()
                for y in H[x]:
                    if y not in color:
                        color[y] = color[x] ^ 1
                        parent[y] = x
                        dq.append(y)
                    elif color[y] == color[x]:
                        # odd cycle found; lift path
                        px, py = x, y
                        cx, cy = [px], [py]
                        while px != py and parent[px] != py and parent[py] != px:
                            if parent[px] is not None:
                                px = parent[px]; cx.append(px)
                            if parent[py] is not None:
                                py = parent[py]; cy.append(py)
                        common = {px, py}
                        cyc = cx + cy[::-1]
                        # deduce minimal cycle: walk parents from x and y to meet
                        seen = {}
                        a, aa = x, [x]
                        while True:
                            seen[a] = len(aa) - 1
                            if parent[a] is None: break
                            a = parent[a]; aa.append(a)
                        b, bb = y, [y]
                        while b not in seen:
                            b = parent[b]; bb.append(b)
                        cycle = aa[:seen[b] + 1] + bb[::-1]
                        return cycle
        return None
    for k in range(1, n + 1):
        def rec(H, removed):
            if time.time() - t0 > cap_seconds:
                raise TimeoutError
            if nx.is_bipartite(H):
                return True
            if len(removed) >= k:
                return False
            cyc = find_odd_cycle(H)
            if cyc is None:
                return True
            for v in sorted(set(cyc)):
                H2 = nx.Graph(H)
                H2.remove_node(v)
                if rec(H2, removed + [v]):
                    return True
            return False
        try:
            if rec(nx.Graph(G), []):
                return k
        except TimeoutError:
            return None

def g2_metrics_matrix(G):
    """Engine B: boolean matrix square for G2, Floyd-Warshall radius."""
    n = G.order()
    nodes = sorted(G.nodes())
    ix = {v: k for k, v in enumerate(nodes)}
    A = [[0] * n for _ in range(n)]
    for u, v in G.edges():
        A[ix[u]][ix[v]] = A[ix[v]][ix[u]] = 1
    A2 = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            s = 0
            for c in range(n):
                s += A[a][c] * A[c][b]
            A2[a][b] = 1 if (A[a][b] or s) else 0
    deg = [sum(row) for row in A2]
    Delta = max(deg)
    INF = 10 ** 9
    D = [[INF] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a == b:
                D[a][b] = 0
            elif A2[a][b]:
                D[a][b] = 1
    for c in range(n):
        for a in range(n):
            for b in range(n):
                if D[a][c] + D[c][b] < D[a][b]:
                    D[a][b] = D[a][c] + D[c][b]
    ecc = [max(D[a]) for a in range(n)]
    assert max(ecc) < INF, "G2 disconnected"
    return Delta, min(ecc)

# ---------------------------------------------------------------- driver ---
def evaluate(G, engines=("A", "B")):
    t0 = time.time()
    res = {}
    res["n"] = G.order()
    gA = gamma_c_enum_cert(G)
    if G.order() == 2:
        lsA = 2
    else:
        certT = spanning_tree_from_cds(G, _last_cds)
        lsA = sum(1 for v in certT.nodes() if certT.degree(v) == 1)
    dA, rA = g2_metrics_nx(G)
    tA = tau_odd_desc_enum(G)
    res["gamma_c_A"], res["L_s_A"], res["Delta_A"], res["rad_A"], res["tau_A"] = (
        gA, lsA, dA, rA, tA)
    res["b_A"] = None if tA is None else res["n"] - tA
    if "B" in engines:
        gB = gamma_c_bnb(G)
        tB = oct_bnb(G)
        dB, rB = g2_metrics_matrix(G)
        res["gamma_c_B"], res["tau_B"], res["Delta_B"], res["rad_B"] = gB, tB, dB, rB
        res["b_B"] = None if tB is None else res["n"] - tB
    res["secs"] = round(time.time() - t0, 2)
    return res

def residual(res, eng="A"):
    L = res.get(f"L_s_{eng}", res["L_s_A"]); b = res.get(f"b_{eng}")
    if b is None or L is None:
        return None
    return L + b - res[f"Delta_{eng}"] - 2 * res[f"rad_{eng}"]

FIXTURES = [
    ("K2", nx.complete_graph(2), 1),
    ("K3", nx.complete_graph(3), 0),
    ("C5", nx.cycle_graph(5), 0),
    ("P7", nx.path_graph(7), 1),
    ("K1,4", star(4), 3),
    ("K7", nx.complete_graph(7), 0),
]

def b_of_line_graph_Tn(n, cap_seconds=55.0):
    """Engine A exact path for T(n)=L(K_n): b(L(K)) = max |S| over edge sets
    S with chi'(K[S]) <= 2 (Koenig), i.e. Delta(K[S])<=2 and K[S] bipartite.
    Deletion-enumeration ascending on k = |E|-|S|."""
    m = n * (n - 1) // 2
    edges = list(itertools.combinations(range(n), 2))
    t0 = time.time()
    for k in range(0, m + 1):
        if time.time() - t0 > cap_seconds:
            return None
        for X in itertools.combinations(range(m), k):
            if time.time() - t0 > cap_seconds:
                return None
            xs = set(X)
            deg = [0] * n
            ok = True
            adjmask = [0] * n
            for eidx, (u, v) in enumerate(edges):
                if eidx in xs:
                    continue
                deg[u] += 1; deg[v] += 1
                if deg[u] > 2 or deg[v] > 2:
                    ok = False; break
                adjmask[u] |= 1 << v; adjmask[v] |= 1 << u
            if not ok or not _bipartite_mask(adjmask, n):
                continue
            return m - k
    return 0

def _bipartite_mask(adjmask, n):
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            m = adjmask[x]
            while m:
                low = m & -m
                y = low.bit_length() - 1
                m ^= low
                if color[y] == -1:
                    color[y] = color[x] ^ 1
                    stack.append(y)
                elif color[y] == color[x]:
                    return False
    return True

def gamma_c_enum_nodes(G, want_set=False, cap_seconds=55.0):
    """gamma_c enumeration returning the vertex SET (original labels)."""
    global _last_cds
    n = G.order()
    nodes = list(G.nodes())
    masks, i = closed_nbd_masks(G, nodes)
    adjm = [0] * len(nodes)
    for v in nodes:
        for u in G[v]:
            adjm[i[v]] |= 1 << i[u]
    full = (1 << len(nodes)) - 1
    t0 = time.time()
    for k in range(1, len(nodes) + 1):
        for combo in itertools.combinations(range(len(nodes)), k):
            if time.time() - t0 > cap_seconds:
                return None
            cov = 0
            for t in combo:
                cov |= masks[t]
            if cov != full:
                continue
            seen = 1 << combo[0]; stack = [combo[0]]
            while stack:
                x = stack.pop()
                mm = adjm[x]
                while mm:
                    low = mm & -mm
                    y = low.bit_length() - 1
                    mm ^= low
                    if not (seen >> y) & 1 and (1 << y) & sum(1 << t for t in combo):
                        seen |= 1 << y; stack.append(y)
            conn_mask = sum(1 << t for t in combo)
            if seen == conn_mask:
                _last_cds = [nodes[t] for t in combo]
                return (_last_cds if want_set else k)
    return None

def evaluate_control(G, label=""):
    """Gate evaluation: engine A full exact; engine B cross-check where it
    terminates inside caps. Line-graph controls route b through the Koenig
    path."""
    t0 = time.time()
    r = {"label": label, "n": G.order()}
    gc = gamma_c_enum_cert(G)
    if G.order() == 2:
        ls = 2
    else:
        T = spanning_tree_from_cds(G, _last_cds)
        ls = sum(1 for v in T.nodes() if T.degree(v) == 1)
    dA, rA = g2_metrics_nx(G)
    if label.startswith("T("):
        nn = int(label[2:-1])
        tau = b_of_line_graph_Tn(nn)
        tauA_exact_path = "koenig-line-graph"
    else:
        tau = tau_odd_desc_enum(G)
        tauA_exact_path = "descending-enum"
    r.update(gamma_c=gc, L_s=ls, Delta=dA, rad=rA, tau_odd=tau,
             b=None if tau is None else G.order() - tau,
             path=tauA_exact_path)
    R = None if tau is None else ls + (G.order() - tau) - dA - 2 * rA
    r["R"] = R
    r["secs"] = round(time.time() - t0, 2)
    return r

def gate():
    import pickle, os
    rows = []
    # atlas connected n<=7
    atl = nx.graph_atlas_g()
    conn = [G for G in atl if G.order() >= 2 and nx.is_connected(G)]
    print(f"atlas total={len(atl)} connected n>=2: {len(conn)}", flush=True)
    t0 = time.time()
    worst = None
    for idx, G in enumerate(conn):
        r = evaluate_control(G, label=f"atlas{idx}")
        rows.append(r)
        if r["R"] is not None and r["R"] < 0:
            print("GATE VIOLATION!", label := r["label"], r, flush=True)
        if idx % 200 == 0:
            print(f"  atlas {idx}/{len(conn)} t={time.time()-t0:.0f}s", flush=True)
    # named controls
    named = {
        "C5": nx.cycle_graph(5), "C6": nx.cycle_graph(6), "C7": nx.cycle_graph(7),
        "C8": nx.cycle_graph(8), "C9": nx.cycle_graph(9),
        "P7": nx.path_graph(7), "Petersen": nx.petersen_graph(),
        "K3,3": nx.complete_bipartite_graph(3, 3),
        "K7": nx.complete_graph(7),
        "T(7)": nx.line_graph(nx.complete_graph(7)),
    }
    for k in range(1, 7):
        named[f"K1,{k}"] = nx.star_graph(k)
    for k in (2, 3, 4):
        named[f"K{k},{k}"] = nx.complete_bipartite_graph(k, k)
    for name, G in named.items():
        G = nx.convert_node_labels_to_integers(G)
        r = evaluate_control(G, label=name)
        rows.append(r)
        print(f"control {name}: R={r['R']} ({r['path']}, {r['secs']}s)", flush=True)
    bad = [r for r in rows if r["R"] is not None and r["R"] < 0]
    incomplete = [r for r in rows if r["R"] is None]
    print(f"GATE RESULT: rows={len(rows)} violations={len(bad)} incomplete={len(incomplete)}")
    if bad:
        for r in bad[:20]:
            print("VIOLATION ROW:", r)
    with open(os.path.join(os.path.dirname(__file__), "gate_rows.json"), "w") as f:
        json.dump(rows, f, default=str)
    return rows

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fixtures"
    if mode == "fixtures":
        ok = True
        for name, G, expected in FIXTURES:
            r = evaluate(G)
            RA, RB = residual(r, "A"), residual(r, "B")
            agree = (RA == RB)
            status = "OK" if (RA == expected and agree) else "MISMATCH"
            if status != "OK":
                ok = False
            print(f"fixture {name}: R_A={RA} R_B={RB} expected={expected} -> {status}")
        sys.exit(0 if ok else 1)
    if mode == "gate":
        gate()
        sys.exit(0)
    if mode == "family":
        FAM = []
        for l in (1, 2, 3, 4):
            FAM.append((f"A1_l{l}", dict(l=l, w=[2]*5, c=[2]*(l-1))))
        for l in (1, 2, 3, 4, 5):
            FAM.append((f"A2_l{l}", dict(l=l, w=[2, 1, 2, 1, 1], c=[1]*(l-1))))
        for l in (2, 3, 4, 5):
            FAM.append((f"A3_l{l}", dict(l=l, w=[1]*5, c=[1]*(l-1))))
        out = []
        for label, kw in FAM:
            G, blobs = c5_blowup_with_bridge(**kw)
            t0 = time.time()
            rA = evaluate(G, engines=())
            gcA = rA["gamma_c_A"]; tauA = tau_odd_desc_enum(G)
            lsA = rA["L_s_A"]; dA = rA["Delta_A"]; rrA = rA["rad_A"]
            bA = None if tauA is None else G.order() - tauA
            RA = None if bA is None else lsA + bA - dA - 2 * rrA
            # engine B cross-check
            gB = gamma_c_bnb(G)
            dB, rBm = g2_metrics_matrix(G)
            tauB = oct_bnb(G, cap_seconds=50.0)
            bB = None if tauB is None else G.order() - tauB
            RB = None if bB is None else (G.order() - gB) + bB - dB - 2 * rBm
            row = {
                "member": label, "l": kw["l"], "w": kw["w"], "c": kw["c"],
                "n": G.order(),
                "gamma_c": gcA, "L_s": lsA, "tau_odd": tauA, "b": bA,
                "Delta_G2": dA, "rad_G2": rrA, "R_A": RA,
                "gamma_c_B": gB, "tau_B": tauB, "R_B": RB,
                "engines_agree": (RA == RB) and (gcA == gB) and (dA == dB) and (rrA == rBm),
                "secs": round(time.time() - t0, 2),
            }
            out.append(row)
            print(json.dumps(row), flush=True)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "family_rows.json"), "w") as f:
            json.dump(out, f)
        neg = [r for r in out if (r["R_A"] is not None and r["R_A"] < 0)]
        print("FAMILY RESULT: members=%d negative=%d" % (len(out), len(neg)))
        sys.exit(0)
