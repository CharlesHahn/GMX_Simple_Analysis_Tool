"""
utils module is part of DuIvyTools. This module provides log parent class.

Written by DuIvy and provided to you by GPLv3 license.
"""

import argparse
import logging
import sys
import time
from typing import List

from colorama import Back, Fore, Style


class log(object):
    """log class, a logging system parent class, provied five functions for output debug, info, warning, error, and critical messages."""

    logging.basicConfig(
        level=logging.INFO,
        ## TODO the line number
        ## format="%(asctime)s-%(filename)s[line:%(lineno)d]\n%(message)s",
        format="%(message)s",
    )
    logger = logging.getLogger(__name__)

    def debug(self, msg):
        time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.debug(
            Fore.CYAN + Back.WHITE + f"{time_info}\nDebug -> {msg}" + Style.RESET_ALL
        )

    def info(self, msg):
        time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info(Fore.GREEN + f"{time_info}\nInfo -> {msg}" + Style.RESET_ALL)

    def warn(self, msg):
        time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.warning(
            Fore.YELLOW + f"{time_info}\nWarning -> {msg}" + Style.RESET_ALL
        )

    def error(self, msg):
        time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.error(
            Fore.WHITE + Back.RED + f"{time_info}\nError -> {msg}" + Style.RESET_ALL
        )
        sys.exit()

    def critical(self, msg):
        time_info = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.critical(
            Fore.WHITE + Back.RED + f"{time_info}\nCRITICAL -> {msg}" + Style.RESET_ALL
        )
        sys.exit()


class Parameters(log):
    """A class to deal with and store user-input parameters"""

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="DuIvyTools: A Simple MD Analysis Tool"
        )
        parser.add_argument("cmd", type=str, help="command of DIT to run")
        parser.add_argument(
            "-f", "--input", nargs="+", help="specify the input file or files"
        )
        parser.add_argument("-o", "--output", type=str, help="specify the output file")
        parser.add_argument(
            "-ns", "--noshow", action="store_true", help="not to show figure"
        )
        parser.add_argument(
            "-c",
            "--columns",
            nargs="+",
            help="select the column indexs for visualization or calculation, or input numerical list",
        )
        parser.add_argument(
            "-l", "--legends", nargs="+", help="specify the legends of figure or data"
        )
        parser.add_argument(
            "-b", "--begin", type=int, help="specify the index for beginning (include)"
        )
        parser.add_argument(
            "-e", "--end", type=int, help="specify the index for ending (not include)"
        )
        parser.add_argument(
            "-dt",
            "--dt",
            type=int,
            default=1,
            help="specify the index step, default to 1",
        )
        parser.add_argument(
            "-x", "--xlabel", type=str, help="specify the xlabel of figure or data"
        )
        parser.add_argument(
            "-y", "--ylabel", type=str, help="specify the ylabel of figure or data"
        )
        parser.add_argument(
            "-z", "--zlabel", type=str, help="specify the zlabel of figure or data"
        )
        parser.add_argument(
            "-t", "--title", type=str, help="specify the title of figure or data"
        )
        parser.add_argument(
            "-xmin", "--xmin", type=float, help="specify the X value limitation, x_min"
        )
        parser.add_argument(
            "-xmax", "--xmax", type=float, help="specify the X value limitation, x_max"
        )
        parser.add_argument(
            "-ymin", "--ymin", type=float, help="specify the Y value limitation, y_min"
        )
        parser.add_argument(
            "-ymax", "--ymax", type=float, help="specify the Y value limitation, y_max"
        )
        parser.add_argument(
            "-zmin", "--zmin", type=float, help="specify the Z value limitation, z_min"
        )
        parser.add_argument(
            "-zmax", "--zmax", type=float, help="specify the Z value limitation, z_max"
        )
        parser.add_argument(
            "--x_precision",
            type=int,
            help="specify the precision of X values for visualization",
        )
        parser.add_argument(
            "--y_precision",
            type=int,
            help="specify the precision of Y values for visualization",
        )
        parser.add_argument(
            "--z_precision",
            type=int,
            help="specify the precision of Z values for visualization",
        )
        parser.add_argument(
            "-xs",
            "--xshrink",
            type=float,
            default=1.0,
            help="modify X values by multipling xshrink, default to 1.0",
        )
        parser.add_argument(
            "-ys",
            "--yshrink",
            type=float,
            default=1.0,
            help="modify Y values by multipling yshrink, default to 1.0",
        )
        parser.add_argument(
            "-zs",
            "--zshrink",
            type=float,
            default=1.0,
            help="modify Z values by multipling zshrink, default to 1.0",
        )
        parser.add_argument(
            "-xp",
            "--xplus",
            type=float,
            default=0.0,
            help="modify X values by plusing xplus, default to 0.0",
        )
        parser.add_argument(
            "-yp",
            "--yplus",
            type=float,
            default=0.0,
            help="modify Y values by plusing yplus, default to 0.0",
        )
        parser.add_argument(
            "-zp",
            "--zplus",
            type=float,
            default=0.0,
            help="modify Z values by plusing zplus, default to 0.0",
        )
        parser.add_argument(
            "-smv",
            "--showMV",
            action="store_true",
            help="whether to show moving averages of data",
        )
        parser.add_argument(
            "-ws",
            "--windowsize",
            type=int,
            default=50,
            help="window size for moving average calculation, default to 50",
        )
        parser.add_argument(
            "-cf",
            "--confidence",
            type=float,
            default=0.95,
            help="confidence for confidence interval calculation, default to 0.95",
        )
        parser.add_argument("--alpha", type=float, help="the alpha of figure items")
        parser.add_argument("-csv", "--csv", type=str, help="store data into csv file")
        parser.add_argument(
            "-eg",
            "--engine",
            type=str,
            default="matplotlib",
            choices=["matplotlib", "plotext", "plotly", "gnuplot"],
            help="specify the engine for plotting: 'matplotlib', 'plotext', 'plotly', 'gnuplot'",
        )
        parser.add_argument(
            "-cmap",
            "--colormap",
            help="specify the colormap applied for figures, available for 'matplotlib' and 'plotly' engine",
        )
        parser.add_argument(
            "--colorbar_location",
            type=str,
            default=None,
            choices=[None, "left", "top", "bottom", "right"],
            help="the location of colorbar, also determining the orientation of colorbar, ['left', 'top', 'bottom', 'right'], available for 'matplotlib'",
        )
        parser.add_argument(
            "--legend_location",
            type=str,
            default=None,
            choices=["inside", "outside"],
            help="the location of legend box, ['inside', 'outside'], available for 'matplotlib' and 'gnuplot'",
        )
        parser.add_argument(
            "-m",
            "--mode",
            type=str,
            choices=[
                "withoutScatter",
                "pcolormesh",
                "3d",
                "contour",
                "AllAtoms",
                "pdf",
                "cdf",
            ],
            help="additional parameter: 'withoutScatter' will NOT show scatter plot for 'xvg_box_compare'; 'imshow', 'pcolormesh', '3d', 'contour' were used for 'xpm_show' command; 'AllAtoms' were used for 'find_center' command; 'cdf' and 'pdf' are for 'xvg_show_distribution' command;",
        )
        parser.add_argument(
            "-al",
            "--additional_list",
            nargs="+",
            help="additional parameters. Used to set xtitles for 'xvg_ave_bar'",
        )
        parser.add_argument(
            "-ip",
            "--interpolation",
            type=str,
            default=None,
            help="specify the interpolation method, default to None",
        )
        parser.add_argument(
            "-ipf",
            "--interpolation_fold",
            type=int,
            default=10,
            help="specify the interpolation fold, default to 10",
        )

        args = parser.parse_args()
        self.__dict__ = args.__dict__
        self.__check_convert()

    def __parse_column(self, msg_line: str) -> List[int]:
        """parse column selections, generate List[int]"""
        lis: List[int] = []
        try:
            for msg in msg_line.strip(",").split(","):
                if msg.strip("-").count("-") == 2:
                    b, e = int(msg.split("-")[0]), int(msg.split("-")[1])
                    dt = int(msg.split("-")[2])
                    lis += [i for i in range(b, e, dt)]
                elif msg.strip("-").count("-") == 1:
                    b, e = int(msg.split("-")[0]), int(msg.split("-")[1])
                    lis += [i for i in range(b, e)]
                elif msg.strip("-").count("-") == 0:
                    lis.append(int(msg))
                else:
                    self.error(
                        f"wrong in parsing {msg}. '1-10', '1-10-2', or '10' were supported for input"
                    )
        except ValueError as verr:
            self.error(
                f"Error occured in parsing column selections, please input INTEGER ! \n {verr}"
            )
        except Exception as ex:
            self.error(f"Error occured in parsing column selections. {ex}")
        return lis

    def __check_convert(self) -> None:
        """check part of parameters and deal with parameter format"""
        ## deal parameters
        if self.input != None and "," in "".join(self.input):
            self.input = [fs.strip(",").split(",") for fs in self.input]
        column_select = []
        if self.columns != None:
            for columns in self.columns:
                column_select.append(self.__parse_column(columns))
        self.columns = column_select
        if self.legends != None and "," in "".join(self.legends):
            self.legends = [ls.strip(",").split(",") for ls in self.legends]
        ## check parameters
        if self.begin and self.begin < 0:
            self.warn(
                "parameter 'begin' should not be a minus, BE SURE for what you are doing"
            )
        if self.end and self.end < 0:
            self.warn(
                "parameter 'end' should not be a minus, BE SURE for what you are doing"
            )
        if self.dt and self.dt < 0:
            self.warn(
                "parameter 'dt' should not be a minus, BE SURE for what you are doing"
            )
        if self.x_precision and self.x_precision < 0:
            self.error("parameter 'x_precision' should not be a minus")
        if self.y_precision and self.y_precision < 0:
            self.error("parameter 'y_precision' should not be a minus")
        if self.z_precision and self.z_precision < 0:
            self.error("parameter 'z_precision' should not be a minus")
