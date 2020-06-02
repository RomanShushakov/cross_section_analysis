# -*- coding: utf-8 -*-

import io
import matplotlib as mpl
from matplotlib.figure import Figure


def draw(x_coords, y_coords, current_stress, stress_description):

    max_stress, min_stress = max(current_stress), min(current_stress)
    cmap = mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=min_stress, vmax=max_stress)

    analyzed_section = Figure()

    ax = analyzed_section.subplots()

    for i, j, k in zip(x_coords, y_coords, current_stress):
        ax.plot([i], [j], marker='s', color=cmap(norm(k)))

    analyzed_section.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, format='%.2f',
                              boundaries=sorted(current_stress), label='stress')

    ax.set_aspect('equal', 'box')
    ax.set_title(f'stress contour plot - {stress_description}')
    ax.set_xlabel(f'max stress: {max_stress:.2f}, min stress: {min_stress:.2f}')

    image = io.BytesIO()
    analyzed_section.savefig(image, fmt='png')
    image.seek(0)

    return image
