"""
This DIT module is part of DuIvyTools library. Written by CharlesHahn.

DIT module provides simple API and CLI commands for you to use conveniently. 

This file is provided to you under GPLv3 License.
"""

import os
import sys
import logging
import matplotlib.pyplot as plt

base = os.path.dirname(os.path.realpath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from XPM import xpm_call_functions
from XVG import xvg_call_functions
from NDX import ndx_call_functions
from MDP import mdp_call_functions
from HELP import help_call_functions, get_welcome_msg
from PipiDistAng import pipi_dist_ang_call_functions
from FindCenter import find_center_call_functions
from HydrogenBond import hbond_call_functions
from MolMap import mol_map_call_functions
from DCCM import dccm_call_functions
from DSSP import dssp_call_functions
from MplStyle import mplstyle_call_functions


logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
logger = logging.getLogger(__name__)


def load_style():
    style_files = [file for file in os.listdir() if file[-9:] == ".mplstyle"]
    if len(style_files) >= 1:
        plt.style.use(style_files[0])
        logging.info("using matplotlib style sheet from {}".format(style_files[0]))
    else:
        data_file_path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        mplstyle = os.path.join(data_file_path, os.path.join("data", "DIT.mplstyle"))
        plt.style.use(mplstyle)
        logging.info("using default matplotlib style sheet")


def main():
    arguments = [argv for argv in sys.argv]
    if len(sys.argv) < 2:
        DIT_infos = get_welcome_msg()
        print(DIT_infos)
        sys.exit()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ["help", "-h", "--help"]:
            help_call_functions(arguments)
        elif sys.argv[1] == "show_style":
            mplstyle_call_functions(arguments)
        else:
            logging.error("unknown command {}, ".format(sys.argv[1]))
            logging.info("type `dit help` for more information")
            sys.exit()
    elif len(sys.argv) == 3:
        if sys.argv[1] == "help":
            help_call_functions(arguments)
        elif sys.argv[2] in ["-h", "--help", "help"]:
            help_call_functions(["dit", "help", sys.argv[1]])
        else:
            logging.error("wrong command, type `dit help` for more information")
            sys.exit()
    elif len(sys.argv) > 3:
        load_style()  # to load style here
        method = sys.argv[1]
        if method.startswith("xvg"):
            xvg_call_functions(arguments)
        elif method.startswith("xpm"):
            xpm_call_functions(arguments)
        elif method.startswith("ndx"):
            ndx_call_functions(arguments)
        elif method.startswith("mdp"):
            mdp_call_functions(arguments)
        elif method.startswith("help"):
            help_call_functions(arguments)
        elif method == "pipi_dist_ang":
            pipi_dist_ang_call_functions(arguments)
        elif method == "find_center":
            find_center_call_functions(arguments)
        elif method == "hbond":
            hbond_call_functions(arguments)
        elif method == "mol_map":
            mol_map_call_functions(arguments)
        elif method == "dccm_ascii":
            dccm_call_functions(arguments)
        elif method == "dssp":
            dssp_call_functions(arguments)
        else:
            logging.error("unknown command {}".format(method))


if __name__ == "__main__":
    main()
