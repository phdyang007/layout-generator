import pya
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *
import os


if __name__ == "__main__":
    #cf: clip center #design:gds/oas path
    centers = np.loadtxt(cf)
    layout = pya.Layout()
    layout.read(design)
    top_cell = layout.top_cell()

    #for i in range(2):
    for i in range(len(centers)):
        print("generate cell %g/%g !"%(i,len(centers)))
        out_cell=layout.create_cell("via%g"%i)
        out_cell=extract_shapes(layout, centers[i], top_cell, out_cell)

        out_cell.write(os.path.join(out, "via%g.gds"%i))

    

