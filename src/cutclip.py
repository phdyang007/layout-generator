import pya
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *
import os
import multiprocessing as mp 

if __name__ == "__main__":
    #cf: clip center #design:gds/oas path
    centers = np.loadtxt(cf)
    layout = pya.Layout()
    layout.read(design)
    top_cell = layout.top_cell()
    args=[]
    #for i in range(2):
    for i in range(len(centers)):
        args.append([layout, centers[i], top_cell, "via%g"%i])
        #out_cell=layout.create_cell("via%g"%i)
        #out_cell=extract_shapes(layout, centers[i], top_cell, out_cell)
#
        #out_cell.write(os.path.join(out, "via%g.gds"%i))

    p=mp.Pool(mp.cpu_count())
    p.map(extract_shapes_mp, args)
    


def extract_shapes_mp(arg):
    cell = extract_shapes(arg[0], arg[1], arg[2], arg[3])
    cell.write(os.path.join("./gds/%s.gds"%arg[3]))