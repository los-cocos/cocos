from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.path import Bezier

curva = Bezier((100, 100), (449, 290), (5, 287), (438, 27))
curva2 = Bezier((587, 587), (-454, -591), (-470, -124), (-49, -584))
new = Bezier((100, 100), (200, 200), (108, 268), (438, 27))
new174332 = Bezier((100, 100), (200, 200), (108, 268), (438, 27))
new228555 = Bezier((100, 100), (422, 291), (353, 255), (438, 27))
circulo = Bezier((7, 7), (0, 1), (630, 237), (630, -234))


if __name__ == '__main__':
    print('this file is part of demo_sprites.py')
