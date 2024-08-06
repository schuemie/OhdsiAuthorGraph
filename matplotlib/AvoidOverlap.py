import math
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.text import Text
from matplotlib.transforms import Bbox
import numpy as np


def get_bounding_box(object: Text) -> Bbox:
    bounding_box = object.get_window_extent().transformed(plt.gca().transData.inverted())
    return bounding_box


def compute_width_height(bounding_box: Bbox):
    return bounding_box.width, bounding_box.height


def compute_translation_vector(bbox1: Bbox, bbox2: Bbox) -> Tuple[float, float]:
    overlap_bbox = Bbox.intersection(bbox1, bbox2)

    if overlap_bbox.width == 0 and overlap_bbox.height == 0:
        return 0, 0  # No overlap, no need to move

    move_x = 0
    move_y = 0

    if overlap_bbox.width > 0:
        if bbox1.x0 < bbox2.x0:
            move_x = overlap_bbox.width
        else:
            move_x = -overlap_bbox.width

    if overlap_bbox.height > 0:
        if bbox1.y0 < bbox2.y0:
            move_y = overlap_bbox.height
        else:
            move_y = -overlap_bbox.height

    return move_x, move_y


def get_centroid(bbox: Bbox):
    x_centroid = (bbox.x0 + bbox.x1) / 2
    y_centroid = (bbox.y0 + bbox.y1) / 2
    return (x_centroid, y_centroid)


def avoid_overlap(g, positions: Dict[str, Tuple[float, float]], max_iterations: int = 1000) -> Dict[str, Tuple[float, float]]:
    plt.figure(figsize=(24, 15))
    nx.draw_networkx_nodes(g, positions)
    texts = []
    for node, (x, y) in positions.items():
        texts.append(plt.text(x, y, node, fontsize=10, ha="center", va="center", color="black"))
    plt.margins(0, 0)
    plt.axis("off")
    plt.gca().figure.canvas.draw()
    bboxes = [get_bounding_box(text) for text in texts]
    plt.close()
    # move_fraction = 0.1
    for iteration in range(max_iterations):
        overlaps = 0
        move_fraction = 0.5 if iteration < 100 else 0.1
        move_vectors = [np.array([0.0, 0.0]) for _ in bboxes]

        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                if bboxes[i].overlaps(bboxes[j]):
                    overlaps += 1
                    move_vector = compute_translation_vector(bboxes[i], bboxes[j])
                    move_vectors[i] -= np.array(move_vector) * move_fraction / 2
                    move_vectors[j] += np.array(move_vector) * move_fraction / 2

        # Apply the computed move vectors
        for k in range(len(bboxes)):
            if np.any(move_vectors[k] != 0):
                bboxes[k] = Bbox.from_extents(
                    bboxes[k].x0 + move_vectors[k][0],
                    bboxes[k].y0 + move_vectors[k][1],
                    bboxes[k].x1 + move_vectors[k][0],
                    bboxes[k].y1 + move_vectors[k][1]
                )

        if overlaps == 0:
            break  # Exit if no overlaps detected
        print(f"Iteration {iteration + 1}: {overlaps} overlaps found")

    for i, key in enumerate(positions.keys(), 0):
        positions[key] = get_centroid(bboxes[i])
    return positions
