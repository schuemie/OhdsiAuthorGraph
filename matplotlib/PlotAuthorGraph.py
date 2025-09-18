import csv
import pickle
import os

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from fa2_modified import ForceAtlas2

import ColorSpace
from AvoidOverlap import avoid_overlap

POS_SPRINGFORCE_FILE = "positionsSpringForce.pkl"
POS_NO_OVERLAP_FILE = "positionsNoOverlap.pkl"
MIN_PAPER_COUNT = 2

g = nx.Graph()

with open("../paperClassification/AuthorClassifications.csv", "r", encoding="utf8") as authors_file:
    csv_reader = csv.DictReader(authors_file, delimiter=",")
    for author in csv_reader:
        if int(author["paperCount"]) >= MIN_PAPER_COUNT:
            g.add_node(author["author"], paper_count=int(author["paperCount"]), color=ColorSpace.get_author_color(
                methods_count=int(author["Methodological research"]) + int(author["Open source development"]),
                standards_count=int(author["Open community data standards"]),
                evidence_count=int(author["Clinical evidence generation"])
            ))

print(f"Number of authors: {len(g.nodes)}")

with open("../cytoscape/links.tsv", "r", encoding="utf8") as links_file:
    tsv_reader = csv.DictReader(links_file, delimiter="\t")
    for link in tsv_reader:
        if link["source"] in g.nodes and link["target"] in g.nodes:
            g.add_edge(link["source"], link["target"], paper_count=int(link["paperCount"]))

# Layout step 1: Spring force to bring frequent co-authors closer together
if os.path.exists(POS_SPRINGFORCE_FILE):
    with open(POS_SPRINGFORCE_FILE, "rb") as file:
        positions = pickle.load(file)
else:
    # fa2_modified is a bit cloogy, but it is the only layout algorithm I could find that works well at this scale and
    # with unconnected nodes. (I also tried igraph and network's sprint_layout).
    forceatlas2 = ForceAtlas2(
                            # Behavior alternatives
                            outboundAttractionDistribution=True,  # Dissuade hubs
                            linLogMode=False,  # NOT IMPLEMENTED
                            adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                            edgeWeightInfluence=0.5,

                            # Performance
                            jitterTolerance=1.0,  # Tolerance
                            barnesHutOptimize=False,
                            barnesHutTheta=1.2,
                            multiThreaded=False,  # NOT IMPLEMENTED

                            # Tuning
                            scalingRatio=1.0,
                            strongGravityMode=True,
                            gravity=0.75,

                            # Log
                            verbose=True)
    positions = forceatlas2.forceatlas2_networkx_layout(g, iterations=1000, weight_attr="paper_count")
    with open(POS_SPRINGFORCE_FILE, "wb") as file:
        pickle.dump(positions, file)


# Layout step 2: Move labels to avoid overlap:
if os.path.exists(POS_NO_OVERLAP_FILE):
    with open(POS_NO_OVERLAP_FILE, "rb") as file:
        positions = pickle.load(file)
else:
    positions = avoid_overlap(g, positions, max_iterations=1000)
    with open(POS_NO_OVERLAP_FILE, "wb") as file:
        pickle.dump(positions, file)

# Draw the graph
plt.figure(figsize=(24, 15))

# Edges
edge_alpha = np.array([g.edges[edge]["paper_count"] for edge in g.edges])
edge_alpha = 0.05 + 0.30 * edge_alpha / edge_alpha.max()
nx.draw_networkx_edges(g,
                       positions,
                       alpha=edge_alpha.tolist(),
                       edge_color=(0.5, 0.5, 0.5))

# Nodes
node_sizes = [g.nodes[node]["paper_count"] * 10 for node in g.nodes]
node_colors = [ColorSpace.rgb_to_hex(g.nodes[node]["color"]) for node in g.nodes]
nx.draw_networkx_nodes(g,
                       positions,
                       alpha=0.7,
                       node_color=node_colors,
                       node_size=node_sizes,
                       linewidths=0)
nx.draw_networkx_labels(g,
                        positions,
                        font_size=10)
plt.margins(0, 0)
plt.axis("off")
plt.savefig("plot.png", dpi=300, bbox_inches="tight")
plt.show()
