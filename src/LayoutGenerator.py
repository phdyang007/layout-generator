import pya
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
        if wire_length < int(wirelength_threshold * (max_length - min_length)):
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
        if t2t < int(t2t_threshold * (max_t2t - min_t2t)):
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
            cellname = "level_"+str(self.level)
        else:
            cellname = "level_"+str(level)
        cell = self.layout.cell(cellname)

        cell.write(outOAS)


class peano:
    def __init__(self, layout, layer_num, layer_dt, length, cd, ptype):
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
        print("Drawing Hilbert Level %g" % self.level)
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
            cellname = "level_"+str(self.level)
        else:
            cellname = "level_"+str(level)
        cell = self.layout.cell(cellname)

        cell.write(outOAS)
