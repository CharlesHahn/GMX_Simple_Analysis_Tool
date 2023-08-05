"""
Visualizer_matplotlib module is part of DuIvyTools providing basic visualization tools based on matplotlib.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
import time
from typing import List, Union

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import colors as mplcolors
from matplotlib.ticker import AutoLocator, FormatStrFormatter

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import log


class ParentMatplotlib(log):
    """parent class for drawing figure by matplotlib"""

    def __init__(self):
        self.load_style()
        self.figure = plt.figure()

    def load_style(self):
        """load matplotlib style file"""
        style_files = [file for file in os.listdir() if file[-9:] == ".mplstyle"]
        if len(style_files) == 1:
            plt.style.use(style_files[0])
            self.info(f"using matplotlib style sheet from {style_files[0]}")
        elif len(style_files) > 1:
            plt.style.use(style_files[0])
            self.info(
                f"more than one mplstyle files detected, using the {style_files[0]}"
            )
        else:
            data_file_path = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__), "../")
            )
            mplstyle = os.path.join(
                data_file_path, os.path.join("data", "DIT.mplstyle")
            )
            plt.style.use(mplstyle)
            self.info(
                "using default matplotlib style sheet, to inspect its content, use 'dit show_style'"
            )

    def final(self, outfig: str, noshow: bool) -> None:
        """do final process of drawing figure with matplotlib

        Args:
            outfig (str): the user specified output figure name
            noshow (bool): True for no display the figure
        """
        plt.tight_layout()
        if outfig != None:
            if os.path.exists(outfig):
                time_info = time.strftime("%Y%m%d%H%M%S", time.localtime())
                new_outfig = f'{".".join(outfig.split(".")[:-1])}_{time_info}.{outfig.split(".")[-1]}'
                self.warn(
                    f"{outfig} is already in current directory, save to {new_outfig} for instead."
                )
                outfig = new_outfig
            self.figure.savefig(outfig)
            self.info(f"save figure to {outfig} successfully")
        if noshow == False:
            plt.show()


class LineMatplotlib(ParentMatplotlib):
    """A matplotlib line plot class for line plots

    Args:
        ParentMatplotlib (object): matplotlib parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[List[float]]
        legends :List[str]
        xmin :float
        xmax :flaot
        ymin :float
        ymax :float
        xlabel :str
        ylabel :str
        title :str
        x_precision :int
        y_precision :int
        # optional
        highs :List[List[float]]
        lows :List[List[float]]
        alpha :float
        legend_location:str #{inside, outside}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for i, data in enumerate(kwargs["data_list"]):
            if len(kwargs["highs"]) != 0 and len(kwargs["lows"]) != 0:
                plt.fill_between(
                    kwargs["xdata_list"][i],
                    kwargs["highs"][i],
                    kwargs["lows"][i],
                    alpha=kwargs["alpha"],
                )
            plt.plot(kwargs["xdata_list"][i], data, label=kwargs["legends"][i])

        if kwargs["xmin"] != None or kwargs["xmax"] != None:
            plt.xlim(kwargs["xmin"], kwargs["xmax"])
        if kwargs["ymin"] != None or kwargs["ymax"] != None:
            plt.ylim(kwargs["ymin"], kwargs["ymax"])

        ax = plt.gca()
        if kwargs["x_precision"] != None:
            x_p = kwargs["x_precision"]
            ax.xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_p}f"))
        if kwargs["y_precision"] != None:
            y_p = kwargs["y_precision"]
            ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_p}f"))

        if kwargs["legend_location"] == "outside":
            ## TODO hard code the legend location???
            plt.legend(bbox_to_anchor=(1.02, 1.00), loc="upper left")
        else:
            plt.legend()
        plt.xlabel(kwargs["xlabel"])
        plt.ylabel(kwargs["ylabel"])
        plt.title(kwargs["title"])


class ScatterMatplotlib(ParentMatplotlib):
    """A matplotlib scatter plot class for scatter plots

    Args:
        ParentMatplotlib (object): matplotlib parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[List[float]]
        color_list :List[List[float]]
        legends :List[str]
        xmin :float
        xmax :flaot
        ymin :float
        ymax :float
        zmin :float
        zmax :float
        xlabel :str
        ylabel :str
        zlabel :str
        title :str
        x_precision :int
        y_precision :int
        z_precision :int
        cmap :str
        colorbar_location:str
        legend_location:str #{inside, outside}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        ## TODO think again, user to define marker by scatter.marker
        marker_list = [
            "o",
            "v",
            "^",
            "<",
            ">",
            "8",
            "s",
            "p",
            "*",
            "h",
            ".",
            "H",
            "D",
            "d",
            "P",
            "X",
        ]
        for i, data in enumerate(kwargs["data_list"]):
            plt.scatter(
                kwargs["xdata_list"][i],
                data,
                c=kwargs["color_list"][i],
                label=kwargs["legends"][i],
                marker=marker_list[i],
                cmap=kwargs["cmap"],
            )
        if kwargs["z_precision"] != None:
            plt.colorbar(
                label=kwargs["zlabel"],
                format=FormatStrFormatter(f"""%.{kwargs["z_precision"]}f"""),
                location=kwargs["colorbar_location"],
            )
        else:
            plt.colorbar(
                label=kwargs["zlabel"],
                location=kwargs["colorbar_location"],
            )

        if kwargs["xmin"] != None or kwargs["xmax"] != None:
            plt.xlim(kwargs["xmin"], kwargs["xmax"])
        if kwargs["ymin"] != None or kwargs["ymax"] != None:
            plt.ylim(kwargs["ymin"], kwargs["ymax"])

        ax = plt.gca()
        if kwargs["x_precision"] != None:
            x_p = kwargs["x_precision"]
            ax.xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_p}f"))
        if kwargs["y_precision"] != None:
            y_p = kwargs["y_precision"]
            ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_p}f"))

        if kwargs["legend_location"] == "outside":
            plt.legend(bbox_to_anchor=(1.02, 1.00), loc="upper left")
        else:
            plt.legend()
        plt.xlabel(kwargs["xlabel"])
        plt.ylabel(kwargs["ylabel"])
        plt.title(kwargs["title"])


class StackMatplotlib(ParentMatplotlib):
    """A matplotlib stack line plot class for stack line plots

    Args:
        ParentMatplotlib (object): matplotlib parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[List[float]]
        legends :List[str]
        xmin :float
        xmax :flaot
        ymin :float
        ymax :float
        xlabel :str
        ylabel :str
        title :str
        x_precision :int
        y_precision :int
        # optional
        highs :List[List[float]]
        lows :List[List[float]]
        alpha :float
        legend_location:str #{inside, outside}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for i, _ in enumerate(kwargs["data_list"]):
            plt.fill_between(
                kwargs["xdata_list"][i],
                kwargs["highs"][i],
                kwargs["lows"][i],
                alpha=kwargs["alpha"],
                label=kwargs["legends"][i],
            )

        if kwargs["xmin"] != None or kwargs["xmax"] != None:
            plt.xlim(kwargs["xmin"], kwargs["xmax"])
        if kwargs["ymin"] != None or kwargs["ymax"] != None:
            plt.ylim(kwargs["ymin"], kwargs["ymax"])

        ax = plt.gca()
        if kwargs["x_precision"] != None:
            x_p = kwargs["x_precision"]
            ax.xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_p}f"))
        if kwargs["y_precision"] != None:
            y_p = kwargs["y_precision"]
            ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_p}f"))

        if kwargs["legend_location"] == "outside":
            plt.legend(bbox_to_anchor=(1.02, 1.00), loc="upper left")
        else:
            plt.legend()
        plt.xlabel(kwargs["xlabel"])
        plt.ylabel(kwargs["ylabel"])
        plt.title(kwargs["title"])


class BarMatplotlib(ParentMatplotlib):
    def __init__(self, **kwargs) -> None:
        super().__init__()


class BoxMatplotlib(ParentMatplotlib):
    """A matplotlib box plot class for box plots

    Args:
        ParentMatplotlib (object): matplotlib parent class

    Parameters:
        data_list :List[List[float]]
        color_list :List[List[float]]
        legends :List[str]
        xmin :float
        xmax :flaot
        ymin :float
        ymax :float
        xlabel :str
        ylabel :str
        zlabel :str
        title :str
        x_precision :int
        y_precision :int
        z_precision :int
        alpha :float
        cmap :str
        colorbar_location:str
        mode :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        ## scatter
        loc = 1.0
        if kwargs["mode"] != "withoutScatter":
            loc = 0.8
            for i, data in enumerate(kwargs["data_list"]):
                plt.scatter(
                    np.random.normal(i + 1.20, 0.04, len(data)),
                    data,
                    alpha=kwargs["alpha"],
                    c=kwargs["color_list"][i],
                    cmap=kwargs["cmap"],
                )
            if kwargs["z_precision"] != None:
                plt.colorbar(
                    label=kwargs["zlabel"],
                    format=FormatStrFormatter(f"""%.{kwargs["z_precision"]}f"""),
                    location=kwargs["colorbar_location"],
                )
            else:
                plt.colorbar(
                    label=kwargs["zlabel"],
                    location=kwargs["colorbar_location"],
                )

        box_positions = [i + loc for i in range(len(kwargs["data_list"]))]
        plt.boxplot(
            kwargs["data_list"],
            sym=".",
            meanline=True,
            showmeans=True,
            patch_artist=True,
            notch=True,
            positions=box_positions,
        )
        plt.xticks([i + 1 for i in range(len(kwargs["data_list"]))], kwargs["legends"])

        if kwargs["xmin"] != None or kwargs["xmax"] != None:
            plt.xlim(kwargs["xmin"], kwargs["xmax"])
        if kwargs["ymin"] != None or kwargs["ymax"] != None:
            plt.ylim(kwargs["ymin"], kwargs["ymax"])

        ax = plt.gca()
        if kwargs["x_precision"] != None:
            x_p = kwargs["x_precision"]
            ax.xaxis.set_major_formatter(FormatStrFormatter(f"%.{x_p}f"))
        if kwargs["y_precision"] != None:
            y_p = kwargs["y_precision"]
            ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{y_p}f"))

        plt.xlabel(kwargs["xlabel"])
        plt.ylabel(kwargs["ylabel"])
        plt.title(kwargs["title"])


class ViolinMatplotlib(ParentMatplotlib):
    def __init__(self, **kwargs) -> None:
        super().__init__()
