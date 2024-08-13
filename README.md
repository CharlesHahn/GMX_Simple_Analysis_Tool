DuIvyTools

[![PyPI version](https://badge.fury.io/py/DuIvyTools.svg)](https://badge.fury.io/py/DuIvyTools)
![PyPI - Downloads](https://img.shields.io/pypi/dm/DuIvyTools)
![PyPI - License](https://img.shields.io/pypi/l/DuIvyTools)
[![Documentation Status](https://readthedocs.org/projects/duivytools/badge/?version=latest)](https://duivytools.readthedocs.io/zh_CN/latest/?badge=latest)
[![commits-since](https://img.shields.io/github/commits-since/CharlesHahn/DuIvyTools/v0.5.0.svg)](https://github.com/CharlesHahn/DuIvyTools/compare/v0.5.0...master)
[![Python Version](https://img.shields.io/pypi/pyversions/DuIvyTools.svg)](https://pypi.org/project/DuIvyTools)



```
  *******           **                  **********               **
 /**////**         /**          **   **/////**///               /**
 /**    /** **   **/** **    **//** **     /**  ******   ****** /**  ******
 /**    /**/**  /**/**/**   /** //***      /** **////** **////**/** **//// 
 /**    /**/**  /**/**//** /**   /**       /**/**   /**/**   /**/**//***** 
 /**    ** /**  /**/** //****    **        /**/**   /**/**   /**/** /////**
 /*******  //******/**  //**    **         /**//****** //****** *** ****** 
 ///////    ////// //    //    //          //  //////   ////// /// //////
```

DuIvyTools (DIT) is a simple analysis and visualization tool for GROMACS result
files, designed for fasten your analysis of molecular dynamics simulations. 

## Intro

The usage of DIT is similar to GMX, type `dit` and followed by commands and 
parameters, like:

```bash
dit xvg_show -f test.xvg
dit xpm_show -f test.xpm
```

Type `dit` for the commands supported. Type `dit <comman> -h` for detailed help information of each command. 

The tutorials (in Chinese) of DIT can be found at https://duivytools.readthedocs.io/

If you got any problem using DIT or suggestions, feel free to issue or contact me by 飞书 (Lark): https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=a22q9297-2060-43d5-8b28-73637c82cad6



## Install

This tool is a python3 library which you can install it by `pip`.

```bash
pip install DuIvyTools
```

## Commands

DuIvyTools provides about 30 commands for visualization and processing of GMX result files like .xvg or .xpm.

```
All commands are shown below:
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

You can type `dit <command> -h` for detailed help messages about each command, like: `dit xvg_show -h`.

All possible parameters could be inspected by `dit -h` or `dit --help`.

```

## Cite

If you used DuIvyTools in your research, cite it by doi please.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6339993.svg)](https://doi.org/10.5281/zenodo.6339993)



## Todo

- [ ] python unittest
- [ ] better docs
- [ ] easy API for draw lines with stddev (data, stddev two columns) in xvg file
- [ ] add a command to do AND/OR set operation to hbond or sltbr existance map
- [ ] add inter-classes to ease the use of plotting xpm or xvg data 
- [x] add -xp to plus or minus X or Y data, and in xpm_show cut to adjust xtick values
- [x] set the row of legends
- [x] to specify the figsize by commands
- [x] add xpm.comments
- [ ] speed up the xpm transforming process
- [ ] unequal number of x and y ticks in xpm like fel.xpm
- [ ] to set the tickintervals
- [ ] set the number of ticks
- [ ] add original xvg data to smv plot

## v0.5.5 new

1. cleaned the none acsii characters in dssp cmd
2. fixed the bug of calculating the confidence interval
3. add -xp to plus or minus data
4. add --legend_ncol to set the number of columns of legends
5. fixed the bug in dssp cmd about b==0
6. add figure.figsize in DIT.mplstyle to set the size of figure


## Others

A lot of time and money have been spent for developing DuIvyTools and improve it. If possible, **REWARD** to help me improve it. 


![reward](docs/static/reward.png)

