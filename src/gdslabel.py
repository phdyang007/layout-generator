import pya
import numpy as np 
import os
from progress.bar import Bar 



layout = pya.Layout()
layout.read(gdsIn)
cell = layout.cell('TOPCELL')

markerLayerIdx = layout.layer(10000,0)
layout.delete_layer(markerLayerIdx)

markerLayerIdx=layout.layer(10000,0)


cellBbox = cell.bbox()
cellWidth = cellBbox.width()  
cellHeight = cellBbox.height() 
cellLeft = cellBbox.left
cellBottom = cellBbox.bottom
cellRight = cellBbox.right
cellTop = cellBbox.top 
clipSize = 2000 
clipPitch = clipSize/2
markerSize = 16

for markerX in xrange(cellLeft, cellRight, clipPitch):
    for markerY in xrange(cellBottom, cellTop, clipPitch):
        markerLeft = markerX
        markerRight = markerLeft + markerSize
        markerBottom = markerY
        markerTop = markerBottom + markerSize

        cell.shapes(markerLayerIdx).insert(pya.Box(markerLeft, markerBottom, markerRight, markerTop))

layout.write(gdsOut)