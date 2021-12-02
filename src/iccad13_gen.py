import sys
sys.path.append('./src')

from LayoutGenerator import *
import os

se = shape_enumerator("./data/iccad13_base")



se.get_shape_lib()
#se._generate_rule_cell()

#se.search_step = 70
se._draw_lib()


for i in range(70, 150, 20):
    se.spacing=i
    for j in range(10000):
        se.draw_layout()




