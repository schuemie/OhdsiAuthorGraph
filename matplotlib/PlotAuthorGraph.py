import csv

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from fa2_modified import ForceAtlas2
from matplotlib import colors

g = nx.Graph()

with open("../cytoscape/authors.tsv", "r", encoding="utf8") as authors_file:
    tsv_reader = csv.DictReader(authors_file, delimiter="\t")
    for author in tsv_reader:
        g.add_node(author["name"], paper_count=int(author["paperCount"]), first_year=int(author["firstYear"]))

with open("../cytoscape/links.tsv", "r", encoding="utf8") as links_file:
    tsv_reader = csv.DictReader(links_file, delimiter="\t")
    for link in tsv_reader:
        g.add_edge(link["source"], link["target"], paper_count=int(link["paperCount"]))

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
positions = forceatlas2.forceatlas2_networkx_layout(g, iterations=10000, weight_attr="paper_count")

# Most important concern is overlapping labels (the plot is no fun if you can"t read all the names).
# We therefore use adjust_texts to avoid overlap, and adjust the position of the nodes based on that.

# Recompute node positions to avoid label overlap:
plt.figure(figsize=(24, 15))
texts = []
for node, (x, y) in positions.items():
    texts.append(plt.text(x, y, node, fontsize=10, ha="center", va="center"))
adjust_text(texts,
            pull_threshold=1000,
            force_text=1.0,
            force_static=1.0,
            force_pull=0.02,
            expand_axes=True,
            ensure_inside_axes=False,
            iter_lim=10)
positions = {text.get_text(): (text.get_position()[0], text.get_position()[1]) for text in texts}
plt.close()

# Redraw the graph with updated node positions
plt.figure(figsize=(24, 15))

# Draw edges
edge_alpha = np.array([g.edges[edge]["paper_count"] for edge in g.edges])
edge_alpha = 0.05 + 0.30 * edge_alpha / edge_alpha.max()
nx.draw_networkx_edges(g,
                       positions,
                       alpha=edge_alpha.tolist(),
                       edge_color=(0.5, 0.5, 0.5))

# Draw nodes
node_sizes = [g.nodes[node]["paper_count"] * 10 for node in g.nodes]
first_years = [g.nodes[node]["first_year"] for node in g.nodes]
cmap = colors.LinearSegmentedColormap.from_list("OHDSI colors", ["#336B91", "#69AED5", "#11A08A", "#FBC511", "#EB6622"])
norm = colors.Normalize(vmin=min(first_years), vmax=max(first_years))
node_colors = cmap(norm(first_years))
nx.draw_networkx_nodes(g,
                       positions,
                       alpha=0.7,
                       node_color=node_colors,
                       node_size=node_sizes,
                       linewidths=0)
nx.draw_networkx_labels(g,
                        positions,
                        font_size=10)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
colorbar = plt.colorbar(sm,
                        ax=plt.gca(),
                        drawedges=False,
                        shrink=0.25)
# for t in colorbar.ax.get_yticklabels():
#      t.set_fontsize(12)
plt.axis("off")
plt.savefig("plot.png", dpi=300)
plt.show()
