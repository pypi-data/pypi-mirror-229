
from math import *


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return floor(n * multiplier) / multiplier


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return ceil(n * multiplier) / multiplier


def byteNotation(size_bytes: int):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "kB", "mB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(floor(log(size_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
