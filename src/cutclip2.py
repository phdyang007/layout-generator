import pya
import numpy as np 
import pandas as pd
import os
from progress.bar import Bar










layout = pya.Layout()
layout.read(gdsIn)
cell = layout.cell('TOP_CELL')
layer = layout.layer(1000,0)
cellBbox = cell.bbox()
cellWidth = cellBbox.width()  
cellHeight = cellBbox.height() 
cellLeft = cellBbox.left
cellBottom = cellBbox.bottom
clipSize = int(2/layout.dbu)
clipPitch = int(0.5/layout.dbu)
dbu=layout.dbu
#markerSize = int(0.016/layout.dbu)
offset = (clipSize-clipPitch)/2


clipCountX = cellWidth//clipPitch+1
clipCountY = cellHeight//clipPitch+1
layer_sraf = layout.layer(2,1)
layer_design = layout.layer(0,0)
layer_opc = layout.layer(2,0)
layer_contour = layout.layer(55,55)
#layer = "sraf"
print (cellBbox, cellWidth, cellHeight, cellLeft, cellBottom, clipCountX, clipCountY, clipSize)
#quit()
sp = pya.ShapeProcessor()
bar=Bar('Generating Clips', max=clipCountX*clipCountY)
for j in range(clipCountY):
    for i in range(clipCountX):
        tmpCell = layout.create_cell('TMP')
        outCell = layout.create_cell('OUT')
        #tmpLayer = layout.layer(1,8)
        tmpLeft = i*clipPitch+cellLeft-int(1/dbu)
        tmpBottom = j*clipPitch+cellBottom-int(1/dbu)
        tmpRight = tmpLeft+clipSize
        tmpTop = tmpBottom+clipSize
        #token = checkHotspot(hotspotInfo, [tmpLeft+offset, tmpBottom+offset, tmpRight-offset, tmpTop-offset])
        #print [tmpLeft+50, tmpBottom+50, tmpRight-50, tmpTop-50]
        #print(tmpLeft,tmpBottom,tmpRight,tmpTop)
        #if(i==10): quit()
        if (layert=="sraf"): tmpCell.shapes(layer_sraf).insert(pya.Box(tmpLeft,tmpBottom,tmpRight,tmpTop))
        if (layert=="design"): tmpCell.shapes(layer_design).insert(pya.Box(tmpLeft,tmpBottom,tmpRight,tmpTop))
        if (layert=="opc"): tmpCell.shapes(layer_opc).insert(pya.Box(tmpLeft,tmpBottom,tmpRight,tmpTop))
        if (layert=="contour"): tmpCell.shapes(layer_contour).insert(pya.Box(tmpLeft,tmpBottom,tmpRight,tmpTop))
        #print(tmpCell.bbox())
        bbox= pya.Box(tmpLeft, tmpBottom, tmpRight, tmpTop)
        
        
        #outLayer = layout.layer(2,0)
        if (layert=="sraf"): sp.boolean(layout, tmpCell, layer_sraf, layout, cell, layer_sraf, outCell.shapes(layer_sraf), pya.EdgeProcessor.ModeAnd, True, False, False)
        if (layert=="design"): sp.boolean(layout, tmpCell, layer_design, layout, cell, layer_design, outCell.shapes(layer_design), pya.EdgeProcessor.ModeAnd, True, False, False)
        if (layert=="opc"): sp.boolean(layout, tmpCell, layer_opc, layout, cell, layer_opc, outCell.shapes(layer_opc), pya.EdgeProcessor.ModeAnd, True, False, False)
        if (layert=="contour"): sp.boolean(layout, tmpCell, layer_contour, layout, cell, layer_contour, outCell.shapes(layer_contour), pya.EdgeProcessor.ModeAnd, True, False, False)
        outCell.shapes(layout.layer(7777,0)).insert(bbox)
        filename = 'clip'+'_'+layert+'_'+str(i)+'_'+str(j)+'.gds'
        path = os.path.join(gdsOut,filename)
        outCell.write(path)
        outCell.delete()
        tmpCell.delete()
        bar.next()
bar.finish()
