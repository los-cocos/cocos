# -*- coding: utf-8 -*-
""" Tests that an actor using RectMapCollider does not get stuck
Run the tests with pytest.

Implementation description
    - The basic situation considered is
          - actor touching wall in one of it sides
          - requested to move a dx, dy that will push against the wall and
            allow free movement in the axis not blocked by the wall

    - They are so many small variations in each situation proposed that
      directly writing each test setup would be error prone, so a layered
      case generator approach was selected
          - base cases depict qualitative diferent situations as a
             (map, actor_rect, push, signed free axis vector)
          - for each parametrizable value , a set of values of
            interest is defined
          - code will walk the (base cases, params values) generating the
            concrete cases to validate
          - as an implementation detail, maps will be cached

    - params desired to change
        map: the basic form and orientation in the situation
        cell_size, actor_size: mostly
           actor side z <=> cell side z
           actor side odd or even (because .center assings; division_errors?)
        push style: dx, dy
        actor start position: move the start position along the wall to cover
          all int alignements with the grid, ie do offsets 1..cell_width if
          free movement axis is x, ... 
"""
from __future__ import division, print_function, unicode_literals

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

# for py.test
import py

import cocos
import cocos.layer
from cocos.tiles import RectMap, RectCell, RectMapCollider 
from cocos.rect import Rect

import aux_RectMapCollider__no_stuck as aux
# set the cocos classes needed in aux before calling any function there
aux.RectMap_cls = RectMap
aux.RectCell = RectCell
aux.Rect = Rect


maps_cache = aux.generate_maps('-')
 
##def test_smoketest_string_to_RectMap():
##    cells_per_row = 5
##    cells_per_column = 6
##    cell_width = 3
##    cell_height = 5
##    string_map = mapstrings['vertical_w_hole']
##    rect_map = string_to_RectMap(string_map, cell_width, cell_height)
##    cells = rect_map.get_in_region(0, 0,
##                                   cells_per_row * cell_width,
##                                   cells_per_column * cell_height)
##    assert len(cells)== cells_per_row * cells_per_column
##    non_empties = set(e for e in cells if e.cell is not None)
##    print(non_empties)
##    # remember rows begin counting from bottom due to openGL origin
##    assert ( set( (e.i, e.j) for e in non_empties ) ==
##             {(2, 0), (2,1), (2, 2), (2, 4), (2, 5) } )
    

def pytest_generate_tests(metafunc):
    # called once per each test function
    for funcargs in metafunc.cls.params[metafunc.function.__name__]:
        # schedule a new test function run with applied **funcargs
        metafunc.addcall(funcargs=funcargs)
 
##class TestClass():
##    params = {
##        'test_equals': [dict(a=1, b=2), dict(a=3, b=3), dict(a=5, b=4)],
##        'test_zerodivision': [dict(a=1, b=0), dict(a=3, b=2)],
##    }
## 
##    def test_equals(self, a, b):
##        assert a == b
## 
##    def test_zerodivision(self, a, b):
##        py.test.raises(ZeroDivisionError, "a/b")
##
##class TestClass2():
##    params = {
##        "test_concatenation": [dict(r='a', s='b', res='ab'),
##                               dict(r='aa', s='bb', res='aabb')]
##        }
##
##    def test_concatenation(self, r, s, res):
##        assert r+s+'z' == res

scenario = [ d for d in aux.case_generator(aux.first_expansion(maps_cache, aux.common_base_cases))]

class TestClass():
    params = {
        'test_no_stuck': scenario,
        }

    def test_no_stuck(self, generic_id, tilemap, start_rect, dx, dy, expect_dxdy):
        collider = RectMapCollider()
        new = start_rect.copy()
        new.x += dx
        new.y += dy
        new_dx, new_dy = collider.collide_map(tilemap, start_rect, new, dx, dy)
        assert new.position == (start_rect.x + expect_dxdy[0],
                                start_rect.y + expect_dxdy[1])
        # uncomment if changed behavior in RectMapCollider 
        assert (new_dx, new_dy) == expect_dxdy

