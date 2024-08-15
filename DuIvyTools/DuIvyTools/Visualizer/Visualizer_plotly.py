"""
Visualizer_plotly module is part of DuIvyTools providing basic visualization tools based on plotly.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
import json
from typing import Tuple

import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

base = os.path.dirname(os.path.realpath(os.path.join(__file__, "..")))
if base not in sys.path:
    sys.path.insert(0, base)

from utils import log


class ParentPlotly(log):
    """parent class of plotly visualizer class"""

    def __init__(self):
        self.load_style()
        self.figure = go.Figure()
        self.nticks: int = 7  # for tick location by hand

    def hex2rgb(self, hex: str) -> Tuple[float]:
        """convert hex color #FF00FF to rgb tuple form rgb(255, 0, 255)"""
        hex = hex.lstrip("#")
        res = tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
        res = f"rgb({res[0]},{res[1]},{res[2]})"
        return res

    def get_color(self, id: int) -> str:
        """colorcycle is by colorway in templates"""
        colors = pio.templates[self.templates_name].layout.colorway
        if colors == None:
            colors = [
                "#38A7D0",
                "#F67088",
                "#66C2A5",
                "#FC8D62",
                "#8DA0CB",
                "#E78AC3",
                "#A6D854",
                "#FFD92F",
                "#E5C494",
                "#B3B3B3",
                "#66C2A5",
                "#FC8D62",
            ]
        res = colors[id % len(colors)]

        if res[0] == "#" and len(res) == 7:
            res = self.hex2rgb(res)
        elif res.startswith("rgb(") and res.endswith(")"):
            pass
        else:
            self.error(
                "DIT plotly engine can only accept colors in hex or rgb form, like: '#F67088' or 'rgb(76, 114, 176)'. {res} is not supported."
            )
        return res

    def set_templates(self, name: str, filename: str) -> None:
        """set the templates to pio.templates"""
        plotly_templates_names = [
            "ggplot2",
            "seaborn",
            "simple_white",
            "plotly",
            "plotly_white",
            "plotly_dark",
            "presentation",
            "xgridoff",
            "ygridoff",
            "gridon",
            "none",
        ]
        if name in plotly_templates_names:
            self.error(
                f"The name {name} is not allowed. Change the file name of your template."
            )
        try:
            with open(filename, "r") as fo:
                template = json.load(fo)
        except Exception as err:
            self.error(
                f"unable to load plotly style template file {filename} by json, check the format of your file. \n"
                + err
            )
        pio.templates[name] = template

    def load_style(self):
        """load default or user-defined templates"""

        templates_files = [file for file in os.listdir() if file[-5:] == ".json"]
        if len(templates_files) == 1:
            name = templates_files[0][:-5]
            self.set_templates(name, templates_files[0])
            self.info(f"using plotly style template from {templates_files[0]}")
        elif len(templates_files) > 1:
            name = templates_files[0][:-5]
            self.set_templates(name, templates_files[0])
            self.info(
                f"more than one plotly style templates detected, using the {templates_files[0]}"
            )
        else:
            data_file_path = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__), "../")
            )
            dit_template = os.path.join(
                data_file_path, os.path.join("data", "plotlystyle", "DIT.json")
            )
            name = "DIT"
            self.set_templates(name, dit_template)
            self.info(
                "using default plotly style template, to inspect its content, use 'dit show_style -eg plotly'"
            )

        pio.templates.default = name
        self.templates_name = name

    def final(self, outfig: str, noshow: bool) -> None:
        """do final process of drawing figure with plotly

        Args:
            outfig (str): the user specified output figure name
            noshow (bool): True for no display the figure
        """
        if outfig != None:
            self.warn("unable to save figure by DIT, please save figure by yourself")
        if noshow == False:
            self.figure.show()

    def set_xyprecision_xyt_label(self, **kwargs) -> None:
        """set x_precision, y_precision, xlabel, ylabel, title"""
        self.figure.update_layout(
            title=kwargs["title"],
            xaxis_title=kwargs["xlabel"],
            yaxis_title=kwargs["ylabel"],
        )
        if kwargs["x_precision"] != None:
            self.figure.update_layout(xaxis_tickformat=f".{kwargs['x_precision']}f")
        if kwargs["y_precision"] != None:
            self.figure.update_layout(yaxis_tickformat=f".{kwargs['y_precision']}f")
        if kwargs["x_numticks"] != None or kwargs["y_numticks"] != None:
            self.warn("unable to set x_numticks and y_numticks on plotly, set it by plotly json template: tickvals and ticktext")

    def set_xytick_precision_xyt_label(self, **kwargs) -> None:
        """set Y tick, precision, Y tick, precision, xlabel, ylabel, title"""
        x_nticks = (self.nticks, kwargs["x_numticks"])[kwargs["x_numticks"] != None]
        y_nticks = (self.nticks, kwargs["y_numticks"])[kwargs["y_numticks"] != None]
        if kwargs["x_precision"] == None:
            kwargs["x_precision"] = 1
        if kwargs["y_precision"] == None:
            kwargs["y_precision"] = 1
        step = len(kwargs["xdata_list"]) // x_nticks
        step = [step, 1][step == 0]
        xdata_index = [i for i in range(0, len(kwargs["xdata_list"]), step)]
        step = len(kwargs["ydata_list"]) // y_nticks
        step = [step, 1][step == 0]
        ydata_index = [i for i in range(0, len(kwargs["ydata_list"]), step)]
        self.figure.update_xaxes(
            tickvals=xdata_index,
            ticktext=[
                f"{kwargs['xdata_list'][x]:.{kwargs['x_precision']}f}"
                for x in xdata_index
            ],
        )
        self.figure.update_yaxes(
            tickvals=ydata_index,
            ticktext=[
                f"{kwargs['ydata_list'][y]:.{kwargs['y_precision']}f}"
                for y in ydata_index
            ],
        )
        self.figure.update_layout(
            title=kwargs["title"],
            xaxis_title=kwargs["xlabel"],
            yaxis_title=kwargs["ylabel"],
        )

    def set_xy_min_max(self, **kwargs) -> None:
        """set xmin, xmax, ymin, ymax"""
        if kwargs["xmin"] != None or kwargs["xmax"] != None:
            self.figure.update_layout(xaxis_range=[kwargs["xmin"], kwargs["xmax"]])
        if kwargs["ymin"] != None or kwargs["ymax"] != None:
            self.figure.update_layout(yaxis_range=[kwargs["ymin"], kwargs["ymax"]])

    def check_repeat_values(self, values) -> bool:
        """True for repeat values exists in values"""
        if len(list(set(values))) < len(values):
            return True  # for repeat values
        else:
            return False

    def check_XY_repeat(self, **kwargs) -> bool:
        """True for repeat values exists in xdata_list or ydata_list"""
        if self.check_repeat_values(kwargs["xdata_list"]):
            return True
        if self.check_repeat_values(kwargs["ydata_list"]):
            return True
        return False


class LinePlotly(ParentPlotly):
    """A plotly line plot class for line plots

    Args:
        Parentplotly (object): plotly parent class

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
        highs :List[List[float]]
        lows :List[List[float]]
        origins :List[List[float]]
        alpha :float
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for i, data in enumerate(kwargs["data_list"]):
            self.figure.add_trace(
                go.Scatter(
                    x=kwargs["xdata_list"][i],
                    y=data,
                    name=kwargs["legends"][i],
                    line=dict(color=self.get_color(i)),
                    showlegend=(kwargs["legends"][i] != ""),
                )
            )
            if len(kwargs["highs"]) != 0 and len(kwargs["lows"]) != 0:
                rgb = self.get_color(i)
                rgba = f"rgba({rgb[4:-1]},{kwargs['alpha']})"
                self.figure.add_trace(
                    go.Scatter(
                        name=f"""high-{kwargs["legends"][i]}""",
                        x=kwargs["xdata_list"][i],
                        y=kwargs["highs"][i],
                        line=dict(width=0, color=rgba),
                        showlegend=False,
                    )
                )
                self.figure.add_trace(
                    go.Scatter(
                        name=f"""low-{kwargs["legends"][i]}""",
                        x=kwargs["xdata_list"][i],
                        y=kwargs["lows"][i],
                        fillcolor=rgba,
                        fill="tonexty",
                        line=dict(width=0, color=rgba),
                        showlegend=False,
                    )
                )
            if "origins" in kwargs and len(kwargs["origins"]) != 0:
                rgb = self.get_color(i)
                rgba = f"rgba({rgb[4:-1]},{kwargs['alpha']})"
                self.figure.add_trace(
                    go.Scatter(
                        x=kwargs["xdata_list"][i],
                        y=kwargs["origins"][i],
                        line=dict(color=rgba),
                        showlegend=False,
                    )
                )


        self.set_xyprecision_xyt_label(**kwargs)
        self.set_xy_min_max(**kwargs)


class StackPlotly(ParentPlotly):
    """A plotly line plot class for line plots

    Args:
        Parentplotly (object): plotly parent class

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
        highs :List[List[float]]
        lows :List[List[float]]
        alpha :float
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        kwargs["data_list"].reverse()  # first in, show at bottom
        kwargs["legends"].reverse()  # reverse as data
        for i, data in enumerate(kwargs["data_list"]):
            rgb = self.get_color(i)
            rgba = f"rgba({rgb[4:-1]},{kwargs['alpha']})"
            self.figure.add_trace(
                go.Scatter(
                    x=kwargs["xdata_list"][i],
                    y=data,
                    name=kwargs["legends"][i],
                    stackgroup="stack",
                    fillcolor=rgba,
                    fill="tonexty",
                    line=dict(width=0, color=rgba),
                )
            )

        self.set_xyprecision_xyt_label(**kwargs)
        self.set_xy_min_max(**kwargs)


class ScatterPlotly(ParentPlotly):
    """A plotly scatter plot class for scatter plots

    Args:
        ParentPlotly (object): plotly parent class

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
        alpha
        cmap :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for i, data in enumerate(kwargs["data_list"]):
            colors = kwargs["color_list"][i]
            if colors != None:
                self.figure.add_trace(
                    go.Scatter(
                        x=kwargs["xdata_list"][i],
                        y=data,
                        mode="markers",
                        name=kwargs["legends"][i],
                        showlegend=(len(kwargs["legends"]) > 1),
                        marker=dict(
                            colorbar={
                                "title": {"text": kwargs["zlabel"]},
                                "tickformat": f".{kwargs['z_precision']}f",
                            },
                            opacity=kwargs["alpha"],
                            color=colors,
                            colorscale=kwargs["cmap"],
                            symbol=i,
                        ),
                    )
                )
            else:
                self.figure.add_trace(
                    go.Scatter(
                        x=kwargs["xdata_list"][i],
                        y=data,
                        mode="markers",
                        name=kwargs["legends"][i],
                        showlegend=(len(kwargs["legends"]) > 1),
                        marker=dict(
                            opacity=kwargs["alpha"],
                            symbol=i,
                        ),
                    )
                )
        self.set_xyprecision_xyt_label(**kwargs)
        self.set_xy_min_max(**kwargs)


class BarPlotly(ParentPlotly):
    """A plotly bar plot class for bar plots

    Args:
        ParentPlotly (object): matplotlib parent class

    Parameters:
        data_list :List[List[float]]
        stds_list :List[List[float]]
        xtitles :List[str]
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
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        for i, data in enumerate(kwargs["data_list"]):
            self.figure.add_trace(
                go.Bar(
                    x=[x for x in range(len(data))],
                    y=data,
                    name=kwargs["legends"][i],
                    error_y=dict(
                        type="data",
                        array=kwargs["stds_list"][i],
                        width=10,
                        visible=True,
                    ),
                )
            )
        self.figure.update_xaxes(
            tickvals=[i for i in range(len(kwargs["data_list"]))],
            ticktext=kwargs["xtitles"],
        )

        self.figure.update_layout(barmode="group")
        self.set_xyprecision_xyt_label(**kwargs)
        self.set_xy_min_max(**kwargs)


class BoxPlotly(ParentPlotly):
    """A plotly box plot class for box plots

    Args:
        ParentPlotly (object): Plotly parent class

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
        mode :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        loc = 1.0
        if kwargs["mode"] != "withoutScatter":
            loc = 0.75
            for i, data in enumerate(kwargs["data_list"]):
                self.figure.add_trace(
                    go.Scatter(
                        x=np.random.normal(i + 1.25, 0.04, len(data)),
                        y=data,
                        mode="markers",
                        showlegend=False,
                        marker=dict(
                            colorbar={
                                "title": {"text": kwargs["zlabel"]},
                                "tickformat": f".{kwargs['z_precision']}f",
                            },
                            opacity=kwargs["alpha"],
                            color=kwargs["color_list"][i],
                            colorscale=kwargs["cmap"],
                            symbol=0,
                        ),
                    )
                )

        for i, data in enumerate(kwargs["data_list"]):
            self.figure.add_trace(
                go.Violin(
                    x=[i + loc for _ in data],
                    y=data,
                    x0=kwargs["legends"][i],
                    box_visible=True,
                    meanline_visible=True,
                    showlegend=False,
                )
            )
        self.figure.update_xaxes(
            tickvals=[i + 1 for i in range(len(kwargs["data_list"]))],
            ticktext=kwargs["legends"],
        )
        self.set_xyprecision_xyt_label(**kwargs)
        self.set_xy_min_max(**kwargs)


class RamachandranPlotly(ParentPlotly):
    """A Plotly ramachandran plot class for ramachandran plots

    Args:
        ParentPlotly (object): plotly parent class

    Parameters:
        normals :Dict[Dict[List[float|str]]]
        outliers :Dict[Dict[List[float|str]]]
        rama_pref_values :List[List[float]]
        rama_preferences :Dict[Dict[str:str|List]]
        xlabel :str
        ylabel :str
        title :str
        outfig :str
        noshow :bool
    """

    def __init__(self, **kwargs) -> None:

        ## draw ramachandran plot
        normals = kwargs["normals"]
        outliers = kwargs["outliers"]
        rama_pref_values = kwargs["rama_pref_values"]
        rama_preferences = kwargs["rama_preferences"]
        outfig = kwargs["outfig"]
        noshow = kwargs["noshow"]
        for key in ["General", "GLY", "Pre-PRO", "PRO"]:
            self.figure = go.Figure()
            if len(normals[key]["phi"]) + len(outliers[key]["phi"]) == 0:
                continue
            bounds = rama_preferences[key]["bounds"]
            cmap = rama_preferences[key]["cmap"]
            colorscale = [[b, c] for b, c in zip(bounds, cmap)]
            colorscale += [[bounds[-1], cmap[-1]]]
            self.figure.add_trace(
                go.Heatmap(
                    x=[x - 180 for x in range(361)],
                    y=[y - 180 for y in range(361)],
                    z=rama_pref_values[key],
                    colorscale=colorscale,
                    showscale=False,
                    name="Probability",
                )
            )
            self.figure.add_trace(
                go.Scatter(
                    x=normals[key]["phi"],
                    y=normals[key]["psi"],
                    mode="markers",
                    name=f"normals (>{bounds[1]})",
                    hovertext=normals[key]["res"],
                    hoverinfo="text",
                    marker=dict(
                        color="#38A7D0",
                    ),
                )
            )
            self.figure.add_trace(
                go.Scatter(
                    x=outliers[key]["phi"],
                    y=outliers[key]["psi"],
                    mode="markers",
                    name=f"outliers (<{bounds[1]})",
                    hovertext=outliers[key]["res"],
                    hoverinfo="text",
                    marker=dict(
                        color="#F67088",
                    ),
                )
            )
            if kwargs["title"] == None:
                title = key
            else:
                title = kwargs["title"]
            self.figure.update_layout(
                xaxis_range=[-180, 180],
                yaxis_range=[-180, 180],
            )
            self.figure.update_layout(
                title=title,
                xaxis_title=kwargs["xlabel"],
                yaxis_title=kwargs["ylabel"],
            )
            if kwargs["x_precision"] != None:
                self.figure.update_layout(xaxis_tickformat=f".{kwargs['x_precision']}f")
            if kwargs["y_precision"] != None:
                self.figure.update_layout(yaxis_tickformat=f".{kwargs['y_precision']}f")

            if outfig != None:
                self.warn(
                    "unable to save figure by DIT, please save figure by yourself"
                )
            if noshow == False:
                self.figure.show()


class PcolormeshPlotly(ParentPlotly):
    """A plotly pcolormesh plot class for heatmap

    Args:
        ParentPlotly (object): plotly parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[float]
        ydata_list :List[float]
        legends :List[str]
        color_list :List[str]
        xlabel :str
        ylabel :str
        zlabel :str
        title :str
        x_precision :int
        y_precision :int
        z_precision :int
        cmap :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        if kwargs["fig_type"] != "Continuous":
            colorscale, tickvals, length = [], [], len(kwargs["legends"])
            for i in range(length):  ## using original colors
                colorscale.append([i / length, kwargs["color_list"][i]])
                colorscale.append([(i + 1) / length, kwargs["color_list"][i]])
            for i in range(length):
                tickvals.append((i + 0.5) / length * (length - 1))

            if not self.check_XY_repeat(**kwargs):
                self.figure.add_trace(
                    go.Heatmap(
                        x=kwargs["xdata_list"],
                        y=kwargs["ydata_list"],
                        z=kwargs["data_list"],
                        colorscale=colorscale,
                        colorbar={
                            "title": {"text": kwargs["zlabel"]},
                            "ticktext": kwargs["legends"],
                            "tickvals": tickvals,
                        },
                    )
                )
                self.set_xyprecision_xyt_label(**kwargs)
            else:
                self.figure.add_trace(
                    go.Heatmap(
                        z=kwargs["data_list"],
                        colorscale=colorscale,
                        colorbar={
                            "title": {"text": kwargs["zlabel"]},
                            "ticktext": kwargs["legends"],
                            "tickvals": tickvals,
                        },
                    )
                )
                self.set_xytick_precision_xyt_label(**kwargs)
        else:
            if not self.check_XY_repeat(**kwargs):
                self.figure.add_trace(
                    go.Heatmap(
                        x=kwargs["xdata_list"],
                        y=kwargs["ydata_list"],
                        z=kwargs["data_list"],
                        colorscale=kwargs["cmap"],
                        colorbar={
                            "title": {"text": kwargs["zlabel"]},
                            "tickformat": f".{kwargs['z_precision']}f",
                        },
                    )
                )
                self.set_xyprecision_xyt_label(**kwargs)
            else:
                self.figure.add_trace(
                    go.Heatmap(
                        z=kwargs["data_list"],
                        colorscale=kwargs["cmap"],
                        colorbar={
                            "title": {"text": kwargs["zlabel"]},
                            "tickformat": f".{kwargs['z_precision']}f",
                        },
                    )
                )
                self.set_xytick_precision_xyt_label(**kwargs)


class ThreeDimensionPlotly(ParentPlotly):
    """A plotly 3d plot class for heatmap

    Args:
        ParentPlotly (object): plotly parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[float]
        ydata_list :List[float]
        legends :List[str]
        color_list :List[str]
        xlabel :str
        ylabel :str
        zlabel :str
        title :str
        x_precision :int
        y_precision :int
        z_precision :int
        cmap :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        if len(kwargs["data_list"]) <= 1 or len(kwargs["data_list"][0]) <= 1:
            self.error("!!! 3d plot unable to proper deal with 1 dimension data !!!")

        if not self.check_XY_repeat(**kwargs):
            self.figure.add_trace(
                go.Surface(
                    x=kwargs["xdata_list"],
                    y=kwargs["ydata_list"],
                    z=kwargs["data_list"],
                    colorscale=kwargs["cmap"],
                    colorbar={
                        "title": {"text": kwargs["zlabel"]},
                        "tickformat": f".{kwargs['z_precision']}f",
                    },
                )
            )
            self.figure.update_layout(
                title=kwargs["title"],
                scene=dict(
                    xaxis=dict(
                        title=kwargs["xlabel"],
                    ),
                    yaxis=dict(
                        title=kwargs["ylabel"],
                    ),
                    zaxis=dict(
                        title=kwargs["zlabel"],
                    ),
                ),
            )
            self.figure.update_traces(
                contours_z=dict(show=True, usecolormap=True, project_z=True)
            )
            if kwargs["x_precision"] != None:
                self.figure.update_scenes(xaxis_tickformat=f".{kwargs['x_precision']}f")
            if kwargs["y_precision"] != None:
                self.figure.update_scenes(yaxis_tickformat=f".{kwargs['y_precision']}f")
            if kwargs["z_precision"] != None:
                self.figure.update_scenes(zaxis_tickformat=f".{kwargs['z_precision']}f")
        else:
            self.figure.add_trace(
                go.Surface(
                    z=kwargs["data_list"],
                    colorscale=kwargs["cmap"],
                    colorbar={
                        "title": {"text": kwargs["zlabel"]},
                        "tickformat": f".{kwargs['z_precision']}f",
                    },
                )
            )
            self.figure.update_layout(
                title=kwargs["title"],
                scene=dict(
                    xaxis=dict(
                        title=kwargs["xlabel"],
                    ),
                    yaxis=dict(
                        title=kwargs["ylabel"],
                    ),
                    zaxis=dict(
                        title=kwargs["zlabel"],
                    ),
                ),
            )
            self.figure.update_traces(
                contours_z=dict(show=True, usecolormap=True, project_z=True)
            )
            x_nticks = (self.nticks, kwargs["x_numticks"])[kwargs["x_numticks"] != None]
            y_nticks = (self.nticks, kwargs["y_numticks"])[kwargs["y_numticks"] != None]
            step = len(kwargs["xdata_list"]) // x_nticks
            step = [step, 1][step == 0]
            xdata_index = [i for i in range(0, len(kwargs["xdata_list"]), step)]
            step = len(kwargs["ydata_list"]) // y_nticks
            step = [step, 1][step == 0]
            ydata_index = [i for i in range(0, len(kwargs["ydata_list"]), step)]
            if kwargs["x_precision"] != None:
                self.figure.update_scenes(
                    xaxis_tickvals=xdata_index,
                    xaxis_ticktext=[
                        f"{kwargs['xdata_list'][x]:.{kwargs['x_precision']}f}"
                        for x in xdata_index
                    ],
                )
            if kwargs["y_precision"] != None:
                self.figure.update_scenes(
                    yaxis_tickvals=ydata_index,
                    yaxis_ticktext=[
                        f"{kwargs['ydata_list'][y]:.{kwargs['y_precision']}f}"
                        for y in ydata_index
                    ],
                )
            if kwargs["z_precision"] != None:
                self.figure.update_scenes(zaxis_tickformat=f".{kwargs['z_precision']}f")


class ContourPlotly(ParentPlotly):
    """A plotly contour plot class for heatmap

    Args:
        ParentPlotly (object): plotly parent class

    Parameters:
        data_list :List[List[float]]
        xdata_list :List[float]
        ydata_list :List[float]
        legends :List[str]
        color_list :List[str]
        xlabel :str
        ylabel :str
        zlabel :str
        title :str
        x_precision :int
        y_precision :int
        z_precision :int
        cmap :str
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

        if len(kwargs["data_list"]) <= 1 or len(kwargs["data_list"][0]) <= 1:
            self.error("!!! contour unable to proper deal with 1 dimension data !!!")

        if not self.check_XY_repeat(**kwargs):
            self.figure.add_trace(
                go.Contour(
                    x=kwargs["xdata_list"],
                    y=kwargs["ydata_list"],
                    z=kwargs["data_list"],
                    colorscale=kwargs["cmap"],
                    colorbar={
                        "title": {"text": kwargs["zlabel"]},
                        "tickformat": f".{kwargs['z_precision']}f",
                    },
                    contours=dict(showlines=False),
                )
            )
            self.set_xyprecision_xyt_label(**kwargs)
        else:
            self.figure.add_trace(
                go.Contour(
                    z=kwargs["data_list"],
                    colorscale=kwargs["cmap"],
                    colorbar={
                        "title": {"text": kwargs["zlabel"]},
                        "tickformat": f".{kwargs['z_precision']}f",
                    },
                    contours=dict(showlines=False),
                )
            )
            self.set_xytick_precision_xyt_label(**kwargs)
