import gdspy
import sys
import os
from PIL import Image, ImageDraw
from progress.bar import Bar
clipsize = 2000

def gds2img(Infolder, Infile, ImgOut):
    GdsIn = os.path.join(Infolder, Infile)
    gdsii   = gdspy.GdsLibrary()
    gdsii.read_gds(GdsIn, unit=1e-9)
    cell    = gdsii.top_level()[0]
    bbox    = cell.get_bounding_box()
    opt_space=40 #Leave space at border in case of edge correction

    width = int((bbox[1,0]-bbox[0,0]))
    height= int((bbox[1,1]-bbox[0,1]))
    w_offset = int(bbox[0,0] - (clipsize-width)/2)
    h_offset = int(bbox[0,1] - (clipsize-height)/2)


    sellayer = [2,20] #Layer Number
    dtype = 0  #Layout Data Type
    polygon  = []
    for i in xrange(len(sellayer)):
        polyset = cell.get_polygons(by_spec=True)[(sellayer[i],dtype)]
        for poly in xrange(0, len(polyset)):
            for points in xrange(0, len(polyset[poly])):
                polyset[poly][points][0]=int(polyset[poly][points][0]-w_offset)
                polyset[poly][points][1]=int(polyset[poly][points][1]-h_offset)
        im = Image.new('1', (clipsize, clipsize))
        draw = ImageDraw.Draw(im)
        for j in xrange(0, len(polyset)):
            tmp = tuple(map(tuple, polyset[j]))
            draw.polygon(tmp, fill=255)
        filename = Infile+".png"
        outpath  = os.path.join(ImgOut,filename)
        im.save(outpath)



Infolder = sys.argv[1]
Outfolder= sys.argv[2]
for dirname, dirnames, filenames in os.walk(Infolder):
    bar=Bar("Converting GDSII to Image", max=len(filenames))
    for f in xrange(0, len(filenames)):
        try:
            gds2img(Infolder, filenames[f], Outfolder)
        except:
            bar.next()
            continue
        bar.next()
bar.finish()
