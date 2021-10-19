import pya
import numpy as np



layout = pya.Layout()
layout.read(gdsIn)
dbu=layout.dbu

cell = layout.top_cell()
cellBbox = cell.bbox()
cellWidth = cellBbox.width()  
cellHeight = cellBbox.height() 
cellLeft = cellBbox.left
cellBottom = cellBbox.bottom


pitch = int(0.5/dbu)

x = range(cellLeft, cellLeft+cellWidth, pitch)
y = range(cellBottom, cellBottom+cellHeight, pitch)

center = np.zeros((len(x)*len(y), 2))


for i in range(len(x)):
    for j in range(len(y)):
        center[i*len(y)+j,0]=x[i]
        center[i*len(y)+j,1]=y[j]

np.savetxt(centerout, center)



