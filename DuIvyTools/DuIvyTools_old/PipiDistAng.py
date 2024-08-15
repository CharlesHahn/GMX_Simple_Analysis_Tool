"""
Pipi_dist_ang module is part of DuIvyTools library, which is a tool for analysis and 
visualization of GROMACS result files. This module is written by CharlesHahn.

This module is designed to calculate the distance ang angles between two rings you 
specified in index file or between a ring and a vector

This module contains:
    - pipi_dist_ang function

This file is provided to you by GPLv3 license."""

import os
import sys
import math
import argparse
import logging


def calcDist(ring_1_frames: list = [], ring_2_frames: list = []) -> list:
    """
    calcDist: to calculate the distances of two rings

    :parameter:
        ring_1_frames: a list stored coordinates of ring 1 of different frames
        ring_2_frames: a list stored coordinates of ring 2 of different frames

    :return:
        distance: a list to store distance
    """

    ## check the frames of two ring
    if len(ring_1_frames) != len(ring_2_frames):
        logging.error("length of frames of coordinates isn't equal")
        sys.exit()
    ## calculate the distance between two ring
    distance = []
    for i in range(len(ring_1_frames)):
        ring_1_coor = ring_1_frames[i]
        ring_2_coor = ring_2_frames[i]
        ring_1_atom_num = len(ring_1_coor) * 1.0
        ring_2_atom_num = len(ring_2_coor) * 1.0
        ## calculate the center of two ring
        ring_1_center = [
            sum([coor[0] for coor in ring_1_coor]) / ring_1_atom_num,
            sum([coor[1] for coor in ring_1_coor]) / ring_1_atom_num,
            sum([coor[2] for coor in ring_1_coor]) / ring_1_atom_num,
        ]
        ring_2_center = [
            sum([coor[0] for coor in ring_2_coor]) / ring_2_atom_num,
            sum([coor[1] for coor in ring_2_coor]) / ring_2_atom_num,
            sum([coor[2] for coor in ring_2_coor]) / ring_2_atom_num,
        ]
        ## calculate the distance
        dist = (
            (ring_1_center[0] - ring_2_center[0]) ** 2
            + (ring_1_center[1] - ring_2_center[1]) ** 2
            + (ring_1_center[2] - ring_2_center[2]) ** 2
        ) ** 0.5
        distance.append(dist)

    return distance


def calcAng(ring_1_frames: list = [], ring_2_frames: list = []) -> list:
    """
    calcAng: to calculate the Angles of two rings

    :parameter:
        ring_1_frames: a list stored coordinates of ring 1 of different frames
        ring_2_frames: a list stored coordinates of ring 2 of different frames

    :return:
        angle: a list to store angles
    """
    ## check the frames of two ring
    if len(ring_1_frames) != len(ring_2_frames):
        logging.error("length of frames of coordinates isn't equal")
        exit()
    ## calculate the angles
    angles = []
    for i in range(len(ring_1_frames)):
        ring_1_coor = ring_1_frames[i]
        ring_2_coor = ring_2_frames[i]
        ## p1 = [ a1, a2, a3 ], p2 = [ b1, b2, b3 ]
        ## p1xp2 = [ a2b3 - a3b2, a3b1 - a1b3, a1b2 - a2b1 ]
        ## calculate the plane normal of ring 1 by cross product
        r1_p1 = [
            ring_1_coor[2][0] - ring_1_coor[0][0],
            ring_1_coor[2][1] - ring_1_coor[0][1],
            ring_1_coor[2][2] - ring_1_coor[0][2],
        ]
        r1_p2 = [
            ring_1_coor[4][0] - ring_1_coor[0][0],
            ring_1_coor[4][1] - ring_1_coor[0][1],
            ring_1_coor[4][2] - ring_1_coor[0][2],
        ]
        r1_xProd = [
            r1_p1[1] * r1_p2[2] - r1_p1[2] * r1_p2[1],
            r1_p1[2] * r1_p2[0] - r1_p1[0] * r1_p2[2],
            r1_p1[0] * r1_p2[1] - r1_p1[1] * r1_p2[0],
        ]
        ## calculate the plane normal of ring 2 by cross product
        r2_p1 = [
            ring_2_coor[2][0] - ring_2_coor[0][0],
            ring_2_coor[2][1] - ring_2_coor[0][1],
            ring_2_coor[2][2] - ring_2_coor[0][2],
        ]
        r2_p2 = [
            ring_2_coor[4][0] - ring_2_coor[0][0],
            ring_2_coor[4][1] - ring_2_coor[0][1],
            ring_2_coor[4][2] - ring_2_coor[0][2],
        ]
        r2_xProd = [
            r2_p1[1] * r2_p2[2] - r2_p1[2] * r2_p2[1],
            r2_p1[2] * r2_p2[0] - r2_p1[0] * r2_p2[2],
            r2_p1[0] * r2_p2[1] - r2_p1[1] * r2_p2[0],
        ]
        ## calc the degree
        dotProduct = r1_xProd[0] * r2_xProd[0] + r1_xProd[1] * r2_xProd[1]
        dotProduct += r1_xProd[2] * r2_xProd[2]
        r1_xProd_norm = (r1_xProd[0] ** 2 + r1_xProd[1] ** 2 + r1_xProd[2] ** 2) ** 0.5
        r2_xProd_norm = (r2_xProd[0] ** 2 + r2_xProd[1] ** 2 + r2_xProd[2] ** 2) ** 0.5
        cos_degree = dotProduct / (r1_xProd_norm * r2_xProd_norm)
        degree = math.acos(cos_degree) * 180 / math.pi
        if degree > 90:
            degree = 180 - degree
        angles.append(degree)

    return angles


def getCoor(gro_file: str = "", ring_1_id: list = [], ring_2_id: list = []) -> tuple:
    """
    getCoor: to get the coordinates of atoms of two rings

    :parameter:
        gro_file: the gro filename
        ring_1_id: the atom ids of ring 1
        ring_2_id: the atom ids of ring 2

    :return:
        time: a list to store frames
        ring_1_frames: a list to store coordinates of frames
        ring_2_frames: a list to store coordinates of frames
    """

    with open(gro_file, "r") as fo:
        lines = fo.readlines()
    frames = []
    atom_lines = []
    for line in lines:
        ## not the atom line, judged by length of line
        if len(line) != 45 and len(line) != 69:
            # number line
            if len(line.strip().split()) == 1:
                if len(atom_lines) != 0:
                    frames.append(atom_lines)
                atom_lines = []
        elif len(line) == 45 or len(line) == 69:
            # suit for atom number < 10000
            if len(line[20:44].split()) == 3 and len(line[15:44].split()) == 4:
                atom_lines.append(line.rstrip())
    ## add the last frame
    if len(atom_lines) != 0:
        frames.append(atom_lines)
    ## read the atom coor
    ring_1_frames = []
    ring_2_frames = []
    for frame in frames:
        ring_1_coor = []
        ring_2_coor = []
        for line in frame:
            if int(line[15:20]) in ring_1_id:
                ring_1_coor.append(
                    [float(line[20:28]), float(line[28:36]), float(line[36:44])]
                )
            if int(line[15:20]) in ring_2_id:
                ring_2_coor.append(
                    [float(line[20:28]), float(line[28:36]), float(line[36:44])]
                )
        if len(ring_1_coor) != len(ring_1_id) or len(ring_2_coor) != len(ring_2_id):
            logging.error("shit happens when reading coordinates of ring")
            sys.exit()
        ring_1_frames.append(ring_1_coor)
        ring_2_frames.append(ring_2_coor)
    ## new a time sequence
    time = [i for i in range(len(frames))]

    return time, ring_1_frames, ring_2_frames


def dealNdx(ndx_file: str = "", select: list = [], vg: bool = False) -> tuple:
    """
    dealNdx: to process the index file

    :parameter:
        ndx_file: the index filename
        select: a list to store the groupnames specified
        vg: whether to use a group in index file for vector calculation

    :return:
        ring_1_id: a list to store the atom id of ring 1
        ring_2_id: a list to store the atom id of ring 2
    """

    with open(ndx_file, "r") as fo:
        content = fo.read()
    ## read in each group
    ndx_dic = {}
    content = content.strip().strip("[").replace("\n", " ")
    ndx_groups = content.split("[")
    for group in ndx_groups:
        items = group.split("]")
        if items[0].strip() in ndx_dic.keys():
            logging.error("two groups with the same name")
            sys.exit()
        ndx_dic[items[0].strip()] = [
            int(n.strip()) for n in items[1].split() if n != ""
        ]
    if select == None:
        ## print to get input from user
        logging.info("reading your index file:")
        for name, num_lis in ndx_dic.items():
            print("    {:30}   {:8} atoms".format(name, len(num_lis)))
            # print(" ".join([ str(i) for i in num_lis]))
        if vg == False:
            ring_1_name = input("Type the name of first ring -> ")
            logging.info("you have chosed " + ring_1_name + " as first ring.")
            ring_2_name = input("Type the name of second ring -> ")
            logging.info("you have chosed " + ring_2_name + " as second ring.")
        elif vg == True:
            ring_1_name = input("Type the name of ring group -> ")
            logging.info("you have chosed " + ring_1_name + " as first ring.")
            ring_2_name = input("Type the name of vector group-> ")
            logging.info("you have chosed " + ring_2_name + " as vector group.")
    elif len(select) == 2:
        if vg == False:
            ring_1_name = select[0]
            logging.info("you have chosed " + ring_1_name + " as first ring.")
            ring_2_name = select[1]
            logging.info("you have chosed " + ring_2_name + " as second ring.")
        elif vg == True:
            ring_1_name = select[0]
            logging.info("you have chosed " + ring_1_name + " as first ring.")
            ring_2_name = select[1]
            logging.info("you have chosed " + ring_2_name + " as vector group.")
    else:
        logging.error("Wrong parameter number of -select")
        sys.exit()

    ## atom id of two ring groups
    ring_1_id = ndx_dic[ring_1_name]
    ring_2_id = ndx_dic[ring_2_name]

    ## return the atom ids of these two rings
    return ring_1_id, ring_2_id


def dealNdx_single(ndx_file: str = "", select: list = []) -> list:
    """
    dealNdx_single: to deal with index file with one group needed

    :parameter:
        ndx_file: the index filename
        select: a list to store index group name specified in command line

    :return:
        ring_1_id: a list to store the atom id
    """

    with open(ndx_file, "r") as fo:
        content = fo.read()
    ## read in each group
    ndx_dic = {}
    content = content.strip().strip("[").replace("\n", " ")
    ndx_groups = content.split("[")
    for group in ndx_groups:
        items = group.split("]")
        if items[0].strip() in ndx_dic.keys():
            logging.error("two groups with the same name")
            sys.exit()
        ndx_dic[items[0].strip()] = [
            int(n.strip()) for n in items[1].split() if n != ""
        ]
    ## print to get input from user
    logging.info("reading your index file:")
    for name, num_lis in ndx_dic.items():
        print("    {:30}   {:8} atoms".format(name, len(num_lis)))
    # print(" ".join([ str(i) for i in num_lis]))
    if select == None:
        ring_1_name = input("Type the name of first ring -> ")
        logging.info("you have chosed " + ring_1_name + " as first ring.")
    elif len(select) == 1:
        ring_1_name = select[0]
        logging.info("you have chosed " + ring_1_name + " as first ring.")
    else:
        logging.error("you may only need one parameter for select")
        sys.exit()

    ## atom id of two ring groups
    ring_1_id = ndx_dic[ring_1_name]

    ## return the atom ids of these two rings
    return ring_1_id


def calcAng_RingVec(ring_frames: list = [], vec_frames: list = []) -> list:
    """
    calcAng_RingVec: to calculate the anglef between a ring and a vector

    :parameter:
        ring_frames: a list to store atom coordinates of frames
        vec_frames: a list to store vector of frames

    :return:
        angles: a list to store angles
    """

    ## check the frames
    if len(ring_frames) != len(vec_frames):
        logging.error("length of frames of ring and vector isn't equal")
        sys.exit()
    ## calculate the angles
    angles = []
    for i in range(len(ring_frames)):
        ring_1_coor = ring_frames[i]
        vector = vec_frames[i]
        ## p1 = [ a1, a2, a3 ], p2 = [ b1, b2, b3 ]
        ## p1xp2 = [ a2b3 - a3b2, a3b1 - a1b3, a1b2 - a2b1 ]
        ## calculate the plane normal of ring 1 by cross product
        r1_p1 = [
            ring_1_coor[2][0] - ring_1_coor[0][0],
            ring_1_coor[2][1] - ring_1_coor[0][1],
            ring_1_coor[2][2] - ring_1_coor[0][2],
        ]
        r1_p2 = [
            ring_1_coor[4][0] - ring_1_coor[0][0],
            ring_1_coor[4][1] - ring_1_coor[0][1],
            ring_1_coor[4][2] - ring_1_coor[0][2],
        ]
        r1_xProd = [
            r1_p1[1] * r1_p2[2] - r1_p1[2] * r1_p2[1],
            r1_p1[2] * r1_p2[0] - r1_p1[0] * r1_p2[2],
            r1_p1[0] * r1_p2[1] - r1_p1[1] * r1_p2[0],
        ]
        ## calc the degree
        dotProduct = r1_xProd[0] * vector[0] + r1_xProd[1] * vector[1]
        dotProduct += r1_xProd[2] * vector[2]
        r1_xProd_norm = (r1_xProd[0] ** 2 + r1_xProd[1] ** 2 + r1_xProd[2] ** 2) ** 0.5
        vector_norm = (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5
        cos_degree = dotProduct / (r1_xProd_norm * vector_norm)
        degree = math.acos(cos_degree) * 180 / math.pi
        if degree > 90:
            degree = 180 - degree
        angles.append(degree)
    return angles


def calcVec(vg_frames: list = []) -> list:
    """
    calcVec: to calculate the vector from vector group

    :parameter:
        vg_frames: a list to store vector atom coordinates of frames

    :return:
        vg_vec_frames: a list to store result vectors
    """

    vg_vec_frames = []
    for atoms in vg_frames:
        vec = [0, 0, 0]
        for i in range(1, len(atoms)):
            vec[0] += atoms[i][0] - atoms[i - 1][0]
            vec[1] += atoms[i][1] - atoms[i - 1][1]
            vec[2] += atoms[i][2] - atoms[i - 1][2]
        vec = [v / (len(atoms) - 1) for v in vec]
        vg_vec_frames.append(vec)
    return vg_vec_frames


def dealTwoRings(
    ndx_file: str = "",
    gro_file: str = "",
    time_b: int = 0,
    time_dt: int = 1,
    output_file: str = "",
    select: list = [],
) -> None:
    """
    dealTwoRings: to calculate the distance and angles of two rings

    :parameter:
        ndx_file: index filename
        gro_file: gro filename
        time_b: the start frame
        time_dt: the frame interval
        output_file: a filename for output
        select: a list to store the selected index group name
    """

    ## get the atom id
    ring_1_id, ring_2_id = dealNdx(ndx_file, select, False)
    if (
        len(ring_1_id) < 5
        or len(ring_1_id) > 7
        or len(ring_2_id) < 5
        or len(ring_2_id) > 7
    ):
        logging.error("index of your ring is more than 7 or less than 5")
        logging.error("only support 5, 6 or 7 membered ring which is in a plane ")
        logging.error("please check your index file")
        logging.error("your index : {} {}".format(ring_1_id, ring_2_id))
        sys.exit()
    ## get the coordinates of two rings
    time, ring_1_frames, ring_2_frames = getCoor(gro_file, ring_1_id, ring_2_id)
    ## modify the time sequence
    time = [t * time_dt + time_b for t in time]
    # print(len(time), len(ring_1_frames), len(ring_2_frames))
    ## calculate the distance of two rings
    distance = calcDist(ring_1_frames, ring_2_frames)
    ## calculate the angles of the normals of two rings
    angles = calcAng(ring_1_frames, ring_2_frames)
    # print(len(time), len(distance), len(angles))
    ## check data and output
    logging.info("there is {} frames in your gro file".format(len(time)))
    if len(time) != len(distance) or len(time) != len(angles):
        logging.error("length of time, dist, ang are not equal")
        logging.info(
            "time: {}; distance: {}; angles: {}".format(
                len(time), len(distance), len(angles)
            )
        )
        sys.exit()
    out_content = "# This file was created by DIT pipi_dist_ang\n"
    out_content += """@    title "Dist_Ang"\n"""
    out_content += """@    xaxis  label "Frames"\n"""
    out_content += """@    yaxis  label ""\n"""
    out_content += """@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n"""
    out_content += """@ legend on\n@ legend box on\n@ legend loctype view\n"""
    out_content += """@ legend 0.78, 0.8\n@ legend length 2\n"""
    out_content += """@ s0 legend "Dist (nm)"\n@ s1 legend "Angle"\n"""
    out_content += "\n".join(
        [
            "{:<10.0f} {:>10.3f} {:>10.3f} ".format(time[i], distance[i], angles[i])
            for i in range(len(distance))
        ]
    )
    with open(output_file, "w") as fo:
        fo.write(out_content)

    ## calc the angle distribution
    ang0_30, ang30_60, ang60_90 = 0, 0, 0
    for ang in angles:
        if ang >= 0 and ang < 30:
            ang0_30 += 1
        elif ang >= 30 and ang < 60:
            ang30_60 += 1
        elif ang > 60:
            ang60_90 += 1
    print("-" * 79)
    print(
        " =>  0 <= angle < 30 : {}/{} = {:>6.2%}".format(
            ang0_30, len(time), ang0_30 * 1.0 / len(time)
        )
    )
    print(
        " => 30 <= angle < 60 : {}/{} = {:>6.2%}".format(
            ang30_60, len(time), ang30_60 * 1.0 / len(time)
        )
    )
    print(
        " => 60 <= angle < 90 : {}/{} = {:>6.2%}".format(
            ang60_90, len(time), ang60_90 * 1.0 / len(time)
        )
    )
    print("-" * 79)
    ## calc the average distance
    logging.info("average distance : {:>10.4f} nm".format(sum(distance) / len(time)))


def dealRingVG(
    ndx_file: str = "",
    gro_file: str = "",
    time_b: int = 0,
    time_dt: int = 1,
    output_file: str = "",
    select: list = [],
) -> None:
    """
    dealRingVG: to calculate the distance and angles of ring and vector from index group

    :parameter:
        ndx_file: index filename
        gro_file: gro filename
        time_b: the start frame
        time_dt: the frame interval
        output_file: a filename for output
        select: a list to store the selected index group name
    """

    ring_id, vg_id = dealNdx(ndx_file, select, True)
    if len(ring_id) < 5 or len(ring_id) > 7:
        logging.error("index of your ring is more than 7 or less than 5")
        logging.error("only support 5, 6 or 7 membered ring which is in a plane ")
        logging.error("please check your index file")
        logging.error("your index : {}".format(ring_id))
        sys.exit()
    if len(vg_id) < 2:
        logging.error("less than 2 atom index in vector group you input")
        logging.error("2 or more atom index are needed")
        logging.error("check your vector index : {}".format(vg_id))
        sys.exit()
    ## get the coordinates of ring and vg
    time, ring_frames, vg_frames = getCoor(gro_file, ring_id, vg_id)
    ## modify the time sequence
    time = [t * time_dt + time_b for t in time]
    # calculate the vector vs time
    vg_vec_frames = calcVec(vg_frames)
    ## calculate the angles
    angles = calcAng_RingVec(ring_frames, vg_vec_frames)
    # save results
    logging.info("there is {} frames in your gro file".format(len(time)))
    if len(time) != len(angles):
        logging.error("length of time, angles are not equal")
        logging.info("time: {}; angles: {}".format(len(time), len(angles)))
    out_content = "# This file was created by DIT pipi_dist_ang\n"
    out_content += """@    title "Angle of ring and vector"\n"""
    out_content += """@    xaxis  label "Frames"\n"""
    out_content += """@    yaxis  label "Angle"\n"""
    out_content += """@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n"""
    out_content += """@ legend on\n@ legend box on\n@ legend loctype view\n"""
    out_content += """@ legend 0.78, 0.8\n@ legend length 2\n"""
    out_content += "\n".join(
        ["{:<10.0f} {:>10.3f} ".format(time[i], angles[i]) for i in range(len(angles))]
    )
    with open(output_file, "w") as fo:
        fo.write(out_content)
    ## calc the angle distribution
    ang0_30, ang30_60, ang60_90 = 0, 0, 0
    for ang in angles:
        if ang >= 0 and ang < 30:
            ang0_30 += 1
        elif ang >= 30 and ang < 60:
            ang30_60 += 1
        elif ang > 60:
            ang60_90 += 1
    print("-" * 79)
    print(
        " =>  0 <= angle < 30 : {}/{} = {:>6.2%}".format(
            ang0_30, len(time), ang0_30 * 1.0 / len(time)
        )
    )
    print(
        " => 30 <= angle < 60 : {}/{} = {:>6.2%}".format(
            ang30_60, len(time), ang30_60 * 1.0 / len(time)
        )
    )
    print(
        " => 60 <= angle < 90 : {}/{} = {:>6.2%}".format(
            ang60_90, len(time), ang60_90 * 1.0 / len(time)
        )
    )
    print("-" * 79)


def dealRingVec(
    ndx_file: str = "",
    gro_file: str = "",
    time_b: int = 0,
    time_dt: int = 1,
    output_file: str = "",
    vec: list = [],
    select: list = [],
) -> None:
    """
    dealRingVec: to calculate the distance and angles of ring and vector

    :parameter:
        ndx_file: index filename
        gro_file: gro filename
        time_b: the start frame
        time_dt: the frame interval
        output_file: a filename for output
        vec: a list to store vector
        select: a list to store the selected index group name
    """

    ring_id = dealNdx_single(ndx_file, select)
    if len(ring_id) < 5 or len(ring_id) > 7:
        logging.error("index of your ring is more than 7 or less than 5")
        logging.error("only support 5, 6 or 7 membered ring which is in a plane ")
        logging.error("please check your index file")
        logging.error("your index : {}".format(ring_id))
        sys.exit()
    time, ring_frames, _ = getCoor(gro_file, ring_id, ring_id)
    ## modify the time sequence
    time = [t * time_dt + time_b for t in time]
    # deal with vec
    vec = [float(i) for i in vec]
    if 0 == vec[0] == vec[1] == vec[2]:
        logging.error("You can't input an all zero vector")
        sys.exit()
    vec_frames = [vec for i in range(len(time))]
    # calculate the angles
    angles = calcAng_RingVec(ring_frames, vec_frames)
    # save results
    logging.info("there is {} frames in your gro file".format(len(time)))
    if len(time) != len(angles):
        logging.error("length of time, angles are not equal")
        logging.info("time: {}; angles: {}".format(len(time), len(angles)))
    out_content = "# This file was created by DIT pipi_dist_ang\n"
    out_content += """@    title "Angle of ring and vector"\n"""
    out_content += """@    xaxis  label "Frames"\n"""
    out_content += """@    yaxis  label "Angle"\n"""
    out_content += """@TYPE xy\n@ view 0.15, 0.15, 0.75, 0.85\n"""
    out_content += """@ legend on\n@ legend box on\n@ legend loctype view\n"""
    out_content += """@ legend 0.78, 0.8\n@ legend length 2\n"""
    out_content += "\n".join(
        ["{:<10.0f} {:>10.3f} ".format(time[i], angles[i]) for i in range(len(angles))]
    )
    with open(output_file, "w") as fo:
        fo.write(out_content)
    ## calc the angle distribution
    ang0_30, ang30_60, ang60_90 = 0, 0, 0
    for ang in angles:
        if ang >= 0 and ang < 30:
            ang0_30 += 1
        elif ang >= 30 and ang < 60:
            ang30_60 += 1
        elif ang > 60:
            ang60_90 += 1
    print("-" * 79)
    print(
        " =>  0 <= angle < 30 : {}/{} = {:>6.2%}".format(
            ang0_30, len(time), ang0_30 * 1.0 / len(time)
        )
    )
    print(
        " => 30 <= angle < 60 : {}/{} = {:>6.2%}".format(
            ang30_60, len(time), ang30_60 * 1.0 / len(time)
        )
    )
    print(
        " => 60 <= angle < 90 : {}/{} = {:>6.2%}".format(
            ang60_90, len(time), ang60_90 * 1.0 / len(time)
        )
    )
    print("-" * 79)


def pipi_dist_ang(
    ndx_file: str = "",
    gro_file: str = "",
    time_b: int = 0,
    time_dt: int = 1,
    output_file: str = "",
    vg: bool = False,
    vec: list = [],
    select: list = [],
) -> None:
    """
    pipi_dist_ang: a list to check parameters and start init calculation

    :parameter:
        ndx_file: index filename
        gro_file: gro filename
        time_b: the start frame
        time_dt: the frame interval
        output_file: a filename for output
        vg: whether to get vector from atom id in index file
        vec: a list to store vector
        select: a list to store the selected index group name
    """

    if ndx_file == "":
        logging.error("please specify index file by -n")
        sys.exit()
    if gro_file == "":
        logging.error("please specify gro file by -f")
        sys.exit()
    if output_file == "":
        logging.error("please specify output file by -o")
        sys.exit()
    if not os.path.exists(ndx_file):
        logging.error("no {} in current directory".format(ndx_file))
        sys.exit()
    if not os.path.exists(gro_file):
        logging.error("no {} in current directory".format(gro_file))
        sys.exit()
    if os.path.exists(output_file):
        logging.error("already one {} in current directory".format(output_file))
        sys.exit()

    if vec == None and vg == False:
        dealTwoRings(ndx_file, gro_file, time_b, time_dt, output_file, select)
    elif vec == None and vg == True:
        dealRingVG(ndx_file, gro_file, time_b, time_dt, output_file, select)
    elif vec != None and vg == False:
        dealRingVec(ndx_file, gro_file, time_b, time_dt, output_file, vec, select)
    elif vec != None and vg == True:
        logging.error("You can't set -vg and -vec at the same time")
        sys.exit()


def pipi_dist_ang_call_functions(arguments: list = []):
    """call functions according to arguments"""

    if len(arguments) == 0:
        arguments = [argv for argv in sys.argv]

    ## parse the command parameters
    description = "To calculate the distance and angles of two 5 or 6 membered"
    description += "rings or vectors you defined"
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input", help="gro file")
    parser.add_argument("-n", "--index", help="index file contains two groups of rings")
    parser.add_argument("-b", default=0, type=int, help="set the start time, default=0")
    parser.add_argument(
        "-dt", default=1, type=int, help="set the time interval, default=1"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.xvg",
        help="the results data, default output.xvg",
    )
    parser.add_argument(
        "-vg", action="store_true", help="whether to get vector by index group"
    )
    parser.add_argument(
        "-vec", nargs=3, help="get vector by your input, eg. -vec 6 6 6"
    )
    parser.add_argument(
        "-select", nargs="*", help="select the groups, eg. -select ring1 ring2"
    )

    if len(arguments) < 2:
        logging.error("no input parameters, -h or --help for help messages")
        sys.exit()

    method = arguments[1]
    # print(method)
    if method in ["-h", "--help"]:
        parser.parse_args(arguments[1:])
        sys.exit()

    if len(arguments) == 2:
        logging.error("no parameters, type 'dit pip_dist_ang -h' for more infos.")
        sys.exit()
    args = parser.parse_args(arguments[2:])
    if method == "pipi_dist_ang":
        pipi_dist_ang(
            args.index,
            args.input,
            args.b,
            args.dt,
            args.output,
            args.vg,
            args.vec,
            args.select,
        )
    else:
        logging.error("unknown method {}".format(method))
        sys.exit()

    logging.info("good day !")


def main():
    pipi_dist_ang_call_functions()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s -> %(message)s")
    logger = logging.getLogger(__name__)
    main()
