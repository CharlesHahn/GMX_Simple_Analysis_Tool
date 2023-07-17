"""
groParser module is part of DuIvyTools for parsing the gro file generated by GROMACS.

Written by DuIvy and provided to you by GPLv3 license.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from DIT import log


class Atom(object):
    def __init__(self, line: str) -> None:
        self.res_id = int(line[:5].strip())
        self.res_name = line[5:10].strip()
        self.atom_name = line[10:15].strip()
        self.atom_id = int(line[15:20].strip())
        self.coor_x = float(line[20:28].strip())
        self.coor_y = float(line[28:36].strip())
        self.coor_z = float(line[36:44].strip())
        self.coor = (self.coor_x, self.coor_y, self.coor_z)
        if len(line) > 45:
            self.velocity_x = float(line[44:52].strip())
            self.velocity_y = float(line[52:60].strip())
            self.velocity_z = float(line[60:68].strip())
        else:
            self.velocity_x = None
            self.velocity_y = None
            self.velocity_z = None
        self.velocity = (self.velocity_x, self.velocity_y, self.velocity_z)


class GRO(log):
    """GRO class for parsing gro file"""

    def __init__(self, grofile: str) -> None:
        self.frame_num: int = 0
        self.atom_number: int = 0
        self.frames: list[list[Atom]] = []
        self.notes: list[str] = []
        self.coors: list[tuple] = []
        with open(grofile, "r") as fo:
            lines = fo.readlines()
        try:
            self.atom_number = int(lines[1].strip())
        except:
            self.error("The second line of gro file must be Int number")
            sys.exit()
        self.frame_num = len(lines) // (self.atom_number + 3)
        for f in range(self.frame_num):
            atom_list: list[Atom] = []
            for line in lines[
                f * (self.atom_number + 3) + 2 : (f + 1) * (self.atom_number + 3) - 1
            ]:
                atom_list.append(Atom(line))
            self.frames.append(atom_list)
            self.notes.append(lines[f * (self.atom_number + 3)])
            coor_line = lines[(f + 1) * (self.atom_number + 3) - 1].strip().split()
            self.coors.append(tuple([float(c) for c in coor_line]))

    def get_time_info(self):
        pass


gro = GRO("../../test/hbond_test.gro")
print(gro.coors)
print(gro.notes)
print(gro.frame_num)
print(gro.frames[0][1].__dict__)
