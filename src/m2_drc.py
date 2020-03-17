import pya
import sys
sys.path.append('./src')
import numpy as np
import pandas as pd
from LayoutGenerator import *
if __name__ == "__main__":
    params = ['cellname', 'wire_cd', 'track_pitch', 'min_t2t', 'max_t2t',
              'min_length', 'max_length', 't2t_grid', 'total_x', 'total_y']
    try:
        # m2_spec=m2_spec[params]
        m2_spec = pd.read_csv(csv_file, delimiter=',',
                              usecols=params, encoding='utf-16')
        # m2_spec
    except:
        print(m2_spec)
        print("Error: Invalid csv file, columns must contain: ", params)
        quit()
    dbu = 1e-3
    t2t_threshold = 0.013 / dbu # (max_t2t - min_t2t) * t2t_threshold
    wirelength_threshold = 0.036 / dbu # (max_length - min_length) * wirelength_threshold
    try:
        verbose = int(verbose)
    except:
        verbose = 1
    cell_number = len(m2_spec.cellname)
    layout = pya.Layout()
    layout.dbu = dbu
    topcell = layout.create_cell("M2")

    outLayer = outLayer.split('/')
    outLayerNum = int(outLayer[0])
    outLayerDT = int(outLayer[1])

    for i in range(cell_number):
        cellname = m2_spec.cellname[i]
        print("generating cell ", i, ":", cellname)
        wire_cd = int(m2_spec.wire_cd[i]/dbu)
        track_pitch = int(m2_spec.track_pitch[i]/dbu)
        min_t2t = int(m2_spec.min_t2t[i]/dbu)
        max_t2t = int(m2_spec.max_t2t[i]/dbu)
        min_length = int(m2_spec.min_length[i]/dbu)
        max_length = int(m2_spec.max_length[i]/dbu)
        #density     = int(m2_spec.density[i]*1e3)
        t2t_grid = int(m2_spec.t2t_grid[i]/dbu)

        total_x = int(m2_spec.total_x[i]/dbu)
        total_y = int(m2_spec.total_y[i]/dbu)
        cell = layout.create_cell(cellname)

        init_loc = [0, 0]

        l_m2 = layout.layer(outLayerNum, outLayerDT, "M2")
        for j in range(init_loc[1], total_y-wire_cd + init_loc[1], track_pitch):
            location = np.array([init_loc[0], j])
            draw_wire_row_drc(layout, outLayerNum, cell, l_m2, wire_cd,
                              min_length, max_length,
                              min_t2t, max_t2t, t2t_grid,
                              total_x, location, t2t_threshold=t2t_threshold, wirelength_threshold=wirelength_threshold)

        l_bb = layout.layer(1, 0, "bounding_box")
        # print c1ur.x,c2ll.x
        origin = [0, 0]
        bbll = pya.Point(origin[0], origin[1])
        bbur = pya.Point(origin[0]+total_x, origin[1]+total_y)
        cell.shapes(l_bb).insert(pya.Box(bbll, bbur))

        cellpath = cellname+'.gds'
        cell.write(os.path.join(dest, cellpath))
