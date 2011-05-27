"""
Interactive test for CollisionManager.objs_touching_point
click over a ball to select
click outside any ball to empty selection
use arrow keys to move selection
"""
import random

import pyglet
from pyglet.window import key
import cocos
from cocos.director import director
import cocos.collision_model as cm
import cocos.euclid as eu

fe = 1.0e-4

consts = {
    "window": {
        "width": 640,
        "height": 480,
        "vsync": True,
        "resizable": False
        },
    "world": {
        "width": 640,
        "height": 480,
        "radius": 16.0,
        "fastness": 160.0,
        "bindings": {
            key.LEFT:'left',
            key.RIGHT:'right',
            key.UP:'up',
            key.DOWN:'down',            
            }
        },
    }

class Actor(cocos.sprite.Sprite):
    colors = [(255, 255, 255), (0, 80, 0) ] 
    def __init__(self):
        super(Actor, self).__init__('ball32.png')
        self._selected = True
        radius = self.image.width / 2.0
        assert abs(radius-16.0)<fe
        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), radius)
#        self.cshape = cm.AARectShape(eu.Vector2(0.0, 0.0), radius, radius)

    def update_position(self, new_position):
        self.position = new_position
        self.cshape.center = new_position

    def set_selected(self, value):
        self._set_selected = value
        self.color = Actor.colors[1 if value else 0]

class TestLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, bindings=None, width=None, height=None, radius=None,
                 fastness=None):
        super(TestLayer, self).__init__()

        self.bindings = bindings
        buttons = {}
        for k in bindings:
            buttons[bindings[k]] = 0
        self.buttons = buttons

##        self.collman = cm.CollisionManagerBruteForce()
        self.collman = cm.CollisionManagerGrid(-radius, width+radius, -radius, height+radius, 1.25*radius, 1.25*radius)
        self.batch = cocos.batch.BatchNode()
        self.add(self.batch)
        self.actors = []
        for i in xrange(10):
            x = random.uniform(0.0, width)
            y = random.uniform(0.0, height)
            actor = Actor()
            actor.update_position(eu.Vector2(x, y))
            self.batch.add(actor)
            self.actors.append(actor)
            self.collman.add(actor)

        self.radius = radius
        self.fastness = fastness
        self.selection = set()
        self.schedule(self.update)

    def update(self, dt):
        if len(self.selection)==0:
            return

        # calc dpos
        mx = self.buttons['right'] - self.buttons['left'] 
        my = self.buttons['up'] - self.buttons['down']
        if mx==0 and my==0:
            return
        
        fastness = self.fastness
        if mx!=0 and my != 0:
            fastness *= 0.707106 # 1/sqrt(2)
        dpos = eu.Vector2(dt*mx*fastness, dt*my*fastness)

        # apply dpos to all selected actors
        for actor in self.selection:
            new_position = actor.cshape.center + dpos
            actor.update_position(new_position)

        # we need an updated collman only when handling on_mouse_press,
        # so we only update collman there

    def on_key_press(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False

    def on_mouse_press(self, x, y, buttons, modifiers):
        # update collman
        self.collman.clear()
        for actor in self.actors:
            self.collman.add(actor)

        # reset selected flag for actors in old selection
        for actor in self.selection:
            actor.set_selected(False)

        # calc selection using collman
        self.selection.clear()
        self.selection = self.collman.objs_touching_point(x, y)

        # set selected flag for actors in selection
        for actor in self.selection:
            actor.set_selected(True)

print """
Interactive test for CollisionManager.objs_touching_point
click over a ball to select
click outside any ball to empty selection
use arrow keys to move selection
"""

director.init(**consts["window"])
scene = cocos.scene.Scene()
scene.add(TestLayer(**consts["world"]))
director.run(scene)
