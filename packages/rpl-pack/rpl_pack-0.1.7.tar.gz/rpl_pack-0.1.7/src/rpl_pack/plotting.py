"""
Convenient plotting tools.

"""


from typing import Any

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText


class _PlotBase:
    """Base class for plotting."""
    def __init__(self):
        pass


class Plot(_PlotBase):
    """Base class for all plotting classes.
    
    A simple plotting interface that includes some basic plots
    with configuration.
    """
    def __init__(self):
        super().__init__()
        self.defaults = {}


# def compare_plot(prop_data: dict, data: list, ylabels: list = [], xvar: str = 'temp',
#                  yvars: list = ['Vw'], suptitle: str = '',
#                  legend_title: str = '', show: bool = False):
#     """A plot to compare multiple data with the same x values."""
#     fig, axs = plt.subplots(len(yvars), 1, squeeze=False, sharex=True)
#     plt.subplots_adjust(right=0.80)
#     x = prop_data[xvar]
#     for i, yvar in enumerate(yvars):
#         for j, d in enumerate(data):
#             y = d[yvar]
#             axs[i, 0].plot(x, y, label=ylabels[j])
#         axs[i, 0].set_ylabel(yvar)
#     axs[-1, 0].set_xlabel(xvar)
#     if suptitle:
#         fig.suptitle(suptitle)
#     handles, labels = axs[-1, 0].get_legend_handles_labels()
#     by_label = dict(zip(labels, handles))
#     fig.legend(by_label.values(), by_label.keys(),
#                title=legend_title, frameon=True,
#                bbox_to_anchor=(0.475, 0.25, 0.5, 0.5), loc='center right')
#     if show:
#         plt.show()