import sys 
sys.path.append('./src')
from LayoutGenerator import layout_parser



lp = layout_parser("glp", path)

lp.glp2gdsii(0,0)


