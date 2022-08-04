OhdsiAuthorGraph
================

Code for visualizing the network of OHDSI authors. Nodes represent authors, links represent co-authorships.

This repo contains the code for preparing the data for visualization. There are two ways to do the visualization:

1. Using [Cytoscape](https://cytoscape.org/). Cytoscape is an open source software platform for visualizing complex networks.

2. Using JavaScript embedded in a web page. This uses the [D3 JavaScript library](https://d3js.org/).

## How to use

1. Get a list of PMIDs (PubMed IDs) of OHDSI papers. 

2. Run [PrepareGraphData.R](PrepareGraphData.R).

3. Either view the results in the provided HTML page (see [docs](docs) folder), or load the `.tsv` files in the [cytoscape](cytoscape) folder in Cytoscape.

