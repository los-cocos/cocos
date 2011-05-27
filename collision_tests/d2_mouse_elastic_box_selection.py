"""
Interactive test for CollisionManager.objs_into_box
Implements click selection plus elastic box selection
Clicking anywhere will select the ball(s) under the mouse cursor
Drag a rectangle to select balls fully into rectangle
Click outside any ball to unselect 
Use arrow keys to move selection
"""
import random

import pyglet
from pyglet.window import key
from pyglet.gl import *

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
#        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), radius)
        self.cshape = cm.AARectShape(eu.Vector2(0.0, 0.0), radius, radius)

    def update_position(self, new_position):
        self.position = new_position
        self.cshape.center = new_position

    def set_selected(self, value):
        self._set_selected = value
        self.color = Actor.colors[1 if value else 0]

class VertexBag2(cocos.cocosnode.CocosNode):
    """ WARN: it is not a real CocosNode, it pays no attention to position,
        rotation, etc. It only draws the quad depicted by the vertexes.
        In other worlds, a nasty hack that gets the work done and you
        should not take as example"""
    def __init__(self):
        super(VertexBag2, self).__init__()
        self.color3 = (255,0,0)
        self.vertexes = [ (0.0, 0.0) ] * 4
        self.visible = False

    def draw(self):
        if not self.visible:
            return
        glLineWidth(2) #deprecated
        glColor3ub(*self.color3)
        glBegin(GL_LINE_STRIP)
        for v in self.vertexes:
            glVertex2f(*v)
        glVertex2f(*self.vertexes[0])
        glEnd()

    def set_vertexes_from_minmax(self, minx, maxx, miny, maxy):
        self.vertexes = [ (minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)] 

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
            self.batch.add(actor, z=i)
            self.actors.append(actor)
            self.collman.add(actor)

        self.elastic_box = VertexBag2()
        self.add(self.elastic_box, z=len(self.actors))
        self.dragging = False
        self.radius = radius
        self.fastness = fastness
        self.selection = set()
        self.schedule(self.update)

    def update(self, dt):
        if len(self.selection)==0 or self.dragging:
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

        # we need an updated collman only when mpuse drag begins,
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

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.dragging = False
        self.elastic_box.visible = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.dragging:
            self.begin_drag(x, y)
            return

        # reset selected flag for actors in old selection
        for actor in self.selection:
            actor.set_selected(False)

        # calc selection using collman
        self.selection.clear()
        minx = min(self.drag_corner[0], x)
        maxx = max(self.drag_corner[0], x)
        miny = min(self.drag_corner[1], y)
        maxy = max(self.drag_corner[1], y)
        self.elastic_box.set_vertexes_from_minmax(minx, maxx, miny, maxy)
        self.selection = self.collman.objs_into_box(minx, maxx, miny, maxy)

        # set selected flag for actors in selection
        for actor in self.selection:
            actor.set_selected(True)


    def begin_drag(self, x, y):
        self.dragging = True
        self.drag_corner = (x, y)
        self.elastic_box.visible = True
        self.elastic_box.set_vertexes_from_minmax(x, x, y, y)
        
        # reset selected flag for actors in old selection
        for actor in self.selection:
            actor.set_selected(False)

        #empty selection
        self.selection.clear()


print """
Interactive test for CollisionManager.objs_into_box
Implements click selection plus elastic box selection
Clicking anywhere will select the ball(s) under the mouse cursor
Drag a rectangle to select balls fully into rectangle
Click outside any ball to unselect 
Use arrow keys to move selection
"""

director.init(**consts["window"])
scene = cocos.scene.Scene()
scene.add(TestLayer(**consts["world"]))
director.run(scene)
