import sys

sys.path.insert(0, '..')

import dbdreader
import logging
import glob
from pympler import asizeof

dbd = dbdreader.MultiDBD("../data/amadeus-2014*[st]bd")
dbd = dbdreader.MultiDBD("../data/amadeus-2014*sbd")
m_depth, m_lat = dbd.get("m_depth", "m_lat", include_source=True)

def f(x):
    return 1, 2, 3, 4
