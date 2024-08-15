"""
MDP module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to generate .mdp file templates. 

This MDP module contains:
    - MDP class

This file is provided to you by GPLv3 license."""

import os
import sys
import argparse
import logging


class MDP(object):
    """
    class MDP are designed to generate kinds of mdp files

    """

    def __init__(self) -> None:
        """init the MDP class"""

        self.application_loc = {
            "ions": os.path.join("data", "ions.mdp"),
            "em": os.path.join("data", "em.mdp"),
            "nvt": os.path.join("data", "nvt.mdp"),
            "npt": os.path.join("data", "npt.mdp"),
            "md": os.path.join("data", "md.mdp"),
            "blank": os.path.join("data", "blank.mdp"),
        }

        logging.info(
            "MDP module could init some mdp templates for you. Specify application (-a) to generate a mdp file. "
        )
        logging.info("Applications to choose: ions, em, nvt, npt, md, blank")
        logging.warning(
            "the generated mdp file may be not appropriate for your system, CHECK IT YOURSELF !"
        )

    def gen_mdp(self, outmdp: str, application: str) -> None:
        """gen mdp template by specified application"""

        ## check parameters
        if outmdp == None or len(outmdp) <= 4 or outmdp[-4:] != ".mdp":
            logging.error("output file name should be with suffix .mdp")
            sys.exit()
        if os.path.exists(outmdp):
            logging.error("{} is already in current directory".format(outmdp))
            sys.exit()
        if application == None or application not in self.application_loc.keys():
            logging.info(
                "application available:\n         {}".format(
                    " ".join(self.application_loc.keys())
                )
            )
            logging.error("no application {} found".format(application))
            sys.exit()

        ## gen mdp
        data_file_path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        with open(
            os.path.join(data_file_path, self.application_loc[application]), "r"
        ) as fo:
            content = fo.read()
        with open(outmdp, "w") as fo:
            fo.write(content)

        logging.info(
            "generate {}.mdp for {} application successfully".format(
                outmdp, application
            )
        )


def mdp_gen(outmdp: str, application: str) -> None:
    """gen mdp templates"""

    mdp = MDP()
    mdp.gen_mdp(outmdp, application)


def mdp_call_functions(arguments: list = None):
    """call functions according to arguments"""

    if arguments == None:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(description="generate mdp file templates")
    parser.add_argument("-o", "--output", help="file name to output")
    parser.add_argument(
        "-a",
        "--application",
        choices=["ions", "em", "nvt", "npt", "md", "blank"],
        help="specify the application of mdp, choices: ions, em, nvt, npt, md, blank",
    )

    if len(arguments) < 2:
        logging.error("no input parameters, -h or --help for help messages")
        sys.exit()
    method = arguments[1]
    if method in ["-h", "--help"]:
        parser.parse_args(arguments[1:])
        sys.exit()
    args = parser.parse_args(arguments[2:])
    if method == "mdp_gen":
        mdp_gen(args.output, args.application)
    else:
        logging.error("unknown method {}".format(method))
        sys.exit()

    logging.info("May you good day !")


def main():
    mdp_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
