"""
DIT module is part of DuIvyTools. This module provides log parent class.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
import inspect

base = os.path.dirname(os.path.realpath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from Commands.otherCommands import *
from Commands.xpmCommands import *
from Commands.xvgCommands import *
from utils import Parameters, log


class DIT(log):
    """DIT class, show information and invoke commands"""

    def __init__(self) -> None:
        self.classes = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
        self.cmds = [
            "xvg_show",
            "xvg_compare",
            "xvg_ave",
            "xvg_energy_compute",
            "xvg_combine",
            "xvg_show_distribution",
            "xvg_show_scatter",
            "xvg_show_stack",
            "xvg_box_compare",
            "xvg_ave_bar",
            "xvg_rama",
            "xpm_show",
            "xpm2csv",
            "xpm2dat",
            "xpm_diff",
            "xpm_merge",
            "mdp_gen",
            "show_style",
            "find_center",
            "dccm_ascii",
            "dssp",
            "ndx_add",
            "ndx_split",
            "ndx_show",
        ]
        self.cmds_infos = """
XVG:
    xvg_show              : easily show xvg file
    xvg_compare           : visualize xvg data
    xvg_ave               : calculate the averages of xvg data
    xvg_energy_compute    : calculate eneries between protein and ligand
    xvg_combine           : combine data of xvg files
    xvg_show_distribution : show distribution of xvg data
    xvg_show_scatter      : show xvg data by scatter plot
    xvg_show_stack        : show xvg data by stack area plot
    xvg_box_compare       : compare xvg data by violin and scatter plots
    xvg_ave_bar           : calculate and show the averages of parallelism 
    xvg_rama              : draw ramachandran plot from xvg data
XPM:
    xpm_show              : visualize xpm data
    xpm2csv               : convert xpm data into csv file in form (x, y, z)
    xpm2dat               : convert xpm data into dat file in form (N*N)
    xpm_diff              : calculate the difference of xpms
    xpm_merge             : merge two xpm by half and half
Others:
    mdp_gen               : generate mdp file templates
    show_style            : show figure control style files
    find_center           : find geometric center of one group of atoms
    dccm_ascii            : convert dccm from ascii data file to xpm
    dssp                  : generate xpm and xvg from ascii file of gmx2023
    ndx_add               : new a index group to ndx file
    ndx_split             : split one index group into several groups
    ndx_show              : show the groupnames of index file
"""
        self.welcome_info = (
            """
 *******           **                  **********               **        
/**////**         /**          **   **/////**///               /**        
/**    /** **   **/** **    **//** **     /**  ******   ****** /**  ******
/**    /**/**  /**/**/**   /** //***      /** **////** **////**/** **//// 
/**    /**/**  /**/**//** /**   /**       /**/**   /**/**   /**/**//***** 
/**    ** /**  /**/** //****    **        /**/**   /**/**   /**/** /////**
/*v0.6.0  //******/**  //**    **         /**//****** //****** *** ****** 
///////    ////// //    //    //          //  //////   ////// /// ////// 

DuIvyTools is a simple analysis and visualization tool for GROMACS result files written by 杜艾维 (https://github.com/CharlesHahn/DuIvyTools). 

DuIvyTools provides about 30 commands for visualization and processing of GMX result files like .xvg or .xpm. 

All commands are shown below: """
            + self.cmds_infos
            + """
You can type `dit <command> -h` for detailed help messages about each command, like: `dit xvg_show -h`. 

All possible parameters could be inspected by `dit -h` or `dit --help`.

Cite DuIvyTools by DOI at https://doi.org/10.5281/zenodo.6339993

Have a good day !
"""
        )

    def run(self) -> None:
        """show help infos and invoke commands"""
        ## help infos
        if len(sys.argv) == 1:
            print(self.welcome_info)
            sys.exit()
        if len(sys.argv) == 3 and sys.argv[2] in ["-h", "--help", "help"]:
            if sys.argv[1] in self.cmds:
                print(f"====== command: {sys.argv[1]} ======")
                print(self.classes[sys.argv[1]].__doc__)
            else:
                self.error(
                    f"Wrong specification of command `{sys.argv[1]}`, type `dit` to see all possible commands"
                )
            sys.exit()

        ## try to run DIT
        parm = Parameters()
        if parm.cmd not in self.cmds:
            self.error(
                f"{parm.cmd} is not available. DIT supports commands as below: \n"
                + self.cmds_infos
            )
        cmd = self.classes.get(parm.cmd, None)
        cmd = cmd(parm)
        cmd()


def main():
    dit = DIT()
    dit.run()
    dit.info("May you good day !")


if __name__ == "__main__":
    main()
