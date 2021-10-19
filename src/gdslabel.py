import pya
import numpy as np 
import os
from progress.bar import Bar 



layout = pya.Layout()
layout.read(gdsIn)
#layout.dbu=1e-3
cell = layout.cell('TOP_CELL')

#markerLayerIdx = layout.layer(10086,0)
#layout.delete_layer(markerLayerIdx)

markerLayerIdx=layout.layer(10086,0)


cellBbox = cell.bbox()
cellWidth = cellBbox.width()  
cellHeight = cellBbox.height() 
cellLeft = cellBbox.left
cellBottom = cellBbox.bottom
cellRight = cellBbox.right
cellTop = cellBbox.top 
clipSize = 2000 
clipPitch = int(0.5/layout.dbu)
markerSize = int(0.016/layout.dbu)

for markerX in range(cellLeft, cellRight, clipPitch):
    for markerY in range(cellBottom, cellTop, clipPitch):
        markerLeft = markerX
        markerRight = markerLeft + markerSize
        markerBottom = markerY
        markerTop = markerBottom + markerSize

        cell.shapes(markerLayerIdx).insert(pya.Box(markerLeft, markerBottom, markerRight, markerTop))

layout.write(gdsOut)