import math
import os


def get_file_list_by_ext(ext, dir="./data"):
    """ Get list of files by extension """
    return [os.path.join(dir, file) for file in os.listdir(dir) if file.endswith(ext)]


def fix_nan_in_list(list):
    return [0 if math.isnan(x) else x for x in list]
