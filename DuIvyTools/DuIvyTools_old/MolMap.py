"""
MolMap module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to map two pdb files which contain two small molecules
with exactly same comformation.

This module contains:
    - mol_map function

This file is provided to you by GPLv3 license."""

import os
import sys
import argparse
import logging


def similarity(li_0, li_1):
    if len(li_0) != len(li_1):
        print("Wrong")
        exit()
    simi = 0
    for i in range(len(li_0)):
        if li_0[i] != li_1[i]:
            simi += (li_0[i] - li_1[i], li_1[i] - li_0[i])[li_0[i] < li_1[i]]
    return simi


def readpdb2dic(file):
    origin = []
    with open(file, "r") as fo:
        lines = [
            line
            for line in fo.readlines()
            if line.startswith("ATOM") or line.startswith("HETATM")
        ]
    for line in lines:
        atom_num = int(line[6:11])
        atom_name = line[12:16].strip()
        coor_x = float(line[30:38])
        coor_y = float(line[38:46])
        coor_z = float(line[46:54])
        symbol = line[76:78].strip()
        dic = {
            "n": atom_num,
            "a": atom_name,
            "x": coor_x,
            "y": coor_y,
            "z": coor_z,
            "s": symbol,
        }
        origin.append(dic)

    heavy = [dic for dic in origin if dic["s"] != "H"]
    hydrogen = [dic for dic in origin if dic["s"] == "H"]

    ## deal with non-H
    distances = []
    for c1 in heavy:
        dist = []
        for c2 in heavy:
            d = (
                (c1["x"] - c2["x"]) ** 2
                + (c1["y"] - c2["y"]) ** 2
                + (c1["z"] - c2["z"]) ** 2
            ) ** 0.5
            dist.append(round(d * 3))
        distances.append(sorted(dist))

    ## deal with H
    nearest = []
    for c1 in hydrogen:
        dist = []
        for c2 in heavy:
            d = (
                (c1["x"] - c2["x"]) ** 2
                + (c1["y"] - c2["y"]) ** 2
                + (c1["z"] - c2["z"]) ** 2
            ) ** 0.5
            dist.append(d)
        nearest.append(dist.index(min(dist)))

    return origin, heavy, hydrogen, distances, nearest


def mol_map(name_file: str = "", coor_file: str = "", out_file: str = "") -> None:
    """
    mol_map: a function to map atom coordinates of one pdb file to another
    pdb file. The molecule in these two file should share exactly same
    comformation.

    :parameters:
        name_file: the pdb file which provedi infos except coordinates.
        coor_file: the pdb file which provide coordinates.
        out_file: the pdb file for output results.

    :return:
        None
    """

    #####################################################################
    #### 使用注意：输入的两个pdb文件中的分子必须一模一样，构象也必须一样
    ####
    #### 匹配算法说明
    #### 在pdb文件中，只有最后一列的原子类型可以作为参考，因为不能直接根
    #### 据原子名称等信息进行匹配。基于图同构之类的算法又太复杂了，这里
    #### 使用的是一种更简单的思路。
    #### 对于重原子：
    #### 每一个原子与其它所有重原子的距离的列表，应该是唯一的。因而计算
    #### 该原子与其它重原子的距离并从小到大排序，得到该原子的指纹。只需
    #### 要匹配到另一个pdb中相似度最高的指纹的原子，就应当是此原子了
    #### 对于氢原子：
    #### 确定了重原子的匹配之后，氢原子可以通过距离最近的重原子进行匹配，
    #### 对于同一个（匹配的）重原子，一定是唯一的那个氢原子与之距离最近，
    #### 对于等效H，如-CH2等，因为H是等效的，所以只需要匹配了之后剔除已
    #### 匹配的就好了，就算匹配交叉了，也不影响结果的正确性
    #####################################################################

    logging.info("The two molecules you input MUST be with the SAME conformation")

    for file in [name_file, coor_file]:
        if not os.path.exists(file):
            logging.error("no {} in current dirrectory. ".format(file))
            sys.exit()
        if file[-4:] != ".pdb":
            logging.error("mol_map only accept pdb file with suffix .pdb")
            sys.exit()

    origin1, heavy1, hydrogen1, distances1, nearest1 = readpdb2dic(name_file)
    origin2, heavy2, hydrogen2, distances2, nearest2 = readpdb2dic(coor_file)

    maplist = []
    for dli1 in distances1:
        sims = []
        for dli2 in distances2:
            sims.append(similarity(dli1, dli2))
        maplist.append(sims.index(min(sims)))
    Hmaplist = [-1 for _ in nearest1]
    for i1, near1 in enumerate(nearest1):
        for i2, near2 in enumerate(nearest2):
            if maplist[near1] == near2:
                Hmaplist[i1] = i2
                nearest2[i2] = -1
                break

    with open(name_file, "r") as fo:
        lines = fo.readlines()
    heavy_count, hydrogen_count = 0, 0
    with open(out_file, "w") as fo:
        for line in lines:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                symbol = line[76:78].strip()
                if symbol == "H":
                    atom = hydrogen2[Hmaplist[hydrogen_count]]
                    coor = "{:>8.3f}{:>8.3f}{:>8.3f}".format(
                        atom["x"], atom["y"], atom["z"]
                    )
                    fo.write(line[:30] + coor + line[54:])
                    hydrogen_count += 1
                else:
                    atom = heavy2[maplist[heavy_count]]
                    coor = "{:>8.3f}{:>8.3f}{:>8.3f}".format(
                        atom["x"], atom["y"], atom["z"]
                    )
                    fo.write(line[:30] + coor + line[54:])
                    heavy_count += 1
            else:
                fo.write(line)
    logging.warning("DIT can't ensure the results to be correct, CHECK IT by yourself")


def mol_map_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    parser = argparse.ArgumentParser(
        description="mapping coordinates of one pdb file to another pdb file"
    )
    parser.add_argument(
        "-n", "--name", help="pdb file providing infos except coordinates"
    )
    parser.add_argument("-c", "--coor", help="pdb file providing coordinates")
    parser.add_argument("-o", "--output", help="pdb file for output")

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
    if method == "mol_map":
        mol_map(args.name, args.coor, args.output)
    else:
        logging.error("unknown method {}".format(method))
        sys.exit()

    logging.info("good day !")


def main():
    mol_map_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
