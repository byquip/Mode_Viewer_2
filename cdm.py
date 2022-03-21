### COMSOL DATA managing ###
### Kostiantyn Vasko 06.10.2021 ###
import numpy as np
from io import StringIO


def replese_long_spaces(line_with_spaces):
    id_start = 0
    id_stop = 0
    prev_ch = ""
    list_of_ids = []
    for k, ch in enumerate(line_with_spaces):
        if ch == " " and prev_ch != " ":
            id_start = k
        if ch == " " and line_with_spaces[k+1] != " ":
            id_stop = k
            list_of_ids.append((id_start, id_stop))
        prev_ch = ch
    # print(list_of_ids)
    lin = line_with_spaces
    long_spaces = []
    for coords in list_of_ids:
        long_spaces.append(line_with_spaces[coords[0]:coords[1]+1])
    long_spaces.sort()
    long_spaces = list(set(long_spaces))
    long_spaces.sort()
    long_spaces.reverse()
    for st in long_spaces:
        lin = lin.replace(st, " ")
    return lin.replace("i", "j")


def get_file_ids(list_of_lists, file_name):
    for _i, lists in enumerate(list_of_lists):
        for _j, ls in enumerate(lists):
            if file_name == ls:
                return _i, _j


def read_comsol_table(path):
    data = ""
    with open(path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i < 5:
                continue  # skip 5 lines
            line_without_space = replese_long_spaces(line)
            data += line_without_space
        tab = np.genfromtxt(StringIO(data), delimiter=" ", dtype=np.complex)
        # tab = tab[:, 0:8]  # 9th colomn is wrong so I remove it.
    """ 
    Colomns: 
    0 - Wavelength
    1 - all the effective indexes
    2 - all the confinement loss
    3 - CL recognised
    4 - Neff recognised
    5 - optical overlap (F)
    6 - effective Area (Aeff)
    7 - Mode Feield Diameter (MFD)
    8 - GVD (broken, removed)
    """
    return tab
