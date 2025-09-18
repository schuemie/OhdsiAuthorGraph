# OhdsiAuthorGraph

Code for visualizing the network of OHDSI authors. Nodes represent authors, links represent co-authorships.

This repo contains the code for preparing the data for visualization. There are three ways to do the visualization:

1.  Using [Cytoscape](https://cytoscape.org/). Cytoscape is an open source software platform for visualizing complex networks.

2.  Using JavaScript embedded in a web page. This uses the [D3 JavaScript library](https://d3js.org/).

3.  Using Python matplotlib (preferred).

## How to use

1.  Get a list of PMIDs (PubMed IDs) of OHDSI papers.

2.  Run [PrepareGraphData.R](PrepareGraphData.R).

3.  Either view the results in the provided HTML page (see [docs](docs) folder), load the `.tsv` files in the [cytoscape](cytoscape) folder in Cytoscape, or proceed to instructions for matplotlib (below).

## Cytoscape instructions

File --\> Import --\> Network from file --\> Select `links.tsv`

File --\> Import --\> Table from file --\> Select `authors.tsv`

You probably want to select the 'Always Show Graphics Details' (looks like a pixelated diamond) in the bottom right of the graph pane. Else you won't see the labels etc. in the preview.

In Style - Node (see bottom tab):

-   Fill color:
    -   Column: firstYear
    -   Mapping Type: Continuous mapping
-   Label Font Size: 15
-   Label Position (Click Properties dropdown to show):
    -   Node Anchor Points: East
    -   Label Anchor Points: West
    -   Label Justification: Left Justified
    -   X Offset Value: 1
    -   Y Offset Value: 0
-   Shape
    -   Ellipse
-   Lock node width and height: check
-   Size:
    -   Column: paperCount
    -   Mapping Type: Continuous mapping

In Style - Edge (see bottom tab):

-   Stroke color: RGB all at 150
-   Transparency:
    -   Column: paperCount
    -   Mapping Type: Continuous mapping
    -   Open mapping. Double click left box, set value to 40. Double click right box, set value to 100

Layout --\> yFiles Organic Layout --\> yFiles Remove Overlaps (Tip: temporarily change node shape to rectangle, uncheck lock node width and heigh, set height to 25 and width to 50, node anchor to west. This will cause layout to avoid (most) label overlap)

Next, move nodes manually to fill screen and avoid label overlap (may take a while)

File --\> Export --\> Network to image

# Matplotlib instructions

The Matplotlib code colors authors by the type of papers they publish. For this, we need to first classify their papers by type, for which we use LLMs:

1.  Run PaperClassification.R. This requires access to an LLM like GPT-4. This will write the classifications to the `paperClassification` folder.
2.  Run matplotlib/PlotAuthorGraph.py. Make sure to delete the pickle files (`positionsSpringForce.pkl` and `positionsNoOverlap.pkl`) first. These are caches from a previous run.
3.  In some image editor (e.g. Gimp), combine the plot (`matplotlib/plot.png`) with the legend (`matplotlib/legend.png`).
