"""
hbond module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to process hbond information.

This module contains:
    - hbond function

This file is provided to you by GPLv2 license."""


################################
#### TODO:
#### 2. user defination of hbond name format
################################

import os
import sys
import logging
import argparse
from XPM import XPM
import matplotlib.pyplot as plt
from matplotlib import pylab as pylab
import matplotlib.colors as mcolors

logging.basicConfig(level=logging.INFO, format='%(levelname)s -> %(message)s')
logger = logging.getLogger(__name__)

myparams = {
    "axes.labelsize": "12",
    "xtick.labelsize": "12",
    "ytick.labelsize": "12",
    "ytick.left": False,
    "ytick.direction": "in",
    "xtick.bottom": False,
    "xtick.direction": "in",
    "lines.linewidth": "2",
    "axes.linewidth": "1",
    "legend.fontsize": "12",
    "legend.loc": "upper right",
    "legend.fancybox": False,
    "legend.frameon": False,
    "font.family": "Arial",
    "font.size": 12,
    "figure.dpi": 150,
    "savefig.dpi": 300,
}
pylab.rcParams.update(myparams)
style_files = [file for file in os.listdir() if file[-9:] == ".mplstyle"]
if len(style_files) >= 1:
    plt.style.use(style_files[0])
    # logging.info("using matplotlib style sheet from {}".format(style_files[0]))


def hbond(xpmfile: str = "", ndxfile: str= "", grofile: str = "", select:list=[], noshow:bool=False, figout:str=None, csv:str=None) -> None:
    """
    hbond: a function to figure out hbond information, occupancy and occupancy
    map, occupancy table.
    This function will read one gro file, one hbmap.xpm, one hbond.ndx, and 
    return some hbond information.

    :parameters:
        gro_file: the gro file which saved coordinates to pare atom names
        hbmap.xpm: the hbond occupancy map file generated by 'gmx hbond'
        hbond.ndx: the index file generated by 'gmx hbond'

    :return:
        None
    """
    
    for suffix, file in zip([".xpm", ".ndx", ".gro"], [xpmfile, ndxfile, grofile]):
        if file == None:
            logging.error("You have to specify the {} file for input".format(suffix))
            sys.exit()
        if not os.path.exists(file):
            logging.error("no {} in current dirrectory. ".format(file))
            sys.exit()
        if file[-4:] != suffix:
            logging.error("only accept {} file with suffix {}".format(suffix.strip("."), suffix))
            sys.exit()

    ## parse ndx file to get index of hydrogen bonds
    donor_ndxs, hydrogen_ndxs, acceptor_ndxs = [], [], []
    with open(ndxfile, 'r') as fo:
        lines = [ line for line in fo.readlines() if line.strip()]
    lines.reverse()
    for line in lines:
        if "hbonds_" in line:
            break
        items = line.split()
        donor_ndxs.append(int(items[0].strip()))
        hydrogen_ndxs.append(int(items[1].strip()))
        acceptor_ndxs.append(int(items[2].strip()))
    donor_ndxs.reverse()
    hydrogen_ndxs.reverse()
    acceptor_ndxs.reverse()
    if len(donor_ndxs) != len(hydrogen_ndxs) != len(acceptor_ndxs):
        logging.error("wrong length in donor, hydrogen, acceptor indexs")
        sys.exit()

    ## read the gro file and parse atom names
    donor_names, hydrogen_names, acceptor_names = [], [], []
    with open(grofile, 'r') as fo:
        lines = fo.readlines()[2:-1]
    for ind in donor_ndxs:
        line = lines[ind-1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        donor_names.append(name)
    for ind in hydrogen_ndxs:
        line = lines[ind-1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        hydrogen_names.append(name)
    for ind in acceptor_ndxs:
        line = lines[ind-1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        acceptor_names.append(name)
    if len(donor_names) != len(hydrogen_names) != len(acceptor_names) != len(acceptor_ndxs):
        logging.error("wrong length in donor, hydrogen, acceptor names")
        sys.exit()
    hbond_names = [ f'{donor_names[i]}->{hydrogen_names[i].split("@")[1]}...{acceptor_names[i]}' for i in range(len(donor_names))]

    ## parse xpmfile
    xpm = XPM(xpmfile)
    if xpm.xpm_height < len(hbond_names):
        logging.warning("height of xpm ({}) in {} is not equal to number of hbond ({}) in {}, removed the excess in xpm".format(xpm.xpm_height, xpmfile, len(hydrogen_names), ndxfile))
        gap = xpm.xpm_height - len(hbond_names)
        xpm.xpm_height -= gap
        xpm.xpm_datalines = xpm.xpm_datalines[gap:]
        xpm.xpm_yaxis = xpm.xpm_yaxis[gap:]
    xpm.xpm_datalines.reverse()
    xpm.xpm_yaxis.reverse()

    ## get occupancy
    occupancy, xpm_datamatrix = [], []
    for dataline in xpm.xpm_datalines:
        dot_list = []
        for i in range(0, xpm.xpm_width*xpm.xpm_char_per_pixel, xpm.xpm_char_per_pixel):
            dot_list.append(xpm.chars.index(dataline[i:i+xpm.xpm_char_per_pixel]))
        xpm_datamatrix.append(dot_list)
        occupancy.append(sum(dot_list)/(1.0*len(dot_list)))

    ## deal with the selection
    # select = [5]
    if select == []:
        select = [ i for i in range(len(hbond_names)) ]
    else:
        occupancy = [ occupancy[i] for i in select]
        xpm_datamatrix = [xpm_datamatrix[i] for i in select]
        hbond_names = [ hbond_names[i] for i in select]

    ## draw map 
    plt.figure()
    cmap = mcolors.ListedColormap(["white", "#F94C66"])
    hbond = plt.pcolormesh(xpm.xpm_xaxis, [i for i in range(len(select))], xpm_datamatrix, cmap=cmap, shading="auto")
    if len(select) == 1:
        hbond = plt.imshow(xpm_datamatrix, cmap=cmap, aspect="auto")
    cb = plt.colorbar(hbond, orientation="horizontal", fraction=0.03)
    cb.set_ticks([0.25, 0.75])
    cb.set_ticklabels(["None", "Present"])
    for i in range(1, len(select)):
        plt.hlines(i-0.5, min(xpm.xpm_xaxis), max(xpm.xpm_xaxis), colors="white")
    plt.title(xpm.xpm_title)
    plt.xlabel(xpm.xpm_xlabel)
    plt.ylabel(xpm.xpm_ylabel)
    if xpm.xpm_height <= 10:
        plt.yticks([i for i in range(len(select))], hbond_names)
    plt.tight_layout()
    if figout != None:
        plt.savefig(figout, dpi=300)
    if not noshow:
        plt.show()

    ## show table
    print("-"*79)
    print("{:<2} {:<60} {}".format("id", "donor->hydrogen...acceptor", "occupancy(%)"))
    print("-"*79)
    for i in range(len(hbond_names)):
        print("{:<2d} {:<60} {:.2f}".format(select[i], hbond_names[i], occupancy[i]*100.0))
    print("-"*79)
    if csv != None:
        with open(csv, 'w') as fo:
            fo.write("{},{},{}\n".format("id", "donor->hydrogen...acceptor", "occupancy(%)"))
            for i in range(len(hbond_names)):
                fo.write("{},{},{:.2f}\n".format(select[i], hbond_names[i], occupancy[i]*100.0))



def hbond_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(description="hbond command process the hbond infos")
    parser.add_argument("-f", "--input", help="gro file for input")
    parser.add_argument("-n", "--index", help="hbond ndx file for input")
    parser.add_argument("-m", "--map", help="hbond map file for input")
    parser.add_argument(
        "-c", "--select", nargs="+", help="to select row of data, like: 1 2-4 6"
    )
    parser.add_argument("-o", "--output", help="figure name for output")
    parser.add_argument("-csv", "--csv", help="store table info into csv file")
    parser.add_argument(
        "-ns",
        "--noshow",
        action="store_true",
        help="whether not to show picture, useful on computer without gui",
    )

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
    select = []
    if args.select != None:
        for c in args.select:
            if "-" in c.strip("-"):
                select += [ i for i in range(int(c.split("-")[0]), int(c.split("-")[1]))]
            else:
                select.append(int(c))

    if method == "hbond":
        grofile = args.input
        ndxfile = args.index
        xpmfile = args.map
        noshow = args.noshow
        figout = args.output
        csv = args.csv
        hbond(xpmfile, ndxfile, grofile, select, noshow, figout, csv)
    else:
        logging.error("unknown method {}".format(method))
        exit()

    logging.info("May you good day !")


def main():
    hbond_call_functions()


if __name__ == "__main__":
    main()
