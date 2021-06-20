# -*- coding: utf-8 -*-
""" Tests that an actor using RectMapCollider or RectMapWithPropsCollider,
 with on_bump_handler==on_bump_slide does not get stuck when moving along a
 wall while at the same time pushing against the wall.
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
          - for each parameterizable value , a set of values of
            interest is defined
          - code will walk the (base cases, params values) generating the
            concrete cases to validate
          - as an implementation detail, maps will be cached

    - params desired to change
        map: the basic form and orientation in the situation
        cell_size, actor_size: mostly
           actor side z <=> cell side z
           actor side odd or even (because .center assigns; division_errors?)
        push style: dx, dy
        actor start position: move the start position along the wall to cover
          all int alignements with the grid, ie do offsets 1..cell_width if
          free movement axis is x, ...

Companion to this file, test_RectMapCollider__no_stuck.py, is
viewer_RectMapCollider__no_stuck.py, which produces a view for the same cases.
This allows visual inspection of test cases and test results.
Changes in any of those files must be in sync so that both scripts remain operational. 
"""
from __future__ import division, print_function, unicode_literals

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
import pytest

import cocos
import cocos.layer
from cocos.tiles import RectMap, RectCell
from cocos.mapcolliders import RectMapCollider, RectMapWithPropsCollider
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
    

##    A scenario received in the 'scenaries = ...' line is sort-of of a case description:
##    misses the param 'cls' (class to test) and includes part of a case descriptive name in
##    'generic'. That was fine for test code writen for pytest < 4.0, here it will be adapted to
##    the new parametrize style.
##    this was the scenario in it's old form
##    d = {
##        'generic_id': generic_id,
##        'tilemap': tilemap,
##        'start_rect': start_rect,
##        'dx': dx,
##        'dy': dy,
##        'expect_dxdy': expect_dxdy
##    }
##    To transform from the old scenario to the new case description we need to
##            - add 'cls' param
##            - extract from d 'generic_id'; combine with 'cls' to form the sufix for parametrized test
##            - transform d to tuple, with known and consistent order
##            - put the sufixces in one list, the tuple params in other

def scenario_to_test_sufix_and_tuple_params(d):
    test_sufix = d["cls"].__name__ + "_" + d["generic_id"]
    params = (d["cls"], d['tilemap'],  d['start_rect'], d['dx'], d['dy'], d['expect_dxdy'])
    return test_sufix, params
    
def params_for_test_no_stuck():
    param_names = ['cls', 'tilemap', 'start_rect', 'dx', 'dy', 'expect_dxdy']
    scenaries = [ d for d in aux.case_generator(aux.first_expansion(maps_cache, aux.common_base_cases))]
    sufixes_parametrized_tests = []
    cases = []
    for cls in [RectMapCollider,  RectMapWithPropsCollider]:
        for d in scenaries:
            d['cls'] = cls
            test_sufix, params = scenario_to_test_sufix_and_tuple_params(d)
            sufixes_parametrized_tests.append(test_sufix)
            cases.append(params)
    return (param_names, cases, False,  sufixes_parametrized_tests)

# (argnames, argvalues, indirect=False, ids=None, scope=None)
@pytest.mark.parametrize(*params_for_test_no_stuck())
def test_no_stuck(cls,  tilemap, start_rect, dx, dy, expect_dxdy):
    collider = cls()
    collider.on_bump_handler = collider.on_bump_slide
    new = start_rect.copy()
    new.x += dx
    new.y += dy
    collider.collide_map(tilemap, start_rect, new, 0, 0)
    assert new.position == (start_rect.x + expect_dxdy[0],
                            start_rect.y + expect_dxdy[1])

