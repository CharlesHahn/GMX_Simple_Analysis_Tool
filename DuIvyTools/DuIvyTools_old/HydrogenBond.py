"""
hbond module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to process hbond information.

This module contains:
    - hbond function

This file is provided to you by GPLv3 license."""

import os
import sys
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from pathlib import Path

base = os.path.dirname(os.path.realpath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from XPM import XPM
from XVG import XVG


def gen_distang_script(donor_ndxs, hydrogen_ndxs, acceptor_ndxs, select):
    """generate scripts to calculate distance and angles of hbond

    Args:
        donor_ndxs (list): donor atom indexs
        hydrogen_ndxs (list): hydrogen atom indexs
        acceptor_ndxs (list): acceptor atom indexs
        select (list): the selected hbond ids
    """

    ## calc distance of donor - acceptor
    for ndx in ["hbdist.ndx", "hbang.ndx"]:
        if ndx in os.listdir():
            logging.error("{} is already in current directory!".format(ndx))
            sys.exit()

    tail = -1
    with open("hbdist.ndx", "w") as fo:
        fo.write("[ hbdist ] \n")
        for i in select:
            if donor_ndxs[i] != tail:
                fo.write("{}  {} \n".format(donor_ndxs[i], acceptor_ndxs[i]))
                tail = acceptor_ndxs[i]
            else:
                fo.write("{}  {} \n".format(acceptor_ndxs[i], donor_ndxs[i]))
                tail = donor_ndxs[i]

    ## gmx distance -f xtc -s tpr -n hbdist.ndx -oall hbdistall.xvg -select '"group"'
    hbdist_script = "run_hbdist.sh"
    if hbdist_script in os.listdir():
        logging.error("{} is already in current directory!".format(hbdist_script))
        sys.exit()
    with open(hbdist_script, "w") as fo:
        fo.write(
            """gmx distance -f xxx.xtc -s xxx.tpr -n hbdist.ndx -oall hbdistall.xvg -select '"hbdist"'"""
        )

    ## calc angle : hydrogen - donor - acceptor
    with open("hbang.ndx", "w") as fo:
        fo.write("[ hbang ] \n")
        for i in select:
            fo.write(
                "{} {} {} \n".format(hydrogen_ndxs[i], donor_ndxs[i], acceptor_ndxs[i])
            )
    ## gmx angle -f xxx.xtc -n hbangndx.ndx -ov hbangall.xvg -all -od angdist.xvg
    hbang_script = "run_hbang.sh"
    if hbang_script in os.listdir():
        logging.error("{} is already in current directory!".format(hbang_script))
        sys.exit()
    with open(hbang_script, "w") as fo:
        fo.write("""gmx angle -f xxx.xtc -n hbang.ndx -ov hbangall.xvg -all""")

    logging.info(
        """
        Please notice: 
            1. if you applied -dt, -b or -e in your command when calculating `gmx hbond`, add same parameters to scripts when calculating distance or angle of hbonds.
            2. YOU MUST apply `-merge no` to `gmx hbond` to get correct atom ids which if critically IMPORTANT for calculating angles and distances of hbonds. 
        """
    )


def calculate_distance_angle(
    xpm_datamatrix: list,
    hbond_names: list,
    distfile: str,
    angfile: str,
    figout: str = None,
    noshow: bool = False,
    xshrink: float = 1,
    xlabel: str = None,
):
    """calculate average distance and angle, draw figures.

    Args:
        xpm_datamatrix (list): source data
        hbond_names (list): name of hbonds
        distfile (str): file name of distances
        angfile (str): file name of angles
    """
    if len(xpm_datamatrix) != len(hbond_names):
        logging.error(
            "wrong in length of datamatrix and hbond names while calculating distances and angles"
        )
        sys.exit()
    if xshrink == None:
        xshrink = 1.0
    print(xshrink)
    dist_xvg = XVG(distfile)
    ang_xvg = XVG(angfile)
    if dist_xvg.xvg_column_num != len(xpm_datamatrix) + 1:
        logging.error("wrong in column number of distance xvg file, check select!")
        sys.exit()
    if ang_xvg.xvg_column_num != len(xpm_datamatrix) + 2:
        logging.error("wrong in column number of distance xvg file, check select!")
        sys.exit()
    if dist_xvg.xvg_row_num != ang_xvg.xvg_row_num != len(xpm_datamatrix[0]):
        logging.error("wrong in length of row, check time selection clearfully!")
        sys.exit()

    ## calc average distance and angle
    dist_ave_std, ang_ave_std = [], []
    for i, dot_line in enumerate(xpm_datamatrix):
        dot_line = np.array(dot_line)
        dist_line = dist_xvg.xvg_columns[i + 1]
        ang_line = ang_xvg.xvg_columns[i + 2]
        dist_present = np.array(dist_line)[dot_line == 1].astype(float)
        ang_present = np.array(ang_line)[dot_line == 1].astype(float)
        dist_ave = np.average(dist_present)
        dist_std = np.std(dist_present, ddof=1)
        ang_ave = np.average(ang_present)
        ang_std = np.std(ang_present, ddof=1)
        dist_ave_std.append((dist_ave, dist_std))
        ang_ave_std.append((ang_ave, ang_std))

    ## draw distance and angle figure
    plt.clf()
    dist_time = np.array(dist_xvg.xvg_columns[0]).astype(float)
    dist_time = dist_time * xshrink
    for i, hbond_name in enumerate(hbond_names):
        dist_line = np.array(dist_xvg.xvg_columns[i + 1]).astype(float)
        plt.plot(dist_time, dist_line, label=hbond_name)
    # plt.plot(dist_time, [0.35 for d in dist_time], "grey")
    if xlabel != None:
        plt.xlabel(xlabel)
    else:
        plt.xlabel(dist_xvg.xvg_xlabel)
    plt.ylabel(dist_xvg.xvg_ylabel)
    plt.title(dist_xvg.xvg_title)
    plt.legend()
    if figout != None:
        plt.savefig("hbond_dist_" + figout, dpi=300)
    if not noshow:
        plt.show()

    plt.clf()
    ang_time = np.array(ang_xvg.xvg_columns[0]).astype(float)
    ang_time = ang_time * xshrink
    for i, hbond_name in enumerate(hbond_names):
        ang_line = np.array(ang_xvg.xvg_columns[i + 2]).astype(float)
        plt.plot(ang_time, ang_line, label=hbond_name)
    # plt.plot(ang_time, [30 for d in dist_time], "grey")
    if xlabel != None:
        plt.xlabel(xlabel)
    else:
        plt.xlabel(dist_xvg.xvg_xlabel)
    plt.ylabel(ang_xvg.xvg_ylabel)
    plt.title(ang_xvg.xvg_title)
    plt.legend()
    if figout != None:
        plt.savefig("hbond_angle_" + figout, dpi=300)
    if not noshow:
        plt.show()

    return dist_ave_std, ang_ave_std


def hbond(
    xpmfile: str = "",
    ndxfile: str = "",
    grofile: str = "",
    select: list = [],
    noshow: bool = False,
    figout: str = None,
    csv: str = None,
    hnf: str = None,
    genscript: bool = False,
    calc_distance_angle: bool = False,
    distancefile: str = None,
    anglefile: str = None,
    xshrink: float = 1.0,
    xlabel: str = None,
    set_operation: str = None,
) -> None:
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
            logging.error(
                "only accept {} file with suffix {}".format(suffix.strip("."), suffix)
            )
            sys.exit()

    ## parse set operation list
    if set_operation != None:
        set_id_list = []
        if set_operation.startswith("AND"):
            set_flag = "AND"
            set_strs = set_operation[3:].strip().split()
        elif set_operation.startswith("OR"):
            set_flag = "OR"
            set_strs = set_operation[2:].strip().split()
        for set_str in set_strs:
            items = set_str.split(",")
            for item in items:
                if "-" in item:
                    set_id_list += [
                        i
                        for i in range(
                            int(item.split("-")[0]), int(item.split("-")[1]) + 1
                        )
                    ]
                else:
                    set_id_list.append(int(item))

    ## parse ndx file to get index of hydrogen bonds
    donor_ndxs, hydrogen_ndxs, acceptor_ndxs = [], [], []
    with open(ndxfile, "r") as fo:
        lines = [line for line in fo.readlines() if line.strip()]
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
    if hnf == None:
        hnf = (
            "d_resname(d_resnum)@d_atomname(d_atomnum)->h_atomname("
            + "h_atomnum)...a_resname(a_resnum)@a_atomname(a_atomnum)"
        )
    features = [
        "d_resname",
        "d_resnum",
        "d_atomname",
        "d_atomnum",
        "h_resname",
        "h_resnum",
        "h_atomname",
        "h_atomnum",
        "a_resname",
        "a_resnum",
        "a_atomname",
        "a_atomnum",
    ]
    for feature in features:
        if feature in hnf or hnf == "number" or hnf == "id":
            break
    else:
        logging.warning(
            "no key feature detected in your specified hbond name "
            + "format, use the default format"
        )
        hnf = (
            "d_resname(d_resnum)@d_atomname(d_atomnum)->h_atomname("
            + "h_atomnum)...a_resname(a_resnum)@a_atomname(a_atomnum)"
        )

    donor_names, hydrogen_names, acceptor_names = [], [], []
    with open(grofile, "r") as fo:
        lines = fo.readlines()[2:-1]
    for ind in donor_ndxs:
        line = lines[ind - 1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        # name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        # donor_names.append(name)
        donor_names.append([res_name, res_num, atom_name, atom_num])
    for ind in hydrogen_ndxs:
        line = lines[ind - 1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        # name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        # hydrogen_names.append(name)
        hydrogen_names.append([res_name, res_num, atom_name, atom_num])
    for ind in acceptor_ndxs:
        line = lines[ind - 1]
        res_num = line[:5].strip()
        res_name = line[5:10].strip()
        atom_name = line[10:15].strip()
        atom_num = line[15:20].strip()
        # name = f"{res_name}({res_num})@{atom_name}({atom_num})"
        # acceptor_names.append(name)
        acceptor_names.append([res_name, res_num, atom_name, atom_num])
    if (
        len(donor_names)
        != len(hydrogen_names)
        != len(acceptor_names)
        != len(acceptor_ndxs)
    ):
        logging.error("wrong length in donor, hydrogen, acceptor names")
        sys.exit()
    # hbond_names = [
    #     f'{donor_names[i]}->{hydrogen_names[i].split("@")[1]}...{acceptor_names[i]}'
    #     for i in range(len(donor_names))]
    hbond_names = []
    for i in range(len(donor_names)):
        hbond_name = hnf.replace("d_resname", donor_names[i][0])
        hbond_name = hbond_name.replace("d_resnum", donor_names[i][1])
        hbond_name = hbond_name.replace("d_atomname", donor_names[i][2])
        hbond_name = hbond_name.replace("d_atomnum", donor_names[i][3])
        hbond_name = hbond_name.replace("h_resname", hydrogen_names[i][0])
        hbond_name = hbond_name.replace("h_resnum", hydrogen_names[i][1])
        hbond_name = hbond_name.replace("h_atomname", hydrogen_names[i][2])
        hbond_name = hbond_name.replace("h_atomnum", hydrogen_names[i][3])
        hbond_name = hbond_name.replace("a_resname", acceptor_names[i][0])
        hbond_name = hbond_name.replace("a_resnum", acceptor_names[i][1])
        hbond_name = hbond_name.replace("a_atomname", acceptor_names[i][2])
        hbond_name = hbond_name.replace("a_atomnum", acceptor_names[i][3])
        hbond_names.append(hbond_name)

    ## parse xpmfile
    xpm = XPM(xpmfile)
    if xpm.xpm_height < len(hbond_names):
        logging.warning(
            "height of xpm ({}) in {} is not equal to number of hbond ({}) in {}, removed the excess in xpm".format(
                xpm.xpm_height, xpmfile, len(hydrogen_names), ndxfile
            )
        )
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
        for i in range(
            0, xpm.xpm_width * xpm.xpm_char_per_pixel, xpm.xpm_char_per_pixel
        ):
            dot_list.append(xpm.chars.index(dataline[i : i + xpm.xpm_char_per_pixel]))
        xpm_datamatrix.append(dot_list)
        occupancy.append(sum(dot_list) / (1.0 * len(dot_list)))

    # set operation
    if set_operation != None:
        set_line = []
        for s in set_id_list:
            if s >= len(xpm_datamatrix):
                logging.error(
                    f"hbond id in set_operation out of range, it should be in 0 to {len(xpm_datamatrix)}(not include)"
                )
                sys.exit()
        for x in range(xpm.xpm_width):
            res = xpm_datamatrix[set_id_list[0]][x]
            for id in set_id_list:
                if set_flag == "AND":
                    res = res and xpm_datamatrix[id][x]
                elif set_flag == "OR":
                    res = res or xpm_datamatrix[id][x]
                else:
                    logging.error("Wrong set operation, only support AND and OR")
            set_line.append(res)

    ## deal with the selection
    # select = [5]
    if select == []:
        select = [i for i in range(len(hbond_names))]
    else:
        occupancy = [occupancy[i] for i in select]
        xpm_datamatrix = [xpm_datamatrix[i] for i in select]
    if hnf == "number":
        hbond_names = [str(i) for i in range(len(select))]
    elif hnf == "id":
        hbond_names = [str(i) for i in select]
    else:
        hbond_names = [hbond_names[i] for i in select]

    if set_operation != None:
        hbond_names.append(set_operation)
        occupancy.append(sum(set_line) / (1.0 * len(set_line)))
        xpm_datamatrix.append(set_line)
        select.append(-1)

    ## draw map
    if xshrink != None and xshrink != 1.0:
        xpm.xpm_xaxis = [x * xshrink for x in xpm.xpm_xaxis]
        xpm.xpm_xlabel = (xlabel, xpm.xpm_xlabel)[xlabel == None]
    plt.figure()
    cmap = mcolors.ListedColormap(["white", "#F94C66"])
    hbond = plt.pcolormesh(
        xpm.xpm_xaxis,
        [i for i in range(len(select))],
        xpm_datamatrix,
        cmap=cmap,
        shading="auto",
    )
    if len(select) == 1:
        hbond = plt.imshow(xpm_datamatrix, cmap=cmap, aspect="auto")
        # TODO: xticks
    cb = plt.colorbar(hbond, orientation="horizontal", fraction=0.03)
    cb.set_ticks([0.25, 0.75])
    cb.set_ticklabels(["None", "Present"])
    for i in range(1, len(select)):
        plt.hlines(i - 0.5, min(xpm.xpm_xaxis), max(xpm.xpm_xaxis), colors="white")
    plt.title(xpm.xpm_title)
    plt.xlabel(xpm.xpm_xlabel)
    plt.ylabel(xpm.xpm_ylabel)
    # if xpm.xpm_height <= 20 and hnf == "number":
    #     plt.yticks([i for i in range(len(select))], [i for i in range(len(select))])
    # elif xpm.xpm_height <= 20 and hnf == "id":
    #     plt.yticks([i for i in range(len(select))], select)
    # elif xpm.xpm_height <= 20 and hnf != "number" and hnf != "id":
    #     plt.yticks([i for i in range(len(select))], hbond_names)
    # else:
    #     logging.warning("DIT can only show hbond name when hbond number <= 20 !")

    if len(xpm_datamatrix) <= 20 and hnf == "number":
        plt.yticks([i for i in range(len(select))], [i for i in range(len(select))])
    elif len(xpm_datamatrix) <= 20 and hnf == "id":
        plt.yticks([i for i in range(len(select))], select)
    elif len(xpm_datamatrix) <= 20 and hnf != "number" and hnf != "id":
        plt.yticks([i for i in range(len(select))], hbond_names)
    else:
        logging.warning("DIT can only show hbond name when hbond number <= 20 !")
    plt.tight_layout()
    if figout != None:
        plt.savefig(figout, dpi=300)
    if not noshow:
        plt.show()

    if set_operation != None and (genscript or calc_distance_angle):
        logging.error(
            "you are not surposed to specify set_operation and genscript or calc_distance_angle together, remove set_operation!"
        )
        sys.exit()
    if genscript:
        logging.warning(
            "!IMPORTANT! remember to set 'merge' option of 'gmx hbond' to 'no' if you wanna to calculate average hbond distance and angle !"
        )
        gen_distang_script(donor_ndxs, hydrogen_ndxs, acceptor_ndxs, select)
    dist_ave_std, ang_ave_std = [], []
    if calc_distance_angle and distancefile != None and anglefile != None:
        dist_ave_std, ang_ave_std = calculate_distance_angle(
            xpm_datamatrix,
            hbond_names,
            distancefile,
            anglefile,
            figout,
            noshow,
            xshrink,
            xlabel,
        )

    ## show table
    print("-" * 115)
    print(
        "{:<2} {:<50} {:>14} {:>14}".format(
            "id", "donor->hydrogen...acceptor", "occupancy(%)", "Present/Frames"
        ),
        end="",
    )
    if len(dist_ave_std) != 0 and len(ang_ave_std) != 0:
        print(" {:>15} {:>15}".format("Distance (nm)", "Angle (°)"))
    else:
        print()
    print("-" * 115)
    for i in range(len(hbond_names)):
        print(
            "{:<2d} {:<50} {:>14.2f} {:>6d}/{:<7}".format(
                select[i],
                hbond_names[i],
                occupancy[i] * 100.0,
                np.sum(xpm_datamatrix[i]),
                len(xpm_datamatrix[i]),
            ),
            end="",
        )
        if len(dist_ave_std) != 0 and len(ang_ave_std) != 0:
            print(
                "  {:>6.4f} ± {:<6.4f} {:>6.2f} ± {:<6.2f}".format(
                    dist_ave_std[i][0],
                    dist_ave_std[i][1],
                    ang_ave_std[i][0],
                    ang_ave_std[i][1],
                )
            )
        else:
            print()
    print("-" * 115)
    if csv != None:
        with open(csv, "w") as fo:
            fo.write(
                "{},{},{},{}".format(
                    "id", "donor->hydrogen...acceptor", "occupancy(%)", "Present/Frames"
                )
            )
            if len(dist_ave_std) != 0 and len(ang_ave_std) != 0:
                fo.write(
                    ",{},{},{},{}\n".format(
                        "Distance ave (nm)",
                        "Distance std (nm)",
                        "Angle ave (°)",
                        "Angle std (°)",
                    )
                )
            else:
                fo.write("\n")
            for i in range(len(hbond_names)):
                fo.write(
                    "{},{},{:.2f},{:>d}/{}".format(
                        select[i],
                        hbond_names[i],
                        occupancy[i] * 100.0,
                        np.sum(xpm_datamatrix[i]),
                        len(xpm_datamatrix[i]),
                    )
                )
                if len(dist_ave_std) != 0 and len(ang_ave_std) != 0:
                    fo.write(
                        ",{:>6.4f},{:<6.4f},{:>6.2f},{:<6.2f}\n".format(
                            dist_ave_std[i][0],
                            dist_ave_std[i][1],
                            ang_ave_std[i][0],
                            ang_ave_std[i][1],
                        )
                    )
                else:
                    fo.write("\n")


def hbond_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(
        description="hbond command process the hbond infos"
    )
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
    parser.add_argument(
        "-hnf",
        "--hbond_name_format",
        help="define the hbond name format by user! Each atom has four"
        + " features: resname, resnum, atomname, atomnum. Distinguish "
        + "donor, hydrogen, acceptor by adding one prefix to each feature,"
        + " like: d_resname, a_resnum, h_atomname. \nSo you may able to "
        + "define hbond name style by: 'd_resname(d_resnum)@d_atomname(d_"
        + "atomnum)->h_atomname(h_atomnum)...a_resname(a_resnum)@a_atomn"
        + "ame(a_atomnum)' which is the default style,  or also you could"
        + " specify 'd_atomname@h_atomname...a_atomname' or some format you "
        + "would like. \nOr you could just set the hnf to be 'number' or 'id'",
    )
    parser.add_argument(
        "-genscript",
        "--genscript",
        action="store_true",
        help="whether to generate scripts for calculating distance and angle of hbonds",
    )
    parser.add_argument(
        "-cda",
        "--calc_distance_angle",
        action="store_true",
        help="whether to calculate distance and angle of hbonds from distance xvg file and angle xvg file",
    )
    parser.add_argument(
        "-distancefile", "--distancefile", help="distance file of hbonds for input"
    )
    parser.add_argument(
        "-anglefile", "--anglefile", help="angle file of hbonds for input"
    )
    parser.add_argument(
        "-xs", "--xshrink", type=float, help="modify x-axis by multipling xshrink"
    )
    parser.add_argument("-x", "--xlabel", type=str, help="the xlabel of figure")
    parser.add_argument(
        "-so",
        "--set_operation",
        type=str,
        help="use AND or OR to operate different hbonds. eg. -so AND1-2,4,7  -so OR0,4,6-8",
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
                select += [i for i in range(int(c.split("-")[0]), int(c.split("-")[1]))]
            else:
                select.append(int(c))

    if method == "hbond":
        grofile = args.input
        ndxfile = args.index
        xpmfile = args.map
        noshow = args.noshow
        figout = args.output
        csv = args.csv
        hnf = args.hbond_name_format
        genscript = args.genscript
        calc_distance_angle = args.calc_distance_angle
        distancefile = args.distancefile
        anglefile = args.anglefile
        xshrink = args.xshrink
        xlabel = args.xlabel
        set_operation = args.set_operation
        hbond(
            xpmfile,
            ndxfile,
            grofile,
            select,
            noshow,
            figout,
            csv,
            hnf,
            genscript,
            calc_distance_angle,
            distancefile,
            anglefile,
            xshrink,
            xlabel,
            set_operation,
        )
    else:
        logging.error("unknown method {}".format(method))
        exit()

    logging.info("May you good day !")


def main():
    hbond_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
