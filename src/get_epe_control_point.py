import pya 


if __name__=="__main__":
    gds_in = gds_in
    epe_control_point_list = []
    layout = pya.Layout()
    layout.read(gds_in)

    top_cell = layout.top_cell()
    

