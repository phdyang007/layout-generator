import pya
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *
import os
import multiprocessing as mp

def manump(group_id):
    layout = pya.Layout()
    layout.read(gdsIn)
    dbu=layout.dbu
    top_cell = layout.top_cell()
    centers = np.loadtxt("%s.txt"%gdsIn)*dbu
    total = len(centers)
    num_threads = 8
    try:
        parts = centers[group_id*total//num_threads:(group_id+1)*total//num_threads]
    except:
        parts = centers[group_id*total//num_threads:-1]
    #for i in range(2):
    for i in range(len(parts)):
        print("generate cell %g/%g/%g !"%(group_id, i,len(parts)))
        out_cell=layout.create_cell("clip%g"%i)
        out_cell=extract_shapes2(layout, parts[i], top_cell, out_cell)

        out_cell.write("./%s/clip%g-%g.gds"%(folder,group_id,i))


if __name__ == "__main__":
    #cf: clip center #design:gds/oas path
    p=mp.Pool(8)
    p.map(manump, range(8))
    





    


