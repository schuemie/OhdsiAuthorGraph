from typing import List, Tuple

import numpy as np
from matplotlib import pyplot as plt
import matplotlib


def hex_to_rgb(hex_color: str) -> List[float]:
    # Remove the hash at the start if it's there
    hex_color = hex_color.lstrip('#')

    # Convert the hex string to an integer and split into RGB components
    rgb_int = int(hex_color, 16)
    r = (rgb_int >> 16) & 255
    g = (rgb_int >> 8) & 255
    b = rgb_int & 255

    # Normalize the RGB values to [0, 1]
    rgb_normalized = (r / 255, g / 255, b / 255)

    return rgb_normalized


COLOR_1 = hex_to_rgb("#0050bb") # Blue: methods
COLOR_2 = hex_to_rgb("#fdd04d") # Yellow: standards
COLOR_3 = hex_to_rgb("#de0026") # Red: evidence


def get_author_color(methods_count: int, standards_count: int, evidence_count: int) -> List[float]:
    # Ensure weights sum to 1
    weights = [methods_count, standards_count, evidence_count]
    weights = np.array(weights) / np.sum(weights)

    # Interpolate each color component
    r = weights[0] * COLOR_1[0] + weights[1] * COLOR_2[0] + weights[2] * COLOR_3[0]
    g = weights[0] * COLOR_1[1] + weights[1] * COLOR_2[1] + weights[2] * COLOR_3[1]
    b = weights[0] * COLOR_1[2] + weights[1] * COLOR_2[2] + weights[2] * COLOR_3[2]

    r = np.clip(r, 0, 1)
    g = np.clip(g, 0, 1)
    b = np.clip(b, 0, 1)

    return r, g, b


def rgb_to_hex(rgb: Tuple[float]) -> str:
    rgb = np.clip(rgb, 0, 1)
    rgb_255 = tuple(int(round(c * 255)) for c in rgb)
    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb_255[0], rgb_255[1], rgb_255[2])
    return hex_color


def plot_legend(filename: str):
    fig, ax = plt.subplots()
    resolution = 100
    triangle = np.array([
        [0, 0],
        [1, 0],
        [0.5, np.sqrt(3) / 2]
    ])
    for i in range(resolution + 1):
        for j in range(resolution + 1 - i):
            u = i / resolution
            v = j / resolution
            w = 1 - u - v
            p = u * triangle[0] + v * triangle[1] + w * triangle[2]
            interpolated_color = get_author_color(u, v, w)
            ax.plot(p[0], p[1], 'o', color=interpolated_color, markersize=3)

    # Draw the triangle borders
    ax.plot(*zip(*triangle, triangle[0]), color='k')
    matplotlib.rcParams.update({'font.size': 22})
    ax.text(0.1, -0.02, "Methods & software", horizontalalignment="center", verticalalignment="top")
    ax.text(0.9, -0.02, "Standards", horizontalalignment="center", verticalalignment="top")
    ax.text(0.5, np.sqrt(3) / 2 + 0.02, "Evidence generation", horizontalalignment="center", verticalalignment="bottom")
    ax.set_aspect('equal')
    ax.axis('off')
    plt.savefig("legend.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    plot_legend("")