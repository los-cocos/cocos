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

# DON'T import cocos or pyglet: they will be imported from other modules in
# utest mode for tests and in normal mode for visualization

# this classes should by defined by the importer before calling functions
RectMap_cls = None # RectMap for utest, RectMapLayer for visualization
RectCell = None # cocos.tiles.RectCell
Rect = None # cocos.rect.Rect

def string_to_RectMap(s, cell_width, cell_height, tile_filled):
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
    'horizontal_no_hole': ( "o o o o o"
                            "o o o o o"
                            "x x x x x"
                            "o o o o o"
                            "o o o o o"
                            "o o o o o" ),

    'horizontal_w_hole':  ( "o o o o o"
                            "o o o o o"
                            "x x o x x"
                            "o o o o o"
                            "o o o o o"
                            "o o o o o" ),

    'vertical_no_hole':   ( "o o x o o"
                            "o o x o o"
                            "o o x o o"
                            "o o x o o"
                            "o o x o o"
                            "o o x o o" ),

    'vertical_w_hole':    ( "o o x o o"
                            "o o x o o"
                            "o o o o o"
                            "o o x o o"
                            "o o x o o"
                            "o o x o o" ),

    'diagonal_gap_1':     ( "o o o o o"
                            "o o o o o"
                            "o x o o o"
                            "o o o x o"
                            "o o o o o"
                            "o o o o o" ),

    'diagonal_gap_2v':    ( "o o o o o"
                            "o o o o o"
                            "x o o o o"
                            "o o o x o"
                            "o o o o o"
                            "o o o o o" ),

    'diagonal_gap_2h':    ( "o o o o o"
                            "o o o o o"
                            "o x o o o"
                            "o o o o o"
                            "o o o o o"
                            "o o o x o" ),
    }

# concrete dx, dy values for push styles, two variants on each style to test
# with potential displacement greater on x than y and the reverse case
dxdy_by_push_style = {
    # name: [(dx, dy), (other_dx, other_dy)]
    'up_left': [(-2, 1), (-1, 2)],
    'up_right': [(2, 1), (1, 2)],
    'down_left': [(-2, -1), (-1, -2)],
    'down_right': [(2, -1), (1, -2)]
    }

combo_sizes = [
    # (cell_width, cell_height, actor_width, actor_height)
    ( 4, 3, 2*4, 2*3),
##    ( 4, 3, 2*4-1, 2*3-1),
##    ( 4, 3, 4, 3), # will need to change / exclude some hole cases
    ]

def generate_maps(tile_filled):
    global mapstrings    
    maps_cache = {}
    cell_sizes = ( (w, h) for w, h, _, _ in combo_sizes) 
    for w, h in cell_sizes:
        for s in mapstrings:
            maps_cache[(s, w, h)] = string_to_RectMap(mapstrings[s], w, h,
                                                      tile_filled)
    return maps_cache

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
    ('horizontal_no_hole', 'up_left', (3, 2), (-1, 0)),
    ('horizontal_no_hole', 'up_right', (1, 2), (1, 0)),
    ('horizontal_w_hole', 'up_left', (3, 2), (-1, 0)),
    ('horizontal_w_hole', 'up_right', (1, 2), (1, 0)),

    # horizontal wall, pushing from above
    ('horizontal_no_hole', 'down_left', (3, 4), (-1, 0)),
    ('horizontal_no_hole', 'down_right', (1, 4), (1, 0)),
    ('horizontal_w_hole', 'down_left', (3, 4), (-1, 0)),
    ('horizontal_w_hole', 'down_right', (1, 4), (1, 0)),

    # vertical wall, pushing toward left
    ('vertical_no_hole', 'up_left', (3, 2), (0, 1)),
    ('vertical_no_hole', 'down_left', (3, 4), (0, -1)),
    ('vertical_w_hole', 'up_left', (3, 2), (0, 1)),
    ('vertical_w_hole', 'down_left', (3, 4), (0, -1)),

    # vertical wall, pushing toward right
    ('vertical_no_hole', 'up_right', (1, 2), (0, 1)),
    ('vertical_no_hole', 'down_right', (1, 4), (0, -1)),
    ('vertical_w_hole', 'up_right', (1, 2), (0, 1)),
    ('vertical_w_hole', 'down_right', (1, 4), (0, -1)),

    # diagonal tricky cases for player size 2x cell size
    ('diagonal_gap_2v', 'up_right', (2, 2), (0, 1)),
    ('diagonal_gap_2v', 'down_left', (1, 3), (0, -1)),
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


def first_expansion(maps_cache, generic_cases):
    """
    expands each generic case into a number of concrete cases

    each concrete case is defined by
        tilemap, start_rect, dx, dy, expected_end_rect
    """
    global combo_sizes
    for sizes in combo_sizes:
        for case in generic_cases:
            generic_id = str(case)
            mapname, push_style, cell_start, delta_start = case
            cell_width = sizes[0]
            cell_height =sizes[1]
            tilemap = maps_cache[(mapname, cell_width, cell_height)]
            for dx, dy in dxdy_by_push_style[push_style]:
                # sanity check, else tunneling across wall, and will show as errors
                assert abs(dx) < cell_width and abs(dy) < cell_height
                base_rect_start, expect_dxdy = calc_base_rect_and_expect_dxdy(
                                        dx, dy, cell_start, delta_start, sizes)
                yield (generic_id, tilemap, base_rect_start, expect_dxdy,
                       dx, dy, delta_start, sizes)
 

def calc_base_rect_and_expect_dxdy(dx, dy, cell_start, delta_start, sizes):
    # sanity 
    assert (abs(delta_start[0]), abs(delta_start[1])) in ((0, 1), (1, 0))
    assert dx != 0 and dy != 0
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
    base_rect_start = Rect(0, 0, actor_width, actor_height)
    align_corner(base_rect_start, cell_start_rect, first + second)

    return base_rect_start, expect_dxdy
 

