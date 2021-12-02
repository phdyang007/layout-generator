try:
    import pya
except:
    print("klayout module not enabled")
import numpy as np
import random as rd
import os
# All the units are listed/calculated in nanometer.
'''
Description: Draw a pair of contact, layer: 71, layer dtype: 0.
Args:
    layout: A klayout layout object
    tmp_cell: cell
    cellname: cellname
    size: (2,) ndarray contains size_x and size_y of the contact
    spacing: (2,) ndarray contains spacing_x and spacing_y of the contact
    dest: path to store  seperate oasis files, take effect only verbose =True
    verbose: whether store each cell in different oasis files
    clip: whether draw a bounding box of the cell
    origin: the reference point to put contacts
Return:
    No return  
'''


def draw_contact_pair(layout, tmp_cell, cellname, size, spacing, dest, dbu, put_in_array=True, verbose=True, clip=True, origin=np.array([0, 0])):

    l_contact = layout.layer(73, 0, "V1")
    c1ll = pya.Point(origin[0], origin[1])
    size = pya.Point(size[0], size[1])
    c1ur = c1ll + size
    spc = pya.Point(spacing[0], spacing[1])
    c2ll = c1ur + spc
    c2ur = c2ll + size
    tmp_cell.shapes(l_contact).insert(pya.Box(c1ll, c1ur))
    tmp_cell.shapes(l_contact).insert(pya.Box(c2ll, c2ur))
    if clip:
        l_bb = layout.layer(1, 0, "bounding_box")
        # print c1ur.x,c2ll.x
        center = pya.Point((c1ur.x+c2ll.x)/2, (c1ur.y+c2ll.y)/2)
        bbll = center - pya.Point(0.125/dbu, 0.125/dbu)
        bbur = center + pya.Point(0.125/dbu, 0.125/dbu)
        tmp_cell.shapes(l_bb).insert(pya.Box(bbll, bbur))

    if verbose == True:
        tmp_name = cellname+'.oas'
        tmp_cell.write(os.path.join(dest, tmp_name))
    # return layout


'''
Description: Draw a metal row with multiple polygons specified by params. 
Args:
    cell: A klayout cell object
    layer: A klayout layer object
    cd: critical dimension
    min/max_length: min or max wire length
    min/max_t2t: min or max tip to tip distance
    t2t_grid: t2t mulitplier
    max_x: row length (including wire length, t2t and offsets)
    location: the left lower corner of the metal row.
Return:
    No return  
'''


def draw_wire_row(cell, layer, cd, min_length, max_length, min_t2t, max_t2t, t2t_grid, max_x, location=np.array([0, 0]), enclosure=0):
    offset_x = location[0]
    offset_y = location[1]
    total_x = 0
    total_y = 0
    if enclosure != 0:
        tmp_layout = cell.layout()
        ast_layer = tmp_layout.layer(10010, 0, "ast")
    while total_x < max_x:
        wire_left = total_x
        wire_lower = total_y
        # print min_length, max_length, max_x
        try:
            tmp = min(max_length, max_x - wire_left)
            wire_length = rd.randint(min_length, tmp)
            # print "wire length", wire_length
        except:
            # print "escape wire"
            break

        wire_right = wire_left + wire_length
        wire_upper = wire_lower + cd
        # if wire_right > max_x:
        #    break

        wire_ll = pya.Point(int(wire_left+offset_x), int(wire_lower+offset_y))
        wire_ur = pya.Point(int(wire_right+offset_x), int(wire_upper+offset_y))
        wire = pya.Box(wire_ll, wire_ur)
        cell.shapes(layer).insert(wire)
        if enclosure != 0:
            ast_wire_ll = pya.Point(
                wire_left+offset_x+enclosure, wire_lower+offset_y)
            ast_wire_ur = pya.Point(
                wire_right+offset_x-enclosure, wire_upper+offset_y)
            ast_wire = pya.Box(ast_wire_ll, ast_wire_ur)
            cell.shapes(ast_layer).insert(ast_wire)
        try:
            if max_t2t > min_t2t:
                tmp = min(max_t2t, max_x - wire_right)
                # print min_t2t, tmp, t2t_grid
                t2t = rd.randrange(min_t2t, tmp, t2t_grid)
                # print "t2t", t2t
            else:
                t2t = max_t2t
        except:
            # print "escape t2t"
            break
        # print total_x, max_x, max_length, wire_left
        total_x = total_x + wire_length + t2t


def draw_wire_row_drc(layout, outLayerNum, cell, layer, cd, min_length, max_length, min_t2t, max_t2t, t2t_grid, max_x, location=np.array([0, 0]), enclosure=0, t2t_threshold=0.4, wirelength_threshold=0.4):
    offset_x = location[0]
    offset_y = location[1]
    total_x = 0
    total_y = 0
    if enclosure != 0:
        tmp_layout = cell.layout()
        ast_layer = tmp_layout.layer(10010, 0, "ast")
    while total_x < max_x:
        wire_left = total_x
        wire_lower = total_y
        # print min_length, max_length, max_x
        try:
            tmp = min(max_length, max_x - wire_left)
            wire_length = rd.randint(min_length, tmp)
            # print "wire length", wire_length
        except:
            # print "escape wire"
            break

        wire_right = wire_left + wire_length
        wire_upper = wire_lower + cd
        # if wire_right > max_x:
        #    break

        wire_ll = pya.Point(int(wire_left+offset_x), int(wire_lower+offset_y))
        wire_ur = pya.Point(int(wire_right+offset_x), int(wire_upper+offset_y))
        wire = pya.Box(wire_ll, wire_ur)
        cell.shapes(layer).insert(wire)
        # TODO: two kind of violations
        # min_t2t<=0.016 smaller)/min_length(0.044 smaller)
        wire_conflict_layer = layout.layer(outLayerNum, 1, "M2")
        #t2t 0.016, min_length 0.036
        if wire_length < wirelength_threshold:
            conflict_wire = pya.Box(wire_ll, wire_ur)
            cell.shapes(wire_conflict_layer).insert(conflict_wire)

        if enclosure != 0:
            ast_wire_ll = pya.Point(
                wire_left+offset_x+enclosure, wire_lower+offset_y)
            ast_wire_ur = pya.Point(
                wire_right+offset_x-enclosure, wire_upper+offset_y)
            ast_wire = pya.Box(ast_wire_ll, ast_wire_ur)
            cell.shapes(ast_layer).insert(ast_wire)
        try:
            if max_t2t > min_t2t:
                tmp = min(max_t2t, max_x - wire_right)
                # print min_t2t, tmp, t2t_grid
                t2t = rd.randrange(min_t2t, tmp, t2t_grid)
                # print "t2t", t2t
            else:
                t2t = max_t2t
        except:
            # print "escape t2t"
            break

        t2t_conflict_layer = layout.layer(outLayerNum, 2, "M2")
        # from IPython import embed;embed()
        if t2t < t2t_threshold:
            t2t_conflict_ll = pya.Point(
                int(wire_right+offset_x), int(wire_lower+offset_y))
            t2t_conflict_ur = pya.Point(
                int(wire_right+t2t+offset_x), int(wire_upper+offset_y))
            conflict_t2t = pya.Box(t2t_conflict_ll, t2t_conflict_ur)
            cell.shapes(t2t_conflict_layer).insert(conflict_t2t)
        # print total_x, max_x, max_length, wire_left
        total_x = total_x + wire_length + t2t


def draw_wire_row_single_args(args):
    # draw_wire_row(*args)
    for param in args:
        draw_wire_row(*param)


def split_args(arg_list, chunk):
    return [arg_list[x:x+chunk] for x in xrange(0, len(arg_list), chunk)]


def draw_wire_column(cell, layer, cd, min_length, max_length, min_t2t, max_t2t, t2t_grid, max_y, location=[0, 0]):
    offset_x = location[0]
    offset_y = location[1]
    total_x = 0
    total_y = 0
    while total_y < max_y:
        wire_left = total_x
        wire_lower = total_y
        # print min_length, max_length, max_y

        try:
            tmp = min(max_length, max_y - wire_lower)
            wire_length = rd.randint(min_length, tmp)
            # print "wire length", wire_length
        except:
            # print "escape wire"
            break

        wire_upper = wire_lower + wire_length
        wire_right = wire_left + cd
        # print(wire_left+offset_x,wire_lower+offset_y,wire_lower,wire_right)
        wire_ll = pya.Point(wire_left+offset_x, wire_lower+offset_y)
        wire_ur = pya.Point(wire_right+offset_x, wire_upper+offset_y)
        wire = pya.Box(wire_ll, wire_ur)
        cell.shapes(layer).insert(wire)
        # print wire_ll, wire_ur
        # quit()
        try:
            if max_t2t > min_t2t:
                tmp = min(max_t2t, max_y - wire_upper)
                # print min_t2t, tmp, t2t_grid
                t2t = rd.randrange(min_t2t, tmp, t2t_grid)
                # print "t2t", t2t
            else:
                t2t = max_t2t
        except:
            # print "escape t2t"
            break
        # print total_x, max_x, max_length, wire_left
        total_y = total_y + wire_length + t2t


def draw_wire_cell(spec):
    cell_name = m2_spec.cellname
    wire_cd = int(m2_spec.wire_cd[i]*1e3)
    track_pitch = int(m2_spec.track_pitch[i]*1e3)
    min_t2t = int(m2_spec.min_t2t[i]*1e3)
    max_t2t = int(m2_spec.max_t2t[i]*1e3)
    min_length = int(m2_spec.min_length[i]*1e3)
    max_length = int(m2_spec.max_length[i]*1e3)
    #density     = int(m2_spec.density[i]*1e3)
    t2t_grid = int(m2_spec.t2t_grid[i]*1e3)
    total_x = int(m2_spec.total_x[i]*1e3)
    total_y = int(m2_spec.total_y[i]*1e3)

    x = ((i) % max_duts_per_row)*(dut_pitch_x+total_x)
    y = ((i) / max_duts_per_row)*(dut_pitch_y+total_y)
    origin = np.array([x, y], dtype=int)
    description.append([m2_spec.cellname[i], x, y])

    cellname = m2_spec.cellname[i]
    cell = layout.create_cell(cellname)
    l_m2 = layout.layer(73, 0, "M2")
    init_loc = origin
    # if i>=8:
    # print init_loc[1], total_y-wire_cd, track_pitch
    location = []
    bar = Bar('Generating Rows', max=total_y/track_pitch)
    for j in xrange(init_loc[1], total_y-wire_cd + init_loc[1], track_pitch):
        if thread == 1:
            location = np.array([init_loc[0], j])
            draw_wire_row(cell, l_m2, wire_cd,
                          min_length, max_length,
                          min_t2t, max_t2t, t2t_grid,
                          total_x, location)
            bar.next()
        else:
            location.append(np.array([init_loc[0], j]))
    bar.finish()
    if thread > 1:

        location = np.asarray(location)
        row_number = len(location)

        args_row_generator = zip([cell]*row_number, [l_m2]*row_number, [wire_cd]*row_number,
                                 [min_length]*row_number, [max_length]*row_number,
                                 [min_t2t]*row_number, [max_t2t] *
                                 row_number, [t2t_grid]*row_number,
                                 [total_x]*row_number, location)

        args = split_args(args_row_generator, mp_chunck)
        # for subargs in args:
        #    p = Process (target=draw_wire_row_single_args, args=[subargs])
        #    p.Daemon = True
        #    p.start()
        #    p.join()

        print(len(args))

        # print "Data preparation time = ", e-s, "seconds"
        p = Pool(thread)
        # print "Applying Multithread: ", thread
        # quit()
        p.map(draw_wire_row_single_args, args)

    if clip:
        l_bb = layout.layer(1, 0, "bounding_box")
        # print c1ur.x,c2ll.x

        bbll = pya.Point(origin[0], origin[1])
        bbur = pya.Point(origin[0]+total_x, origin[1]+total_y)
        cell.shapes(l_bb).insert(pya.Box(bbll, bbur))
    if verbose == True:
        cellpath = cellname+'.oas'
        cell.write(os.path.join(dest, cellpath))
    tmp_cell_inst = pya.CellInstArray(
        cell.cell_index(), pya.Trans(pya.Point(0, 0)))
    topcell.insert(tmp_cell_inst)


def check_via_pitch_pass(v_x, v_y, via_mtx, wire_pitch_v, wire_pitch_h, min_via_pitch_x=0, min_via_pitch_y=0):

    x_skip = int(min_via_pitch_x > wire_pitch_v)
    y_skip = int(min_via_pitch_y > wire_pitch_h)

    p1 = 1
    if x_skip > 0:
        if not v_x == 0:
            if via_mtx[v_y, v_x-1] == 1:
                p1 = 0

    p2 = 1
    if y_skip > 0:
        if not v_y == 0:
            if via_mtx[v_y-1, v_x] == 1:
                p2 = 0

    # else:
    #    p =1
    # print p

    p = p1*p2
    return p


def trans_cell(in_cell, angle=0, mirror=0, x=0, y=0, scale=1):
    bbx = in_cell.bbox()
    x_0 = bbx.left
    y_0 = bbx.bottom
    # print x_0,y_0
    #x= x-x_0
    #y= y-y_0
    # print scale, angle, mirror, x, y
    trans = pya.CplxTrans(scale, angle, mirror, x, y)
    tmp_inst = pya.CellInstArray(in_cell.cell_index(), trans)
    return tmp_inst


def drawViaArray(layout, cell, origin, cdX, cdY, pX, pY, Nx, Ny, layerSpec):
    layer = layout.layer(layerSpec[0], layerSpec[1], layerSpec[2])

    for i in xrange(Nx):
        for j in xrange(Ny):
            l = origin[0]+pX*i
            b = origin[1]+pY*j
            r = l+cdX
            t = b+cdY
            ll = pya.Point(int(l), int(b))
            tr = pya.Point(int(r), int(t))
            cell.shapes(layer).insert(pya.Box(ll, tr))


def drawCellArray(targetCell, refCell, pX, pY, Nx, Ny):
    for i in xrange(Ny):
        for j in xrange(Nx):
            x = j*pX
            y = i*pY
            refInst = trans_cell(refCell, x=x, y=y)
            targetCell.insert(refInst)


def layerparse(string):
    layerinfo = string.split('/')
    return [int(layerinfo[0]), int(layerinfo[1])]


class hilbert:
    def __init__(self, layout, layer_num, layer_dt, length, cd, via_layer, cell_prefix="hilbert"):
        self.length = length
        self.cd = cd
        self.level = 0
        self.layer_num = layer_num
        self.layer_dt = layer_dt
        self.via_layer = via_layer
        self.cell_prefix = cell_prefix
        self.layout = layout
        self.box_size = self.length
        self.cell = layout.create_cell(self.cell_prefix + "level_0")
        self.layer = self.layout.layer(self.layer_num, self.layer_dt)
        self.draw_init()

    def draw_init(self):
        p1 = pya.Point(self.cd/2, self.cd/2+self.length)
        p2 = pya.Point(self.cd/2, self.cd/2)
        p3 = pya.Point(self.cd/2+self.length, self.cd/2)
        p4 = pya.Point(self.cd/2+self.length, self.cd/2+self.length)
        self.cell.shapes(self.layer).insert(
            pya.Path([p1, p2, p3, p4], self.cd, self.cd/2, self.cd/2).polygon())

#        self.cell.shapes(self.layout.layer(10,0)).insert(pya.Box(self.cd,0,self.cd*2,self.cd))
        self.cell.shapes(self.layout.layer(self.via_layer, 0)).insert(
            pya.Box(0, 0, self.cd*2, self.cd))

    def next_level(self):
        self.level += 1
        print("Drawing Hilbert Level %g" % self.level)
        newcell = self.layout.create_cell(
            self.cell_prefix + "level_"+str(self.level))
        transll = pya.Trans(0, 0)
        translr = pya.Trans(self.box_size+self.length, 0)
        transul = pya.Trans(1, False, self.box_size +
                            self.cd, self.box_size+self.length)
        transur = pya.Trans(3, False, self.box_size+self.length,
                            self.box_size*2+self.length+self.cd)
        print("    Placing Cells...")
        ll_inst = pya.CellInstArray(self.cell.cell_index(), transll)
        lr_inst = pya.CellInstArray(self.cell.cell_index(), translr)
        ul_inst = pya.CellInstArray(self.cell.cell_index(), transul)
        ur_inst = pya.CellInstArray(self.cell.cell_index(), transur)

        newcell.insert(ll_inst)
        newcell.insert(lr_inst)
        newcell.insert(ur_inst)
        newcell.insert(ul_inst)
        print("    Connecting Quadrants...")
        p11 = pya.Point(self.box_size+self.cd/2, self.box_size+self.cd/2)
        p12 = pya.Point(self.box_size+self.cd/2 +
                        self.length, self.box_size+self.cd/2)
        p21 = pya.Point(self.cd/2, self.cd/2+self.box_size)
        p22 = pya.Point(self.cd/2, self.cd/2+self.box_size+self.length)
        p31 = pya.Point(self.box_size*2+self.length +
                        self.cd/2, self.cd/2+self.box_size)
        p32 = pya.Point(self.box_size*2+self.length+self.cd /
                        2, self.cd/2+self.box_size+self.length)
        path1 = pya.Path([p11, p12], self.cd, self.cd/2, self.cd/2).polygon()
        path2 = pya.Path([p21, p22], self.cd, self.cd/2, self.cd/2).polygon()
        path3 = pya.Path([p31, p32], self.cd, self.cd/2, self.cd/2).polygon()

        newcell.shapes(self.layer).insert(path1)
        newcell.shapes(self.layer).insert(path2)
        newcell.shapes(self.layer).insert(path3)
        print("    Updating Box Size...")
        self.box_size = self.box_size*2+self.length
        self.cell = newcell
        print("Done!")

    def write_layout(self, outOAS):
        self.layout.write(outOAS)

    def write_level(self, level, outOAS):
        if level == -1:
            cellname = self.cell_prefix + "level_"+str(self.level)
        else:
            cellname = self.cell_prefix + "level_"+str(level)
        # from IPython import embed;embed()
        cell = self.layout.cell(cellname)

        cell.write(outOAS)


class peano:
    def __init__(self, layout, layer_num, layer_dt, length, cd, ptype, cell_prefix="peano"):
        self.length = length
        self.cd = cd
        self.level = 0
        self.layer_num = layer_num
        self.layer_dt = layer_dt
        self.layout = layout
        self.box_size = self.length*2
        self.cell = layout.create_cell("level_0")
        self.layer = self.layout.layer(self.layer_num, self.layer_dt)
        self.ptype = ptype
        self.cell_prefix = cell_prefix
        self.draw_init(self.ptype)
    """
    PEANO TYPE=1
     __
    |  |  |
    |  |__|

    PEANO TYPE=2

     __ __
    |__ __
     __ __|
    """

    def draw_init(self, type):
        p1 = pya.Point(self.cd/2, self.cd/2)
        p2 = pya.Point(self.cd/2+self.length*2, self.cd/2)
        p31 = pya.Point(self.cd/2+self.length, self.cd/2+self.length*2)
        p32 = pya.Point(self.cd/2+self.length*2, self.cd/2+self.length)
        p41 = pya.Point(self.cd/2+self.length, self.cd/2)
        p42 = pya.Point(self.cd/2, self.cd/2+self.length)
        p5 = pya.Point(self.cd/2, self.cd/2+self.length*2)
        p6 = pya.Point(self.cd/2+self.length*2, self.cd/2+self.length*2)
        if type == 1:
            self.cell.shapes(self.layer).insert(
                pya.Path([p1, p5, p31, p41, p2, p6], self.cd, self.cd/2, self.cd/2).polygon())
        elif type == 2:
            self.cell.shapes(self.layer).insert(
                pya.Path([p1, p2, p32, p42, p5, p6], self.cd, self.cd/2, self.cd/2).polygon())

    def next_level(self):
        self.level += 1
        print("Drawing Peano Level %g" % self.level)
        newcell = self.layout.create_cell("level_"+str(self.level))

        # translation class transforms based on Rotation, Mirror, X, Y -- 4 item list
        trans11 = pya.Trans(0, 0)
        trans12 = pya.Trans(0, True, self.length +
                            self.box_size, self.box_size+self.length/2)

        #trans12=pya.Trans(0, True, self.cd+self.box_size+self.box_size+self.length,0)
#        trans13=pya.Trans(2*(self.box_size+self.length),0)
#        trans21=pya.Trans(0, True, self.cd+self.box_size, self.box_size+self.length)
#        trans22=pya.Trans(self.box_size+self.length,self.box_size+self.length)
#        trans23=pya.Trans(0, True, self.cd+self.box_size+2*(self.box_size+self.length), self.box_size+self.length)
#        trans31=pya.Trans(0, 2*(self.box_size+self.length))
#        trans32=pya.Trans(0, True, self.cd+self.box_size+self.box_size+self.length,2*(self.box_size+self.length))
#        trans33=pya.Trans(2*(self.box_size+self.length), 2*(self.box_size+self.length))
#        trans=[trans11, trans12, trans13, trans21, trans22, trans23, trans31, trans32, trans33]
        trans = [trans11, trans12]
        print("    Placing Cells...")
        for tran in trans:
            tmp_inst = pya.CellInstArray(self.cell.cell_index(), tran)
            newcell.insert(tmp_inst)
        paths = []

        p1 = pya.Point(self.cd/2, self.cd/2+self.box_size*2+self.length)
        p2 = pya.Point(self.cd/2, self.cd/2+self.box_size*2+self.length*2)
        paths.append(pya.Path([p1, p2], self.cd,
                              self.cd/2, self.cd/2).polygon())

        p1 = pya.Point(self.cd/2+self.box_size, self.cd/2+self.box_size)
        p2 = pya.Point(self.cd/2+self.box_size, self.cd /
                       2+self.box_size+self.length)
        paths.append(pya.Path([p1, p2], self.cd,
                              self.cd/2, self.cd/2).polygon())

        p1 = pya.Point(self.cd/2+self.box_size +
                       self.length, self.cd/2+self.box_size)
        p2 = pya.Point(self.cd/2+self.box_size+self.length,
                       self.cd/2+self.box_size+self.length)
        paths.append(pya.Path([p1, p2], self.cd,
                              self.cd/2, self.cd/2).polygon())

        p1 = pya.Point(self.cd/2+2*(self.box_size+self.length),
                       self.cd/2+self.box_size)
        p2 = pya.Point(self.cd/2+2*(self.box_size+self.length),
                       self.cd/2+self.box_size+self.length)
        paths.append(pya.Path([p1, p2], self.cd,
                              self.cd/2, self.cd/2).polygon())

        p1 = pya.Point(self.cd/2+self.box_size +
                       self.length, self.cd/2+self.box_size)
        p2 = pya.Point(self.cd/2+self.box_size+self.length,
                       self.cd/2+self.box_size+self.length)
        paths.append(pya.Path([p1, p2], self.cd,
                              self.cd/2, self.cd/2).polygon())

        print("    Connecting Quadrants...")

        print("    Updating Box Size...")
        self.box_size = self.box_size*2+self.length
        self.cell = newcell
        print("Done!")

    def write_layout(self, outOAS):
        self.layout.write(outOAS)

    def write_level(self, level, outOAS):
        if level == -1:
            cellname = self.cell_prefix + "level_"+str(self.level)
        else:
            cellname = self.cell_prefix + "level_"+str(level)
        cell = self.layout.cell(cellname)

        cell.write(outOAS)



class track:
    def __init__(self, cd):
        self.rec_num = 0
        self.cd = cd
        self.rec_list = []
        self.geo_or_space = []

    def append(self, ll_x, ll_y, ur_x, ur_y, is_geo):
        self.rec_list.append([ll_x, ll_y, ur_x, ur_y])
        self.geo_or_space.append(is_geo)
        self.rec_num += 1
    

def get_max_proj(track1, track2):
    #TODO ziyang
    return proj


def draw_wire_track(cell, layer, min_cd, max_cd, min_length, max_length, min_t2t, max_t2t, t2t_grid, max_x, location=np.array([0, 0]), enclosure=0):
    cd = rd.randint(min_cd, max_cd)
    track_obj=track(cd) #init track class

    
    offset_x = location[0]
    offset_y = location[1]
    total_x = 0
    total_y = 0
    if enclosure != 0:
        tmp_layout = cell.layout()
        ast_layer = tmp_layout.layer(10010, 0, "ast")
    while total_x < max_x:
        wire_left = total_x
        wire_lower = total_y
        # print min_length, max_length, max_x
        try:
            tmp = min(max_length, max_x - wire_left)
            wire_length = rd.randint(min_length, tmp)
            # print "wire length", wire_length
        except:
            # print "escape wire"
            break

        wire_right = wire_left + wire_length
        wire_upper = wire_lower + cd
        # if wire_right > max_x:
        #    break
        
        wire_ll = pya.Point(int(wire_left+offset_x), int(wire_lower+offset_y))
        wire_ur = pya.Point(int(wire_right+offset_x), int(wire_upper+offset_y))
        track_obj.append(wire_ll.x, wire_ll.y, wire_ur.x, wire_ur.y, 1) 
        wire = pya.Box(wire_ll, wire_ur)
        cell.shapes(layer).insert(wire)
        if enclosure != 0:
            ast_wire_ll = pya.Point(
                wire_left+offset_x+enclosure, wire_lower+offset_y)
            ast_wire_ur = pya.Point(
                wire_right+offset_x-enclosure, wire_upper+offset_y)
            ast_wire = pya.Box(ast_wire_ll, ast_wire_ur)
            cell.shapes(ast_layer).insert(ast_wire)
        try:
            if max_t2t > min_t2t:
                tmp = min(max_t2t, max_x - wire_right)
                # print min_t2t, tmp, t2t_grid
                t2t = rd.randrange(min_t2t, tmp, t2t_grid)
                # print "t2t", t2t
            else:
                t2t = max_t2t
            track_obj.append(wire_ur.x, wire_ur.y-cd, wire_ur.x+t2t, wire_ur.y, 0)
        except:
            # print "escape t2t"
            break
            track_obj.append(wire_ur.x, wire_ur.y-cd, wire_ur.x+max_x-wire_right, wire_ur.y, 0)
        # print total_x, max_x, max_length, wire_left
        total_x = total_x + wire_length + t2t
        
    return track_obj


#for ispd 
#0 1 200   design and mask
#2 sraf
def extract_shapes(layout, center, target_cell, out_cell):
    sp = pya.ShapeProcessor()
    #all_layers = layout.layer_indexes()
    layer_sraf = layout.layer(2,0)
    layer_design = layout.layer(0,0)
    layer_opc = layout.layer(1,0)
    layer_contour = layout.layer(200,0)
    
    design_layers = [layer_design, layer_opc, layer_contour]
    tmp_cell   = layout.create_cell("tmp")
    bbox = pya.Box((center[0]-1)/layout.dbu, (center[1]-1)/layout.dbu,(center[0]+1)/layout.dbu, (center[1]+1)/layout.dbu)
    bbox2= pya.Box((center[0]-0.5)/layout.dbu, (center[1]-0.5)/layout.dbu,(center[0]+0.5)/layout.dbu, (center[1]+0.5)/layout.dbu)
    tmp_cell.shapes(layer_sraf).insert(bbox)
    tmp_cell.shapes(layer_design).insert(bbox)
    tmp_cell.shapes(layer_opc).insert(bbox)
    tmp_cell.shapes(layer_contour).insert(bbox)

    sp.boolean(layout, tmp_cell, layer_sraf, layout, target_cell, layer_sraf, out_cell.shapes(layer_sraf), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_design, layout, target_cell, layer_design, out_cell.shapes(layer_design), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_opc, layout, target_cell, layer_opc, out_cell.shapes(layer_opc), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_contour, layout, target_cell, layer_contour, out_cell.shapes(layer_contour), pya.EdgeProcessor.ModeAnd, True, False, False)
    print("Done Boolean")
    opc_iter = layout.begin_shapes(out_cell, layer_opc)
    while not opc_iter.at_end():
        current = opc_iter.shape().bbox()
        if not current.touches(bbox2):
            opc_iter.shape().delete()
        opc_iter.next()
    print("Remove Out OPC")
    contour_iter = layout.begin_shapes(out_cell, layer_contour)
    opc_box = out_cell.bbox_per_layer(layer_opc)
    while not contour_iter.at_end():
        current = contour_iter.shape().bbox()
        if not current.touches(opc_box):
            contour_iter.shape().delete() 
        contour_iter.next()
    print("Remove Out Contour")
    out_cell.shapes(layout.layer(7777,0)).insert(bbox)
    return out_cell


def extract_shapes2(layout, center, target_cell, out_cell):
    sp = pya.ShapeProcessor()
    #all_layers = layout.layer_indexes()
    layer_sraf = layout.layer(2,1)
    layer_design = layout.layer(0,0)
    layer_opc = layout.layer(2,0)
    layer_contour = layout.layer(55,55)
    
    design_layers = [layer_design, layer_opc, layer_contour]
    tmp_cell   = layout.create_cell("tmp")
    bbox = pya.Box((center[0]-1)/layout.dbu, (center[1]-1)/layout.dbu,(center[0]+1)/layout.dbu, (center[1]+1)/layout.dbu)
    bbox2= pya.Box((center[0]-0.5)/layout.dbu, (center[1]-0.5)/layout.dbu,(center[0]+0.5)/layout.dbu, (center[1]+0.5)/layout.dbu)
    tmp_cell.shapes(layer_sraf).insert(bbox)
    tmp_cell.shapes(layer_design).insert(bbox)
    tmp_cell.shapes(layer_opc).insert(bbox)
    tmp_cell.shapes(layer_contour).insert(bbox)

    sp.boolean(layout, tmp_cell, layer_sraf, layout, target_cell, layer_sraf, out_cell.shapes(layer_sraf), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_design, layout, target_cell, layer_design, out_cell.shapes(layer_design), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_opc, layout, target_cell, layer_opc, out_cell.shapes(layer_opc), pya.EdgeProcessor.ModeAnd, True, False, False)
    sp.boolean(layout, tmp_cell, layer_contour, layout, target_cell, layer_contour, out_cell.shapes(layer_contour), pya.EdgeProcessor.ModeAnd, True, False, False)
    print("Done Boolean")

    out_cell.shapes(layout.layer(7777,0)).insert(bbox)
    return out_cell
#import gdstk

class shape_enumerator:
    def __init__(self, glp_path, shape_level=1, core = 1000, tile_size=2000, search_step = 100, spacing = 70):
        self.glp_path=glp_path
        self.shape_level=shape_level
        self.core=core
        self.tile_size=tile_size
        self.spacing=spacing
        self.search_step  = search_step
        self.shape_lib = []
        self.polygon_coords=[]
        self.rectangle_coords=[]
        self.layout =pya.Layout()
        self.mask_layer = self.layout.layer(1,0)
        self.contour_layer = self.layout.layer(2,0)
        self.design_layer = self.layout.layer(3,0)
        self.rule_layer = self.layout.layer(99,0)
        self.layout.dbu=1e-3
        self.cell_id = 0
        self.out_path = "./iccad13"
        self._generate_rule_cell()
        self.offset_x = (self.tile_size-self.core)//2
        self.offset_y = (self.tile_size-self.core)//2
    def get_shape_lib(self):
        for dirname, dirnames, filenames in os.walk(self.glp_path):
            #bar = Bar("Converting GDSII to Image", max=len(filenames))
            #print(filenames)
            for i in range(0, len(filenames)):
                with open(os.path.join(dirname, filenames[i]),"r") as f:
                    for line in f:
                        if line.startswith(" "):
                            _info=line.split()
                            if _info[0]=="RECT":
                                info=_info[3:]
                                temp_rect = []
                                temp_rect.append([int(info[0]), int(info[1])])
                                temp_rect.append([int(info[0])+int(info[2]), int(info[1])+int(info[3])])
                                self.rectangle_coords.append(np.array(temp_rect))

                            if _info[0]=="PGON":
                                info=_info[3:]
                                temp_poly = []
                                for j in range(len(info)//2):
                                    temp_poly.append([int(info[j*2]), int(info[j*2+1])])
                                self.polygon_coords.append(np.array(temp_poly))


        for i in range(len(self.rectangle_coords)):
            shape = self.rectangle_coords[i]
            offset_x = np.min(shape[:,0])
            offset_y = np.min(shape[:,1])
            shape[:,0] = shape[:,0]-offset_x
            shape[:,1] = shape[:,1]-offset_y
            self.rectangle_coords[i] = shape

        for i in range(len(self.polygon_coords)):
            shape = self.polygon_coords[i]
            offset_x = np.min(shape[:,0])
            offset_y = np.min(shape[:,1])
            shape[:,0] = shape[:,0]-offset_x
            shape[:,1] = shape[:,1]-offset_y
            self.polygon_coords[i] = shape
        tmp_length=[len(x) for x in self.polygon_coords]
        tmp_id=np.argsort(tmp_length)
        sort_length=np.sort(tmp_length)
        print(tmp_id)
        print(sort_length)
        self.rectangle_coords=np.unique(np.array(self.rectangle_coords),axis=0)
        tmp_poly_coords = np.unique(np.array(self.polygon_coords[:10]),axis=0)

        for i in tmp_poly_coords:
            self.polygon_coords.append(i)
        self.polygon_coords = self.polygon_coords[10:]


        for shape in self.rectangle_coords:
            #print(shape[0,0])
            #pya.Point(1,1)
            
            ll=pya.Point(int(shape[0,0]),int(shape[0,1]))
            ur=pya.Point(int(shape[1,0]),int(shape[1,1]))
            self.shape_lib.append(pya.Polygon(pya.Box(ll,ur)))
        
        for shape in self.polygon_coords:
            points=[]
            for v in shape:
                points.append(pya.Point(int(v[0]), int(v[1])))
            self.shape_lib.append(pya.Polygon(points))

        print(self.shape_lib)
    def _generate_rule_cell(self):
        self.rule_cell =  self.layout.create_cell("rule_cell")
        tile = pya.Polygon(pya.Box(0,0,self.tile_size, self.tile_size))
        core = pya.Box((self.tile_size-self.core)//2,(self.tile_size-self.core)//2,(self.tile_size+self.core)//2,(self.tile_size+self.core)//2)
        tile.insert_hole(core)
        self.rule_cell.shapes(self.rule_layer).insert(tile)
        self.rule_cell.write(os.path.join(self.out_path, "rule_cell.oas"))
        #print(tile)
    def _sort_shape_lib(self, shape_lib):
        areas = [x.bbox().area() for x in shape_lib]
        return np.argsort(areas)[::-1]
    def _draw_lib(self):
        cell = self.layout.create_cell("libs")
        layer = self.layout.layer(100,0)
        i=0
        for shape in self.shape_lib:
            tshape = shape.transformed(pya.Trans(1000*i, 0))
            cell.shapes(layer).insert(tshape)
            i+=1
        
        cell.write("./iccad13/lib.oas")
 
    def draw_layout(self):
        #print("debug drawcell")
        cell = self.layout.create_cell(str(self.cell_id))
        #print(cell.bbox().width(), cell.bbox().height())
        shape = rd.sample(self.shape_lib, 1)[0]
        trans = pya.Trans(self.offset_x,self.offset_y)
        shape_transformed = shape.transformed(trans)
        cell.shapes(self.design_layer).insert(shape_transformed)
        #for attempts in range(100):
        #print("debug while")

        shape_lib = rd.choices(self.shape_lib, k=rd.randint(5, 25))
        #print(shape_lib)
        sorted_id = self._sort_shape_lib(shape_lib)
        #quit()
        for id in sorted_id:
            shape = shape_lib[id]
            #print(cell.bbox().width(), cell.bbox().height())
            for i in range(self.offset_x+1, self.offset_x+self.core, self.search_step):
                for j in range(self.offset_y+1, self.offset_y+self.core, self.search_step):
                    inserted = 0
                    #print("debug pos search %g, %g"%(i,j))
                    trans = pya.Trans(i,j)
                    shape_transformed = shape.transformed(trans)
                    shape_sized = shape_transformed.sized(self.spacing)
                    violation = 0
                    contour_iter = self.layout.begin_shapes(cell, self.design_layer)
                    while not contour_iter.at_end():
                        current = contour_iter.shape().polygon
                        if current.touches(shape_sized):
                            violation = 1
                            break
                        contour_iter.next()
                    if violation == 1:
                        continue
                    else:
                        cell.shapes(self.design_layer).insert(shape_transformed)
                        inserted = 1
                        break 
                if inserted ==1:
                    break
        
        #cell.shapes(self.design_layer).insert(shape)
        #print(cell.bbox().width())
        contour_iter = self.layout.begin_shapes(cell, self.design_layer)
        tile = pya.Polygon(pya.Box(0,0,self.tile_size, self.tile_size))
        core = pya.Box((self.tile_size-self.core)//2,(self.tile_size-self.core)//2,(self.tile_size+self.core)//2,(self.tile_size+self.core)//2)
        tile.insert_hole(core)
        #opc_box = out_cell.bbox_per_layer(layer_opc)
        while not contour_iter.at_end():
            current = contour_iter.shape().polygon
            if current.touches(tile):
                contour_iter.shape().delete() 
            contour_iter.next()
        #print("Remove Out Contour")
        cell.shapes(self.rule_layer).insert(tile)
        cell.write(os.path.join(self.out_path, "cell%g.gds"%self.cell_id))
        self.cell_id+=1
        cell.delete()


