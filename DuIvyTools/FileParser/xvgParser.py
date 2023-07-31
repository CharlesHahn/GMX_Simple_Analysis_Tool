"""
xvgParser module is part of DuIvyTools for parsing the xvg file generated by GROMACS.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
import numpy as np
import scipy.stats as stats
from typing import List, Union, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import log


class XVG(log):
    def __init__(
        self,
        xvgfile: Union[str, List[str]],
        is_file: bool = True,
        new_file: bool = False,
    ) -> None:
        self.comments: str = ""
        self.title: str = ""
        self.xlabel: str = ""
        self.ylabel: str = ""
        self.xmin: float = None
        self.xmax: float = None
        self.ymin: float = None
        self.ymax: float = None
        self.legends: List[str] = []
        self.column_num: int = 0
        self.row_num: int = 0
        self.data_heads: List[str] = []
        self.data_columns: List[Union(float, str)] = []

        if new_file:
            self.xvgfile = xvgfile
        else:
            if is_file:
                self.xvgfile: str = xvgfile
                if not os.path.exists(xvgfile):
                    self.error(f"No {xvgfile} detected ! check it !")
                with open(xvgfile, "r") as fo:
                    lines = fo.readlines()
            else:
                lines = xvgfile
            self.parse_xvg(lines)
            if is_file:
                self.info(f"parsing data from {xvgfile} successfully !")

    def parse_xvg(self, lines: List[str]) -> None:
        """parse xvg content

        Args:
            lines (List[str]): xvg file lines
        """
        ## parse data
        for line in lines:
            line = line.strip()
            if line.startswith("#") or line.startswith("&"):
                self.comments += line + "\n"
            elif line.startswith("@"):
                if " title " in line:
                    self.title = line.strip('"').split('"')[-1]
                elif " xaxis " in line and " label " in line:
                    self.xlabel = line.strip('"').split('"')[-1]
                elif " yaxis " in line and " label " in line:
                    self.ylabel = line.strip('"').split('"')[-1]
                elif line.startswith("@ s") and " legend " in line:
                    self.legends.append(line.strip('"').split('"')[-1])
                elif " world xmin " in line:
                    self.xmin = float(line.split()[-1])
                elif " world xmax " in line:
                    self.xmax = float(line.split()[-1])
                elif " world ymin " in line:
                    self.ymin = float(line.split()[-1])
                elif " world ymax " in line:
                    self.ymax = float(line.split()[-1])
                else:
                    pass
            else:
                items = line.split()
                if self.column_num == 0:
                    self.data_columns = [[] for _ in range(len(items))]
                    self.column_num = len(items)
                    self.row_num = 0
                if len(items) != self.column_num:
                    self.error(
                        f"the number of columns in {self.xvgfile} is not equal at line {self.row_num}"
                    )
                for i in range(len(items)):
                    self.data_columns[i].append(items[i])
                self.row_num += 1

        ## convert data
        self.data_heads.append(self.xlabel)
        self.data_columns[0] = [float(c) for c in self.data_columns[0]]
        if len(self.legends) == 0 and len(self.data_columns) > 1:
            self.data_heads.append(self.ylabel)
            self.data_columns[1] = [float(c) for c in self.data_columns[1]]

        if len(self.legends) > 0 and self.column_num > len(self.legends):
            items = [item.strip() for item in self.ylabel.split(",")]
            heads = [l for l in self.legends]
            if len(items) == len(self.legends):
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
                self.warn("failed to pair ylabel to legends, use legends in xvg file")
            self.data_heads += heads
            for i in range(len(heads)):
                self.data_columns[i + 1] = [float(c) for c in self.data_columns[i + 1]]

        ## check infos
        for c in range(self.column_num):
            if len(self.data_columns[c]) != self.row_num:
                self.error(f"length of column {c} is not equal to other columns")
        if self.column_num == 0 or self.row_num == 0:
            self.error(f"no data line detected in {self.xvgfile}")
        if len(self.data_heads) < self.column_num:
            self.warn(
                f"string column may detected, data_heads {len(self.data_heads)} < column_num {self.column_num}"
            )

    def dump2xvg(self, outxvg: str) -> None:
        """dump xvg class to xvg file

        Args:
            outxvg (str): output xvg file name
        """
        outstr: str = ""
        outstr += self.comments
        outstr += f'@    title "{self.title} computed by DIT"\n'
        outstr += f'@    xaxis label "{self.xlabel}"\n'
        outstr += f'@    yaxis label "{self.ylabel}"\n'
        outstr += "@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n"
        outstr += "@ legend on\n@ legend box on\n@ legend loctype view\n"
        outstr += "@ legend 0.78, 0.8\n@ legend length 9\n"
        for i, leg in enumerate(self.legends):
            outstr += f'@ s{i} legend "{leg}"\n'
        for row in range(self.row_num):
            for i in range(self.column_num):
                outstr += f"{self.data_columns[i][row]:>16.6f} "
            outstr += "\n"
        with open(outxvg, "w") as fo:
            fo.write(outstr)
        self.info(f"dump xvg to {outxvg} successfully")

    def calc_mvave(
        self, windowsize: int, confidence: float, column_index: int
    ) -> Tuple[List]:
        """
        calculate the moving average of each column

        :parameters:
            windowsize: the window size for calculating moving average
            confidence: the confidence to calculate interval
            conlumn_index: the index for the column to calculate

        :return:
            mvaves: a list contains moving average
            highs: the high value of interval of moving averages
            lows: the low value of interval of moving averages
        """

        if windowsize <= 0 or windowsize > int(self.row_num / 2):
            self.error("windowsize value is not proper")
        if confidence <= 0 or confidence >= 1:
            self.error("confidence value is not proper, it should be in (0,1)")

        if column_index < 0 or column_index >= self.column_num:
            self.error("wrong selection of column_index to calculate moving averages")
        column_data = self.data_columns[column_index]
        mvaves = [np.nan for _ in range(windowsize)]
        highs = [np.nan for _ in range(windowsize)]
        lows = [np.nan for _ in range(windowsize)]
        for i in range(windowsize, self.row_num):
            window_data = np.array(column_data[i - windowsize : i])
            ave = np.mean(window_data)
            std = np.std(window_data)
            interval = stats.norm.interval(confidence, ave, std)
            mvaves.append(ave)
            lows.append(interval[0])
            highs.append(interval[1])
        return mvaves, highs, lows

    def calc_ave(
        self, begin: int, end: int, dt: int, column_index: int
    ) -> Tuple[float]:
        """calculate the average of selected column

        Args:
            begin (int): the begin index
            end (int): the end index
            dt (int): the index step
            column_index (int): the selected column index

        Returns:
            Tuple[float]: legend, average, std.err
        """
        if (begin != None and end != None) and (begin >= end):
            self.error("start index should be less than end index")
        if (begin != None and begin >= self.row_num) or (
            end != None and end >= self.row_num
        ):
            self.error(
                f"start or end index should be less than the number of rows {self.row_num} in xvg file"
            )
        if column_index >= self.column_num:
            self.error(
                f"column index selected should be less than column number {self.column_num}"
            )

        column = self.data_columns[column_index]
        legend = self.data_heads[column_index]
        ave = np.average(column[begin:end:dt])
        std = np.std(column[begin:end:dt], ddof=1)
        return legend, ave, std


class XVGS(log):
    def __init__(self, xvgfile: str) -> None:
        self.xvgfile: str = xvgfile
        self.frames: list[XVG] = []

        with open(xvgfile, "r") as fo:
            lines = fo.readlines()
        contents: List[List[str]] = [[]]
        for line in lines:
            item = line.strip()
            if item != "&" and item != "":
                contents[-1].append(line)
            elif item == "&":
                contents.append([])

        for content in contents:
            if len(content) == 0:
                continue
            xvg = XVG(content, is_file=False)
            self.frames.append(xvg)
        self.info(f"parsing multi-frames data from {xvgfile} successfully !")

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, index: int) -> XVG:
        return self.frames[index]


def main():
    # xvg = XVGS("../../test/pc1.xvg")[0]
    # xvg = XVGS("../../test/rama.xvg")[0]
    # xvg = XVG("../../test/gyrate.xvg")
    # xvg = XVG("../../test/dssp_sc.xvg")
    xvg = XVG("../../test/hbond.xvg")

    print(xvg.title)
    print(xvg.xlabel)
    print(xvg.ylabel)
    print(xvg.xmin)
    print(xvg.xmax)
    print(xvg.ymin)
    print(xvg.ymax)
    print(xvg.legends)
    print(xvg.column_num)
    print(xvg.row_num)
    print(xvg.data_heads)
    for data in xvg.data_columns:
        print(data[:10])
