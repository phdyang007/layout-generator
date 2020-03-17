import pya
import pandas as pd 
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *

if __name__ == "__main__":  
    params = ['cellname','length','wire_cd']
    try:
        #peano_spec=peano_spec[params]
        peano_spec = pd.read_csv(csv_file, delimiter=',', usecols=params, encoding='utf-16')
        #peano_spec
    except:
        print(peano_spec)
        print("Error: Invalid csv file, columns must contain: ", params)
        quit()
    dbu=1e-3
    try:
        verbose=int(verbose)
    except:
        verbose=1
    cell_number = len(peano_spec.cellname)
    layout = pya.Layout()
    layout.dbu=dbu
    topcell = layout.create_cell("peano")

    levels = 7
    outLayer=outLayer.split('/')
    outLayerNum=int(outLayer[0])
    outLayerDT=int(outLayer[1])

    for i in range(cell_number):
        cellname    = peano_spec.cellname[i]
        print("generating cell ", i, ":", cellname)
        length = int(peano_spec.length[i]/dbu)
        wire_cd  = int(peano_spec.wire_cd[i]/dbu)

        l_peano = layout.layer(outLayerNum, outLayerDT, "peano")
        peano_generator = peano(layout, outLayerNum, outLayerDT, length,  wire_cd, 1)
        for _ in range(levels):
            peano_generator.next_level()
            cellpath = cellname+'.oas'
            # peano_generator.write_level(peano_generator.level, os.path.join(dest, cellpath))
        peano_generator.write_layout(os.path.join(dest, cellpath))

    