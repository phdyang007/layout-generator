import pya
import pandas as pd 
import numpy as np 
import sys
sys.path.append('./src')
from LayoutGenerator import *
import random 


if __name__ == "__main__":  
    params = ['cellname','wire_cd','track_pitch','min_t2t','max_t2t',
              'min_length','max_length','t2t_grid','total_x','total_y']
    #m2_spec = pd.read_csv(csv_file, delimiter='\t', usecols=params, encoding='utf-16')
    try:
        #m2_spec=m2_spec[params]
        m2_spec = pd.read_csv(csv_file, delimiter=',', usecols=params, encoding='utf-16')
        #print(csv_file)
        #m2_spec
    except:
        #print(m2_spec)
        print("Error: Invalid csv file, columns must contain: ", params)
        quit()
    dbu=1e-3
    try:
        verbose=int(verbose)
    except:
        verbose=1
    cell_number = len(m2_spec.cellname)
    layout = pya.Layout()
    layout.dbu=dbu
    topcell = layout.create_cell("M2")

    outLayer=outLayer.split('/')
    outLayerNum=int(outLayer[0])
    outLayerDT=int(outLayer[1])

    for i in range(cell_number):
        cellname    = m2_spec.cellname[i]
        print("generating cell ", i, ":", cellname)
        wire_cd     = int(m2_spec.wire_cd[i]/dbu)
        track_pitch = int(m2_spec.track_pitch[i]/dbu)
        min_t2t     = int(m2_spec.min_t2t[i]/dbu)
        max_t2t     = int(m2_spec.max_t2t[i]/dbu)
        min_length  = int(m2_spec.min_length[i]/dbu)
        max_length  = int(m2_spec.max_length[i]/dbu)
        #density     = int(m2_spec.density[i]*1e3)
        t2t_grid    = int(m2_spec.t2t_grid[i]/dbu)

        total_x     = int(m2_spec.total_x[i]/dbu)
        total_y     = int(m2_spec.total_y[i]/dbu)
        cell = layout.create_cell(cellname)
        #print("tile size is x: %g y:%g"%(total_x, total_y))
        #quit()
        init_loc=[0,0]

        l_m2 = layout.layer(outLayerNum, outLayerDT, "M2")
        for j in range(init_loc[1], total_y-wire_cd + init_loc[1], track_pitch):
            location = np.array([init_loc[0], j])
            draw_wire_row(cell, l_m2, wire_cd,
                            min_length, max_length,
                            min_t2t, max_t2t, t2t_grid,
                            total_x, location, stoc=0.6)


        l_bb = layout.layer(2, 0, "bounding_box")
        #print c1ur.x,c2ll.x
        origin=[0,0]
        bbll = pya.Point(origin[0], origin[1])
        bbur = pya.Point(origin[0]+total_x, origin[1]+total_y)
        cell.shapes(l_bb).insert(pya.Box(bbll, bbur))

        cellpath = cellname+'.gds'
        cell.write(os.path.join(dest, cellpath))


        with open(os.path.join(dest, cellname+'.glp'), "w") as glp:
            glp.write("BEGIN\n")
            glp.write("EQUV  1  1000  MICRON  +X,+Y\n")
            glp.write("CNAME Temp_Top\n")
            glp.write("LEVEL M1\n\n")
            glp.write("CELL Temp_Top PRIME\n")
            contour_iter = layout.begin_shapes(cell, l_m2)
            viabbox = cell.bbox_per_layer(l_m2)
            glpoffset_x = viabbox.left -70 + random.randint(-400, 400)
            glpoffset_y = viabbox.bottom -70 + random.randint(-400, 400)
            while not contour_iter.at_end():
                current = contour_iter.shape().polygon
                if(current.is_box()):
                    box = current.bbox()
                    glp.write("   RECT N M1 %g %g %g %g\n"%(box.left-glpoffset_x, box.bottom-glpoffset_y, box.width(), box.height()))
                else:
                    polygon = current
                    glp.write("   PGON N M1 ")
                    for point in polygon.each_point_hull():
                        glp.write("%g %g "%(point.x-glpoffset_x, point.y-glpoffset_y))
                    glp.write("\n")
                contour_iter.next()
            glp.write("ENDMSG\n")


    