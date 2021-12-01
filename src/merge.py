import pya 


layout1 = pya.Layout()
layout2 = pya.Layout()

layout1.read(gds1)
layout2.read(gds2)

cell1 = layout1.top_cell()
cell2 = layout2.top_cell()

cell1.copy_shapes(cell2)

layout1.write(gds3)
