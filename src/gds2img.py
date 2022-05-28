import gdspy
import sys
import os
from PIL import Image, ImageDraw
from progress.bar import Bar
clipsize = 8192
import numpy as np

def gds2img(Infolder, Infile, ImgOut, layerSpecs, type = 'v'): #h v via
    h_epe = []
    v_epe = []
    GdsIn = os.path.join(Infolder, Infile)
    gdsii = gdspy.GdsLibrary(unit=1e-9)
    gdsii.read_gds(GdsIn, units='convert')
    cell = gdsii.top_level()[0]
    bbox = cell.get_bounding_box()
    opt_space = 40  # Leave space at border in case of edge correction

    #bbox2s = cell.get_polygons(by_spec=True)[(2, 0)][0] #metal
    bbox2s = cell.get_polygons(by_spec=True)[(22, 0)][0] #via


    width = int((bbox2s[2, 0]-bbox2s[0, 0]))
    height = int((bbox2s[2, 1]-bbox2s[0, 1]))
    w_offset = int(bbox2s[0, 0] - (clipsize-width)/2)
    h_offset = int(bbox2s[0, 1] - (clipsize-height)/2)


    sellayer = layerSpecs[0]  # Layer Number
    dtype = layerSpecs[1]  # Layout Data Type
    polygon = []
    im = Image.new('1', (clipsize, clipsize))
    draw = ImageDraw.Draw(im)
    token = 1
    for i in range(len(sellayer)):
        try:
            polyset = cell.get_polygons(by_spec=True)[(sellayer[i], dtype[i])]
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
            #print(polyset[j])
            ll = polyset[j][0].astype(int)
            ur = polyset[j][2].astype(int)
            #print(ll,ur)
            if type=='h':
                #get line-end points
                h_epe.append([ll[0],(ll[1]+ur[1])//2,-1]) #[x,y,dir] -1 left, 1 right
                h_epe.append([ur[0],(ll[1]+ur[1])//2,1]) 
                if ll[0]+40<ur[0]-40:
                    for x in range(ll[0]+40,ur[0]-40,40):
                        v_epe.append([x,ll[1], 1])
                        v_epe.append([x,ur[1],-1])
            if type=='v':
                h_epe.append([ll[0],(ll[1]+ur[1])//2,-1]) #[x,y,dir] -1 left, 1 right
                h_epe.append([ur[0],(ll[1]+ur[1])//2,1]) 
                v_epe.append([(ll[0]+ur[0])//2,ll[1],-1]) #[x,y,dir] -1 left, 1 right
                v_epe.append([(ll[0]+ur[0])//2,ur[1],1])                 
            tmp = tuple(map(tuple, polyset[j]))
            draw.polygon(tmp, fill=255)
    if token == 1:
        filename = Infile+".png"
        vepefile = Infile+".v.csv"
        hepefile = Infile+".h.csv"
        outpath = os.path.join(ImgOut, filename)
        vpath   = os.path.join(ImgOut, vepefile)
        hpath   = os.path.join(ImgOut, hepefile)
        im.save(outpath)
        h_epe=np.array(h_epe)
        v_epe=np.array(v_epe)
        np.savetxt(vpath, v_epe, delimiter=",",fmt="%d")
        np.savetxt(hpath, h_epe, delimiter=",",fmt="%d")


Infolder = sys.argv[1]
Outfolder = sys.argv[2]
#cell_type = int(sys.argv[3])

layerSpecs=np.array([[2],[0]]) #opc + sraf
#layerSpecs=np.array([[55],[55]]) #opc + sraf
#layerSpecs=np.array([[0,1]]) #opc
#layerSpecs=np.array([[2],[0]]) #sraf
#layerSpecs=np.array([[200],[0]]) #nominal
for dirname, dirnames, filenames in os.walk(Infolder):
    bar = Bar("Converting GDSII to Image", max=len(filenames))
    for f in range(0, len(filenames)):
        try:
            gds2img(Infolder, filenames[f], Outfolder, layerSpecs)
            #quit()
        except:
            bar.next()
            continue
        bar.next()
bar.finish()


# for dirname, dirnames, filenames in os.walk(Infolder):
#    bar=Bar("Converting GDSII to Image", max=len(filenames))
#    for f in range(0, len(filenames)):
#        gds2img(Infolder, filenames[f], Outfolder)
