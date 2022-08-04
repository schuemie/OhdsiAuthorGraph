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


## Cytoscape instructions

File --> Import --> Network from file --> Select `links.tsv`

File --> Import --> Table from file --> Select `authors.tsv`

In Filter:

- `+` --> Node: paperCount --> Change min value to 2
- 'show' --> Apply (see bottom)

In Style - Node (see bottom tab):

- Fill color:
    - Column: firstYear
    - Mapping Type: Continuous mapping
- Label Font Size: 15
- Label Position (Click Properties dropdown to show): 
    - Node Anchor Points: East
    - Object Anchor Points: West
    - Label Justification: Left Justified
    - X Offset Value: 1
    - Y Offset Value: 0
- Shape
    - Ellipse
- Lock node width and height: check
- Size: 
    - Column: paperCount
    - Mapping Type: Continuous mapping
 
In Style - Edge (see bottom tab):

- Stroke color: RGB all at 150
- Transparency: 
    - Column: paperCount
    - Mapping Type: Continuous mapping
    - Open mapping. Double click left box, set value to 40. Double click right box, set value to 100
	
	
Layout --> Settings

- Layout Algorithm: Prefuse Force Directed OpenCL Layout
- Edge column: paperCount
- How to interpret: -Log(value)
- Iterations: 100
- Edge-repulsive iterations: 100
- Default Sprint Coefficient: 2E-5
- Default Spring Length: 1
- Default Node Mass: 3

Next, move nodes manually to fill screen and avoid label overlap (may take a while)

File --> Export --> Network to image


