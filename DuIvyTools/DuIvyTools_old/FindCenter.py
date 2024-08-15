"""
FindCenter module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to provide some useful funcitons.

This module contains:
    - find_center function

This file is provided to you by GPLv3 license."""

import os
import sys
import argparse
import logging

base = os.path.dirname(os.path.realpath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from NDX import NDX


def get_ndx(ndx_file: str = ""):
    ndx = NDX(ndx_file)
    ndx.show_ndx()
    select = input("Select one group: ")
    if select.isnumeric() and int(select) < ndx.group_number:
        index = ndx.group_index_list[int(select)]
        logging.info(
            "You selected group {} which contains {} atoms".format(
                ndx.group_name_list[int(select)], len(index)
            )
        )
    elif select in ndx.group_name_list:
        index = ndx.group_index_list[ndx.group_name_list.index(select)]
        logging.info(
            "You selected group {} which contains {} atoms".format(select, len(index))
        )
    else:
        logging.error("Wrong selection, type Int number or name of group")
        sys.exit()
    return index


def find_center(
    gro_file: str = "", ndx_file: str = None, AllAtoms: bool = None
) -> None:
    """
    find_center: a function to figure out one atom coordinates which
    is the closest one to group center, useful for adjusting PBC
    This function will read one gro file and return the center of coordinates
    and the atom number which is close to it.

    :parameters:
        gro_file: the gro file which saved coordinates

    :return:
        None
    """

    if not os.path.exists(gro_file):
        logging.error("no {} in current dirrectory. ".format(gro_file))
        sys.exit()
    if gro_file[-4:] != ".gro":
        logging.error("find_center only accept gro file with suffix .gro")
        sys.exit()
    if ndx_file != None and (not os.path.exists(ndx_file)):
        logging.error("no {} in current dirrectory. ".format(ndx_file))
        sys.exit()

    with open(gro_file, "r") as fo:
        lines = fo.readlines()
    atom_count = int(lines[1].strip())
    logging.info("{:d} atoms in {}".format(atom_count, gro_file))
    atom_lines = lines[2 : atom_count + 2]

    if ndx_file != None:
        index = get_ndx(ndx_file)
    else:
        index = [i for i in range(1, atom_count + 1)]

    atom_count = len(index)
    ## calculate the center point
    center_x, center_y, center_z = 0, 0, 0
    for i in index:
        line = atom_lines[i - 1]
        center_x += float(line[20:28])
        center_y += float(line[28:36])
        center_z += float(line[36:44])
    center_x = center_x / atom_count
    center_y = center_y / atom_count
    center_z = center_z / atom_count
    logging.info(
        "the center point is ({:.3f}, {:.3f}, {:.3f})".format(
            center_x, center_y, center_z
        )
    )

    ## find the closed atom
    atom_info = ""
    dist = 5  # nm, find closed atom in sphere of 5nm
    for i, line in enumerate(atom_lines):
        if (not AllAtoms) and (i + 1 not in index):
            continue
        x = float(line[20:28])
        y = float(line[28:36])
        z = float(line[36:44])
        atom_center_dist = (
            (x - center_x) ** 2 + (y - center_y) ** 2 + (z - center_z) ** 2
        ) ** 0.5
        if atom_center_dist < dist:
            dist = atom_center_dist
            atom_info = line[:44]
    if atom_info == "":
        logging.info("no atom detected in 5 nm sphere of center point. ")
        sys.exit()
    else:
        logging.info("distance from nearest atom to center: {:.3f} nm".format(dist))
        print("--------------------------------------------")
        print("ResID Name Atom  Num       X       Y       Z")
        print("--------------------------------------------")
        print(atom_info)
        print("--------------------------------------------")


def find_center_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(description="Find the center of a group of atoms")
    parser.add_argument("-f", "--input", help="gro file for input")
    parser.add_argument("-n", "--index", help="index file for input")
    parser.add_argument(
        "-aa",
        "--AllAtoms",
        action="store_true",
        help="if to find center in all atoms of gro file",
    )

    if len(arguments) < 2:
        logging.error("no input parameters, -h or --help for help messages")
        sys.exit()

    method = arguments[1]
    if method in ["-h", "--help"]:
        parser.parse_args(arguments[1:])
        sys.exit()

    if len(arguments) == 2:
        logging.error("no parameters, type 'dit <command> -h' for more infos.")
        sys.exit()
    args = parser.parse_args(arguments[2:])
    if method == "find_center":
        print(args.input, args.index, args.AllAtoms)
        find_center(args.input, args.index, args.AllAtoms)
    else:
        logging.error("unknown method {}".format(method))
        sys.exit()

    logging.info("good day !")


def main():
    find_center_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
