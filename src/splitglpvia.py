import pya 
import os 
import numpy as np 


if __name__=='__main__':
    input_oas = input_oas 
    try:
        os.makedirs(input_oas+'s')
    except:
        print("W: path exists")
    layout = pya.Layout()
    layout.read(input_oas)
    bbox_layer = layout.layer(1,0)
    design_layer = layout.layer(2,0)
    subbox_layer  = layout.layer(99,0)
    top_cell = layout.top_cell()
    _bbox_center = top_cell.bbox_per_layer(design_layer).center() 
    bbox = pya.Box(_bbox_center.x-4000,_bbox_center.y-4000, _bbox_center.x+4000,_bbox_center.y+4000)
    ref_x = bbox.left
    ref_y = bbox.bottom
    subsize=2000
    sp = pya.ShapeProcessor()
    for i in range(7):
        for j in range(7):
            print("processing subtile_%g_%g"%(i,j))
            tmp_cell = layout.create_cell("subtile_%g_%g"%(i,j))
            left = ref_x + i*subsize//2
            bottom = ref_y + j*subsize//2
            top = bottom+2000
            right = left+2000
            glpoffset_x = left
            glpoffset_y = bottom
            subbox = pya.Box(left, bottom, right, top)
            tmp_cell.shapes(subbox_layer).insert(subbox)
            sp.boolean(layout, top_cell, design_layer, layout, tmp_cell, subbox_layer, tmp_cell.shapes(design_layer), pya.EdgeProcessor.ModeAnd, True, False, False)
            with open(os.path.join(input_oas+'s', tmp_cell.name+'.glp'), "w") as glp:
                glp.write("BEGIN\n")
                glp.write("EQUV  1  1000  MICRON  +X,+Y\n")
                glp.write("CNAME Temp_Top\n")
                glp.write("LEVEL M1\n\n")
                glp.write("CELL Temp_Top PRIME\n")
                contour_iter = layout.begin_shapes(tmp_cell, design_layer)
                #viabbox = tmp_cell.bbox_per_layer(design_layer)
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
            tmp_cell.write(os.path.join(input_oas+'s', tmp_cell.name+'.gds'))





