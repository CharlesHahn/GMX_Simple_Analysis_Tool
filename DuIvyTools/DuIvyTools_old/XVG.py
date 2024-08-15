"""
XVG module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

XVG module contains the code to process xvg files, including reading 
information from xvg file, visualization, and data convertion.

This module requires Numpy, Matplotlib and argparse. 

This module contains:
    class XVG
    function xvg_combine, xvg_compare, energy_compute, ramachandran
    ......

This file is provided to you under GPLv3 License"""

import os
import sys
import argparse
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.colors as mplcolors
import logging


class XVG(object):
    """XVG module was defined to process XVG file

    Attributes:
    xvg_filename: the name of xvg file
    xvg_title: the title of xvg file
    xvg_xlabel: the x-label of xvg file
    xvg_ylabel: the y-label of xvg file
    xvg_legends: a list to store legends
    xvg_columns: a list to store data
    xvg_data: a dict to store data

    Functions:
    __init__: read xvg file and extract infos
    calc_average: calculate the average of xvg data
    calc_mvave: calculate the moving average of xvg data
    xvg2csv : convert xvg data to csv format
    draw: draw xvg data to figure
    """

    def __init__(self, xvgfile: str = "", xshrink: float = 1.0) -> None:
        """read xvg file and extract infos"""

        self.xvg_filename = xvgfile
        self.xvg_title = ""
        self.xvg_xlabel = ""
        self.xvg_ylabel = ""
        self.xvg_legends = []
        self.xvg_column_num = 0
        self.xvg_row_num = 0
        self.xvg_columns = []

        self.data_heads = []
        self.data_columns = []

        ## check and read xpm file
        if xshrink <= 0:
            logging.warning("The parameter xshrink should be larger than zero")
        if not os.path.exists(xvgfile):
            logging.error("no {} in current directory".format(xvgfile))
            sys.exit()
        if xvgfile[-4:] != ".xvg":
            logging.error("specify a xvg file with suffix xvg")
            sys.exit()
        with open(xvgfile, "r") as fo:
            lines = [line.strip() for line in fo.readlines() if line.strip() != ""]

        ## extract data from xvg file content
        for line in lines:
            if line.startswith("#") or line.startswith("&"):
                continue
            elif line.startswith("@"):
                if " title " in line:
                    self.xvg_title = line.strip('"').split('"')[-1]
                elif " xaxis " in line and " label " in line:
                    self.xvg_xlabel = line.strip('"').split('"')[-1]
                elif " yaxis " in line and " label " in line:
                    self.xvg_ylabel = line.strip('"').split('"')[-1]
                elif line.startswith("@ s") and " legend " in line:
                    self.xvg_legends.append(line.strip('"').split('"')[-1])
            else:
                ## extract the column data part
                items = line.split()
                if len(self.xvg_columns) == 0:
                    self.xvg_columns = [[] for _ in range(len(items))]
                    self.xvg_column_num = len(items)
                    self.xvg_row_num = 0
                if len(items) != len(self.xvg_columns):
                    logging.error(
                        "the number of columns in {} is not equal. ".format(
                            self.xvg_filename
                        )
                    )
                    logging.info("{} -> ".format(self.xvg_row_num) + line)
                    sys.exit()
                for i in range(len(items)):
                    self.xvg_columns[i].append(items[i])
                self.xvg_row_num += 1

        ## post-process the infos
        for c in range(self.xvg_column_num):
            if len(self.xvg_columns[c]) != self.xvg_row_num:
                logging.error(
                    "length of column {} if not equal to count of rows".format(c)
                )
                sys.exit()
        if self.xvg_column_num == 0 or self.xvg_row_num == 0:
            logging.error("no data line detected in xvg file")
            sys.exit()

        self.data_heads.append(self.xvg_xlabel)
        self.data_columns.append([float(c) * xshrink for c in self.xvg_columns[0]])
        if len(self.xvg_legends) == 0 and len(self.xvg_columns) > 1:
            self.data_heads.append(self.xvg_ylabel)
            self.data_columns.append([float(c) for c in self.xvg_columns[1]])
        if len(self.xvg_legends) > 0 and len(self.xvg_columns) > len(self.xvg_legends):
            items = [item.strip() for item in self.xvg_ylabel.split(",")]
            heads = [l for l in self.xvg_legends]
            if len(items) == len(self.xvg_legends):
                for i in range(len(items)):
                    heads[i] += " " + items[i]
            elif (
                len(items) == 1
                and items[0] != ""
                and (items[0][0] == "(" and items[0][-1] == ")")
            ):
                for i in range(len(heads)):
                    heads[i] += " " + items[0]
            else:
                logging.warning(
                    "failed to pair ylabel to legends, use legends in xvg file"
                )
            self.data_heads += heads
            for i in range(len(heads)):
                self.data_columns.append([float(c) for c in self.xvg_columns[i + 1]])

        logging.info("read {} successfully. ".format(self.xvg_filename))

    def calc_average(self, start: int = None, end: int = None) -> tuple:
        """
        calculate the average of each column

        :parameters:
            start: the start index
            end: the end index
        :return:
            data_heads: a list contains all data legends
            column_averages: a list contains all average numbers
            column_stds: a list contains all standard error numbers
        """

        if (start != None and end != None) and (start >= end):
            logging.error("start index should be less than end index")
            sys.exit()
        if (start != None and start >= self.xvg_row_num) or (
            end != None and end >= self.xvg_row_num
        ):
            logging.error(
                "start or end index should be less than the number of rows in xvg file"
            )
            sys.exit()

        column_averages = []
        column_stds = []
        for column in self.data_columns:
            column_averages.append(np.average(column[start:end]))
            column_stds.append(np.std(column[start:end]))

        return self.data_heads, column_averages, column_stds

    def calc_mvave(self, windowsize: int = 50, confidence: float = 0.90) -> tuple:
        """
        calculate the moving average of each column

        :parameters:
            windowsize: the window size for calculating moving average
            confidence: the confidence to calculate interval

        :return:
            data_heads: a list contains all data legends
            column_mvaves: a list contains all moving average
            column_highs: the high value of interval of moving averages
            column_lows: the low value of interval of moving averages
        """

        if windowsize <= 0 or windowsize > int(self.xvg_row_num / 2):
            logging.error("windowsize value is not proper")
            sys.exit()
        if confidence <= 0 or confidence >= 1:
            logging.error("confidence value is not proper, it should be in (0,1)")
            sys.exit()

        column_mvaves, column_highs, column_lows = [], [], []
        for column in self.data_columns:
            mv_ave = [np.nan for _ in range(windowsize)]
            high = [np.nan for _ in range(windowsize)]
            low = [np.nan for _ in range(windowsize)]
            for i in range(windowsize, self.xvg_row_num):
                window_data = np.array(column[i - windowsize : i])
                ave = np.mean(window_data)
                std = np.std(window_data)
                interval = stats.norm.interval(confidence, ave, std)
                mv_ave.append(ave)
                low.append(interval[0])
                high.append(interval[1])
            column_mvaves.append(mv_ave)
            column_lows.append(low)
            column_highs.append(high)

        return self.data_heads, column_mvaves, column_highs, column_lows

    def xvg2csv(self, outcsv: str = "") -> None:
        """
        convert xvg data into csv file

        :parameters:
            outcsv: the csv file name for output
        """

        ## check parameters
        if outcsv == "":
            outcsv = self.xvg_filename[:-4] + ".csv"
        if outcsv[-4:] != ".csv":
            logging.error("please specify a csv file name with suffix .csv")
            sys.exit()
        if os.path.exists(outcsv):
            logging.error("already a {} in current directory".format(outcsv))
            sys.exit()

        ## write csv file
        out_data = []
        if len(self.data_columns) == len(self.xvg_columns):
            out_data = [column for column in self.data_columns]
        elif len(self.data_columns) < len(self.xvg_columns):
            out_data = [column for column in self.data_columns]
            out_data += [
                column for column in self.xvg_columns[len(self.data_columns) :]
            ]
        with open(outcsv, "w") as fo:
            fo.write(",".join(self.data_heads) + "\n")
            for row in range(self.xvg_row_num):
                fo.write(",".join([str(column[row]) for column in out_data]) + "\n")

        logging.info(
            "convert {} into {} successfully.".format(self.xvg_filename, outcsv)
        )

    def draw(self, outpng: str = "", noshow: bool = False) -> None:
        """
        draw xvg data into figure

        :parameters:
            outpng: the output picture file name.
            noshow: whether not to show figure in GUI.
        """

        plt.clf()
        column_num = len(self.data_columns)
        x_min = np.min(self.data_columns[0])
        x_max = np.max(self.data_columns[0])
        x_space = int((x_max - x_min) / 100)
        if column_num == 2:
            plt.plot(self.data_columns[0], self.data_columns[1])
            plt.ylabel(self.data_heads[1])
        else:
            for i in range(1, column_num):
                plt.plot(
                    self.data_columns[0], self.data_columns[i], label=self.data_heads[i]
                )
            plt.legend()
        if int(x_min - x_space) < int(x_max + x_space) - 1.0:
            plt.xlim(int(x_min - x_space), int(x_max + x_space))
        plt.xlabel(self.data_heads[0])
        plt.title(self.xvg_title)
        plt.tight_layout()

        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng, dpi=300)
        if noshow == False:
            plt.show()

    def draw_subplot(self, outpng: str = "", noshow: bool = False) -> None:
        """
        draw xvg data into figure by subplots

        :parameters:
            outpng: the output picture file name.
            noshow: whether not to show figure in GUI.
        """

        plt.clf()
        column_num = len(self.data_columns)
        x_min = np.min(self.data_columns[0])
        x_max = np.max(self.data_columns[0])
        x_space = int((x_max - x_min) / 100)
        grid = (plt.GridSpec(1, column_num), plt.GridSpec(2, int(column_num / 2)))[
            column_num > 2
        ]
        for i in range(1, column_num):
            ## use grid for subplots layout
            if i == column_num - 1:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i - 1 < int((column_num) / 2)],
                        (i - 1) % int((column_num) / 2) :,
                    ]
                )
            else:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i - 1 < int((column_num) / 2)],
                        (i - 1) % int((column_num) / 2),
                    ]
                )
            ax.plot(self.data_columns[0], self.data_columns[i])
            ax.set_ylabel(self.data_heads[i])
            if int(x_min - x_space) < int(x_max + x_space) - 1.0:
                plt.xlim(int(x_min - x_space), int(x_max + x_space))
            plt.xlabel(self.data_heads[0])
        if column_num > 2:
            plt.suptitle(self.xvg_title)
        else:
            plt.title(self.xvg_title)
        plt.tight_layout()

        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng, dpi=300)
        if noshow == False:
            plt.show()

    def draw_distribution(
        self, bin: int = 100, outpng: str = "", noshow: bool = False
    ) -> None:
        """
        calculate the distribution of each column and draw

        :parameters:
            bin: the bin size of frequency calculation
            outpng: the output picture file name.
            noshow: whether not to show figure in GUI.
        """

        plt.clf()
        column_num = len(self.data_columns)
        grid = plt.GridSpec(2, int((column_num + 1) / 2))
        for i in range(column_num):
            column = self.data_columns[i]
            ## calculate distribution
            column_min = np.min(column)
            column_max = np.max(column)
            bin_window = (column_max - column_min) / bin
            if bin_window != 0:
                frequency = [0 for _ in range(bin)]
                for value in column:
                    index = int((value - column_min) / bin_window)
                    if index == bin:  # for the column_max
                        index = bin - 1
                    frequency[index] += 1
                if sum(frequency) != self.xvg_row_num:
                    logging.error("wrong in calculating distribution")
                    sys.exit()
                frequency = [f * 100.0 / self.xvg_row_num for f in frequency]
                x_value = [column_min + bin_window * b for b in range(bin)]
            else:  # for data without fluctuation
                frequency = [1]
                x_value = [column_min]
            ## draw distribution
            if i == column_num - 1:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i < int((column_num + 1) / 2)],
                        i % int((column_num + 1) / 2) :,
                    ]
                )
            else:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i < int((column_num + 1) / 2)],
                        i % int((column_num + 1) / 2),
                    ]
                )
            # ax = plt.subplot(int((column_num+1)/2), 2, i+1)
            ax.plot(x_value, frequency)
            ax.set_xlabel(self.data_heads[i])
            ax.set_ylabel("Frequency %")
            plt.xlim(column_min - bin_window, column_max + bin_window)
        plt.suptitle("Frequency of " + self.xvg_title)
        # plt.subplots_adjust(wspace=0.8)
        plt.tight_layout()

        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng, dpi=300)
        if noshow == False:
            plt.show()

    def draw_stacking(
        self,
        column_select: list = [],
        legend_list: list = [],
        start: int = 0,
        end: int = None,
        outpng: str = "",
        noshow: bool = False,
        xlabel: str = None,
        ylabel: str = None,
    ) -> None:
        """
        draw xvg data into stacking figure

        :parameters:
            column_select: a list to store the column indexs you want to stack
            legend_list: a list to store legends specified by user
            outpng: the output picture file name.
            noshow: whether not to show figure in GUI.
        """

        ## check parameters
        if column_select == None or len(column_select) == 0:
            logging.error("please specify column indexs you want to stack")
            sys.exit()
        if not set(column_select).issubset(
            set([i for i in range(len(self.data_columns))])
        ):
            logging.error(
                "some column index you specified may not in range of [0:{}], check it".format(
                    len(self.data_columns)
                )
            )
            sys.exit()

        if legend_list == None:
            legend_list = []
        if len(legend_list) != 0 and len(legend_list) != len(column_select):
            logging.warning("length of legends and column_select isn't equal")
            logging.warning("using default legends for instead")
            legend_list = []
        for legend in legend_list:
            if not isinstance(legend, str):
                logging.error("you are not supposed to type comma in legends here")
                sys.exit()
        if start == None:
            start = 0
        if start < 0 or start >= self.xvg_row_num:
            logging.error(
                "start of row index not in proper range [0:{}]".format(self.xvg_row_num)
            )
            sys.exit()
        if end != None and (end <= start or end >= self.xvg_row_num):
            logging.error(
                "end of row index not in proper range [{}:{}]".format(
                    start + 1, self.xvg_row_num
                )
            )
            sys.exit()

        ## draw stacked plot
        plt.clf()
        column_select.reverse()
        legend_list.reverse()
        ylim_max, ylim_min = 0, 0
        labels = (legend_list, [self.data_heads[c] for c in column_select])[
            len(legend_list) == 0
        ]
        for index_id, _ in enumerate(column_select):
            stack_data = [
                sum([self.data_columns[c][row] for c in column_select[index_id:]])
                for row in range(self.xvg_row_num)
            ][start:end]
            plt.fill_between(
                self.data_columns[0][start:end],
                stack_data,
                [0 for _ in range(len(stack_data))],
                label=labels[index_id],
            )
            ylim_max = (ylim_max, max(stack_data))[ylim_max < max(stack_data)]
            ylim_min = (ylim_min, min(stack_data))[ylim_min > min(stack_data)]
        # print(ylim_min, ylim_max)
        if xlabel != None:
            plt.xlabel(xlabel)
        else:
            plt.xlabel(self.data_heads[0])
        if ylabel != None:
            plt.ylabel(ylabel)
        else:
            plt.ylabel(self.xvg_ylabel)
        plt.title("Stacked plot of " + self.xvg_title)
        plt.xlim(
            np.min(self.data_columns[0][start:end]),
            np.max(self.data_columns[0][start:end]),
        )
        plt.ylim(ylim_min, ylim_max)
        plt.legend(loc=3)

        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng, dpi=300)
        if noshow == False:
            plt.show()

    def draw_scatter(
        self,
        x_index: int = 0,
        y_index: int = None,
        color_index: int = None,
        outpng: str = "",
        noshow: bool = False,
    ) -> None:
        """
        draw xvg data to scatter plot

        :parameters:
            x_index: the column index of x values for scatter plot
            y_index: the column index of y values for scatter plot
            color_index: the column index for color value
            outpng: the output picture file name
            noshow: whether not to show figure in GUI
        """

        ## check parameters
        if x_index >= len(self.data_columns) or x_index < 0:
            logging.warning("x_index not in proper range, use default value.")
            x_index = 0
        if y_index == None:
            y_index = (len(self.data_columns) - 1, 1)[len(self.data_columns) >= 2]
        else:
            if y_index >= len(self.data_columns) or y_index < 0:
                logging.warning("y_index not in proper range, use default value.")
                y_index = (len(self.data_columns) - 1, 1)[len(self.data_columns) >= 2]

        ## draw scatter plot
        plt.clf()
        if color_index != None:
            if color_index >= len(self.data_columns):
                logging.error(
                    "color_index you specified is out of range ({})".format(
                        len(self.data_columns)
                    )
                )
                sys.exit()
            plt.scatter(
                self.data_columns[x_index],
                self.data_columns[y_index],
                c=self.data_columns[color_index],
                cmap="coolwarm",
            )
            plt.colorbar(
                label=self.data_heads[color_index], orientation="vertical", shrink=0.8
            )
        else:
            plt.scatter(self.data_columns[x_index], self.data_columns[y_index])
        plt.ylabel(self.data_heads[y_index])
        plt.xlabel(self.data_heads[x_index])
        plt.title(
            "Scatter plot of {} vs {}".format(
                self.data_heads[x_index], self.data_heads[y_index]
            )
        )
        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng, dpi=300)
        if noshow == False:
            plt.show()


def xvg_combine(
    xvgfiles: list = [],
    column_select: list = [],
    outfile: str = None,
) -> None:
    """
    combine two xvg files by specified column index

    :parameters:
        xvgfiles: a list to store files you specify
        column_select: a list to specify the columns
        outfile: the output xvg file name
    """

    ## check parameters
    if outfile == None:
        logging.error("please specify ouput xvg file name")
        sys.exit()
    if column_select == None or len(column_select) == 0:
        logging.error("please specify the column indexs by -c")
        sys.exit()
    if os.path.exists(outfile):
        logging.error("{} already in current directory".format(outfile))
        sys.exit()
    if len(outfile) < 4 or outfile[-4:] != ".xvg":
        logging.error("please specify a output filename with suffix .xvg")
        sys.exit()
    if not isinstance(column_select, list):
        logging.error("column_select must be a list")
        sys.exit()
    for indexs in column_select:
        if isinstance(indexs, list):
            break
    else:
        column_select = [[columns] for columns in column_select]
    for xvgs in xvgfiles:
        if not isinstance(xvgs, str):
            logging.error("item of xvgfiles should be str, do not use ,")
            sys.exit()

    ## process xvg combination
    xvgs = [XVG(file) for file in xvgfiles]
    row_num = xvgs[0].xvg_row_num
    combined_data_heads, combined_data_columns = [], []
    for id, indexs in enumerate(column_select):
        if xvgs[id].xvg_row_num != row_num:
            logging.error("the row number of input files are not equal")
            sys.exit()
        for index in indexs:
            if index >= len(xvgs[id].data_heads):
                logging.error(
                    "wrong column_select index {} of {}".format(
                        index, xvgs[id].xvg_filename
                    )
                )
                sys.exit()
            combined_data_heads.append(xvgs[id].data_heads[index])
            combined_data_columns.append(xvgs[id].data_columns[index])
    combined_title = " And ".join([xvg.xvg_title for xvg in xvgs])
    combined_xlabel = combined_data_heads[0]

    ## write combined results
    with open(outfile, "w") as fo:
        fo.write("# this file was created by combination of thess xvg files:\n")
        for i in range(len(xvgfiles)):
            fo.write(
                "#    file: {}; indexs: {};\n".format(
                    xvgfiles[i], ",".join([str(c) for c in column_select[i]])
                )
            )
        fo.write('@    title "{}"\n'.format(combined_title))
        fo.write('@    xaxis label "{}"\n'.format(combined_xlabel))
        fo.write("@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n")
        fo.write("@ legend on\n@ legend box on\n@ legend loctype view\n")
        fo.write(
            "@ legend 0.78, 0.8\n@ legend length {}\n".format(
                len(combined_data_heads) - 1
            )
        )
        for s in range(1, len(combined_data_heads)):
            fo.write('@ s{} legend "{}"\n'.format(s - 1, combined_data_heads[s]))
        for row in range(row_num):
            fo.write(
                " ".join(
                    [
                        "{:>16.6f}".format(combined_data_columns[i][row])
                        for i in range(len(combined_data_columns))
                    ]
                )
                + "\n"
            )
    logging.info("xvg files combined sucessfully.")


def energy_compute(xvgfiles: list = [], outfile: str = None):
    """
    compute the interaction between protein and ligand by:
        binding energy  = prolig energy - pro energy - lig energy

    :parameters::
        xvgfiles: a list contains three xvg files
            prolig_xvg: energy xvg file of prolig
            pro_xvg: energy xvg file of protein
            lig_xvg: energy xvg file of ligand
        outfile: the output xvg file name

    IMPORTANT:
        the xvg file used here should contain and ONLY contain five columns:
        Time, LJ(SR), Disper.corr., Coulomb(SR), Coul.recip.
    """

    ## check parameters
    if len(xvgfiles) != 3:
        logging.error(
            "wrong number of input xvg files, must be prolig.xvg, pro.xvg and lig.xvg by order"
        )
        sys.exit()
    prolig_xvg = xvgfiles[0]
    pro_xvg = xvgfiles[1]
    lig_xvg = xvgfiles[2]
    for xvgfile in [prolig_xvg, pro_xvg, lig_xvg]:
        if not os.path.exists(xvgfile):
            logging.error("No {} in current directory".format(xvgfile))
            sys.exit()
    if outfile == None:
        logging.error("please specify output xvg file name")
        sys.exit()
    if os.path.exists(outfile):
        logging.error("{} already in current directory".format(outfile))
        sys.exit()
    if len(outfile) < 4 or outfile[-4:] != ".xvg":
        logging.error("please specify a output filename with suffix .xvg")
        sys.exit()
    prolig, pro, lig = XVG(prolig_xvg), XVG(pro_xvg), XVG(lig_xvg)
    if not (prolig.data_heads == pro.data_heads == lig.data_heads) or (
        len(prolig.data_heads) != 5
    ):
        logging.error(
            "three xvg files should contain same number (5) of columns, "
            + "and the order should be: \n"
            + "    Time, LJ(SR), Disper.corr., Coulomb(SR), Coul.recip. "
        )
        sys.exit()
    if not (
        ("Time" in prolig.data_heads[0])
        and ("LJ" in prolig.data_heads[1])
        and ("Disper" in prolig.data_heads[2])
        and ("Coulomb" in prolig.data_heads[3])
        and ("recip" in prolig.data_heads[4])
    ):
        logging.error(
            "the legend order should be: \n"
            + "    Time, LJ(SR), Disper.corr., Coulomb(SR), Coul.recip. "
        )
        sys.exit()
    if not (prolig.xvg_row_num == pro.xvg_row_num == lig.xvg_row_num):
        logging.error("{}, {}, {} should contain same number of rows.")
        sys.exit()
    if not (prolig.data_columns[0] == pro.data_columns[0] == lig.data_columns[0]):
        logging.error("the Time axis may not be the same, check the interval of time.")
        sys.exit()

    ## compute the bingding energy
    ## time
    out_data = [prolig.data_columns[0]] + [[] for _ in range(9)]
    out_heads = (
        [prolig.data_heads[0]]
        + [head for head in prolig.xvg_legends]
        + ["LJ(all)", "Coulomb(all)", "Short-Range", "Long-Range", "Total Energy"]
    )
    ## LJ(SR)
    out_data[1] = [
        prolig.data_columns[1][row]
        - pro.data_columns[1][row]
        - lig.data_columns[1][row]
        for row in range(prolig.xvg_row_num)
    ]
    ## Disper.corr.
    out_data[2] = [
        prolig.data_columns[2][row]
        - pro.data_columns[2][row]
        - lig.data_columns[2][row]
        for row in range(prolig.xvg_row_num)
    ]
    ## Coulomb(SR)
    out_data[3] = [
        prolig.data_columns[3][row]
        - pro.data_columns[3][row]
        - lig.data_columns[3][row]
        for row in range(prolig.xvg_row_num)
    ]
    ## Coul.recip.
    out_data[4] = [
        prolig.data_columns[4][row]
        - pro.data_columns[4][row]
        - lig.data_columns[4][row]
        for row in range(prolig.xvg_row_num)
    ]
    ## LJ(all)
    out_data[5] = [
        out_data[1][row] + out_data[2][row] for row in range(prolig.xvg_row_num)
    ]
    ## Coulomb(all)
    out_data[6] = [
        out_data[3][row] + out_data[4][row] for row in range(prolig.xvg_row_num)
    ]
    ## Short-Range
    out_data[7] = [
        out_data[1][row] + out_data[3][row] for row in range(prolig.xvg_row_num)
    ]
    ## Long-Range
    out_data[8] = [
        out_data[2][row] + out_data[4][row] for row in range(prolig.xvg_row_num)
    ]
    ## Total Energy
    out_data[9] = [
        out_data[5][row] + out_data[6][row] for row in range(prolig.xvg_row_num)
    ]

    ## write energy computation results
    with open(outfile, "w") as fo:
        fo.write("# this file was created by XVG.energy_compute through: \n")
        fo.write("#    binding = prolig energy - protein energy - ligand energy\n")
        fo.write('@    title "{}"\n'.format(prolig.xvg_title))
        fo.write('@    xaxis label "{}"\n'.format(out_heads[0]))
        fo.write('@    yaxis label "{}"\n'.format("(kJ/mol)"))
        fo.write("@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n")
        fo.write("@ legend on\n@ legend box on\n@ legend loctype view\n")
        fo.write("@ legend 0.78, 0.8\n@ legend length 9\n")
        for s in range(1, 10):
            fo.write('@ s{} legend "{}"\n'.format(s - 1, out_heads[s]))
        for row in range(prolig.xvg_row_num):
            fo.write(
                " ".join(["{:>16.6f}".format(out_data[i][row]) for i in range(10)])
                + "\n"
            )

    logging.info(
        "energy computation through {}, {} and {} sucessfully.".format(
            prolig_xvg, pro_xvg, lig_xvg
        )
    )


def xvg_ramachandran(xvgfile: str = "", outpng: str = "", noshow: bool = False) -> None:
    """
    convert xvg data into ramachandran plot

    :parameters:
        xvgfile: a xvg file contains phi, psi and AA name data which generated by gmx rama
        outpng: the output picture file name.
        noshow: whether not to show figure in GUI.
    """

    ## check parameters
    if not os.path.exists(xvgfile):
        logging.error("No {} in current directory".format(xvgfile))
        sys.exit()

    xvg = XVG(xvgfile)

    ## check column number
    if (
        len(xvg.xvg_columns) != 3
        or len(xvg.data_columns) != 2
        or (xvg.data_heads[0] != "Phi" or xvg.data_heads[1] != "Psi")
    ):
        logging.error(
            "Check your input xvg file ! It has to contains 3 columns: Phi, Psi, AA name. And x-label should be Phi and Y-label should be Psi"
        )
        sys.exit()

    ## draw background
    ## Psi and Phi data are from DOI: 10.1002/prot.10286
    ## reference : pyrama
    rama_preferences = {
        "General": {
            "file": os.path.join("data", "pref_general.data"),
            "cmap": mplcolors.ListedColormap(["#FFFFFF", "#B3E8FF", "#7FD9FF"]),
            "bounds": [0, 0.0005, 0.02, 1],
        },
        "GLY": {
            "file": os.path.join("data", "pref_glycine.data"),
            "cmap": mplcolors.ListedColormap(["#FFFFFF", "#FFE8C5", "#FFCC7F"]),
            "bounds": [0, 0.002, 0.02, 1],
        },
        "PRO": {
            "file": os.path.join("data", "pref_proline.data"),
            "cmap": mplcolors.ListedColormap(["#FFFFFF", "#D0FFC5", "#7FFF8C"]),
            "bounds": [0, 0.002, 0.02, 1],
        },
        "Pre-PRO": {
            "file": os.path.join("data", "pref_preproline.data"),
            "cmap": mplcolors.ListedColormap(["#FFFFFF", "#B3E8FF", "#7FD9FF"]),
            "bounds": [0, 0.002, 0.02, 1],
        },
    }

    rama_pref_values = {}
    for key, val in rama_preferences.items():
        data_file_path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        rama_pref_values[key] = [[0 for _ in range(361)] for _ in range(361)]
        with open(os.path.join(data_file_path, val["file"]), "r") as fn:
            for line in fn:
                if line.startswith("#"):
                    continue
                else:
                    phi = int(float(line.split()[0]))
                    psi = int(float(line.split()[1]))
                    ## plt.imshow show transpose of img
                    rama_pref_values[key][psi + 180][phi + 180] = float(line.split()[2])
                    rama_pref_values[key][psi + 179][phi + 180] = float(line.split()[2])
                    rama_pref_values[key][psi + 180][phi + 179] = float(line.split()[2])
                    rama_pref_values[key][psi + 179][phi + 179] = float(line.split()[2])

    normals, outliers = {}, {}
    for key in rama_preferences.keys():
        normals[key] = {"phi": [], "psi": []}
        outliers[key] = {"phi": [], "psi": []}
    for row in range(xvg.xvg_row_num):
        if row < xvg.xvg_row_num - 1 and "PRO" in xvg.xvg_columns[2][row + 1]:
            AA_type = "Pre-PRO"
        elif "PRO" in xvg.xvg_columns[2][row]:
            AA_type = "PRO"
        elif "GLY" in xvg.xvg_columns[2][row]:
            AA_type = "GLY"
        else:
            AA_type = "General"
        phi, psi = xvg.data_columns[0][row], xvg.data_columns[1][row]
        if (
            rama_pref_values[AA_type][int(psi) + 180][int(phi) + 180]
            < rama_preferences[AA_type]["bounds"][1]
        ):
            outliers[AA_type]["phi"].append(phi)
            outliers[AA_type]["psi"].append(psi)
        else:
            normals[AA_type]["phi"].append(phi)
            normals[AA_type]["psi"].append(psi)

    ## print some infos
    logging.info(
        "ramachandran method can draw four types of figure: "
        + "\n        Pre-PRO: the dihedrals of amino acids before prolines"
        + "\n        PRO: the dihedrals of prolines"
        + "\n        GLY: the dihedrals of glynine"
        + "\n        General: the dihedrals of other amino acids"
    )
    print("\n" + "-" * 79)
    print("{:<10} {:>20} {:>20}".format("", "Normal Dihedrals", "Outlier Dihedrals"))
    for key in ["General", "GLY", "Pre-PRO", "PRO"]:
        print(
            "{:<10} {:>20} {:>20}".format(
                key, len(normals[key]["phi"]), len(outliers[key]["phi"])
            )
        )
    print("-" * 79)

    ## draw ramachandran plot
    for key in ["General", "GLY", "Pre-PRO", "PRO"]:
        if len(normals[key]["phi"]) + len(outliers[key]["phi"]) == 0:
            continue
        plt.clf()
        plt.title(key)
        plt.imshow(
            rama_pref_values[key],
            cmap=rama_preferences[key]["cmap"],
            norm=colors.BoundaryNorm(
                rama_preferences[key]["bounds"], rama_preferences[key]["cmap"].N
            ),
            extent=(-180, 180, 180, -180),
        )
        plt.scatter(normals[key]["phi"], normals[key]["psi"], s=8)
        plt.scatter(outliers[key]["phi"], outliers[key]["psi"], s=8)
        plt.xlim([-180, 180])
        plt.ylim([-180, 180])
        plt.xticks([-180, -120, -60, 0, 60, 120, 180])
        plt.yticks([-180, -120, -60, 0, 60, 120, 180])
        plt.tick_params(left=False, bottom=False, top=False, right=False)
        plt.xlabel("Phi")
        plt.ylabel("Psi")
        if outpng != None:
            if os.path.exists(outpng):
                logging.error("{} already in current directory".format(outpng))
                sys.exit()
            plt.savefig(outpng.split(".")[0] + "_" + key + ".png", dpi=300)
        if noshow == False:
            plt.show()


def xvg_compare(
    xvgfiles: list = [],
    column_select: list = [],
    legend_list: list = [],
    start: int = 0,
    end: int = None,
    xlabel: str = None,
    ylabel: str = None,
    title: str = None,
    showMV: bool = False,
    windowsize: int = 50,
    confidence: float = 0.90,
    alpha: float = 0.4,
    outpng: str = "",
    noshow: bool = False,
    xshrink: float = None,
) -> None:
    """
    comparison of xvgfiles, draw different columns into figure.

    :parameters:
        xvgfiles: a list to store all xvg files you want to compare
        column_select: a list to store the columns you select to compare
                        This list has to contain lists with same number to xvg files
        legend_list: a list to store the legends you specify, and it's number should
                     be the same with column_index_list and xvgfilees
        start: the start index of column data you want to compare
        end: the end index of column data you want to compare
        xlabel: the xlabel of final figure
        ylabel: the ylbael of final figure
        title: the title of final figure
        showMV: whether to show moving average
        windowsize: the size of window for calculation of moving average
        confidence: the confidence to calculate interval
        alpha: the alpha (transparency) of figure
        outpng: the output picture file name.
        noshow: whether not to show figure in GUI.

    :example:
        xvg_compare([file1, file2], [[1,2], [2,3]],
                    ["legend1", "legend2", "legend3", "legend4"],
                    0, 100, "Time", "ylabel", "title")
    """

    ## check parameters
    if title == None:
        title = "XVG Comparison"
    if windowsize == None:
        windowsize = 50
    if confidence == None:
        confidence = 0.90
    if alpha == None:
        alpha = 0.4
    if legend_list == None:
        legend_list == []
    if len(xvgfiles) == 0:
        logging.error("no input xvg file to compare")
        sys.exit()
    if len(xvgfiles) != len(column_select):
        logging.error("column_select must contain {} list".format(len(xvgfiles)))
        sys.exit()
    for xvgs in xvgfiles:
        if not isinstance(xvgs, str):
            logging.error("item of xvgfiles should be str, do not use ,")
            sys.exit()
    if not isinstance(column_select, list):
        logging.error("column_select must be a list")
        sys.exit()
    for indexs in column_select:
        if isinstance(indexs, list):
            break
    else:
        column_select = [[columns] for columns in column_select]
    if len(legend_list) != 0 and len(legend_list) != sum(
        [len(column) for column in column_select]
    ):
        logging.error("number of legends you input can not pair to columns you select")
        sys.exit()
    if xshrink == None:
        xshrink = 1.0

    ## draw comparison
    plt.clf()
    XVGS = [XVG(xvg, xshrink) for xvg in xvgfiles]
    legend_count, xmin, xmax = 0, None, None
    for id, column_indexs in enumerate(column_select):
        xvg = XVGS[id]
        if showMV == True:
            _, mvaves, highs, lows = xvg.calc_mvave(windowsize, confidence)
        else:
            _, mvaves, highs, lows = [], [], [], []
        if start != None and start < 0:
            start = 0
        if end != None and (end >= xvg.xvg_row_num or end <= start):
            end = None
        if xlabel == None:
            xlabel = xvg.xvg_xlabel
        if ylabel == None:
            ylabel = xvg.xvg_ylabel
        for index in column_indexs:
            if len(legend_list) != 0:
                legend = legend_list[legend_count]
            else:
                legend = "{} of {}".format(xvg.data_heads[index], xvg.xvg_filename)
            legend_count += 1
            if xmin == None:
                xmin = min(xvg.data_columns[0][start:end])
            if xmax == None:
                xmax = max(xvg.data_columns[0][start:end])
            xmin = (min(xvg.data_columns[0][start:end]), xmin)[
                xmin < min(xvg.data_columns[0][start:end])
            ]
            xmax = (max(xvg.data_columns[0][start:end]), xmax)[
                xmax > max(xvg.data_columns[0][start:end])
            ]
            if showMV == True:
                plt.fill_between(
                    xvg.data_columns[0][start:end],
                    highs[index][start:end],
                    lows[index][start:end],
                    alpha=alpha,
                )
                plt.plot(
                    xvg.data_columns[0][start:end],
                    mvaves[index][start:end],
                    label=legend,
                )
            else:
                plt.plot(
                    xvg.data_columns[0][start:end],
                    xvg.data_columns[index][start:end],
                    label=legend,
                )
    plt.xlim(xmin, xmax)
    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if outpng != None:
        if os.path.exists(outpng):
            logging.error("{} already in current directory".format(outpng))
            sys.exit()
        plt.savefig(outpng, dpi=300)
    if noshow == False:
        plt.show()


def xvg_bar_compare(
    xvgfiles: list = [],
    column_list: list = [],
    legend_list: list = [],
    xtitle_list: list = [],
    start: int = 0,
    end: int = None,
    xlabel: str = None,
    ylabel: str = None,
    title: str = None,
    ave2csv: str = None,
    output: str = None,
    noshow: bool = False,
) -> None:
    """
    draw bar figure of averages of xvg files

    :parameters:
        xvgfiles: a list (with list in ) to store xvg files
                  eg. [["f0_0","f0_1","f0_2"], ["f1_0","f1_1","f1_2"]]
        column_list: a list to store column index
        legend_list: a list to store legends you specify
        xtitle_list: a list to store xtitles
        start: the start index of data
        end: th eend index of data
        xlabel: the xlabel of figure
        ylabel: the ylabel of figure
        title: the title of figure
        ave2csv: save average data to specified csv file
        output: the output picture file name.
        noshow: whether not to show figure in GUI.
    :example:
        average_bar_draw([["f0_0","f0_1","f0_2"], ["f1_0","f1_1","f1_2"]],
                        [1,2,3,4], ["l1","l2","l3","l4"], ["x1","x2","x3","x4"],
                        0, 10, "xlabel", "ylabel", "title", "bar_ave.csv",
                        "test.png", False)
    """

    ## check parameters
    if len(xvgfiles) == 0:
        logging.error("no input xvg files")
        sys.exit()
    if not isinstance(xvgfiles, list):
        logging.error("input files must be in list")
        sys.exit()
    for xvgs in xvgfiles:
        if isinstance(xvgs, list):
            break
    else:
        xvgfiles = [[xvg] for xvg in xvgfiles]

    if len(legend_list) != 0 and len(legend_list) != len(xvgfiles):
        logging.error("wrong number of legends you specified")
        sys.exit()
    if len(legend_list) == 0:
        for xvg_list in xvgfiles:
            legend_list.append(xvg_list[0])
    if xtitle_list == None:
        xtitle_list = []
    if len(xtitle_list) != 0 and len(xtitle_list) != len(column_list):
        logging.error("wrong number of legends you specified")
        sys.exit()
    if len(column_list) == 0:
        logging.error("please specify column_select")
        sys.exit()
    for columns in column_list:
        if not isinstance(columns, int):
            logging.error("the item of column_select must be int, do not use ,")
            sys.exit()

    ## calculate averages
    final_averages, final_stds = [], []
    for xvg_list in xvgfiles:
        column_averages_matrix = [[] for _ in column_list]
        for xvgfile in xvg_list:
            xvg = XVG(xvgfile)
            heads, averages, _ = xvg.calc_average(start, end)
            for index in column_list:
                if index >= len(heads):
                    logging.error(
                        "index {} is out of range of file {}".format(
                            index, xvg.xvg_filename
                        )
                    )
                    sys.exit()
            if len(xtitle_list) == 0:
                xtitle_list = [heads[c] for c in column_list]
            for i, value in enumerate([averages[c] for c in column_list]):
                column_averages_matrix[i].append(value)
        column_averages, column_stds = [], []
        for lis in column_averages_matrix:
            column_averages.append(np.mean(lis))
            column_stds.append(np.std(lis))
        final_averages.append(column_averages)
        final_stds.append(column_stds)

    # print averages
    print("\n" + " ".join("{:<20}".format(item) for item in ["Average"] + xtitle_list))
    for i in range(len(final_averages)):
        print("{:<20}".format(legend_list[i]), end=" ")
        print(" ".join(["{:<20.4f}".format(ave) for ave in final_averages[i]]))
    print("\n" + " ".join("{:<20}".format(item) for item in ["std"] + xtitle_list))
    for i in range(len(final_stds)):
        print("{:<20}".format(legend_list[i]), end=" ")
        print(" ".join(["{:<20.4f}".format(std) for std in final_stds[i]]))

    ## save average data to csv file
    if ave2csv != None:
        if len(ave2csv) < 4 or ave2csv[-4:] != ".csv":
            logging.error("file name for -ac should with suffix .csv")
            sys.exit()
        if os.path.exists(ave2csv):
            logging.error("{} is already in current directory".format(ave2csv))
            sys.exit()
        with open(ave2csv, "w") as fo:
            fo.write(",".join(["Average"] + xtitle_list) + "\n")
            for i in range(len(final_averages)):
                fo.write(legend_list[i] + ",")
                fo.write(",".join(["{:.4f}".format(ave) for ave in final_averages[i]]))
                fo.write("\n")
            fo.write(",".join(["std"] + xtitle_list) + "\n")
            for i in range(len(final_stds)):
                fo.write(legend_list[i] + ",")
                fo.write(",".join(["{:.4f}".format(std) for std in final_stds[i]]))
                fo.write("\n")

    ## draw bar figure
    plt.clf()
    width = 80 // len(xvgfiles) * 0.01
    x_loc = [x - 0.4 + width / 2.0 for x in range(len(column_list))]
    for i in range(len(final_averages)):
        plt.bar(
            [x + width * i for x in x_loc],
            final_averages[i],
            width,
            yerr=final_stds[i],
            capsize=2,
            label=legend_list[i],
        )
    plt.xticks([x for x in range(len(column_list))], labels=xtitle_list)
    plt.axhline(0, color="k", linewidth=1)
    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if output != None:
        if os.path.exists(output):
            logging.error("{} already in current directory".format(output))
            sys.exit()
        plt.savefig(output, dpi=300)
    if noshow == False:
        plt.show()


def xvg_box_compare(
    xvgfiles: list = [],
    column_select: list = [],
    xtitle_list: list = [],
    start: int = 0,
    end: int = None,
    xlabel: str = None,
    ylabel: str = None,
    title: str = None,
    outpng: str = "",
    noshow: bool = False,
) -> None:
    """
    convert xvg data into box figure

    :parameters:
        xvgfiles: a list to store input files
        column_select: a list to store column indexs
        xtitle_list: a list to store xtitles
        start: the start index of xvg data
        end: the end index of xvg data
        xlabel: xlabel of box figure
        ylabel: ylabel of box figure
        title: title of box figure
        outpng: the output picture file name.
        noshow: whether not to show figure in GUI.

    :example:
        xvg_box_compare(["f1", "f2"], [1,3], ["A", "B"], 0, 1000,
                        "xlabel", "ylabel", "title")
    """

    ## check parameters
    if title == None:
        title = "XVG box Comparison"
    if start == None:
        start = 0
    if xtitle_list == None:
        xtitle_list = []
    if column_select == None:
        column_select = []
    for xvgs in xvgfiles:
        if not isinstance(xvgs, str):
            logging.error("item of xvgfiles should be str, do not use ,")
            sys.exit()
    for column in column_select:
        if not isinstance(column, int):
            logging.error("item of column_select should be int, do not use ,")
            sys.exit()
    if len(xvgfiles) == 0:
        logging.error("no input xvg file to compare")
        sys.exit()
    if len(xtitle_list) != 0 and len(xtitle_list) != len(column_select):
        logging.error("number of xtitle you input can not pair to columns you select")
        sys.exit()

    ## draw bar comparison
    plt.clf()
    XVGS = [XVG(xvg) for xvg in xvgfiles]
    box_data, positions_list = [], []
    width = 80 // len(xvgfiles) * 0.01
    for id, xvg in enumerate(XVGS):
        if start < 0 or start > xvg.xvg_row_num:
            logging.warning("start index not in proper range, set it to be 0")
            start = 0
        if end != None and (end <= start or end >= xvg.xvg_row_num):
            logging.warning("end index not in proper range, set it to be None")
            end = None
        for index, column in enumerate(column_select):
            box_data.append(xvg.data_columns[column][start:end])
            positions_list.append(index - 0.4 + width / 2.0 + width * id)

    plt.boxplot(box_data, meanline=True, showmeans=True, positions=positions_list)
    if len(xtitle_list) == 0:
        xtitle_list = [XVGS[0].data_heads[i] for i in column_select]
    plt.xticks([i for i in range(len(column_select))], xtitle_list)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    if outpng != None:
        if os.path.exists(outpng):
            logging.error("{} already in current directory".format(outpng))
            sys.exit()
        plt.savefig(outpng, dpi=300)
    if noshow == False:
        plt.show()


def xvg_calc_ave(file: str = None, start: int = None, end: int = None) -> None:
    """do average calculation and print results"""
    if file == None:
        logging.error("no input file")
        sys.exit()
    xvg = XVG(file)
    heads, averages, stds = xvg.calc_average(start, end)
    print("\n" + "-" * 79)
    print("".join(["{:>16}".format(item) for item in [" "] + heads]))
    print(
        "".join(
            ["{:>16}".format("ave")] + ["{:>16.4f}".format(item) for item in averages]
        )
    )
    print(
        "".join(["{:>16}".format("std")] + ["{:>16.4f}".format(item) for item in stds])
    )


def xvg_calc_mvave2csv(
    file: str = None, outcsv: str = None, windowsize: int = 50, confidence: float = 0.90
) -> None:
    """do moving average calculation and output data to csv"""
    if file == None:
        logging.error("no input file")
        sys.exit()
    if outcsv == None:
        logging.error("specify the output csv file name")
        sys.exit()
    if os.path.exists(outcsv):
        logging.error("{} already in current directory".format(outcsv))
        sys.exit()
    if windowsize == None:
        windowsize = 50
    if confidence == None:
        confidence = 0.90
    xvg = XVG(file)
    heads, mvaves, _, _ = xvg.calc_mvave(windowsize, confidence)
    with open(outcsv, "w") as fo:
        fo.write(",".join(heads) + "\n")
        for row in range(xvg.xvg_row_num):
            fo.write(",".join(["{}".format(column[row]) for column in mvaves]))
            fo.write("\n")
    logging.info("moving averages have been saved to {}".format(outcsv))


def xvg2csv(xvgfile: str = "", outcsv: str = "") -> None:
    """convert xvg file to csv file"""
    xvg = XVG(xvgfile)
    xvg.xvg2csv(outcsv)


def xvg_show(
    xvgfile: str = "", outpng: str = "", noshow: bool = False, subplot=False
) -> None:
    """visualization of xvg file"""
    xvg = XVG(xvgfile)
    if subplot == True:
        xvg.draw_subplot(outpng, noshow)
    else:
        xvg.draw(outpng, noshow)


def xvg_show_distribution(
    xvgfile: str = "", bin: int = 100, outpng: str = "", noshow: bool = False
) -> None:
    """visualization of distribution of xvg data"""
    if bin == None:
        bin = 100
    xvg = XVG(xvgfile)
    xvg.draw_distribution(bin, outpng, noshow)


def xvg_show_stacking(
    xvgfile: str = "",
    column_select: list = [],
    legend_list: list = [],
    start: int = 0,
    end: int = None,
    outpng: str = "",
    noshow: bool = False,
    xshrink: float = None,
    xlabel: str = None,
    ylabel: str = None,
) -> None:
    """visualization of stacked xvg data"""
    if xshrink == None:
        xshrink = 1.0
    xvg = XVG(xvgfile, xshrink)
    xvg.draw_stacking(
        column_select, legend_list, start, end, outpng, noshow, xlabel, ylabel
    )


def xvg_show_scatter(
    xvgfile: str = "",
    x_index: int = 0,
    y_index: int = None,
    column_select: list = [],
    outpng: str = "",
    noshow: bool = False,
) -> None:
    """visualization of scatter plot of xvg file"""
    color_index = None
    if len(column_select) == 1 and isinstance(column_select[-1], int):
        color_index = int(column_select[-1])
    elif len(column_select) == 0:
        pass
    else:
        logging.error("There should be only one color index which is a number")
        sys.exit()
    if x_index == None:
        x_index = 0
    xvg = XVG(xvgfile)
    xvg.draw_scatter(x_index, y_index, color_index, outpng, noshow)


def xvg_call_functions(arguments: list = None):
    """call functions by method"""

    if arguments == None:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(description="GROMACS Simple Analysis Tool")
    parser.add_argument("-f", "--input", nargs="+", help="input your file or files")
    parser.add_argument("-o", "--output", type=str, help="file name for output")
    parser.add_argument("-s", "--start", type=int, help="the start index of data")
    parser.add_argument("-e", "--end", type=int, help="the end index of data")
    parser.add_argument("-x", "--xlabel", type=str, help="the xlabel of figure")
    parser.add_argument("-y", "--ylabel", type=str, help="the ylabel of figure")
    parser.add_argument("-t", "--title", type=str, help="the title of figure")
    parser.add_argument(
        "-c", "--column_select", nargs="+", help="to select column of data"
    )
    parser.add_argument(
        "-l", "--legend_list", nargs="+", help="the legends you wanna specify"
    )
    parser.add_argument(
        "-ws",
        "--windowsize",
        type=int,
        help="window size for moving average calculation",
    )
    parser.add_argument(
        "-cf",
        "--confidence",
        type=float,
        help="confidence for confidence interval calculation",
    )
    parser.add_argument(
        "-bin", "--bin", type=int, help="the bin number for distribution calculation"
    )
    parser.add_argument(
        "-xi", "--x_index", type=int, help="the x index of data for drawing scatter"
    )
    parser.add_argument(
        "-yi", "--y_index", type=int, help="the y index of data for drawing scatter"
    )
    parser.add_argument(
        "-smv", "--showMV", action="store_true", help="whether to show moving average"
    )
    parser.add_argument(
        "-ns", "--noshow", action="store_true", help="whether not to show figure"
    )
    parser.add_argument(
        "-a", "--alpha", type=float, help="the alpha of background lines"
    )
    parser.add_argument(
        "-ac",
        "--ave2csv",
        help="the output csv file name to save averages, used in xvg_bar_draw",
    )
    parser.add_argument(
        "-xt", "--xtitles", nargs="+", help="the x tick labels for box comparison"
    )
    parser.add_argument(
        "-subplot", "--subplot", action="store_true", help="whether to show in subplots"
    )
    parser.add_argument(
        "-xs", "--xshrink", type=float, help="modify x-axis by multipling xshrink"
    )

    if len(arguments) < 2:
        logging.error("no input parameters, -h or --help for help messages")
        sys.exit()
    method = arguments[1]
    # print(method)
    if method in ["-h", "--help"]:
        parser.parse_args(arguments[1:])
        sys.exit()
    args = parser.parse_args(arguments[2:])
    # for key, value in vars(args).items():
    #     print(key, value)

    ## process nargs="+"
    if args.input == None:
        logging.error("No input parameters")
        sys.exit()
    xvgfiles = []
    if "," in "".join(args.input):
        for xvgs in args.input:
            xvgfiles.append(xvgs.strip(",").split(","))
    else:
        xvgfiles = [f for f in args.input]
    column_select = []
    if args.column_select != None:
        if "," in "".join(args.column_select):
            for columns in args.column_select:
                column_select.append([int(c) for c in columns.strip(",").split(",")])
        else:
            column_select = [int(c) for c in args.column_select]
    legend_list = []
    if args.legend_list != None:
        if "," in "".join(args.legend_list):
            for legends in args.legend_list:
                ## ~~ is used to reprensent space
                legend_list.append(
                    [l.replace("~~", " ") for l in legends.strip(",").split(",")]
                )
        else:
            ## ~~ Is used to reprensent space
            legend_list = [l.replace("~~", " ") for l in args.legend_list]
    firstfile = (xvgfiles[0], xvgfiles[0][0])[isinstance(xvgfiles[0], list)]

    ## call functions
    if method == "xvg_ave":
        xvg_calc_ave(firstfile, args.start, args.end)
    elif method == "xvg_mvave":
        xvg_calc_mvave2csv(firstfile, args.output, args.windowsize, args.confidence)
    elif method == "xvg2csv":
        xvg2csv(firstfile, args.output)
    elif method == "xvg_show":
        xvg_show(firstfile, args.output, args.noshow, args.subplot)
    elif method == "xvg_rama":
        xvg_ramachandran(firstfile, args.output, args.noshow)
    elif method == "xvg_show_distribution":
        xvg_show_distribution(firstfile, args.bin, args.output, args.noshow)
    elif method == "xvg_show_stack":
        xvg_show_stacking(
            firstfile,
            column_select,
            legend_list,
            args.start,
            args.end,
            args.output,
            args.noshow,
            args.xshrink,
            args.xlabel,
            args.ylabel,
        )
    elif method == "xvg_show_scatter":
        xvg_show_scatter(
            firstfile,
            args.x_index,
            args.y_index,
            column_select,
            args.output,
            args.noshow,
        )
    elif method == "xvg_energy_compute":
        energy_compute(xvgfiles, args.output)
    elif method == "xvg_combine":  # [], [[],[]]
        xvg_combine(xvgfiles, column_select, args.output)
    elif method == "xvg_compare":  # [], [[], []]
        xvg_compare(
            xvgfiles,
            column_select,
            legend_list,
            args.start,
            args.end,
            args.xlabel,
            args.ylabel,
            args.title,
            args.showMV,
            args.windowsize,
            args.confidence,
            args.alpha,
            args.output,
            args.noshow,
            args.xshrink,
        )
    elif method == "xvg_ave_bar":  # [[], []], []
        xvg_bar_compare(
            xvgfiles,
            column_select,
            legend_list,
            args.xtitles,
            args.start,
            args.end,
            args.xlabel,
            args.ylabel,
            args.title,
            args.ave2csv,
            args.output,
            args.noshow,
        )
    elif method == "xvg_box":  # [], []
        xvg_box_compare(
            xvgfiles,
            column_select,
            args.xtitles,
            args.start,
            args.end,
            args.xlabel,
            args.ylabel,
            args.title,
            args.output,
            args.noshow,
        )
    else:
        logging.error("no command {} found".format(method))
        sys.exit()

    logging.info("May you good day !")


def main():
    xvg_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
