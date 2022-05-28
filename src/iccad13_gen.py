import sys
sys.path.append('./src')

from LayoutGenerator import *
import os
from progress.bar import Bar

se = shape_enumerator("./data/iccad13_base")



se.get_shape_lib()
#se._generate_rule_cell()

#se.search_step = 70
#se._draw_lib()



clip_num_per_density=1000
for i in range(40, 80, 10):
    se.spacing=i
    bar = Bar("enumerating layouts spacing %g"%i, max=clip_num_per_density)
    for pc in range(clip_num_per_density):
        se.draw_layout()
        bar.next()
    
    bar.finish()



