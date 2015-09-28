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

# to run as a script for visualization DONT set cocos_utest in the env
# to run as a unit test SET cocos_utest in the env
import os
TEST_RUN = ('cocos_utest' in os.environ)

if TEST_RUN:
    # set the desired pyglet mockup
    import sys
    sys.path.insert(0,'pyglet_mockup1')
    import pyglet
    assert pyglet.mock_level == 1
else:
    import pyglet
    
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
from cocos.sprite import Sprite

def string_to_RectMap(s, cell_width, cell_height, RectMap_cls, tile_filled):
    cells_per_row = 5
    cells_per_column = 6
    properties = {'top': True, 'right': True, 'left': True, 'bottom': True}
    tile_empty = None
    

    cells = [[None]*cells_per_column for r in range(cells_per_row)]
    s = s.replace(' ', '')
    assert len(s) == cells_per_column * cells_per_row
    for k, c in enumerate(s):
        column = k % cells_per_row
        row = k // cells_per_row
        # cellmap uses origin at bottom.left, so reverse the rows 
        i = column
        j = (cells_per_column -1) - row
        
        if c == 'o':
            cell = RectCell(i, j, cell_width, cell_height, properties, tile_empty)
        elif c == 'x':
            cell = RectCell(i, j, cell_width, cell_height, properties, tile_filled)
        cells[i][j] = cell

    rect_map = RectMap_cls(42, cell_width, cell_height, cells)
    return rect_map    


def align_corner(rect, reference, corner):
    """ corner in ['topleft', 'topright', 'bottomleft', 'bottomright']"""
    setattr(rect, corner, getattr(reference, corner))        


mapstrings = {
    'empty':              ( "o o o o o" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o o o" ),
    
    'horizontal_no_hole': ( "o o o o o" +
                            "o o o o o" +
                            "x x x x x" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o o o" ),

    'horizontal_w_hole':  ( "o o o o o" +
                            "o o o o o" +
                            "x x o x x" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o o o" ),

    'vertical_no_hole':   ( "o o x o o" +
                            "o o x o o" +
                            "o o x o o" +
                            "o o x o o" +
                            "o o x o o" +
                            "o o x o o" ),

    'vertical_w_hole':    ( "o o x o o" +
                            "o o x o o" +
                            "o o o o o" +
                            "o o x o o" +
                            "o o x o o" +
                            "o o x o o" ),

    'diagonal_gap_1':     ( "o o o o o" +
                            "o o o o o" +
                            "o x o o o" +
                            "o o o x o" +
                            "o o o o o" +
                            "o o o o o" ),

    'diagonal_gap_2v':    ( "o o o o o" +
                            "o o o o o" +
                            "x o o o o" +
                            "o o o x o" +
                            "o o o o o" +
                            "o o o o o" ),

    'diagonal_gap_2h':    ( "o o o o o" +
                            "o o o o o" +
                            "o x o o o" +
                            "o o o o o" +
                            "o o o o o" +
                            "o o o x o" ),
    }

# concrete dx, dy values for push styles, two variants on each style to test
# with potential displacement greater on x than y and the reverse case
dxdy_by_push_style = {
    # name: [(dx, dy), (other_dx, other_dy)]
    'up_left': [(-2, 3), (-3, 2)],
    'up_right': [(2, 3), (3, 2)],
    'down_left': [(-2, -3), (-3, -2)],
    'down_right': [(2, -3), (3, -2)]
    }

combo_sizes = [
    # (cell_width, cell_height, actor_width, actor_height)
    ( 4, 3, 2*4, 2*3),
##    ( 4, 3, 2*4-1, 2*3-1),
##    ( 4, 3, 4, 3), # will need to change / exclude some hole cases
    ]

maps_cache = {}
def generate_maps(RectMap_cls, tile_filed):
    global mapstrings, maps_cache
    cell_sizes = ( (w, h) for w, h, _, _ in combo_sizes) 
    for w, h in cell_sizes:
        for s in mapstrings:
            maps_cache[(s, w, h)] = string_to_RectMap(mapstrings[s], w, h,
                                                      RectMap_cls, tile_filled)
if TEST_RUN:
    generate_maps(RectMap, '-')

# generic test cases description
# mapname: a name in mapstrings
# push_style: a name in dxdy_by_push_style
# cell_start: a (i,j) cell location in the map that generically determines the
#             actor start position. Remember i counts from below
# delta_start: a signed unit vector with the direction the actor should move
#              after the collision with tiles are accounted
common_base_cases = [
    # mapname, push_style, cell_start, delta_start
    # horizontal wall, pushing from below
#    ('empty', 'up_left', (2, 3), (-1, 0)),
#    ('horizontal_no_hole', 'up_left', (3, 2), (-1, 0)),
#    ('horizontal_no_hole', 'up_right', (1, 2), (1, 0)),
#    ('horizontal_w_hole', 'up_left', (3, 2), (-1, 0)),
#    ('horizontal_w_hole', 'up_right', (1, 2), (1, 0)),

    # horizontal wall, pushing from above
#    ('horizontal_no_hole', 'down_left', (3, 4), (-1, 0)),
#    ('horizontal_no_hole', 'down_right', (1, 4), (1, 0)),
#    ('horizontal_w_hole', 'down_left', (3, 4), (-1, 0)),
#    ('horizontal_w_hole', 'down_right', (1, 4), (1, 0)),

##    # vertical wall, pushing toward left
#    ('vertical_no_hole', 'up_left', (3, 2), (0, 1)),
#    ('vertical_no_hole', 'down_left', (3, 4), (0, -1)),
#    ('vertical_w_hole', 'up_left', (3, 2), (0, 1)),
#    ('vertical_w_hole', 'down_left', (3, 4), (0, -1)),

##    # vertical wall, pushing toward right
#    ('vertical_no_hole', 'up_right', (1, 2), (0, 1)),
#    ('vertical_no_hole', 'down_right', (1, 4), (0, -1)),
#    ('vertical_w_hole', 'up_right', (1, 2), (0, 1)),
#    ('vertical_w_hole', 'down_right', (1, 4), (0, -1)),

##    # diagonal tricky cases for player size 2x cell size
#    ('diagonal_gap_2v', 'up_right', (2, 2), (0, 1)),
#    ('diagonal_gap_2v', 'down_left', (1, 3), (0, -1)),
    ('diagonal_gap_2h', 'up_right', (1, 2), (1, 0)),
    ('diagonal_gap_2h', 'down_left', (3, 1), (-1, 0)),
    ]
    

def case_generator(first_expansion_generator):
    for e in first_expansion_generator:
        (generic_id, tilemap, base_rect_start, expect_dxdy,
         dx, dy, delta_start, sizes) = e
        
        # each base_rect generates cases by offseting with 1..cell_dim
        # in the direction of delta_start
        cell_width, cell_height, actor_width, actor_height = sizes
        x0, y0 = base_rect_start.position
        max_start_displacement = max(abs(cell_height * delta_start[0]),
                                     abs(cell_width * delta_start[1]))
                                         
        for k in range(0, max_start_displacement):
            start_rect = Rect(x0 + delta_start[0] * k, y0 + delta_start[1] * k,
                              actor_width, actor_height)
            # py.test expects a dict with test params
            d = {'generic_id': generic_id,
                 'tilemap': tilemap,
                 'start_rect': start_rect,
                 'dx': dx,
                 'dy': dy,
                 'expect_dxdy': expect_dxdy
                 }
            yield d


def first_expansion(generic_cases):
    """
    expands each generic case into a number of concrete cases

    each concrete case is defined by
        tilemap, start_rect, dx, dy, expected_end_rect
    """
    global maps_cache, combo_sizes
    for sizes in combo_sizes:
        for case in generic_cases:
            generic_id = str(case)
            mapname, push_style, cell_start, delta_start = case
            tilemap = maps_cache[(mapname, sizes[0], sizes[1])]
            for dx, dy in dxdy_by_push_style[push_style]:
                base_rect_start, expect_dxdy = calc_base_rect_and_expect_dxdy(
                                        dx, dy, cell_start, delta_start, sizes)
                yield (generic_id, tilemap, base_rect_start, expect_dxdy,
                       dx, dy, delta_start, sizes)
 

def calc_base_rect_and_expect_dxdy(dx, dy, cell_start, delta_start, sizes):
    # sanity 
    assert (abs(delta_start[0]), abs(delta_start[1])) in ((0, 1), (1, 0))
    assert dx != 0 and dy != 0
    print("in calc_")
    # calc in which corner want to align cell_start_rect and player_rect
    if delta_start[0] == 0:
        # moving vertical
        first = 'top' if delta_start[1] == 1 else 'bottom'
        second = 'left' if dx < 0 else 'right'
        expect_dxdy = (0, dy)
    else:
        # moving horizontal
        second = 'left' if delta_start[0] == -1 else 'right' 
        first = 'top' if dy > 0 else 'bottom'
        expect_dxdy = (dx, 0)

    # build base_rect_start
    cell_width, cell_height, actor_width, actor_height = sizes
    cell_start_rect = Rect(cell_start[0]*cell_width, cell_start[1]*cell_height,
                           cell_width, cell_height)
    print("start:", cell_start_rect)
    base_rect_start = Rect(0, 0, actor_width, actor_height)
    align_corner(base_rect_start, cell_start_rect, first + second)
    print("end:", cell_start_rect)

    return base_rect_start, expect_dxdy
 

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
    

##def pytest_generate_tests(metafunc):
##    # called once per each test function
##    for funcargs in metafunc.cls.params[metafunc.function.__name__]:
##        # schedule a new test function run with applied **funcargs
##        metafunc.addcall(funcargs=funcargs)
## 
####class TestClass():
####    params = {
####        'test_equals': [dict(a=1, b=2), dict(a=3, b=3), dict(a=5, b=4)],
####        'test_zerodivision': [dict(a=1, b=0), dict(a=3, b=2)],
####    }
#### 
####    def test_equals(self, a, b):
####        assert a == b
#### 
####    def test_zerodivision(self, a, b):
####        py.test.raises(ZeroDivisionError, "a/b")
####
####class TestClass2():
####    params = {
####        "test_concatenation": [dict(r='a', s='b', res='ab'),
####                               dict(r='aa', s='bb', res='aabb')]
####        }
####
####    def test_concatenation(self, r, s, res):
####        assert r+s+'z' == res
##
##class TestClass():
##    params = {
##        'test_no_stuck': [ d for d in case_generator(first_expansion(common_base_cases))]
##        }
##    def test_no_stuck(self, generic_id, tilemap, start_rect, dx, dy, expect_dxdy):
##        collider = RectMapCollider()
##        new = start_rect.copy()
##        new.x += dx
##        new.y += dy
##        new_dx, new_dy = collider.collide_map(tilemap, start_rect, new, dy, dx)
##        assert new.position == (start_rect.x + expect_dxdy[0],
##                                start_rect.y + expect_dxdy[1])
##        # uncomment if changed behavior in RectMapCollider 
##        # assert new_dx, new_dy == expect_dxdy

if __name__ == "__main__":
    if TEST_RUN:
        print("To run as visualizer delete the env var cocos_utest")
    else:    
        from cocos.director import director
        from cocos.layer import Layer, ColorLayer, ScrollingManager, ScrollableLayer
        from cocos.tiles import RectMapLayer, Tile
        from pyglet.window import key as pkey
        from cocos.text import Label
        class Model(object):
            """remember to set .scroller before allowing to recive .change calls"""
            def __init__(self, cases):
                self.scroller = None
                self.cases = cases
                self.current_tilemap = None
                self.iCase = None
                self.view_start = Sprite('frame8x6.png', color=(0,255,0), anchor=(0,0))
                self.view_new = Sprite('frame8x6.png', color=(255,0,0), anchor=(0,0))
                self.view_expected = Sprite('frame8x6.png', color=(0,0,255), anchor=(0,0))
                self.label = None

            def change(self, delta):
                
                if self.current_tilemap is not None:
                    self.current_tilemap.remove(self.view_start)
                    self.current_tilemap.remove(self.view_new)
                    self.current_tilemap.remove(self.view_expected)
                    self.scroller.remove(self.current_tilemap)
                    print("num active tilemaps:", len(self.scroller.children))
                    self.iCase = (self.iCase + delta) % len(self.cases)
                else:
                    self.iCase = 0
                case = self.cases[self.iCase]
                generic_id = case['generic_id']
                tilemap = case['tilemap']
                start_rect = case['start_rect']
                dx = case['dx']
                dy = case['dy']
                expect_dxdy = case['expect_dxdy']

                s = "dxdy: %s, %s ep_dxdy: %s" % (dx, dy, expect_dxdy)
                self.label.element.text = s
  
                self.current_tilemap = tilemap

                # calc as in test_no_stuck
                collider = RectMapCollider()
                new = start_rect.copy()
                new.x += dx
                new.y += dy
                new_dx, new_dy = collider.collide_map(tilemap, start_rect, new, dy, dx)
                expected = start_rect.copy()
                expected.position = (expected.x + expect_dxdy[0],
                                     expected.y + expect_dxdy[1])

                # update the view
                self.scroller.add(tilemap)
                self.view_start.position = start_rect.position
                self.view_new.position = new.position
                self.view_expected.position = expected.position
                tilemap.add(self.view_start, z=1)
                tilemap.add(self.view_new, z=2)
                tilemap.add(self.view_expected, z=3)
                tilemap.add(self.label, z=4)
                
                

        class ControllerLayer(Layer):
            is_event_handler = True
            def on_key_press(self, key, modifier):
                if key == pkey.UP:
                    # next case
                    self.model.change(1)
                elif key == pkey.DOWN:
                    # prev case
                    self.model.change(-1)

        director.init()
        tile_filled = Tile('z', {}, pyglet.image.load('white4x3.png'))
        generate_maps(RectMapLayer, tile_filled)

        cases = [ d for d in case_generator(first_expansion(common_base_cases))]
        model = Model(cases)
        scene = cocos.scene.Scene()
        label = Label("-----------------",
                           anchor_x='center', anchor_y='center',
                           color=(255, 255, 255, 160))
        label.position = 320, 20
        scene.add(label, z=10)
        model.label = label

        scroller = ScrollingManager()
        model.scroller = scroller
        scroller.scale = 8.0
        scene.add(scroller, z=1)
        controller = ControllerLayer()
        controller.model = model
        scene.add(controller)
        director.run(scene)
