"""
DSSP module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to deal and present figures about secondary structure

This DSSP module contains:
    - DSSP function

This file is provided to you by GPLv3 license."""

import os
import sys
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt


base = os.path.dirname(os.path.realpath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from XPM import XPM


def dssp(
    xpmfile: str = None,
    xlabel: str = None,
    ylabel: str = None,
    title: str = None,
    xshrink: float = 1.0,
):
    """read xpm file, generate xpm figure, stacked Residue vs time, stacked time occupancy vs residue"""

    xpm = XPM(xpmfile, xlabel, ylabel, title, xshrink)
    xpm.draw_origin(False, None, False)

    xpm.xpm_datalines.reverse()
    xpm.xpm_yaxis.reverse()
    xpm_datamatrix = []
    for dataline in xpm.xpm_datalines:
        dot_list = []
        for i in range(
            0, xpm.xpm_width * xpm.xpm_char_per_pixel, xpm.xpm_char_per_pixel
        ):
            dot_list.append(xpm.chars.index(dataline[i : i + xpm.xpm_char_per_pixel]))
        xpm_datamatrix.append(dot_list)

    # residue_occupancy
    residue_occupancy_dic = {k: [] for k in xpm.notes}
    for x, xaxis in enumerate(xpm.xpm_xaxis):
        for key in residue_occupancy_dic.keys():
            residue_occupancy_dic[key].append(0)
        for y, yaxis in enumerate(xpm.xpm_yaxis):
            dot = xpm_datamatrix[y][x]
            key = xpm.notes[dot]
            residue_occupancy_dic[key][-1] += 1
    labels = [k for k in residue_occupancy_dic.keys()]
    labels.reverse()
    data_columns = [residue_occupancy_dic[l] for l in labels]
    if "residue_occupancy_data.csv" in os.listdir():
        logging.error(
            "residue_occupancy_data.csv already in current directory, unable to output file with same name"
        )
        sys.exit()
    with open("residue_occupancy_data.csv", "w") as fo:
        fo.write(",".join(labels) + "\n")
        for t in range(len(data_columns[0])):
            fo.write(
                ",".join([str(data_columns[d][t]) for d in range(len(data_columns))])
                + "\n"
            )
    ylim_max, ylim_min = 0, 0
    for index, _ in enumerate(labels):
        stack_data = [
            sum([data_columns[c][x] for c in range(index, len(labels))])
            for x in range(len(xpm.xpm_xaxis))
        ]
        plt.fill_between(
            xpm.xpm_xaxis,
            stack_data,
            [0 for _ in range(len(stack_data))],
            label=labels[index],
        )
        ylim_max = (ylim_max, max(stack_data))[ylim_max < max(stack_data)]
        ylim_min = (ylim_min, min(stack_data))[ylim_min > min(stack_data)]

    plt.xlabel(xpm.xpm_xlabel)
    plt.ylabel(xpm.xpm_ylabel)
    plt.title("Stacked plot of " + xpm.xpm_title)
    plt.xlim(
        np.min(xpm.xpm_xaxis),
        np.max(xpm.xpm_xaxis),
    )
    plt.ylim(ylim_min, ylim_max)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

    # time_occupancy
    time_occupancy_dic = {k: [] for k in xpm.notes}
    for y, yaxis in enumerate(xpm.xpm_yaxis):
        for key in time_occupancy_dic.keys():
            time_occupancy_dic[key].append(0)
        for x, xaxis in enumerate(xpm.xpm_xaxis):
            dot = xpm_datamatrix[y][x]
            key = xpm.notes[dot]
            time_occupancy_dic[key][-1] += 1
    labels = [k for k in time_occupancy_dic.keys()]
    labels.reverse()
    data_columns = [time_occupancy_dic[l] for l in labels]
    if "time_occupancy_data.csv" in os.listdir():
        logging.error(
            "time_occupancy_data.csv already in current directory, unable to output file with same name"
        )
        sys.exit()
    with open("time_occupancy_data.csv", "w") as fo:
        fo.write(",".join(labels) + "\n")
        for t in range(len(data_columns[0])):
            fo.write(
                ",".join([str(data_columns[d][t]) for d in range(len(data_columns))])
                + "\n"
            )
    ylim_max, ylim_min = 0, 0
    for index, _ in enumerate(labels):
        stack_data = [
            sum([data_columns[c][x] for c in range(index, len(labels))])
            for x in range(len(xpm.xpm_yaxis))
        ]
        plt.bar(xpm.xpm_yaxis, stack_data, label=labels[index], width=1)
        # plt.fill_between(
        #     xpm.xpm_yaxis,
        #     stack_data,
        #     [0 for _ in range(len(stack_data))],
        #     label=labels[index],
        # )
        ylim_max = (ylim_max, max(stack_data))[ylim_max < max(stack_data)]
        ylim_min = (ylim_min, min(stack_data))[ylim_min > min(stack_data)]

    plt.xlabel(xpm.xpm_ylabel)
    plt.ylabel(xpm.xpm_xlabel)
    ytics, _ = plt.yticks()
    yticklabels = [xpm.xpm_xaxis[int(y)] for y in ytics[:-1]]
    plt.yticks(ytics[:-1], yticklabels)
    plt.title("Stacked plot of " + xpm.xpm_title)
    plt.xlim(np.min(xpm.xpm_yaxis) - 0.5, np.max(xpm.xpm_yaxis) + 0.5)
    plt.ylim(ylim_min, ylim_max)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()


def dssp_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(
        description="hbond command process the hbond infos"
    )
    parser.add_argument("-f", "--input", help="the xpm file for input")
    parser.add_argument(
        "-xs",
        "--xshrink",
        type=float,
        default=1.0,
        help="modify x-axis by multipling xshrink",
    )
    parser.add_argument("-x", "--xlabel", type=str, help="the xlabel of figure")
    parser.add_argument("-y", "--ylabel", type=str, help="the ylabel of figure")
    parser.add_argument("-t", "--title", type=str, help="the title of figure")

    if len(arguments) < 2:
        logging.error("no input parameters, -h or --help for help messages")
        exit()

    method = arguments[1]
    if method in ["-h", "--help"]:
        parser.parse_args(arguments[1:])
        exit()
    if len(arguments) == 2:
        logging.error("no parameters, type 'dit <command> -h' for more infos.")
        exit()

    args = parser.parse_args(arguments[2:])

    if method == "dssp":
        xpmfile = args.input
        xshrink = args.xshrink
        dssp(xpmfile, args.xlabel, args.ylabel, args.title, xshrink)
    else:
        logging.error("unknown method {}".format(method))
        exit()

    logging.info("May you good day !")


def main():
    dssp_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
