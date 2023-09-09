import sys

sys.path.insert(0, '..')

import dbdreader
import logging
import glob

fns=glob.glob("../data/amadeus*.[ST]BD")
#fns=glob.glob("../data/amadeus*.[st]bd")

#fns = "b.sbd a.sbd b.tbd a.tbd".split()
#fns = "b.SBD a.SBD b.TBD a.TBD".split()

fns = dbdreader.DBDList(fns)

fns.sort()


#logging.basicConfig(level=logging.DEBUG)
#dbd = dbdreader.MultiDBD(pattern = "../data/*-2014-204-05-000.dbd")
#dbd = dbdreader.MultiDBD(pattern = "../data/amadeus*.[ST]BD")
