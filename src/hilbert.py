import pya
import pandas as pd 
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *

if __name__ == "__main__":  
    params = ['cellname','length','wire_cd']
    try:
        #hilbert_spec=hilbert_spec[params]
        hilbert_spec = pd.read_csv(csv_file, delimiter=',', usecols=params, encoding='utf-16')
        #hilbert_spec
    except:
        print(hilbert_spec)
        print("Error: Invalid csv file, columns must contain: ", params)
        quit()
    dbu=1e-3
    try:
        verbose=int(verbose)
    except:
        verbose=1
    cell_number = len(hilbert_spec.cellname)
    layout = pya.Layout()
    layout.dbu=dbu
    topcell = layout.create_cell("hilbert")

    outLayer=outLayer.split('/')
    outLayerNum=int(outLayer[0])
    outLayerDT=int(outLayer[1])

    for i in range(cell_number):
        cellname    = hilbert_spec.cellname[i]
        print("generating cell ", i, ":", cellname)
        length = int(hilbert_spec.length[i]/dbu)
        wire_cd  = int(hilbert_spec.wire_cd[i]/dbu)

        init_loc=[0,0]

        l_hilbert = layout.layer(outLayerNum, outLayerDT, "hilbert")
        hilbert_generator = hilbert(layout, outLayerNum, outLayerDT, length,  wire_cd, 1)
        for _ in range(3):
            hilbert_generator.next_level()
            cellpath = cellname+'.oas'
            # hilbert_generator.write_level(hilbert_generator.level, os.path.join(dest, cellpath))
        hilbert_generator.write_layout(os.path.join(dest, cellpath))

    