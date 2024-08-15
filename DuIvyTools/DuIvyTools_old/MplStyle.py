"""
MplStyle module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to generate .mplstyle file templates. 

This MplStyle module contains:
    - MplStyle class

This file is provided to you by GPLv3 license."""

import os
import sys
import argparse
import logging


class MplStyle(object):
    """
    class MplStyle are designed to generate kinds of matplotlib style files

    """

    def __init__(self) -> None:
        """init the MDP class"""

        self.application_loc = {
            "DIT": os.path.join("data", "DIT.mplstyle"),
        }

    def gen_mplstyle(self) -> None:
        """gen mplstyle template"""

        ## check parameters
        if os.path.exists("DIT.mplstyle"):
            logging.error("{} is already in current directory".format("DIT.mplstyle"))
            sys.exit()

        ## gen mdp
        data_file_path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        with open(os.path.join(data_file_path, self.application_loc["DIT"]), "r") as fo:
            content = fo.read()
        with open("DIT.mplstyle", "w") as fo:
            fo.write(content)

        logging.info("generate DIT.mplstyle in current folder successfully")


def mplstyle_gen() -> None:
    """gen mplstyle templates"""

    mplstyle = MplStyle()
    mplstyle.gen_mplstyle()


def mplstyle_call_functions(arguments: list = None):
    """call functions according to arguments"""

    if arguments == None:
        arguments = [argv for argv in sys.argv]

    mplstyle_gen()

    logging.info("May you good day !")


def main():
    mplstyle_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
