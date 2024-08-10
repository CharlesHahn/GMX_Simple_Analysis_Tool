"""
otherCommander module is part of DuIvyTools providing basic commands.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys
from itertools import chain
from typing import Dict, List, Union

import numpy as np
import pandas as pd

base = os.path.dirname(os.path.realpath(os.path.join(__file__, "..")))
if base not in sys.path:
    sys.path.insert(0, base)

from Commands.Commands import Command
from FileParser.groParser import GRO
from FileParser.ndxParser import NDX
from FileParser.xpmParser import XPM
from FileParser.xvgParser import XVG
from utils import Parameters


class mdp_gen(Command):
    """
    Generate gromacs mdp templates. DIT provides several mdp templates for general MD process, including blank.mdp, ions.mdp, em.mdp, nvt.mdp, npt.mdp, md.mdp.
    You can type `dit mdp_gen` to see all possible mdp templates, and use `-o` with filename to generate corresponding mdp file in you working directory.

    :Parameters:
        -o, --ouput
                specify the name of mdp templates for generating.

    :Usage:
        dit mdp_gen -o nvt.mdp
        dit mdp_gen -o blank.mdp
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in mdp_gen")
        # print(self.parm.__dict__)

        mdp_path = os.path.realpath(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                os.path.join("..", "data", "mdps"),
            )
        )
        mdp_files = [f for f in os.listdir(mdp_path) if f.endswith(".mdp")]
        if self.parm.output != None and self.parm.output not in mdp_files:
            self.warn(
                f'the specified output file "{self.parm.output}" were unable to provide'
            )
            self.parm.output = None
        if self.parm.output == None:
            print("-" * 70)
            print(
                "You can get one of the following mdp file by specifying the output parameter: \n"
            )
            print("  ".join(mdp_files))
            print("-" * 70)
        if self.parm.output in mdp_files:
            with open(os.path.join(mdp_path, self.parm.output), "r") as fo:
                content = fo.read()
            self.parm.output = self.check_output_exist(self.parm.output)
            with open(self.parm.output, "w") as fo:
                fo.write(content)
            self.info(f"generated {self.parm.output} successfully")


class show_style(Command):
    """
    Generate the default style file at current working directory.
    For matplotlib, DIT provides DIT.mplstyle (default), science.mplstyle, nature.mplstyle, and a blank.mplstyle which contained all possible matplotlib parameters. For more details about matplotlib style sheet, visit: https://matplotlib.org/stable/tutorials/introductory/customizing.html#the-matplotlibrc-file
    For plotly, DIT provides several style files. DIT.json is the default style files for plotly. For more details about customizing plotly style with templates, visit: https://plotly.com/python/reference/index/. For more possible style templates, visit: https://github.com/AnnMarieW/dash-bootstrap-templates/tree/main/src/dash_bootstrap_templates/templates
    For gnuplot, DIT provides DIT.gpstyle. For more colormaps or style files, visit: https://github.com/hesstobi/Gnuplot-Templates, https://github.com/Gnuplotting/gnuplot-palettes, or so many others.

    :Parameters:
        -o, --output (optional)
                specify the name of style file to generate
        -eg, --engine (optional)
                specify the plot engine to generate corresponding style file, default to matplotlib

    :Usage:
        dit show_style
        dit show_style -o science.mplstyle
        dit show_style -eg plotly
        dit show_style -eg plotly -o bootstrap.json
        dit show_style -eg gnuplot
        dit show_style -eg gnuplot -o DIT.gpstyle
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in show_style")
        # print(self.parm.__dict__)

        mplstyle_path = os.path.realpath(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                os.path.join("..", "data", "mplstyle"),
            )
        )
        mplstyle_files = [
            f for f in os.listdir(mplstyle_path) if f.endswith(".mplstyle")
        ]
        plotlystyle_path = os.path.realpath(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                os.path.join("..", "data", "plotlystyle"),
            )
        )
        plotlystyle_files = [
            f for f in os.listdir(plotlystyle_path) if f.endswith(".json")
        ]
        gnuplotstyle_path = os.path.realpath(
            os.path.join(
                os.getcwd(),
                os.path.dirname(__file__),
                os.path.join("..", "data", "gnuplotstyle"),
            )
        )
        gnuplotstyle_files = [
            f for f in os.listdir(gnuplotstyle_path) if f.endswith(".gpstyle")
        ]

        if self.parm.engine == "plotly":
            files = plotlystyle_files
            path = plotlystyle_path
            default_output = "DIT.json"
        elif self.parm.engine == "gnuplot":
            files = gnuplotstyle_files
            path = gnuplotstyle_path
            default_output = "DIT.gpstyle"
        else:
            files = mplstyle_files
            path = mplstyle_path
            default_output = "DIT.mplstyle"
            self.parm.engine = "matplotlib"

        print("-" * 80)
        print(
            f"You can get one of the following style files for plot engine {self.parm.engine} by specifying the output parameter with same file name: \n"
        )
        for i in range(0, len(files), 5):
            print("  ".join(files[i : i + 5]))
        print("-" * 80)
        print(f">> The default style file for {self.parm.engine} is {default_output}")
        print("-" * 80)

        if self.parm.output != None and self.parm.output not in files:
            self.error(
                f'the specified output file "{self.parm.output}" were unable to provide'
            )
        elif self.parm.output == None:
            self.parm.output = default_output
        if self.parm.output != None and self.parm.output in files:
            with open(os.path.join(path, self.parm.output), "r") as fo:
                content = fo.read()
            self.parm.output = self.check_output_exist(self.parm.output)
            with open(self.parm.output, "w") as fo:
                fo.write(content)
            self.info(
                f"generated {self.parm.output} for {self.parm.engine} successfully"
            )


class find_center(Command):
    """
    Find the geometric center of one group of atoms by a gro file (or with an index file).
    By specifying a gro file, `find_center` would fetch the center of all atoms in gro file. With an index file, you would be able to select the atom group which are used to find geomertric center. The command would find out the atom (in the group you specified) nearest to the geometric center. But with paratmer `--mode AllAtoms`, DIT would find out the atom nearest to the geometric center IN ALL ATOMS of gro file.

    :Parameters:
        -f, --input
                specify the input gro file (or with an index file)
        -m, --mode (optional)
                by specifying `--mode AllAtoms` to find the atom nearest to geometric center in All atoms of gro file

    :Usage:
        dit find_center -f test.gro
        dit find_center -f test.gro index.ndx
        dit find_center -f test.gro index.ndx -m AllAtoms
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in find_center")
        # print(self.parm.__dict__)

        ## read user input
        if self.parm.input == None:
            self.error(
                "you must specify a gro file (or with an index file) for finding atom group center"
            )
        else:
            indexfile, grofile = "", ""
            if ".gro" in "".join(self.parm.input):
                for file in self.parm.input:
                    if file.endswith(".gro") and grofile == "":
                        grofile = file
                        self.info(f"{file} has been used as gro file")
            if ".ndx" in "".join(self.parm.input):
                for file in self.parm.input:
                    if file.endswith(".ndx") and indexfile == "":
                        indexfile = file
                        self.info(f"{file} has been used as index file")
        if grofile == "":
            self.error(
                "you must specify a gro file (or with an index file) for finding atom group center"
            )

        ## deal with logic
        gro = GRO(grofile)
        if indexfile == "":
            indexs = [i for i in range(1, gro.atom_number + 1)]
        else:
            ndx = NDX(indexfile)
            print(ndx.show_names)
            indexs: Union[List[int], None] = None
            while indexs == None:
                key = input("==> select a group to calculate center: ")
                if key.isnumeric():  # if key could be int, treat as group id
                    key = int(key)
                name, indexs = ndx[key]
                if indexs == None:
                    print(">>> wrong selection, no atom indexs fetched <<<")
                else:
                    print(f">>> selected group {name}")
        ## calculate the center point
        center_x, center_y, center_z = 0, 0, 0
        for i in indexs:
            coor = gro.frames[0][i - 1].coor
            center_x += coor[0]
            center_y += coor[1]
            center_z += coor[2]
        center_x = center_x / len(indexs)
        center_y = center_y / len(indexs)
        center_z = center_z / len(indexs)
        self.info(
            "the center point is ({:.3f}, {:.3f}, {:.3f})".format(
                center_x, center_y, center_z
            )
        )
        ## find the closed atom
        AllAtoms: bool = False
        if self.parm.mode == "AllAtoms":
            AllAtoms = True
        atom_info = ""
        dist = 5  # nm, find closed atom in sphere of 5 nm
        for i, atom in enumerate(gro.frames[0]):
            if (not AllAtoms) and (i + 1 not in indexs):
                continue
            x = atom.coor[0]
            y = atom.coor[1]
            z = atom.coor[2]
            atom_center_dist = (
                (x - center_x) ** 2 + (y - center_y) ** 2 + (z - center_z) ** 2
            ) ** 0.5
            if atom_center_dist < dist:
                dist = atom_center_dist
                atom_info = str(atom)
        if atom_info == "":
            self.info("no atom detected in 5.0 nm sphere of center point. ")
        else:
            self.info(f"distance from nearest atom to center: {dist:.3f} nm")
            print("--------------------------------------------")
            print("ResID Name Atom  Num       X       Y       Z")
            print("--------------------------------------------")
            print(atom_info)
            print("--------------------------------------------")


class dccm_ascii(Command):
    """
    Converting covariance ascii data file generated by `gmx covar -ascii` into dynamics cross-correlation matrix (DCCM) and store into xpm
    You can difine the precision of DCCM values by specifing `--z_precision` which is suggested to be 3 (also is the default value).

    :Parameters:
        -f, --input
                specify the file name of covariance ascii data file
        -o, --output
                specify the output xpm file name
        --z_precision (optional)
                specify the value precision to save in xpm file

    :Usage:
        dit dccm_ascii -f covar.dat -o dccm.xpm
        dit dccm_ascii -f covar.dat -o dccm.xpm --z_precision 3
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in dccm_ascii")
        # print(self.parm.__dict__)

        ## check parameters
        if not self.parm.input:
            self.error(
                "you must specify ascii data file generated by 'gmx dccm -ascii' for input"
            )
        if len(self.parm.input) > 1:
            self.warn(f"only the first file {self.parm.input[0]} will be used")
        if not self.parm.output:
            self.error("you must specify a XPM file for output")
        if not os.path.exists(self.parm.input[0]):
            self.error(f"no {self.parm.input[0]} in current directory")

        ## read ascii
        covar = pd.read_csv(self.parm.input[0], sep=" ", header=None)
        resnum = int(np.sqrt((covar.shape[0]) / 3))
        results = pd.DataFrame()
        for i in range(resnum):
            one_N = pd.DataFrame()
            for j in range(
                (i * resnum) * 3, int(len(covar) / resnum) * (i + 1), resnum
            ):
                df = covar[j : resnum + j].reset_index(drop=True)
                one_N = pd.concat([one_N, df], ignore_index=True, axis=1)
            results = pd.concat([results, one_N], ignore_index=True, axis=0)
        results["sum"] = results.sum(axis=1)
        covar = results["sum"].to_numpy()
        covar = covar.reshape(resnum, resnum)
        ## convert covar to corr
        if self.parm.z_precision == None:
            self.parm.z_precision = 3
        corr = np.zeros((resnum, resnum))
        for i in range(resnum):
            for j in range(resnum):
                corr_ij = covar[i, j] / np.sqrt(covar[i, i] * covar[j, j])
                corr[i, j] = float(f"{corr_ij:.{self.parm.z_precision}f}")

        ## save to xpm
        xpm = XPM(self.parm.output, is_file=False, new_file=True)
        xpm.title = "DCCM by DIT"
        xpm.type = "Continuous"
        xpm.xlabel = "Residue No."
        xpm.ylabel = "Residue No."
        xpm.width = resnum
        xpm.height = resnum
        xpm.value_matrix = corr.tolist()
        xpm.xaxis = [i + 1 for i in range(resnum)]
        xpm.yaxis = [i + 1 for i in range(resnum)]
        xpm.yaxis.reverse()
        xpm.value_matrix.reverse()
        xpm.refresh_by_value_matrix()
        self.parm.output = self.check_output_exist(self.parm.output)
        xpm.save(self.parm.output)


class dssp(Command):
    """
    For GROMACS 2023 or later, gmx do not generate dssp xpm and xvg of protein secondary structures. For instead, a symbol matrix was generated by `gmx2023 dssp`. This command was designed for converting symbol matrix generated by `gmx2023 dssp` into normal dssp xpm and xvg data files, just like the ones `gmx2022 do_dssp` generated.
    A dssp xpm will be generated, with two xvg files. One is like the one generated by `gmx2022 do_dssp -sc`, recording the residue numbers of varies of secondary structures along the time. The other records the time frame numbers of varies of secondary structures along the residues.

    :Parameters:
        -f, --input
                specify the dssp symbol matrix data file generated by `gmx2023 dssp`
        -o, --output (optional)
                the file name for output. Would be used to save xpm, and two xvg, default to "dit_dssp_gmx2023"
        -x, --xlabel (optional)
                set the xlabel of xpm figure, normally "time (ps)", default to "Frame"
        -y, --ylabel (optional)
                set the ylabel of xpm figure, default to "Residue"
        -t, --title (optional)
                set the title of xpm figure, tefault to "Secondary Structure"
        -c, --columns (optional)
                set the yaxis (residue indexs) of xpm figure
        -b, --begin (optional)
                set the begin value for generating the time series (xaxis)
        -e, --end (optional)
                set the end value for generating the time series (xaxis)
        -dt, --dt (optional)
                set the step value for generating the time series (xaxis)

    :Usage:
        dit dssp -f dssp.dat
        dit dssp -f dssp.dat -o test.xpm -x "Time (ps)" -y "Residue No." -t "title"
        dit dssp -f dssp.dat -c 1-43,1-43,1-43 -b 10000 -e 2000 -dt 10 -x "Time (ps)"
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in dssp")
        # print(self.parm.__dict__)

        ## for 2023, read in dat file and output normal xpm and ss.xvg
        if not self.parm.input:
            self.error(
                "you must specify data file generated by 'gmx2023 dssp' for input"
            )
        if len(self.parm.input) > 1:
            self.warn(f"only the first file {self.parm.input[0]} will be used")
        if not os.path.exists(self.parm.input[0]):
            self.error(f"no {self.parm.input[0]} in current directory")
        datafile: str = self.parm.input[0]
        outname = "dit_dssp_gmx2023"
        if self.parm.output:
            outname = self.parm.output.split(".")[0]
        outxpm: str = f"{outname}.xpm"
        outxvg_sc: str = f"{outname}_sc.xvg"
        outxvg_res: str = f"{outname}_residue.xvg"
        for file in [outxpm, outxvg_sc, outxvg_res]:
            new_file = self.check_output_exist(file)
            if new_file != file:
                outname = new_file.split(".")[0]
                outxpm: str = f"{outname}.xpm"
                outxvg_sc: str = f"{outname}_sc.xvg"
                outxvg_res: str = f"{outname}_residue.xvg"
                break

        ## the note infos were get from https://github.com/gromacs/gromacs/blob/main/src/gromacs/trajectoryanalysis/modules/dssp.cpp#L220
        char_note_dict = {
            "~": "Loops",  # Loop
            "E": "β-Strands",  # Strands
            "B": "β-Bridges",  # Bridge
            "S": "Bends",  # Bend
            "T": "Turns",  # Turn
            "P": "PP-Helices",  # Helix_PP
            "I": "5-Helices",  # "π-Helices",   # Helix_5
            "H": "α-Helices",  # Helix_4
            "G": "3-Helices",  # "3⏨-Helices",  # Helix_3
            "=": "Breaks",  # Break
        }
        char_color_dict = {
            "~": "#FFFFFF",  # Loop
            "E": "#FF0000",  # Strands
            "B": "#000000",  # Bridge
            "S": "#008000",  # Bend
            "T": "#FFFF00",  # Turn
            "P": "#00FFFF",  # Helix_PP
            "I": "#000080",  # Helix_5
            "H": "#00FF00",  # Helix_4
            "G": "#808080",  # Helix_3
            "=": "#E6E6E6",  # Break
        }

        # deal with logic
        with open(datafile, "r") as fo:
            lines = [l.strip() for l in fo.readlines() if l.strip() != ""]

        xpm = XPM(outxpm, new_file=True)
        xpm.title = self.sel_parm(self.parm.title, "Secondary Structure")
        xpm.xlabel = self.sel_parm(self.parm.xlabel, "Frame")
        xpm.ylabel = self.sel_parm(self.parm.ylabel, "Residue")
        xpm.type = "Discrete"
        xpm.width = len(lines)
        xpm.height = len(lines[0])
        xpm.dot_matrix = [["" for _ in range(xpm.width)] for _ in range(xpm.height)]
        for id, line in enumerate(lines):
            if len(line) != xpm.height:
                self.error(
                    f"wrong line length of line {id} ({len(line)}), not equal to the first line ({xpm.height})"
                )
            for i, c in enumerate(line):
                xpm.dot_matrix[i][id] = c  # residue, top low, bottom high
        xpm.dot_matrix.reverse()  # residue, top high, bottom low
        xpm.datalines = ["".join(lis) for lis in xpm.dot_matrix]
        xpm.chars = sorted(
            list(set(chain(*xpm.dot_matrix))), key=lambda x: "~EBSTPIHG=".index(x)
        )
        for h in range(xpm.height):
            value_line: List[int] = []
            for w in range(xpm.width):
                value_line.append(xpm.chars.index(xpm.dot_matrix[h][w]))
            xpm.value_matrix.append(value_line)
        xpm.notes = [char_note_dict[c] for c in xpm.chars]
        xpm.colors = [char_color_dict[c] for c in xpm.chars]
        xpm.color_num = len(xpm.chars)
        xpm.char_per_pixel = 1

        if len(self.parm.columns) == 0:
            xpm.yaxis = [i + 1 for i in range(xpm.height)]
        elif len(self.parm.columns) != 0 and len(self.parm.columns[0]) == xpm.height:
            xpm.yaxis = self.parm.columns[0]
        elif len(self.parm.columns) != 0 and len(self.parm.columns[0]) != xpm.height:
            self.error(
                f"wrong specification of yaxis, need {xpm.height} numbers, but only {len(self.parm.columns[0])} were specified"
            )
        xpm.yaxis.reverse()  # turn into: from high to low
        if self.parm.begin and self.parm.end:
            xpm.xaxis = [i for i in range(self.parm.begin, self.parm.end, self.parm.dt)]
            if len(xpm.xaxis) != xpm.width:
                self.error(
                    f"wrong specification of xaxis, need {xpm.width} numbers, only get {len(xpm.xaxis)} numbers by -b, -e, and -dt"
                )
        elif self.parm.begin and not self.parm.end:
            xpm.xaxis = [
                i
                for i in range(
                    self.parm.begin,
                    self.parm.begin + xpm.width * self.parm.dt,
                    self.parm.dt,
                )
            ]
        elif not self.parm.begin and self.parm.end:
            self.error("you can not generate xaxis by only specifying -e without -b")
        else:
            xpm.xaxis = [i for i in range(xpm.width)]
        ## save xpm
        xpm.save(outxpm)

        ## dssp_sc
        time_residue_count: Dict[str : List[int]] = {}
        for char in xpm.chars:
            time_residue_count[char] = []
        for id, line in enumerate(lines):
            for key in time_residue_count.keys():
                time_residue_count[key].append(line.count(key))
        xaxis = xpm.xaxis[:]
        xvg_sc = XVG(outxvg_sc, new_file=True)
        xvg_sc.title = xpm.title
        xvg_sc.xlabel = xpm.xlabel
        xvg_sc.ylabel = "Number of Residues"
        xvg_sc.legends = [char_note_dict[c] for c in xpm.chars]
        xvg_sc.column_num = xpm.color_num + 1
        xvg_sc.row_num = len(xaxis)
        xvg_sc.data_heads = [xvg_sc.xlabel] + xvg_sc.legends
        xvg_sc.data_columns.append(xaxis)
        for char in xpm.chars:
            xvg_sc.data_columns.append(time_residue_count[char])
        Totals: List[int] = []
        for data in xvg_sc.data_columns[1:]:
            Totals.append(sum(data))
        SSpr: List[str] = [f"{t/sum(Totals):6.2f}" for t in Totals]
        xvg_sc.comments_tail += "# Totals " + " ".join([f"{t:6}" for t in Totals])
        xvg_sc.comments_tail += "\n# SS pr. " + " ".join(SSpr)
        xvg_sc.save(outxvg_sc)

        ## dssp_residue
        residue_frame_count: Dict[str : List[int]] = {}
        for char in xpm.chars:
            residue_frame_count[char] = []
        for id, line in enumerate(reversed(xpm.datalines)):
            for key in residue_frame_count.keys():
                residue_frame_count[key].append(line.count(key))
        xaxis = [x for x in reversed(xpm.yaxis)]
        xvg_res = XVG(outxvg_res, new_file=True)
        xvg_res.title = xpm.title
        xvg_res.xlabel = xpm.ylabel
        xvg_res.ylabel = "Number of Frames"
        xvg_res.legends = [char_note_dict[c] for c in xpm.chars]
        xvg_res.column_num = xpm.color_num + 1
        xvg_res.row_num = len(xaxis)
        xvg_res.data_heads = [xvg_res.xlabel] + xvg_res.legends
        xvg_res.data_columns.append(xaxis)
        for char in xpm.chars:
            xvg_res.data_columns.append(residue_frame_count[char])
        Totals: List[int] = []
        for data in xvg_res.data_columns[1:]:
            Totals.append(sum(data))
        SSpr: List[str] = [f"{t/sum(Totals):6.2f}" for t in Totals]
        xvg_res.comments_tail += "# Totals " + " ".join([f"{t:6}" for t in Totals])
        xvg_res.comments_tail += "\n# SS pr. " + " ".join(SSpr)
        xvg_res.save(outxvg_res)

        infos = """
        One-symbol secondary structure designations that are used in the output file:
        H - alpha-helix;
        B - residue in isolated beta-bridge;
        E - extended strand that participates in beta-ladder;
        G - 3_10_-helix;
        I - pi-helix;
        P - kappa-helix (poly-proline II helix);
        S - bend;
        T - hydrogen-bonded turn;
        = - break;
        ~ - loop (no special secondary structure designation).
        """
        self.info(infos)


class ndx_add(Command):
    """
    Generating a group of atom indexs and add it to index file. User can generate the atom indexs through `-c` by syntax like: `1-10-2,20-23`, which means generating [1,3,5,7,9,20,21,22]. And user can specify the index group name by `-al`.

    :Parameters:
        -al, --additional_list
                specify the groups name
        -c, --columns
                specify the atom indexs of groups
        -f, --input (optional)
                specify an existed index file to add group at its end
        -o, --ouput (optional)
                specify the output file name, default to `dit_index.ndx`

    :Usage:
        dit ndx_add -al lig mol -c 1-10-3,11-21 21-42
        dit ndx_add -f index.ndx -o test.ndx -al lig -c 1-10
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in ndx_add")
        # print(self.parm.__dict__)

        if self.parm.additional_list != None:
            groupnames = [l for l in self.parm.additional_list]
        else:
            self.error("you must specify additional_list to provide groupnames")
        if len(self.parm.columns) != 0:
            indexs_list = [c for c in self.parm.columns]
        else:
            self.error("you must specify columns to provide index groups")
        if len(groupnames) != len(indexs_list):
            self.error(
                f"The number of groupnames ({len(groupnames)}) should be equal to number of index groups ({len(indexs_list)})"
            )
        if self.parm.output:
            outname = self.parm.output
        else:
            outname = "dit_index.ndx"
        outname = self.check_output_exist(outname)
        if self.parm.input == None:
            ndx = NDX(outname, new_file=True)
        else:
            ndx = NDX(self.parm.input[0])
            if len(self.parm.input) > 1:
                self.warn(f"Only the first input file ({self.parm.input[0]}) was used")

        for name, indexs in zip(groupnames, indexs_list):
            if name in ndx.names:
                self.warn(
                    f"{name} already exists in ndxfile {ndx.ndxfile}. Anyway, added it for you"
                )
            ndx.add(name, indexs, 15)
        ndx.save(outname)


class ndx_split(Command):
    """
    Equally split one index group into N groups. Specify the group name (or group id) and the number N by `-al`. The new generated groups will be named by adding number to original name, like Protein_0.

    :Parameters:
        -f, --input
            specify the index file you contained the index group you wanna split
        -al, --additional_list
            specify the group name and the number N to split
        -o, --output (optional)
            specify the output file name, default to `dit_index.ndx`

    :Usage:
        dit ndx_split -f index.ndx -al 1 2
        dit ndx_split -f index.ndx -al Protein 2
        dit ndx_split -f index.ndx -al Protein 2 -o test.ndx
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in ndx_split")
        # print(self.parm.__dict__)

        if self.parm.additional_list == None:
            self.error(
                "you must specify additional_list to provide groupname and split_fold, like: Protein 2"
            )
        if (
            len(self.parm.additional_list) == 2
            and self.parm.additional_list[1].isnumeric()
        ):
            groupname = self.parm.additional_list[0]
            split_fold = int(self.parm.additional_list[1])
        else:
            self.error(
                "you must specify additional_list to provide groupname and split_fold, like: Protein 2"
            )
        if self.parm.output:
            outname = self.parm.output
        else:
            outname = "dit_index.ndx"
        outname = self.check_output_exist(outname)
        if self.parm.input == None:
            ndx = NDX(outname, new_file=True)
        else:
            ndx = NDX(self.parm.input[0])
            if len(self.parm.input) > 1:
                self.warn(f"Only the first input file ({self.parm.input[0]}) was used")

        if groupname.isnumeric():
            groupname = ndx.names[int(groupname)]
        name, indexs = ndx[groupname]
        if len(indexs) % split_fold != 0:
            self.error(
                f"got {len(indexs)} from group {name}, unable to equally devide into {split_fold} groups"
            )
        for i in range(split_fold):
            ndx[f"{groupname}_{i}"] = indexs[
                i * len(indexs) // split_fold : (i + 1) * len(indexs) // split_fold
            ]
        self.info(f"split '{name}' into {split_fold} groups successfully")

        ndx.save(outname)


class ndx_show(Command):
    """
    Show the index group names of one index file.

    :Parameters:
        -f, --input
            specify the index file name

    :Usage:
        dit ndx_show -f index.ndx
    """

    def __init__(self, parm: Parameters) -> None:
        self.parm = parm

    def __call__(self):
        # self.info("in ndx_show")
        # print(self.parm.__dict__)

        if self.parm.input == None:
            self.error("you have to specify a index file to show grounames")
        else:
            for ndxfile in self.parm.input:
                ndx = NDX(ndxfile)
                print(ndx.show_names)
