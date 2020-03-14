import gdspy
import sys
import os
from PIL import Image, ImageDraw
from progress.bar import Bar
clipsize = 2000


def gds2img(Infolder, Infile, ImgOut, cell_type=0):
    GdsIn = os.path.join(Infolder, Infile)
    gdsii = gdspy.GdsLibrary(unit=1e-9)
    gdsii.read_gds(GdsIn, units='convert')
    cell = gdsii.top_level()[0]
    bbox = cell.get_bounding_box()
    opt_space = 40  # Leave space at border in case of edge correction

    width = int((bbox[1, 0]-bbox[0, 0]))
    height = int((bbox[1, 1]-bbox[0, 1]))
    w_offset = int(bbox[0, 0] - (clipsize-width)/2)
    h_offset = int(bbox[0, 1] - (clipsize-height)/2)

    sellayer = [2]  # Layer Number
    dtype = cell_type  # Layout Data Type
    polygon = []
    im = Image.new('1', (clipsize, clipsize))
    draw = ImageDraw.Draw(im)
    token = 1
    for i in range(len(sellayer)):
        try:
            polyset = cell.get_polygons(by_spec=True)[(sellayer[i], dtype)]
        except:
            token = 0
            print("Layer not found, skipping...")
            break
        for poly in range(0, len(polyset)):
            for points in range(0, len(polyset[poly])):
                polyset[poly][points][0] = int(
                    polyset[poly][points][0]-w_offset)
                polyset[poly][points][1] = int(
                    polyset[poly][points][1]-h_offset)

        for j in range(0, len(polyset)):
            tmp = tuple(map(tuple, polyset[j]))
            draw.polygon(tmp, fill=255)
    if token == 1:
        filename = Infile+str(dtype)+".png"
        outpath = os.path.join(ImgOut, filename)
        # from IPython import embed;embed()
        im.save(outpath)


Infolder = sys.argv[1]
Outfolder = sys.argv[2]
cell_type = int(sys.argv[3])

for dirname, dirnames, filenames in os.walk(Infolder):
    bar = Bar("Converting GDSII to Image", max=len(filenames))
    for f in range(0, len(filenames)):
        try:
            gds2img(Infolder, filenames[f], Outfolder, cell_type)
        except:
            bar.next()
            continue
        bar.next()
bar.finish()


# for dirname, dirnames, filenames in os.walk(Infolder):
#    bar=Bar("Converting GDSII to Image", max=len(filenames))
#    for f in range(0, len(filenames)):
#        gds2img(Infolder, filenames[f], Outfolder)
