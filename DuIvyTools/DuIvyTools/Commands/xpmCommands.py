"""
xpmCommander module is part of DuIvyTools providing xpm related commands.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
from typing import List, Union

from scipy.interpolate import RectBivariateSpline, interp2d

base = os.path.dirname(os.path.realpath(os.path.join(__file__, "..")))
if base not in sys.path:
    sys.path.insert(0, base)

from Commands.Commands import Command
from FileParser.xpmParser import XPM
from utils import Parameters
from Visualizer.Visualizer_gnuplot import *
from Visualizer.Visualizer_matplotlib import *
from Visualizer.Visualizer_plotext import *
from Visualizer.Visualizer_plotly import *


class xpm_show(Command):
    """
    Visualize the xpm file.
    DIT support 4 plot engines (matplotlib, plotly, gnuplot, and plotext) and several modes to plot xpm into figures. 4 modes for matplotlib (imshow which is default, pcolormesh, 3d, and contour), and 3 modes for plotly and gnuplot (pcolormesh which is default, 3d, and contour). Plotext only support plotting simple and small size xpm in gray.
    Modes imshow and pcolormesh mainly show the matrix of xpm. For `Continuous` type xpms, matplotlib, plotly and gnuplot will NOT use its original colors, and the colormaps of each engine will be used. For matploblib and plotly, you can set colormaps by `-cmap`. For `Discrete` type of xpms, only pcolormesh of matploblib will NOT use its original colors. But you can set colors by mplstyle file or other style files.For the methods using its original colors, you can set colors by directly modifing the xpm file.
    Mode 3d mainly plot a 3d figure for `Continuous` xpm. Mode contour plot a contour figure for `Continuous` xpm. Also, you can set colormaps by `-cmap`.
    You can perform INTERPOLATION to data by specifing `-ip`.
    For imshow of matplotlib, the interpolation method was using the interpolation method of imshow function of matplobli, and there are lots of interpolation methods could be selected. If you do not know the names of interpolation methods, simply specify `-ip hhh`, then the error message will show you all names of interpolation methods for you to choose.
    For any other engines or modes, DIT use `scipy.interpolate.interp2d` to do the interpolation, so the methods for you to choose is `linear`, `cubic`, and `quintic`. Also, `-ip hhh` trick works. For this interpolation methods, you need to define a `--interpolation_fold` (default to 10).
    DIT support performing xpm cutting by `-xmin`, `-xmax`, `-ymin`, and `-ymax`, like only show 100*100 pixels from a 132*10000 DSSP xpm by setting `-xmin 100 -xmax 200 -ymin 200 -ymax 300`.

    :Parameters:
        -f, --input
                specify the input xpm file (or files)
        -o, --output (optional)
                specify the file name for saving figures
        -ns, --noshow (optional)
                whether not to show figures. When applied to gnuplot, DIT will generate a gnuplot input script
        -x, --xlabel (optional)
                specify the xlabel of figure
        -y, --ylabel (optional)
                specify the ylabel of figure
        -z, --zlabel (optional)
                specify the zlabel of figure
        -t, --title (optional)
                specify the title of figure
        -xs, --xshrink (optional)
                specify the shrink fold number of X values
        -ys, --yshrink (optional)
                specify the shrink fold number of Y values
        -zs, --zshrink (optional)
                specify the shrink fold number of Z values
        -xp, --xplus (optional)
                specify the addtion number of X values
        -yp, --yplus (optional)
                specify the addtion number of Y values
        -zp, --zplus (optional)
                specify the addtion number of Z values
        -xmin, --xmin (optional)
                specify the xmin index of xpm matrix to show
        -xmax, --xmax (optional)
                specify the xmax index of xpm matrix to show
        -ymin, --ymin (optional)
                specify the ymin index of xpm matrix to show
        -ymax, --ymax (optional)
                specify the ymax index of xpm matrix to show
        -zmin, --zmin (optional)
                specify the min value of colorbar to show
        -zmax, --zmax (optional)
                specify the max value of colorbar to show
        -m, --mode (optional)
                specify the mode of visualization: imshow, pcolormesh, 3d, contour
        -eg, --engine (optional)
                specify the plot engine: matplotlib (default), plotly, gnuplot, plotext
        -cmap, --colormap (optional)
                specify the colormap for visualization
        -ip, --interpolation (optional)
                specify the interpolation method
        -ipf, --interpolation_fold (optional)
                specify the multiple of interpolation
        --alpha (optional)
                specify the alpha of figure
        --x_precision (optional)
                specify the precision of X ticklabels
        --y_precision (optional)
                specify the precision of Y ticklabels
        --z_precision (optional)
                specify the precision of Z ticklabels
        --legend_location (optional)
                specify the location of legend, inside or outside
        --colorbar_location (optional)
                specify the location of colorbar, available for matplotlib: left, top, bottom, right

    :Usage:
        dit xpm_show -f FEL.xpm
        dit xpm_show -f hbond.xpm
        dit xpm_show -f DSSP.xpm -ns -o dssp.png
        dit xpm_show -f FEL.xpm -m pcolormesh -ip linear -ipf 5 -cmap solar
        dit xpm_show -f FEL.xpm -m 3d -x PC1 -y PC2 -z Energy -t FEL --alpha 0.5
        dit xpm_show -f FEL.xpm -m 3d --x_precision 1 --y_precision 2 --z_precision 0
        dit xpm_show -f FEL.xpm -m contour -cmap jet --colorbar_location bottom
        dit xpm_show -f FEL.xpm -m contour -cmap jet -zmin 0 -zmax 20
        dit xpm_show -f DSSP.xpm -xs 0.001 -x Time(ns) --legend_location outside
        dit xpm_show -f DSSP.xpm -eg plotly -xmin 1000 -xmax 2001 -ymin 50 -ymax 101
        dit xpm_show -f FEL.xpm -eg plotly -m 3d
        dit xpm_show -f FEL.xpm -eg plotly -m contour
        dit xpm_show -f DSSP.xpm -eg gnuplot --legend_location outside
        dit xpm_show -f FEL.xpm -eg gnuplot -m 3d -ip cubic
        dit xpm_show -f FEL.xpm -eg gnuplot -m contour -ns -o contour.png
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def calc_interpolation(
        self,
        xaxis: List[float],
        yaxis: List[float],
        matrix: List[List[float]],
        method: str,
        ip_fold: int,
    ) -> Union[List[float], List[List[float]]]:
        """perform the interpolation of matrix data

        Args:
            xaxis (List[float]): the X data
            yaxis (List[float]): the Y data
            matrix (List[List[float]]): the matrix values
            method (str): method for interpolation
            ip_fold (int): the multiple of interpolation

        Returns:
            x_new (List[float]): the X data after interpolation
            y_new (List[float]): the Y data after interpolation
            matrix_new (List[List[float]]): the matrix values after interpolation
        """
        # interp2d : linear, cubic, quintic
        ip_func = interp2d(xaxis, yaxis, matrix, kind=method)
        # ip_func = RectBivariateSpline(xaxis, yaxis, matrix)#, kx=3, ky=3)
        x_new = np.linspace(np.min(xaxis), np.max(xaxis), ip_fold * len(xaxis))
        y_new = np.linspace(np.min(yaxis), np.max(yaxis), ip_fold * len(yaxis))
        matrix_new = ip_func(x_new, y_new)
        return x_new, y_new, matrix_new

    def hex2rgb(self, value):
        value = value.lstrip("#")
        res = tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
        return res

    def image_split(
        self, xaxis: List[float], yaxis: List[float], value_matrix: List[List[float]]
    ) -> Union[List[float], List[List[float]]]:
        """image cutting by xmin, xmax, ymin, and ymax

        Args:
            xaxis (List[float]): xaxis data
            yaxis (List[float]): yaxis data
            value_matrix (List[List[float]]): image value matrix

        Returns:
            xaxis (List[float]): xaxis data after cutting
            yaxis (List[float]): yaxis data after cutting
            value_matrix (List[List[float]]): image value matrix after cutting
        """

        if self.parm.xmin != None and not isinstance(self.parm.xmin, int):
            self.parm.xmin = int(self.parm.xmin)
        if self.parm.xmax != None and not isinstance(self.parm.xmax, int):
            self.parm.xmax = int(self.parm.xmax)
        if self.parm.ymin != None and not isinstance(self.parm.ymin, int):
            self.parm.ymin = int(self.parm.ymin)
        if self.parm.ymax != None and not isinstance(self.parm.ymax, int):
            self.parm.ymax = int(self.parm.ymax)

        if len(xaxis) != len(value_matrix[0]) or len(yaxis) != len(value_matrix):
            self.error(
                f"unequal size detected in image splitting: xaxis ({len(xaxis)}), yaxis ({len(yaxis)}), value_matrix ({len(value_matrix[0])}*{len(value_matrix)})"
            )

        if self.parm.xmin == None:
            self.parm.xmin = 0
        if self.parm.xmax == None:
            self.parm.xmax = len(xaxis)
        if self.parm.ymin == None:
            self.parm.ymin = 0
        if self.parm.ymax == None:
            self.parm.ymax = len(yaxis)

        xmin, xmax = self.parm.xmin, self.parm.xmax
        ymin, ymax = self.parm.ymin, self.parm.ymax
        xaxis = xaxis[xmin:xmax]
        for y, _ in enumerate(yaxis):
            value_matrix[y] = value_matrix[y][xmin:xmax]
        value_matrix.reverse()  # from bottom to top
        yaxis.reverse()
        value_matrix = value_matrix[ymin:ymax]
        yaxis = yaxis[ymin:ymax]
        value_matrix.reverse()  # from top to bottom
        yaxis.reverse()

        if len(xaxis) < 1 or len(yaxis) < 1:
            self.error(
                f"the image ({len(xaxis)}*{len(yaxis)}) less than 1 dimensions, unable to draw"
            )
        self.info(
            f"cutting image by x_index in range [{xmin}, {xmax}), y_index in range [{ymin}, {ymax})"
        )
        self.info(
            f"cutting image by xaxis in range [{xaxis[0]}, {xaxis[-1]}], yaxis in range [{yaxis[-1]}, {yaxis[0]}]"
        )

        return xaxis, yaxis, value_matrix

    def __call__(self):
        # self.info("in xpm_show")
        # print(self.parm.__dict__)

        if not self.parm.input:
            self.error("you must specify a xpm file to show")

        for xpmfile in self.parm.input:
            xpm = XPM(xpmfile)
            self.file = xpm
            self.remove_latex(filetype="XPM")

            xaxis = [x * self.parm.xshrink + self.parm.xplus for x in xpm.xaxis]
            yaxis = [y * self.parm.yshrink + self.parm.yplus for y in xpm.yaxis]
            value_matrix = []
            for y, _ in enumerate(yaxis):
                v_lis = []
                for x, _ in enumerate(xaxis):
                    v_lis.append(xpm.value_matrix[y][x] * self.parm.zshrink + self.parm.zplus)
                value_matrix.append(v_lis)

            ## top -> bottom ===>>> bottom to top
            yaxis.reverse()
            value_matrix.reverse()

            xaxis, yaxis, value_matrix = self.image_split(xaxis, yaxis, value_matrix)

            kwargs = {
                "data_list": value_matrix,
                "xdata_list": xaxis,
                "ydata_list": yaxis,
                "legends": self.sel_parm(self.parm.legends, xpm.notes),
                "color_list": xpm.colors,
                "zmin": self.parm.zmin,
                "zmax": self.parm.zmax,
                "xlabel": self.get_parm("xlabel"),
                "ylabel": self.get_parm("ylabel"),
                "zlabel": self.sel_parm(self.parm.zlabel, xpm.legend),
                "title": self.get_parm("title"),
                "x_precision": self.parm.x_precision,
                "y_precision": self.parm.y_precision,
                "z_precision": self.parm.z_precision,
                "alpha": self.parm.alpha,
                "legend_location": self.sel_parm(self.parm.legend_location, "outside"),
                "colorbar_location": self.parm.colorbar_location,
                "fig_type": xpm.type,
                "cmap": self.parm.colormap,
            }

            interpolation = self.parm.interpolation
            ip_fold = self.parm.interpolation_fold
            mode = self.parm.mode

            if self.parm.engine == "matplotlib":
                if mode in ["pcolormesh", "3d", "contour"]:
                    if interpolation != None:
                        if self.file.type != "Continuous":
                            self.warn(
                                f"you are applying interpolation to {self.file.type} type of XPM. It should not be, but DIT would do it. BE CAREFUL for what you get !"
                            )
                        xaxis, yaxis, value_matrix = self.calc_interpolation(
                            xaxis, yaxis, value_matrix, interpolation, ip_fold
                        )
                        kwargs["xdata_list"] = xaxis
                        kwargs["ydata_list"] = yaxis
                        kwargs["data_list"] = value_matrix
                    else:
                        kwargs["xdata_list"] = np.array(xaxis)
                        kwargs["ydata_list"] = np.array(yaxis)
                        kwargs["data_list"] = np.array(kwargs["data_list"])
                if mode == "pcolormesh":
                    fig = PcolormeshMatplotlib(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)
                elif mode == "3d":
                    fig = ThreeDimensionMatplotlib(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)
                elif mode == "contour":
                    fig = ContourMatplotlib(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)
                else:
                    kwargs["interpolation"] = interpolation
                    fig = ImshowMatplotlib(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)

            elif self.parm.engine == "plotly":
                if interpolation != None:
                    if self.file.type != "Continuous":
                        self.warn(
                            f"you are applying interpolation to {self.file.type} type of XPM. It should not be, but DIT would do it. BE CAREFUL for what you get !"
                        )
                    xaxis, yaxis, value_matrix = self.calc_interpolation(
                        xaxis, yaxis, value_matrix, interpolation, ip_fold
                    )
                    kwargs["xdata_list"] = xaxis
                    kwargs["ydata_list"] = yaxis
                    kwargs["data_list"] = value_matrix
                if mode == "3d":
                    fig = ThreeDimensionPlotly(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)
                elif mode == "contour":
                    fig = ContourPlotly(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)
                else:
                    fig = PcolormeshPlotly(**kwargs)
                    fig.final(self.parm.output, self.parm.noshow)

            elif self.parm.engine == "gnuplot":
                if interpolation != None:
                    if self.file.type != "Continuous":
                        self.warn(
                            f"you are applying interpolation to {self.file.type} type of XPM. It should not be, but DIT would do it. BE CAREFUL for what you get !"
                        )
                    xaxis, yaxis, value_matrix = self.calc_interpolation(
                        xaxis, yaxis, value_matrix, interpolation, ip_fold
                    )
                    kwargs["xdata_list"] = xaxis
                    kwargs["ydata_list"] = yaxis
                    kwargs["data_list"] = value_matrix
                if mode not in ["3d", "contour"]:
                    mode = "imshow"
                fig = ImshowGnuplot(mode, **kwargs)
                fig.final(self.parm.output, self.parm.noshow)

            elif self.parm.engine == "plotext":
                if interpolation != None:
                    self.warn(
                        "plotext engine do not support interpolation now, ignored it"
                    )
                color_matrix = []
                for y, _ in enumerate(yaxis):
                    c_lis = []
                    for x, _ in enumerate(xaxis):
                        c = xpm.colors[xpm.chars.index(xpm.dot_matrix[y][x])]
                        c_lis.append(self.hex2rgb(c))
                    color_matrix.append(c_lis)
                kwargs["data_list"] = color_matrix
                ImshowPlotext(**kwargs)
            else:
                self.error("wrong selection of plot engine")


class xpm2csv(Command):
    """
    Converting xpm file into csv file in (X, Y, Z) data format.

    :Parameters:
        -f, --input
                specify the input xpm file (or files)
        -o, --output (optional)
                specify the csv file name for saving data, default to 'dit_{input}.csv'
        -x, --xlabel (optional)
                specify the xlabel of XPM
        -y, --ylabel (optional)
                specify the ylabel of XPM
        -z, --zlabel (optional)
                specify the zlabel of XPM
        -xs, --xshrink (optional)
                specify the shrink fold number of X values
        -ys, --yshrink (optional)
                specify the shrink fold number of Y values
        -zs, --zshrink (optional)
                specify the shrink fold number of Z values
        -xp, --xplus (optional)
                specify the addtion number of X values
        -yp, --yplus (optional)
                specify the addtion number of Y values
        -zp, --zplus (optional)
                specify the addtion number of Z values

    :Usage:
        dit xpm2csv -f FEL.xpm -o fel.csv
        dit xpm2csv -f DSSP.xpm -o dssp.csv -x Time(ns) -xs 0.001 -y "Residue No."
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in xpm2csv")
        # print(self.parm.__dict__)

        if not self.parm.input:
            self.error("you must specify a xpm file for converting to csv file")
        if len(self.parm.input) > 1:
            self.warn(f"only the first xpm file {self.parm.input[0]} will be used !")
        if not self.parm.output:
            self.parm.output = f"dit_{self.parm.input[0].split('.')[0]}.csv"
        self.parm.output = self.check_output_exist(self.parm.output)

        xpm = XPM(self.parm.input[0])
        with open(self.parm.output, "w") as fo:
            if xpm.type != "Continuous":
                fo.write("#### DIT: it's not a Continuous type xpm file\n")
                fo.write("#### labels of values were recorded below: \n")
                for index, label in enumerate(xpm.notes):
                    fo.write(f"#### {index} : {label}\n")
            x_title = (xpm.xlabel, "x-axis")[len(xpm.xlabel) == 0]
            y_title = (xpm.ylabel, "y-axis")[len(xpm.ylabel) == 0]
            z_title = (xpm.legend, "value")[len(xpm.legend) == 0]
            x_title = self.sel_parm(self.parm.xlabel, x_title)
            y_title = self.sel_parm(self.parm.ylabel, y_title)
            z_title = self.sel_parm(self.parm.zlabel, z_title)
            fo.write(f"{x_title},{y_title},{z_title}\n")
            for y, y_value in enumerate(xpm.yaxis):
                for x, x_value in enumerate(xpm.xaxis):
                    z_value = xpm.value_matrix[y][x]
                    x_value *= self.parm.xshrink + self.parm.xplus
                    y_value *= self.parm.yshrink + self.parm.yplus
                    z_value *= self.parm.zshrink + self.parm.zplus
                    fo.write(f"{x_value:.6f},{y_value:.6f},{z_value:.6f}\n")
        self.info(
            f"extract data from {xpm.xpmfile} and saved into {self.parm.output} successfully"
        )


class xpm2dat(Command):
    """
    Converting xpm file into dat file in data matrix format.

    :Parameters:
        -f, --input
                specify the input xpm file (or files)
        -o, --output (optional)
                specify the dat file name for saving data, default to 'dit_{input}.dat'
        -x, --xlabel (optional)
                specify the xlabel of XPM
        -y, --ylabel (optional)
                specify the ylabel of XPM
        -z, --zlabel (optional)
                specify the zlabel of XPM
        -xs, --xshrink (optional)
                specify the shrink fold number of X values
        -ys, --yshrink (optional)
                specify the shrink fold number of Y values
        -zs, --zshrink (optional)
                specify the shrink fold number of Z values
        -xp, --xplus (optional)
                specify the addtion number of X values
        -yp, --yplus (optional)
                specify the addtion number of Y values
        -zp, --zplus (optional)
                specify the addtion number of Z values

    :Usage:
        dit xpm2dat -f FEL.xpm -o fel.dat
        dit xpm2dat -f DSSP.xpm -o dssp.dat -x Time(ns) -xs 0.001
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in xpm2dat")
        # print(self.parm.__dict__)

        if not self.parm.input:
            self.error("you must specify a xpm file for converting to dat file")
        if len(self.parm.input) > 1:
            self.warn("only the first xpm file you specified will be used !")
        if not self.parm.output:
            self.parm.output = f"dit_{self.parm.input[0].split('.')[0]}.dat"
        self.parm.output = self.check_output_exist(self.parm.output)

        xpm = XPM(self.parm.input[0])
        with open(self.parm.output, "w") as fo:
            if xpm.type != "Continuous":
                fo.write("#### DIT: it's not a Continuous type xpm file\n")
                fo.write("#### labels of values were recorded below: \n")
                for index, label in enumerate(xpm.notes):
                    fo.write(f"#### {index} : {label}\n")
            x_title = (xpm.xlabel, "x-axis")[len(xpm.xlabel) == 0]
            y_title = (xpm.ylabel, "y-axis")[len(xpm.ylabel) == 0]
            z_title = (xpm.legend, "value")[len(xpm.legend) == 0]
            x_title = self.sel_parm(self.parm.xlabel, x_title)
            y_title = self.sel_parm(self.parm.ylabel, y_title)
            z_title = self.sel_parm(self.parm.zlabel, z_title)
            fo.write(
                "#### "
                + f"{x_title} (xaxis) data were shown below, from left to right:\n"
            )
            fo.write(",".join([f"{x*self.parm.xshrink+self.parm.xplus:.6f}" for x in xpm.xaxis]) + "\n")
            fo.write(
                "#### "
                + f"{y_title} (yaxis) data were shown below, from top to bottom:\n"
            )
            fo.write(",".join([f"{y*self.parm.yshrink+self.parm.yplus:.6f}" for y in xpm.yaxis]) + "\n")
            fo.write(
                "#### "
                + f"{y_title} (yaxis) data were shown below, from bottom to top:\n"
            )
            y_lis = [f"{y*self.parm.yshrink+self.parm.yplus:.6f}" for y in xpm.yaxis]
            y_lis.reverse()
            fo.write(",".join(y_lis) + "\n")
            fo.write(
                "#### "
                + f"{z_title} (figure dots) data were shown below, from top to bottom, from left to right:\n"
            )
            for y, _ in enumerate(xpm.yaxis):
                line_list: List[str] = []
                for x, _ in enumerate(xpm.xaxis):
                    z_value = xpm.value_matrix[y][x]
                    line_list.append(f"{z_value*self.parm.zshrink+self.parm.zplus:.6f}")
                fo.write(",".join(line_list) + "\n")
        self.info(
            f"extract data from {xpm.xpmfile} and saved into {self.parm.output} successfully"
        )


class xpm_diff(Command):
    """
    Calculate the difference of two xpm files.
    By calculating the difference of matrix values of two xpms correspondingly (first xpm - second xpm), this command could be used for presentation the variation of two xpm files.

    :Parameters:
        -f, --input
                specify the two xpm files for input
        -o, --output (optional)
                specify the xpm file name for output, default to 'dit_xpm_diff.xpm'
        -x, --xlabel (optional)
                specify the xlabel of XPM of output
        -y, --ylabel (optional)
                specify the ylabel of XPM of output
        -z, --zlabel (optional)
                specify the zlabel of XPM of output
        -xs, --xshrink (optional)
                specify the shrink fold number of X values
        -ys, --yshrink (optional)
                specify the shrink fold number of Y values
        -zs, --zshrink (optional)
                specify the shrink fold number of Z values
        -xp, --xplus (optional)
                specify the addtion number of X values
        -yp, --yplus (optional)
                specify the addtion number of Y values
        -zp, --zplus (optional)
                specify the addtion number of Z values

    :Usage:
        dit xpm_diff -f DCCM0.xpm DCCM1.xpm -o DCCM0-1.xpm
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in xpm_diff")
        # print(self.parm.__dict__)

        if not self.parm.input:
            self.error("you must specify two xpm file for calcuelation")
        if len(self.parm.input) > 2:
            self.warn("only the first two xpm file you specified will be used !")
        if len(self.parm.input) < 2:
            self.warn("at least two xpm file are needed for calculation !")
        if not self.parm.output:
            self.parm.output = "dit_xpm_diff.xpm"
        self.parm.output = self.check_output_exist(self.parm.output)

        xpm0 = XPM(self.parm.input[0])
        xpm1 = XPM(self.parm.input[1])
        xpm = xpm0 - xpm1
        xpm.xpmfile = self.parm.output
        xpm.xlabel = self.sel_parm(self.parm.xlabel, xpm.xlabel)
        xpm.ylabel = self.sel_parm(self.parm.ylabel, xpm.ylabel)
        xpm.legend = self.sel_parm(self.parm.zlabel, xpm.legend)
        xpm.title = self.sel_parm(self.parm.title, f"{xpm0.xpmfile} - {xpm1.xpmfile}")
        xpm.xaxis = [x * self.parm.xshrink+self.parm.xplus for x in xpm.xaxis]
        xpm.yaxis = [y * self.parm.yshrink+self.parm.yplus for y in xpm.yaxis]
        for y, _ in enumerate(xpm.yaxis):
            for x, _ in enumerate(xpm.xaxis):
                xpm.value_matrix[y][x] *= self.parm.zshrink+self.parm.zplus
        xpm.save(self.parm.output)


class xpm_merge(Command):
    """
    Merge two xpm files half by half.
    The first specified xpm will be located at left top corner, the second one will be located at right bottom corner. Thi command might be useful for stitching two xpm together.

    :Parameters:
        -f, --input
                specify the two xpm files for input
        -o, --output (optional)
                specify the xpm file name for output, default to 'dit_xpm_merge.xpm'
        -x, --xlabel (optional)
                specify the xlabel of XPM of output
        -y, --ylabel (optional)
                specify the ylabel of XPM of output
        -z, --zlabel (optional)
                specify the zlabel of XPM of output
        -xs, --xshrink (optional)
                specify the shrink fold number of X values
        -ys, --yshrink (optional)
                specify the shrink fold number of Y values
        -zs, --zshrink (optional)
                specify the shrink fold number of Z values
        -xp, --xplus (optional)
                specify the addtion number of X values
        -yp, --yplus (optional)
                specify the addtion number of Y values
        -zp, --zplus (optional)
                specify the addtion number of Z values

    :Usage:
        dit xpm_merge -f DCCM0.xpm DCCM1.xpm -o DCCM0-1.xpm
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in xpm_merge")
        # print(self.parm.__dict__)

        if not self.parm.input:
            self.error("you must specify two xpm file for calcuelation")
        if len(self.parm.input) > 2:
            self.warn("only the first two xpm file you specified will be used !")
        if len(self.parm.input) < 2:
            self.warn("at least two xpm file are needed for calculation !")
        if not self.parm.output:
            self.parm.output = "dit_xpm_merge.xpm"
        self.parm.output = self.check_output_exist(self.parm.output)

        xpm0 = XPM(self.parm.input[0])
        xpm1 = XPM(self.parm.input[1])
        for key in ["title", "xlabel", "ylabel", "xaxis", "yaxis"]:
            if xpm0.__dict__[key] != xpm1.__dict__[key]:
                self.warn(
                    f"Detected different {key} in {xpm0.xpmfile} and {xpm1.xpmfile}. \nDIT strongly warns you that different type (meanings) of xpms should NOT be used to merge. The results may NOT be reliable !!! "
                )
        if xpm0.type != xpm1.type:
            self.error(
                f"Do not support different types of xpm to merge:{xpm0.xpmfile}({xpm0.type}), and {xpm1.xpmfile}({xpm1.type})"
            )
        if xpm0.width != xpm1.width or xpm0.height != xpm1.height:
            self.error(
                f"The shape of {xpm0.xpmfile} ({xpm0.width}, {xpm0.height}) and {xpm1.xpmfile} ({xpm1.width}, {xpm1.height}) are different, unable to calculate difference."
            )

        out = XPM(self.parm.output, is_file=False, new_file=True)
        for key, value in xpm0.__dict__.items():
            out.__dict__[key] = value
        if out.type == "Continuous":
            for h in range(xpm0.height):
                for w in range(xpm0.width):
                    if h / xpm0.height + w / xpm0.width < 1:
                        value = xpm0.value_matrix[h][w]  # left top
                    else:
                        value = xpm1.value_matrix[h][w]  # right bottom
                    out.value_matrix[h][w] = value
            out.refresh_by_value_matrix()
        else:
            for h in range(xpm0.height):
                for w in range(xpm0.width):
                    if h / xpm0.height + w / xpm0.width < 1:
                        value = xpm0.notes[xpm0.value_matrix[h][w]]  # left top
                    else:
                        value = xpm1.notes[xpm1.value_matrix[h][w]]  # right bottom
                    out.value_matrix[h][w] = value
            out.refresh_by_value_matrix(is_Continuous=False)

        out.title = self.sel_parm(
            self.parm.title, f"{xpm0.xpmfile}(left) / {xpm1.xpmfile}(right)"
        )
        out.xlabel = self.sel_parm(self.parm.xlabel, out.xlabel)
        out.ylabel = self.sel_parm(self.parm.ylabel, out.ylabel)
        out.legend = self.sel_parm(self.parm.zlabel, out.legend)
        out.xaxis = [x * self.parm.xshrink+self.parm.xplus for x in out.xaxis]
        out.yaxis = [y * self.parm.yshrink+self.parm.yplus for y in out.yaxis]
        for y, _ in enumerate(out.yaxis):
            for x, _ in enumerate(out.xaxis):
                out.value_matrix[y][x] *= self.parm.zshrink+self.parm.zplus
        out.save(self.parm.output)
