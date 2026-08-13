#!/usr/bin/env python3
"""Frozen exact Erdős 23 C5-blow-up and triangle-free surgery trial."""

import argparse
import itertools
import json
import math
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


RECORD_PATH = None


def persist(row):
    if RECORD_PATH is not None:
        with RECORD_PATH.open("a", encoding="utf-8") as output:
            output.write(json.dumps(row) + "\n")
            output.flush()
    return row


def c5_blowup(sizes):
    graph = nx.Graph(); parts=[]; nxt=0
    for size in sizes:
        part=list(range(nxt,nxt+size)); nxt+=size
        graph.add_nodes_from(part); parts.append(part)
    for i in range(5):
        graph.add_edges_from(itertools.product(parts[i],parts[(i+1)%5]))
    return graph, parts


def dihedral_key(sizes):
    values=[]
    for reverse in (False,True):
        row=tuple(reversed(sizes)) if reverse else tuple(sizes)
        values.extend(row[i:]+row[:i] for i in range(5))
    return min(values)


def exact_maxcut_bruteforce(graph):
    vertices=list(graph); best=-1; best_side=set()
    root=vertices[0] if vertices else None
    rest=vertices[1:]
    for mask in range(1<<len(rest)):
        side={root} if root is not None else set()
        side.update(rest[i] for i in range(len(rest)) if mask>>i&1)
        value=sum((u in side)!=(v in side) for u,v in graph.edges())
        if value>best: best=value; best_side=side
    return best,best_side,"vertex_bruteforce"


def exact_maxcut_blowup(graph,parts):
    best=-1; best_bits=None
    for bits in itertools.product((0,1),repeat=5):
        value=sum(len(parts[i])*len(parts[(i+1)%5])
                  for i in range(5) if bits[i]!=bits[(i+1)%5])
        if value>best: best=value; best_bits=bits
    side={v for i,part in enumerate(parts) if best_bits[i] for v in part}
    return best,side,"exact_32_part_assignments"


def exact_maxcut_milp(graph):
    vertices=list(graph); edges=list(graph.edges()); n=len(vertices); m=len(edges)
    index={v:i for i,v in enumerate(vertices)}
    # x_v is the side, y_e indicates an edge crossing the cut.
    rows=[]; lower=[]; upper=[]
    for j,(u,v) in enumerate(edges):
        iu,iv=index[u],index[v]
        for coefficients,lo,hi in [
            ((-1,-1,1),-np.inf,0), ((1,1,1),-np.inf,2),
            ((1,-1,-1),-np.inf,0), ((-1,1,-1),-np.inf,0),
        ]:
            row=np.zeros(n+m); row[iu]=coefficients[0]; row[iv]=coefficients[1]
            row[n+j]=coefficients[2]; rows.append(row); lower.append(lo); upper.append(hi)
    objective=np.zeros(n+m); objective[n:]=-1
    result=milp(objective,integrality=np.ones(n+m),
        bounds=Bounds(np.zeros(n+m),np.ones(n+m)),
        constraints=LinearConstraint(np.asarray(rows),np.asarray(lower),np.asarray(upper)),
        options={"time_limit":10,"mip_rel_gap":0.0})
    if not result.success: raise TimeoutError
    side={v for v in vertices if result.x[index[v]]>0.5}
    value=sum((u in side)!=(v in side) for u,v in edges)
    return value,side,"scipy_milp_zero_gap"


def record(name,graph,maxcut_solver,meta,stage):
    start=time.monotonic(); graph=nx.convert_node_labels_to_integers(graph)
    triangles=sum(nx.triangles(graph).values())//3
    if triangles: raise AssertionError((name,"not triangle-free",triangles))
    maxcut,side,method=maxcut_solver(graph)
    other=set(graph)-side
    kept=sorted([u,v] for u,v in graph.edges() if (u in side)!=(v in side))
    deleted=sorted([u,v] for u,v in graph.edges() if (u in side)==(v in side))
    witness=nx.Graph(); witness.add_nodes_from(graph); witness.add_edges_from(kept)
    assert nx.is_bipartite(witness) and len(deleted)==graph.number_of_edges()-maxcut
    n=len(graph); divisor=n//5; bound=divisor*divisor
    return persist({"event":"graph_evaluated","stage":stage,"name":name,"meta":meta,
        "n":n,"m":graph.number_of_edges(),"graph6":nx.to_graph6_bytes(graph,header=False).strip().decode(),
        "triangle_count":triangles,"maxcut":maxcut,"cut_side":sorted(side),
        "cut_other_side":sorted(other),"kept_cut_edges":kept,"deleted_edges":deleted,
        "edge_bipartization":len(deleted),"bound_n_squared":bound,
        "slack":bound-len(deleted),"crossing":len(deleted)>bound,
        "maxcut_method":method,"witness_replay":True,
        "seconds":round(time.monotonic()-start,6)})


def base_inputs():
    rows=[]
    for order in (15,20,25):
        seen=set()
        for sizes in itertools.product(range(1,9),repeat=5):
            if sum(sizes)!=order: continue
            key=dihedral_key(sizes)
            if key in seen: continue
            seen.add(key); imbalance=sum((5*x-order)**2 for x in key)
            rows.append((imbalance,order,key))
    rows.sort()
    for _,order,sizes in rows[:1000]:
        graph,parts=c5_blowup(sizes)
        yield f"C5_blowup_{sizes}",graph,parts,{"sizes":sizes,"order":order}


def gate():
    def pad_to_five(graph):
        graph=nx.convert_node_labels_to_integers(graph)
        target=5*math.ceil(len(graph)/5)
        graph.add_nodes_from(range(len(graph),target))
        return graph

    inputs=[]
    for i,g in enumerate(nx.graph_atlas_g()):
        if len(g)==5 and nx.is_connected(g) and sum(nx.triangles(g).values())==0:
            inputs.append((f"atlas5_{i}",g,{}))
    inputs += [("C5",nx.cycle_graph(5),{}),("Petersen",nx.petersen_graph(),{})]
    for a in range(1,6):
        for b in range(a,7):
            inputs.append((f"K{a}_{b}_padded",pad_to_five(nx.complete_bipartite_graph(a,b)),
                           {"padded_isolates":5*math.ceil((a+b)/5)-(a+b)}))
    for size in range(1,6):
        graph,_=c5_blowup((size,)*5); inputs.append((f"balanced_C5_{size}",graph,{}))
    outputs=[]
    for name,graph,meta in inputs:
        if len(graph)<=15:
            solver=exact_maxcut_bruteforce
        else:
            _,parts=c5_blowup((len(graph)//5,)*5)
            solver=lambda g,p=parts: exact_maxcut_blowup(g,p)
        outputs.append(record(name,graph,solver,meta,"gate"))
    return outputs


def surgery_inputs(parent_path,limit):
    parents=[json.loads(line) for line in open(parent_path) if line.strip()]
    parents=[r for r in parents if r.get('event')=='graph_evaluated' and r['slack']<=2]
    parents.sort(key=lambda r:(r['slack'],r['n'],r['graph6']))
    candidates=[]
    for parent in parents:
        graph=nx.from_graph6_bytes(parent['graph6'].encode())
        for edge in sorted(tuple(sorted(e)) for e in graph.edges()):
            changed=graph.copy(); changed.remove_edge(*edge)
            candidates.append((parent,changed,"delete",edge))
        for edge in sorted(tuple(sorted(e)) for e in nx.non_edges(graph)):
            if set(graph[edge[0]]).isdisjoint(graph[edge[1]]):
                changed=graph.copy(); changed.add_edge(*edge)
                candidates.append((parent,changed,"add",edge))
    seen=set(); emitted=0
    for parent,graph,operation,edge in candidates:
        key=(len(graph),graph.number_of_edges(),nx.weisfeiler_lehman_graph_hash(graph))
        if key in seen: continue
        seen.add(key); emitted+=1
        yield f"{operation}_{edge}_of_{parent['name']}",graph,{"parent":parent['name'],"operation":operation,"edge":edge}
        if emitted>=limit:return


def main():
    global RECORD_PATH
    parser=argparse.ArgumentParser(); parser.add_argument('--lane',choices=('gate','base','surgery'),required=True)
    parser.add_argument('--parents'); parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--record-file'); args=parser.parse_args()
    if args.record_file is not None: RECORD_PATH=Path(args.record_file)
    start=time.monotonic(); outputs=[]; timeouts=0
    if args.lane=='gate': outputs=gate()
    elif args.lane=='base':
        for name,graph,parts,meta in base_inputs():
            outputs.append(record(name,graph,lambda g,p=parts:exact_maxcut_blowup(g,p),meta,'base'))
    else:
        for name,graph,meta in surgery_inputs(args.parents,args.limit):
            try: outputs.append(record(name,graph,exact_maxcut_milp,meta,'surgery'))
            except TimeoutError:
                timeouts+=1; outputs.append(persist({"event":"timeout","name":name,"n":len(graph)}))
    print(json.dumps({"summary":{"lane":args.lane,"evaluated":len(outputs),
        "crossings":sum(r.get('crossing',False) for r in outputs),"timeouts":timeouts,
        "seconds":round(time.monotonic()-start,6)}}))
    for output in outputs: print(json.dumps(output))


if __name__=='__main__': main()
