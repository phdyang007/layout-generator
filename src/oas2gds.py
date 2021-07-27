import pya 



def oas2gds(oas):
    layout = pya.Layout()
    layout.read(oas)
    gds = oas[:-3]+"gds"
    layout.write(gds)
    layout.clear()

def gds2oas(gds):
    layout = pya.Layout()
    layout.read(gds)
    gds = oas[:-3]+"oas"
    layout.write(oas)
    layout.clear()



def main():
    mode=int(mode)
    for dirname, dirnames, filenames in os.walk(infolder):
        bar = Bar("Converting OASIS <-> GDSII", max=len(filenames))
        for f in range(0, len(filenames)):
            filename = os.path.join(infolder, filenames[f])
            if(mode==1):
                oas2gds(filename)
            if(mode==2):
                gds2oas(filename)
            bar.next()
        bar.finish()


