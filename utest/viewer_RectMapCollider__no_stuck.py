# -*- coding: utf-8 -*-
"""
Visualization for test cases used by test_RectMapCollider__no_stuck.py

Use arrows UP and DOWN to change the case, ESC to quit.

Solid white are filled, solid cells in the map

Rectangular frames depicts rectangles associated to an actor:
    green the starting actor position
    blue the expected (correct) actor position after a step is done 
    red is the real position observed after a step is done

In cases with no fail, red and blue overlaps, so only green and violet are seen

In fail cases when the actor is stuck at the starting position, red and green
overlaps, so only blue and brown are seen

In fail cases with a stuck not in the startting position, some red sides are
seen within the big rect depicted by the union of green and blue

Some cases show red outside the green + blue rect: that is a missing in the
collision detection, not a stuck
"""

from __future__ import division, print_function, unicode_literals

# to run as a script for visualization DONT set cocos_utest in the env
import os
assert 'cocos_utest' not in os.environ
    
# will use the cocos in the same checkout, except if you move this file.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cocos
import cocos.layer
from cocos.tiles import RectMap, RectCell, RectMapCollider 
from cocos.rect import Rect
from cocos.sprite import Sprite
from cocos.director import director
from cocos.layer import Layer, ColorLayer, ScrollingManager, ScrollableLayer
from cocos.tiles import RectMapLayer, Tile
import pyglet
from pyglet.window import key as pkey
from cocos.text import Label

import aux_RectMapCollider__no_stuck as aux
# set the cocos classes needed in aux before calling any function there
aux.RectMap_cls = RectMapLayer
aux.RectCell = RectCell
aux.Rect = Rect


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
            # ? unrelated to collision, but seen some strange:
            # if not removing the sprites opacity intensifies, like if the
            # associated triangles were not removed
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
        new_dx, new_dy = collider.collide_map(tilemap, start_rect, new, dx, dy)
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

print(__doc__)
director.init()
tile_filled = Tile('z', {}, pyglet.image.load('white4x3.png'))
maps_cache = aux.generate_maps(tile_filled)

cases = [ d for d in aux.case_generator(aux.first_expansion(maps_cache, aux.common_base_cases))]
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
