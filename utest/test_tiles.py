#!/usr/bin/env python

'''Testing the map model.

This test should just run without failing.
'''

from __future__ import division, print_function, unicode_literals

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

import cocos.layer
from cocos.tiles import Rect, RectCell, RectMap, HexCell, HexMap, Tile
import cocos.euclid as eu

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
                cell = HexCell(0, 0, None, h, None, None)
            k = j
            if not i % 2:  k += 1
            c.append(HexCell(i, j, None, h, dict(info), Tile('dbg', {}, None)))
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
        self.assertEqual(t.top, 16)
        self.assertEqual(t.bottom, 0)
        self.assertEqual(t.left, 0)
        self.assertEqual(t.right, 10)
        self.assertEqual(t.topleft, (0, 16))
        self.assertEqual(t.topright, (10, 16))
        self.assertEqual(t.bottomleft, (0, 0))
        self.assertEqual(t.bottomright, (10, 0))
        self.assertEqual(t.midtop, (5, 16))
        self.assertEqual(t.midleft, (0, 8))
        self.assertEqual(t.midright, (10, 8))
        self.assertEqual(t.midbottom, (5, 0))

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
        self.assertEqual((t.x, t.y), (0, 0))
        self.assertEqual(t.properties['meta'], 'a')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEqual(m.get_neighbor(t, m.UP).properties['meta'], 'd')
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEqual(m.get_neighbor(t, m.RIGHT).properties['meta'], 'b')
        t = m.get_neighbor(t, m.UP)
        self.assertEqual((t.i, t.j), (0, 1))
        self.assertEqual((t.x, t.y), (0, 16))
        self.assertEqual(t.properties['meta'], 'd')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEqual(m.get_neighbor(t, m.RIGHT).properties['meta'], 'e')
        t = m.get_neighbor(t, m.RIGHT)
        self.assertEqual((t.i, t.j), (1, 1))
        self.assertEqual((t.x, t.y), (10, 16))
        self.assertEqual(t.properties['meta'], 'e')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'b')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEqual(m.get_neighbor(t, m.RIGHT).properties['meta'], 'f')
        self.assertEqual(m.get_neighbor(t, m.LEFT).properties['meta'], 'd')
        t = m.get_neighbor(t, m.RIGHT)
        self.assertEqual((t.i, t.j), (2, 1))
        self.assertEqual((t.x, t.y), (20, 16))
        self.assertEqual(t.properties['meta'], 'f')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'c')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEqual(m.get_neighbor(t, m.LEFT).properties['meta'], 'e')
        t = m.get_neighbor(t, m.DOWN)
        self.assertEqual((t.i, t.j), (2, 0))
        self.assertEqual((t.x, t.y), (20, 0))
        self.assertEqual(t.properties['meta'], 'c')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEqual(m.get_neighbor(t, m.UP).properties['meta'], 'f')
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEqual(m.get_neighbor(t, m.LEFT).properties['meta'], 'b')

    def test_rect_pixel(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)
        t = m.get_at_pixel(0,0)
        self.assertEqual((t.i, t.j), (0, 0))
        self.assertEqual(t.properties['meta'], 'a')
        t = m.get_at_pixel(9,15)
        self.assertEqual((t.i, t.j), (0, 0))
        self.assertEqual(t.properties['meta'], 'a')
        t = m.get_at_pixel(10,15)
        self.assertEqual((t.i, t.j), (1, 0))
        self.assertEqual(t.properties['meta'], 'b')
        t = m.get_at_pixel(9,16)
        self.assertEqual((t.i, t.j), (0, 1))
        self.assertEqual(t.properties['meta'], 'd')
        t = m.get_at_pixel(10,16)
        self.assertEqual((t.i, t.j), (1, 1))
        self.assertEqual(t.properties['meta'], 'e')

    def test_rect_region(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 64, 64)
        t = m.get_in_region(0, 0, 63, 63)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].properties['meta'], 'a')
        t = m.get_in_region(64, 64, 127, 127)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].properties['meta'], 'e')
        t = m.get_in_region(32, 32, 96, 96)
        self.assertEqual(len(t), 4)

    def test_rect_region_alt__rect_with_area_gt_0(self):
        tile_width = tile_height_h = 2
        nrows = 7
        ncols = 6
        cells = [ [ 'col_%d_row_%d'%(yy, xx) for xx in range(ncols)]
                                                      for yy in range(nrows)]        
        m = RectMap(42, tile_width, tile_height_h, cells, origin=(0, 0, 0))
        x1, y1 = 5, 8
        x2, y2 = 8, 12
        overlaps = m.get_in_region(x1, y1, x2, y2)
        print(overlaps)
        # expects all cells which overlaps the x1,y1,x2,y2 rect in an area > 0
        assert set(overlaps) == set( ['col_2_row_4', 'col_3_row_4',
                                     'col_2_row_5', 'col_3_row_5'] )

        # all rect boundaries overlaps cell boundaries
        x1, y1 = 6, 8
        x2, y2 = 8, 12
        overlaps = m.get_in_region(x1, y1, x2, y2)
        print(overlaps)
        # expects all cells which overlaps the x1,y1,x2,y2 rect in an area > 0
        assert set(overlaps) == set( ['col_3_row_4', 'col_3_row_5'] )

    def test_rect_region_alt__rect_is_a_segment_not_in_cells_boundary(self):
        # this is emergent behavior , not planed one
        tile_width = tile_height_h = 2
        nrows = 7
        ncols = 6
        cells = [ [ 'col_%d_row_%d'%(yy, xx) for xx in range(ncols)]
                                                      for yy in range(nrows)]        
        m = RectMap(42, tile_width, tile_height_h, cells, origin=(0, 0, 0))
        x1, y1 = 5, 8
        x2, y2 = 5, 12
        overlaps = m.get_in_region(x1, y1, x2, y2)
        print('rect is a segment not overlapping cells boundary:', overlaps)
        assert set(overlaps) == set( ['col_2_row_4', 'col_2_row_5'] )

    def test_rect_region_alt__rect_is_a_segment_not_in_cells_boundary(self):
        # this is emergent behavior , not planed one
        tile_width = tile_height_h = 2
        nrows = 7
        ncols = 6
        cells = [ [ 'col_%d_row_%d'%(yy, xx) for xx in range(ncols)]
                                                      for yy in range(nrows)]        
        m = RectMap(42, tile_width, tile_height_h, cells, origin=(0, 0, 0))
        x1, y1 = 4, 8
        x2, y2 = 4, 12
        overlaps = m.get_in_region(x1, y1, x2, y2)
        print('rect is a segment overlapping cells boundary:', overlaps)
        assert set(overlaps) == set( [] )

    def test_rect_region_alt__rect_is_a_point(self):
        # this is emergent behavior , not planed one
        tile_width = tile_height_h = 2
        nrows = 7
        ncols = 6
        cells = [ [ 'col_%d_row_%d'%(yy, xx) for xx in range(ncols)]
                                                      for yy in range(nrows)]        
        m = RectMap(42, tile_width, tile_height_h, cells, origin=(0, 0, 0))
        x1, y1 = 5, 8
        x2, y2 = 5, 8
        overlaps = m.get_in_region(x1, y1, x2, y2)
        print('rect is point:', overlaps)
        assert set(overlaps) == set( [] )

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
        self.assertEqual((t.i, t.j), (0, 0))
        self.assertEqual(t.properties['meta'], 'a')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEqual(m.get_neighbor(t, m.UP).properties['meta'], 'b')
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEqual(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'c')
        t = m.get_neighbor(t, m.UP)
        self.assertEqual((t.i, t.j), (0, 1))
        self.assertEqual(t.properties['meta'], 'b')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        self.assertEqual(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'c')
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEqual(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'd')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        self.assertEqual((t.i, t.j), (1, 0))
        self.assertEqual(t.properties['meta'], 'c')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEqual(m.get_neighbor(t, m.UP).properties['meta'], 'd')
        self.assertEqual(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'a')
        self.assertEqual(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'e')
        self.assertEqual(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'b')
        self.assertEqual(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'f')
        t = m.get_neighbor(t, m.UP_RIGHT)
        self.assertEqual((t.i, t.j), (2, 1))
        self.assertEqual(t.properties['meta'], 'f')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'e')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEqual(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'c')
        self.assertEqual(m.get_neighbor(t, m.DOWN_RIGHT).properties['meta'], 'g')
        self.assertEqual(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'd')
        self.assertEqual(m.get_neighbor(t, m.UP_RIGHT).properties['meta'], 'h')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        self.assertEqual((t.i, t.j), (3, 0))
        self.assertEqual(t.properties['meta'], 'g')
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEqual(m.get_neighbor(t, m.UP).properties['meta'], 'h')
        self.assertEqual(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'e')
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        self.assertEqual(m.get_neighbor(t, m.UP_LEFT).properties['meta'], 'f')
        assert m.get_neighbor(t, m.UP_RIGHT) is None
        t = m.get_neighbor(t, m.UP)
        self.assertEqual((t.i, t.j), (3, 1))
        self.assertEqual(t.properties['meta'], 'h')
        self.assertEqual(m.get_neighbor(t, m.DOWN).properties['meta'], 'g')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEqual(m.get_neighbor(t, m.DOWN_LEFT).properties['meta'], 'f')
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
        self.assertEqual(t00.top, 32)
        self.assertEqual(t00.bottom, 0)
        self.assertEqual(t00.left, (0, 16))
        self.assertEqual(t00.right, (36, 16))
        self.assertEqual(t00.center, (18, 16))
        self.assertEqual(t00.topleft, (9, 32))
        self.assertEqual(t00.topright, (27, 32))
        self.assertEqual(t00.bottomleft, (9, 0))
        self.assertEqual(t00.bottomright, (27, 0))
        self.assertEqual(t00.midtop, (18, 32))
        self.assertEqual(t00.midbottom, (18, 0))
        self.assertEqual(t00.midtopleft, (4, 24))
        self.assertEqual(t00.midtopright, (31, 24))
        self.assertEqual(t00.midbottomleft, (4, 8))
        self.assertEqual(t00.midbottomright, (31, 8))

        t10 = m.get_cell(1, 0)
        self.assertEqual(t10.top, 48)
        self.assertEqual(t10.bottom, 16)
        self.assertEqual(t10.left, t00.topright)
        self.assertEqual(t10.right, (63, 32))
        self.assertEqual(t10.center, (45, 32))
        self.assertEqual(t10.topleft, (36, 48))
        self.assertEqual(t10.topright, (54, 48))
        self.assertEqual(t10.bottomleft, t00.right)
        self.assertEqual(t10.bottomright, (54, 16))
        self.assertEqual(t10.midtop, (45, 48))
        self.assertEqual(t10.midbottom, (45, 16))
        self.assertEqual(t10.midtopleft, (31, 40))
        self.assertEqual(t10.midtopright, (58, 40))
        self.assertEqual(t10.midbottomleft, t00.midtopright)
        self.assertEqual(t10.midbottomright, (58, 24))

        t = m.get_cell(2, 0)
        self.assertEqual(t.top, 32)
        self.assertEqual(t.bottom, 0)
        self.assertEqual(t.left, t10.bottomright)
        self.assertEqual(t.right, (90, 16))
        self.assertEqual(t.center, (72, 16))
        self.assertEqual(t.topleft, t10.right)
        self.assertEqual(t.midtopleft, t10.midbottomright)

    def test_hex_pixel(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)
        
        # bottom-left map corner will return None
        t = m.get_at_pixel(0,0)
        self.assertEqual(t, None)

        # moving a bit from any corner roughtly towards the center
        # gives a point that hit the cell
        t00 = m.get_cell(0, 0)

        near_left = eu.Vector2(*t00.left) + eu.Vector2(1, 0)
        t = m.get_at_pixel(*near_left)
        self.assertEqual(t00, t)

        near_right = eu.Vector2(*t00.right) + eu.Vector2(-1, 0)
        t = m.get_at_pixel(*near_right)
        self.assertEqual(t00, t)

        near_topright = eu.Vector2(*t00.topright) + eu.Vector2(-1, -1)
        t = m.get_at_pixel(*near_topright)
        self.assertEqual(t00, t)

        near_topleft = eu.Vector2(*t00.topleft) + eu.Vector2(1, -1)
        t = m.get_at_pixel(*near_topleft)
        self.assertEqual(t00, t)

        near_bottomright = eu.Vector2(*t00.bottomright) + eu.Vector2(-1, 1)
        t = m.get_at_pixel(*near_bottomright)
        self.assertEqual(t00, t)

        near_bottomleft = eu.Vector2(*t00.bottomleft) + eu.Vector2(1, 1)
        t = m.get_at_pixel(*near_bottomleft)
        self.assertEqual(t00, t)


        # Whereas moving from the corner outwards gives a point outside
        # the cell
        near_left = eu.Vector2(*t00.left) - eu.Vector2(1, 0)
        t = m.get_at_pixel(*near_left)
        self.assertFalse(t00 == t)

        near_right = eu.Vector2(*t00.right) - eu.Vector2(-1, 0)
        t = m.get_at_pixel(*near_right)
        self.assertFalse(t00 == t)

        near_topright = eu.Vector2(*t00.topright) - eu.Vector2(-1, -1)
        t = m.get_at_pixel(*near_topright)
        self.assertFalse(t00 == t)

        near_topleft = eu.Vector2(*t00.topleft) - eu.Vector2(1, -1)
        t = m.get_at_pixel(*near_topleft)
        self.assertFalse(t00 == t)

        near_bottomright = eu.Vector2(*t00.bottomright) - eu.Vector2(-1, 1)
        t = m.get_at_pixel(*near_bottomright)
        self.assertFalse(t00 == t)

        near_bottomleft = eu.Vector2(*t00.bottomleft) - eu.Vector2(1, 1)
        t = m.get_at_pixel(*near_bottomleft)
        self.assertFalse(t00 == t)

    def test_hex_dimensions(self):
        m = gen_hex_map([[{'a':'a'}]], 32)
        self.assertEqual((m.px_width, m.px_height), (36, 32))
        m = gen_hex_map([[{'a':'a'}]*2], 32)
        self.assertEqual((m.px_width, m.px_height), (36, 64))
        m = gen_hex_map([[{'a':'a'}]]*2, 32)
        self.assertEqual((m.px_width, m.px_height), (63, 48))

if __name__ == '__main__':
    unittest.main()

