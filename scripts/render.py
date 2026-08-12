"""Render C5[K4] for the README: 5 K4-blobs on a pentagon, white background."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


def build():
    G = nx.Graph()
    G.add_nodes_from(range(20))
    blob = lambda v: v // 4
    for u in range(20):
        for v in range(u + 1, 20):
            if blob(u) == blob(v) or (blob(u) - blob(v)) % 5 in (1, 4):
                G.add_edge(u, v)
    return G


G = build()
blob = lambda v: v // 4

# blob centers on a pentagon, members on a small square around each center
R, r = 3.0, 0.62
pos = {}
for v in range(20):
    i, j = blob(v), v % 4
    cx = R * math.sin(2 * math.pi * i / 5)
    cy = R * math.cos(2 * math.pi * i / 5)
    ang = 2 * math.pi * j / 4 + math.pi / 4 + 2 * math.pi * i / 5
    pos[v] = (cx + r * math.cos(ang), cy + r * math.sin(ang))

blob_colors = ["#e63946", "#f4a261", "#2a9d8f", "#457b9d", "#8338ec"]
node_colors = [blob_colors[blob(v)] for v in range(20)]
in_blob = [(u, v) for u, v in G.edges() if blob(u) == blob(v)]
cross = [(u, v) for u, v in G.edges() if blob(u) != blob(v)]

fig, ax = plt.subplots(figsize=(9, 9), facecolor="white")
ax.set_facecolor("white")
nx.draw_networkx_edges(G, pos, edgelist=cross, edge_color="#c7c7c7",
                       width=0.9, alpha=0.75, ax=ax)
nx.draw_networkx_edges(G, pos, edgelist=in_blob, edge_color="#333333",
                       width=2.2, ax=ax)
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=520,
                       edgecolors="#222222", linewidths=1.4, ax=ax)
ax.set_axis_off()
ax.set_aspect("equal")
fig.tight_layout(pad=0.4)
fig.savefig("assets/c5k4.png", dpi=180, facecolor="white",
            bbox_inches="tight")
print("wrote assets/c5k4.png")
