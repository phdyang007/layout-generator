import pya
import numpy as np
import pandas as pd
import random as rd
import os
import time
import sys
sys.path.append('./src')
from LayoutGenerator import *
if __name__ == "__main__":  
    params = ['cellname','m1_wire_cd', 'm1_track_pitch', 'm2_wire_cd', 'm2_track_pitch',   
              'm2_min_t2t','m2_max_t2t','m2_min_length','m2_max_length','m2_t2t_grid',    
              'total_x','total_y', 'via1_x', 'via1_y', 'm1_enc', 'm2_enc', 'min_via1_pitch_x', 'via_fraction', 'min_via1_pitch_y']
    try:
        #via1_spec=via1_spec[params]
        via1_spec = pd.read_csv(csv_file, delimiter=',', usecols=params, encoding='utf-16')
        #via1_spec
    except:
        print ("Error: Invalid csv file, columns must contain: ", params)
        quit()

    dbu = 0.001 # Database Unit in um.
    try:
        verbose=int(verbose)
    except:
        verbose=0
    cell_number = len(via1_spec.cellname)
    layout = pya.Layout()
    layout.dbu=dbu
    topcell = layout.create_cell("VIAS")
    dut_pitch_x = 0.1/dbu
    dut_pitch_y = 0.1/dbu
    max_duts_per_row=int(np.sqrt(cell_number))
    description = []
    sp = pya.ShapeProcessor()
    outLayer=outLayer.split('/')
    outLayerNum=int(outLayer[0])
    outLayerDT=int(outLayer[1])
    for i in range(cell_number):
        

        cellname    = via1_spec.cellname[i]
        print ("generating cell ", i, ":", cellname)
        m1_wire_cd     = int(via1_spec.m1_wire_cd[i]/dbu)
        m1_track_pitch = int(via1_spec.m1_track_pitch[i]/dbu)
        m2_wire_cd     = int(via1_spec.m2_wire_cd[i]/dbu)
        m2_track_pitch = int(via1_spec.m2_track_pitch[i]/dbu)
        m2_min_t2t     = int(via1_spec.m2_min_t2t[i]/dbu)
        m2_max_t2t     = int(via1_spec.m2_max_t2t[i]/dbu)
        m2_min_length  = int(via1_spec.m2_min_length[i]/dbu)
        m2_max_length  = int(via1_spec.m2_max_length[i]/dbu)
        #density     = int(via1_spec.density[i]*1e3)
        m2_t2t_grid    = int(via1_spec.m2_t2t_grid[i]/dbu)
        total_x     = int(via1_spec.total_x[i]/dbu)
        total_y     = int(via1_spec.total_y[i]/dbu)
        via1_x      = int(via1_spec.via1_x[i]/dbu)
        via1_y      = int(via1_spec.via1_y[i]/dbu)
        m1_enc      = int(via1_spec.m1_enc[i]/dbu)
        m2_enc      = int(via1_spec.m2_enc[i]/dbu)
        print(via1_spec.min_via1_pitch_x[i])
        min_via1_pitch_x = int(via1_spec.min_via1_pitch_x[i]/dbu)
        min_via1_pitch_y = int(via1_spec.min_via1_pitch_y[i]/dbu)
        via_fraction = via1_spec.via_fraction[i]

        #x=((i) % max_duts_per_row)*(dut_pitch_x+total_x)
        #y=((i) / max_duts_per_row)*(dut_pitch_y+total_y)
        origin = [0,0]
        #description.append([via1_spec.cellname[i], x, y])

       
        cellname = via1_spec.cellname[i]
        cell = layout.create_cell('TOP')
        '''Generate M1 Gratings'''
        l_m1 = layout.layer(93, 0, "M1")
        init_loc = origin
        m1_min_t2t =total_y
        m1_max_length = total_y
        m1_min_length = total_y
        m1_max_t2t =total_y
        m1_t2t_grid = total_y


        via_xcnt =0
        for j in range(init_loc[0], total_x-m1_wire_cd + init_loc[0], m1_track_pitch):
            via_xcnt+=1
            location = [j, init_loc[1]]
            draw_wire_column(cell, l_m1, m1_wire_cd,
                            m1_min_length, m1_max_length,
                            m1_min_t2t, m1_max_t2t, m1_t2t_grid,
                            total_y, location)


        '''Generate M2'''
        via_ycnt=0
        l_m2 = layout.layer(94, 0, "M2")
        for j in range(init_loc[1]+m1_enc, total_y-m2_wire_cd + init_loc[1], m2_track_pitch):
            via_ycnt+=1
            location = [init_loc[0], j]
            draw_wire_row(cell, l_m2, m2_wire_cd,
                            m2_min_length, m2_max_length,
                            m2_min_t2t, m2_max_t2t, m2_t2t_grid,
                            total_x, location, m2_enc)


        via_mtx = np.zeros((via_ycnt, via_xcnt))
        '''Generate Vias'''

        l_m2_ast = layout.layer(10010,0,"ast")
        l_via1 = layout.layer(outLayerNum,outLayerDT,"V1")
        sp.boolean(layout, cell, l_m1, layout, cell, l_m2_ast, cell.shapes(l_via1), pya.EdgeProcessor.ModeAnd, False, False, False)


        #l_m2_ast._destroy()
        print ("via_fraction = ", via_fraction)
        via_iter = layout.begin_shapes(cell, l_via1)
        
        print (via_mtx.shape)
        while not via_iter.at_end():
            current = via_iter.shape().bbox()
            v_x = (current.left-  init_loc[0])//m1_track_pitch
            v_y = (current.bottom -   init_loc[1]-m1_enc)// m2_track_pitch
            if via_iter.shape().area() ==m1_wire_cd*m2_wire_cd:
                th= rd.uniform(0,1)
                if th>via_fraction:                 
                    via_iter.shape().delete()
                else:
                    via_mtx[v_y,v_x]=1
            else:
                via_iter.shape().delete()
            via_iter.next()


        via_iter = layout.begin_shapes(cell, l_via1)
        while not via_iter.at_end():
            current = via_iter.shape().bbox()
            v_x = (current.left-  init_loc[0])//m1_track_pitch
            v_y = (current.bottom -   init_loc[1]-m1_enc)// m2_track_pitch
            if not check_via_pitch_pass(v_x, v_y, via_mtx, m1_track_pitch, m2_track_pitch, min_via_pitch_x=min_via1_pitch_x):
                via_iter.shape().delete()
                via_mtx[v_y, v_x] =0
            via_iter.next()

        via_iter = layout.begin_shapes(cell, l_via1)
        while not via_iter.at_end():
            current = via_iter.shape().bbox()
            v_x = (current.left-  init_loc[0])//m1_track_pitch
            v_y = (current.bottom -   init_loc[1]-m1_enc)// m2_track_pitch
            if not check_via_pitch_pass(v_x, v_y, via_mtx, m1_track_pitch, m2_track_pitch, min_via_pitch_y=min_via1_pitch_y):
                via_iter.shape().delete()
                via_mtx[v_y, v_x] =0
            via_iter.next()
        

        '''draw sraf forbidden and access region / store via/contact coordinates'''
        l_forbidden = layout.layer(210, 0)
        l_access    = layout.layer(230, 0)
        offset_forbidden = pya.Vector(100, 100)
        offset_access    = pya.Vector(500, 500)
        via_iter = layout.begin_shapes(cell, l_via1)
        tmp_iter = 0
        while not via_iter.at_end():
            current = via_iter.shape().bbox()
            llp = current.p1 
            urp = current.p2
            llp_forbidden = llp-offset_forbidden
            urp_forbidden = urp+offset_forbidden
            cell.shapes(l_forbidden).insert(pya.Box(llp_forbidden, urp_forbidden))

            llp_access = llp-offset_access
            urp_access = urp+offset_access
            cell.shapes(l_access).insert(pya.Box(llp_access, urp_access))

            center_x = round(current.center().x*dbu, 3)
            center_y = round(current.center().y*dbu, 3)
            center   = np.array([[center_x, center_y]])
            if tmp_iter == 0:
                centers  = center
            else:
                centers  = np.concatenate((centers, center), axis = 0)

            via_iter.next()
            tmp_iter += 1
        

        '''write out via coordinates'''
        centers_df = pd.DataFrame(data = centers)
        centers_df.to_csv(os.path.join(dest, cellname+'.txt'), sep=' ',header=False, index=False)

            
            


        '''Generater Bounding Box'''
        l_bb = layout.layer(22, 0, "bounding_box")
        cell.shapes(l_bb).insert(cell.bbox())
        #bbll = pya.Point(origin[0], origin[1])
        #bbur = pya.Point(origin[0]+total_x, origin[1]+total_y)
        #cell.shapes(l_bb).insert(pya.Box(bbll, bbur))
        #tmp_cell_inst = pya.CellInstArray(cell.cell_index(), pya.Trans(pya.Point(0,0)))
        #topcell.insert(tmp_cell_inst)


        '''merge boxes'''

        l_forbidden_merged = layout.layer(21, 0)
        l_access_merged    = layout.layer(23, 0)
        #shapes_forbidden = cell.shapes(l_forbidden)
        sp.merge(layout, cell, l_forbidden, cell.shapes(l_forbidden_merged), False, 0, False, False)
        #cell.shapes(l_forbidden_merged).insert(shapes_forbidden_merged)


        sp.merge(layout, cell, l_access, cell.shapes(l_access_merged), False, 0, False, False)

        layout.delete_layer(l_m2_ast)
        layout.delete_layer(l_forbidden)
        layout.delete_layer(l_access)

        cell.write(os.path.join(dest, cellname+'.gds'))
        layout.clear()
    #topcell.write(outOAS)
