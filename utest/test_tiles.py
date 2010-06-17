#!/usr/bin/env python

'''Testing the map model.

This test should just run without failing.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: MAP_MODEL.py 1078 2007-08-01 03:43:38Z r1chardj0n3s $'

# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1 

# will use the cocos in the same checkout, except if you move this file.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from cocos.tiles import Rect, RectCell, RectMap, HexCell, HexMap, Tile

rmd = [
   [ {'meta': x} for x in m ] for m in ['ad', 'be', 'cf']
]
hmd = [
   [ {'meta': x} for x in m ] for m in ['ab', 'cd', 'ef', 'gh']
]

def gen_hex_map(meta, h):
    r = []
    cell = None
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            if cell is None:
                cell = HexCell(0, 0, h, None, None)
            k = j
            if not i % 2:  k += 1
            c.append(HexCell(i, j, h, dict(info), Tile('dbg', {}, None)))
    return HexMap('debug', h, r)

def gen_rect_map(meta, w, h):
    r = []
    cell = None
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            c.append(RectCell(i, j, w, h, dict(info), Tile('dbg', {}, None)))
    return RectMap('debug', w, h, r)


def gen_recthex_map(meta, h):
    r = []
    cell = None
    w = int(h / math.sqrt(3)) * 2
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            c.append(RectCell(i, j, w, h, dict(info), Tile('dbg', {}, None)))
    return RectMap('debug', w, h, r)

class RectTest(unittest.TestCase):
    def test_rect_coords(self):
        t = Rect(0, 0, 10, 16)
        self.assertEquals(t.top, 16)
        self.assertEquals(t.bottom, 0)
        self.assertEquals(t.left, 0)
        self.assertEquals(t.right, 10)
        self.assertEquals(t.topleft, (0, 16))
        self.assertEquals(t.topright, (10, 16))
        self.assertEquals(t.bottomleft, (0, 0))
        self.assertEquals(t.bottomright, (10, 0))
        self.assertEquals(t.midtop, (5, 16))
        self.assertEquals(t.midleft, (0, 8))
        self.assertEquals(t.midright, (10, 8))
        self.assertEquals(t.midbottom, (5, 0))

class MapModelTest(unittest.TestCase):

    def test_rect_neighbor(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)
        t = m.get_cell(0,0)
        self.assertEquals((t.x, t.y), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).properties['meta'], 'd')
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).properties['meta'], 'b')
        t = m.get_neighbor(t, m.UP)
        self.assertEquals((t.i, t.j), (0, 1))
        self.assertEquals((t.x, t.y), (0, 16))
        self.assertEquals(t.properties['meta'], 'd')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).properties['meta'], 'e')
        t = m.get_neighbor(t, m.RIGHT)
        self.assertEquals((t.i, t.j), (1, 1))
        self.assertEquals((t.x, t.y), (10, 16))
        self.assertEquals(t.properties['meta'], 'e')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'b')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).properties['meta'], 'f')
        self.assertEquals(m.get_neighbor(t, m.LEFT).properties['meta'], 'd')
        t = m.get_neighbor(t, m.RIGHT)
        self.assertEquals((t.i, t.j), (2, 1))
        self.assertEquals((t.x, t.y), (20, 16))
        self.assertEquals(t.properties['meta'], 'f')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'c')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.LEFT).properties['meta'], 'e')
        t = m.get_neighbor(t, m.DOWN)
        self.assertEquals((t.i, t.j), (2, 0))
        self.assertEquals((t.x, t.y), (20, 0))
        self.assertEquals(t.properties['meta'], 'c')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).properties['meta'], 'f')
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.LEFT).properties['meta'], 'b')

    def test_rect_pixel(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)
        t = m.get_at_pixel(0,0)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')
        t = m.get_at_pixel(9,15)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')
        t = m.get_at_pixel(10,15)
        self.assertEquals((t.i, t.j), (1, 0))
        self.assertEquals(t.properties['meta'], 'b')
        t = m.get_at_pixel(9,16)
        self.assertEquals((t.i, t.j), (0, 1))
        self.assertEquals(t.properties['meta'], 'd')
        t = m.get_at_pixel(10,16)
        self.assertEquals((t.i, t.j), (1, 1))
        self.assertEquals(t.properties['meta'], 'e')

    def test_rect_region(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 64, 64)
        t = m.get_in_region(0, 0, 63, 63)
        self.assertEquals(len(t), 1)
        self.assertEquals(t[0].properties['meta'], 'a')
        t = m.get_in_region(64, 64, 127, 127)
        self.assertEquals(len(t), 1)
        self.assertEquals(t[0].properties['meta'], 'e')
        t = m.get_in_region(32, 32, 96, 96)
        self.assertEquals(len(t), 4)


    def test_hex_neighbor(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)
        t = m.get_cell(0,0)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).properties['meta'], 'b')
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'c')
        t = m.get_neighbor(t, m.UP)
        self.assertEquals((t.i, t.j), (0, 1))
        self.assertEquals(t.properties['meta'], 'b')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'c')
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'd')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        self.assertEquals((t.i, t.j), (1, 0))
        self.assertEquals(t.properties['meta'], 'c')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).properties['meta'], 'd')
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'a')
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'e')
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'b')
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'f')
        t = m.get_neighbor(t, m.UP_RIGHT)
        self.assertEquals((t.i, t.j), (2, 1))
        self.assertEquals(t.properties['meta'], 'f')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'e')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'c')
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'g')
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'd')
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'h')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        self.assertEquals((t.i, t.j), (3, 0))
        self.assertEquals(t.properties['meta'], 'g')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).properties['meta'], 'h')
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'e')
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'f')
        assert m.get_neighbor(t, m.UP_RIGHT) is None
        t = m.get_neighbor(t, m.UP)
        self.assertEquals((t.i, t.j), (3, 1))
        self.assertEquals(t.properties['meta'], 'h')
        self.assertEquals(m.get_neighbor(t, m.DOWN).properties['meta'], 'g')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'f')
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        assert m.get_neighbor(t, m.UP_LEFT) is None
        assert m.get_neighbor(t, m.UP_RIGHT) is None

    def test_hex_coords(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)

        # test tile sides / corners
        t00 = m.get_cell(0, 0)
        self.assertEquals(t00.top, 32)
        self.assertEquals(t00.bottom, 0)
        self.assertEquals(t00.left, (0, 16))
        self.assertEquals(t00.right, (36, 16))
        self.assertEquals(t00.center, (18, 16))
        self.assertEquals(t00.topleft, (9, 32))
        self.assertEquals(t00.topright, (27, 32))
        self.assertEquals(t00.bottomleft, (9, 0))
        self.assertEquals(t00.bottomright, (27, 0))
        self.assertEquals(t00.midtop, (18, 32))
        self.assertEquals(t00.midbottom, (18, 0))
        self.assertEquals(t00.midtopleft, (4, 24))
        self.assertEquals(t00.midtopright, (31, 24))
        self.assertEquals(t00.midbottomleft, (4, 8))
        self.assertEquals(t00.midbottomright, (31, 8))

        t10 = m.get_cell(1, 0)
        self.assertEquals(t10.top, 48)
        self.assertEquals(t10.bottom, 16)
        self.assertEquals(t10.left, t00.topright)
        self.assertEquals(t10.right, (63, 32))
        self.assertEquals(t10.center, (45, 32))
        self.assertEquals(t10.topleft, (36, 48))
        self.assertEquals(t10.topright, (54, 48))
        self.assertEquals(t10.bottomleft, t00.right)
        self.assertEquals(t10.bottomright, (54, 16))
        self.assertEquals(t10.midtop, (45, 48))
        self.assertEquals(t10.midbottom, (45, 16))
        self.assertEquals(t10.midtopleft, (31, 40))
        self.assertEquals(t10.midtopright, (58, 40))
        self.assertEquals(t10.midbottomleft, t00.midtopright)
        self.assertEquals(t10.midbottomright, (58, 24))

        t = m.get_cell(2, 0)
        self.assertEquals(t.top, 32)
        self.assertEquals(t.bottom, 0)
        self.assertEquals(t.left, t10.bottomright)
        self.assertEquals(t.right, (90, 16))
        self.assertEquals(t.center, (72, 16))
        self.assertEquals(t.topleft, t10.right)
        self.assertEquals(t.midtopleft, t10.midbottomright)

    def test_hex_pixel(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)
        
        # bottom-left map corner will return A
        t = m.get_at_pixel(0,0)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')

        # left-most corner of A
        t = m.get_at_pixel(0, 16)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')

        t = m.get_at_pixel(16, 16)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')

        t = m.get_at_pixel(35,16)
        self.assertEquals((t.i, t.j), (0, 0))
        self.assertEquals(t.properties['meta'], 'a')

        t = m.get_at_pixel(36,16)
        self.assertEquals((t.i, t.j), (1, 0))
        self.assertEquals(t.properties['meta'], 'c')

    def test_hex_dimensions(self):
        m = gen_hex_map([[{'a':'a'}]], 32)
        self.assertEquals((m.px_width, m.px_height), (36, 32))
        m = gen_hex_map([[{'a':'a'}]*2], 32)
        self.assertEquals((m.px_width, m.px_height), (36, 64))
        m = gen_hex_map([[{'a':'a'}]]*2, 32)
        self.assertEquals((m.px_width, m.px_height), (63, 48))

if __name__ == '__main__':
    unittest.main()

