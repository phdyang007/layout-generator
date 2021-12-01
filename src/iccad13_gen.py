import sys
sys.path.append('./src')

from LayoutGenerator import *
import os

se = shape_enumerator("./data/iccad13_base")



se.get_shape_lib()
#se._generate_rule_cell()

se.search_step = 70
se.draw_layout()

