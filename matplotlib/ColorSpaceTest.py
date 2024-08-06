import math

import numpy as np
import matplotlib.pyplot as plt
import colorspacious as cs


def rgb_to_lab(color):
    return cs.cspace_convert(color, "sRGB1", "CIELab")


def lab_to_rgb(color):
    return cs.cspace_convert(color, "CIELab", "sRGB1")


def interpolate_colors_lab(color1, color2, color3, weights):
    # Convert RGB colors to Lab
    lab1 = rgb_to_lab(color1)
    lab2 = rgb_to_lab(color2)
    lab3 = rgb_to_lab(color3)

    # Ensure weights sum to 1
    weights = np.array(weights) / np.sum(weights)

    # Interpolate each Lab component
    L = weights[0] * lab1[0] + weights[1] * lab2[0] + weights[2] * lab3[0]
    a = weights[0] * lab1[1] + weights[1] * lab2[1] + weights[2] * lab3[1]
    b = weights[0] * lab1[2] + weights[1] * lab2[2] + weights[2] * lab3[2]

    interpolated_lab = (L, a, b)

    # Convert the interpolated Lab color back to RGB
    interpolated_rgb = lab_to_rgb(interpolated_lab)

    # Ensure the RGB values are within the valid range [0, 1]
    interpolated_rgb = np.clip(interpolated_rgb, 0, 1)

    return interpolated_rgb


def interpolate_colors_rgb(color1, color2, color3, weights):
    # Ensure weights sum to 1
    weights = np.array(weights) / np.sum(weights)

    # Interpolate each color component
    r = weights[0] * color1[0] + weights[1] * color2[0] + weights[2] * color3[0]
    g = weights[0] * color1[1] + weights[1] * color2[1] + weights[2] * color3[1]
    b = weights[0] * color1[2] + weights[1] * color2[2] + weights[2] * color3[2]

    r = np.clip(r, 0, 1)
    g = np.clip(g, 0, 1)
    b = np.clip(b, 0, 1)

    return (r, g, b)


def blend_with_gray(color, weights, gray=(0.5, 0.5, 0.5)):
    # Calculate the variance of the weights
    variance = np.var(weights)

    # Determine the blend factor (higher variance means less blending towards gray)
    blend_factor = np.clip(math.sqrt(variance)*4, 0.75, 1)  # Adjust the factor as needed

    # Blend the color with gray
    blended_color = blend_factor * np.array(color) + (1 - blend_factor) * np.array(gray)

    # Ensure the blended RGB values are within the valid range [0, 1]
    blended_color = np.clip(blended_color, 0, 1)

    return blended_color


def hex_to_rgb(hex_color):
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

# Example colors in RGB (normalized to [0, 1])
# color1 = (1, 0.76, 0)  # Yellow
# #color2 = (0.07, 0.27, 0.37)  # Blue
# color2 = (0.08, 0.43, 0.58)  # Blue
# color3 = (0.99, 0.25, 0)  # Red

# color1 = (1, 1, 0)  # Yellow
# color2 = (0, 0, 1)  # Blue
# color3 = (1, 0, 0)  # Red

# color1 = (1, 0.2, 0.2)  # Red
# color2 = (0.2, 1, 0.2)  # Green
# color3 = (0.2, 0.2, 1)  # Blue

# From observablehq:
# color1 = hex_to_rgb("#fdd04d") # Yellow
# color2 = hex_to_rgb("#0067ba") # Blue
# color3 = hex_to_rgb("#de0026") # Red

color1 = hex_to_rgb("#fdd04d") # Yellow
color2 = hex_to_rgb("#0050bb")  # Blue
color3 = hex_to_rgb("#de0026") # Red


# Create a grid of points within the triangle
resolution = 100
triangle = np.array([
    [0, 0],
    [1, 0],
    [0.5, np.sqrt(3) / 2]
])


def barycentric_interpolate(triangle, p):
    A = triangle[0]
    B = triangle[1]
    C = triangle[2]
    v0 = B - A
    v1 = C - A
    v2 = p - A
    d00 = np.dot(v0, v0)
    d01 = np.dot(v0, v1)
    d11 = np.dot(v1, v1)
    d20 = np.dot(v2, v0)
    d21 = np.dot(v2, v1)
    denom = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1 - v - w
    return u, v, w


# Generate the plot
fig, ax = plt.subplots()
for i in range(resolution + 1):
    for j in range(resolution + 1 - i):
        u = i / resolution
        v = j / resolution
        w = 1 - u - v
        weights = [u, v, w]
        p = u * triangle[0] + v * triangle[1] + w * triangle[2]
        #interpolated_color = interpolate_colors_lab(color1, color2, color3, weights)
        interpolated_color = interpolate_colors_rgb(color1, color2, color3, weights)
        #interpolated_color = blend_with_gray(interpolated_color, weights)
        ax.plot(p[0], p[1], 'o', color=interpolated_color, markersize=3)

# Draw the triangle borders
ax.plot(*zip(*triangle, triangle[0]), color='k')

ax.set_aspect('equal')
ax.axis('off')
plt.show()