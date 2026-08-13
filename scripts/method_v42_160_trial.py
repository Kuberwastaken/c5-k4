#!/usr/bin/env python3
"""Frozen exact family trial for current DeepMind WOWII 160."""

import itertools
import json
import networkx as nx


def c4_free(G):
    nodes=list(G)
    return all(len(set(G[u]) & set(G[v])) < 2 for u,v in itertools.combinations(nodes,2))


def alpha_induced(G, vertices):
    vs=list(vertices); n=len(vs)
    for k in range(n,-1,-1):
        for S in itertools.combinations(vs,k):
            if all(not G.has_edge(u,v) for u,v in itertools.combinations(S,2)):
                return k
    return 0


def local_invariants(G):
    maxL=max(alpha_induced(G,G[v]) for v in G)
    maxT=max(G.subgraph(G[v]).number_of_edges() for v in G)
    return maxL,maxT


def connected_dominating(G,S):
    S=set(S)
    if not S: return False
    if len(S)>1 and not nx.is_connected(G.subgraph(S)): return False
    return all(v in S or any(u in S for u in G[v]) for v in G)


def max_leaves(G):
    n=len(G)
    if n==2: return 2
    for k in range(1,n+1):
        for S in itertools.combinations(G.nodes(),k):
            if connected_dominating(G,S): return n-k
    raise AssertionError


def profile(G):
    G=nx.convert_node_labels_to_integers(G)
    if len(G)<2 or not nx.is_connected(G): return None
    cf=c4_free(G)
    ml,mt=local_invariants(G)
    ls=max_leaves(G)
    return {"n":len(G),"m":G.number_of_edges(),"c4free":cf,
            "maxL":ml,"maxT":mt,"Ls":ls,"rhs":ml+(mt if cf else 0),
            "crossing":cf and ls<ml+mt,
            "graph6":nx.to_graph6_bytes(G,header=False).decode().strip(),
            "edges":sorted([sorted(e) for e in G.edges()])}


def clique_block_path(sizes):
    G=nx.Graph(); last=None
    for s in sizes:
        if last is None:
            block=list(range(s)); G.add_edges_from(itertools.combinations(block,2)); last=block[-1]
        else:
            fresh=list(range(len(G),len(G)+s-1)); block=[last]+fresh
            G.add_edges_from(itertools.combinations(block,2)); last=block[-1]
    return G


def clique_block_star(sizes):
    G=nx.Graph(); G.add_node(0)
    for s in sizes:
        fresh=list(range(len(G),len(G)+s-1)); block=[0]+fresh
        G.add_edges_from(itertools.combinations(block,2))
    return G


def friendship(t):
    G=nx.Graph(); G.add_node(0)
    for _ in range(t):
        a,b=len(G),len(G)+1; G.add_edges_from([(0,a),(a,b),(b,0)])
    return G


def triangle_chain(t):
    G=nx.Graph(); G.add_edges_from([(0,1),(1,2),(2,0)]); portal=2
    for _ in range(1,t):
        a,b=len(G),len(G)+1; G.add_edges_from([(portal,a),(a,b),(b,portal)]); portal=b
    return G


def variants():
    seen=set()
    def emit(name,G):
        if len(G)>16:return
        key=(len(G),G.number_of_edges(),nx.weisfeiler_lehman_graph_hash(G))
        if key not in seen:
            seen.add(key); yield name,G.copy()
    # Block paths/stars, deterministic bounded size patterns.
    for blocks in range(2,7):
        patterns=[(s,)*blocks for s in range(2,6)]
        patterns += [tuple(2+((j+phase)%4) for j in range(blocks)) for phase in range(4)]
        for sizes in patterns:
            yield from emit(f"block_path:{sizes}",clique_block_path(sizes))
            yield from emit(f"block_star:{sizes}",clique_block_star(sizes))
    # Friendship and portal pendants.
    for t in range(2,8):
        G=friendship(t); yield from emit(f"friendship:{t}",G)
        outer=list(range(1,len(G)))
        for count in range(1,min(4,len(outer))+1):
            H=G.copy()
            for portal in outer[:count]: H.add_edge(portal,len(H))
            yield from emit(f"friendship_pendants:{t}:{count}",H)
        for portal in outer[:min(4,len(outer))]:
            H=G.copy(); a,b=len(H),len(H)+1
            H.add_edges_from([(portal,a),(a,b),(b,portal)])
            yield from emit(f"friendship_portal_triangle:{t}:{portal}",H)
    # Triangle cactus chains and stars plus pendant paths.
    for t in range(2,7):
        for label,G in (("chain",triangle_chain(t)),("star",friendship(t))):
            yield from emit(f"triangle_{label}:{t}",G)
            portals=list(G)[:min(5,len(G))]
            for plen in (1,2):
                for portal in portals:
                    H=G.copy(); prev=portal
                    for _ in range(plen): H.add_edge(prev,len(H)); prev=len(H)-1
                    yield from emit(f"triangle_{label}_pendant:{t}:{portal}:{plen}",H)
    # Frozen one-move surgeries of everything accumulated so far are generated
    # from a snapshot of representative base families.
    bases=[friendship(t) for t in range(2,6)]+[triangle_chain(t) for t in range(2,6)]
    bases += [clique_block_path((3,)*b) for b in range(2,5)]
    for bi,G in enumerate(bases):
        for u,v in list(G.edges())[:12]:
            H=G.copy(); H.remove_edge(u,v); w=len(H); H.add_edges_from([(u,w),(w,v)])
            yield from emit(f"subdivide:{bi}:{u}:{v}",H)


def atlas_gate():
    total=c4=0; crossings=[]; tight=[]
    for G in nx.graph_atlas_g():
        if not (2<=len(G)<=7) or not nx.is_connected(G):continue
        total+=1
        p=profile(G)
        if p["c4free"]:
            c4+=1
            if p["crossing"]:crossings.append(p)
            if p["Ls"]==p["rhs"]:tight.append(p["graph6"])
    return {"connected":total,"c4free":c4,"crossings":crossings,"tight_count":len(tight)}


def main():
    controls={"K3":nx.complete_graph(3),"claw":nx.star_graph(3),
              "F2":friendship(2),"P5":nx.path_graph(5),"C5":nx.cycle_graph(5),
              "C4":nx.cycle_graph(4)}
    print(json.dumps({"event":"sanity","controls":{k:profile(v) for k,v in controls.items()},
                      "atlas":atlas_gate()},sort_keys=True))
    generated=exact=0; crosses=[]; tight=[]; near=[]
    for name,G in variants():
        generated+=1
        if generated>20000:break
        if not nx.is_connected(G) or not c4_free(G):continue
        exact+=1
        if exact>3000:break
        p=profile(G);p["family"]=name
        if p["crossing"]:crosses.append(p)
        if p["Ls"]==p["rhs"]:tight.append(p)
        near.append(p);near.sort(key=lambda x:(x["Ls"]-x["rhs"],x["n"]));near=near[:10]
    print(json.dumps({"event":"trial","generated":generated,"exact":exact,
                      "crossings":crosses,"tight_count":len(tight),"near":near},sort_keys=True))


if __name__=="__main__":main()
