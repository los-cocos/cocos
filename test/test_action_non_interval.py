from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "f 10 0.033, s, f 20 0.033, s, f 30 0.033, s, f 30 0.033, s, f 30 0.033, s, q"
tags = "Action"

import random
import math
import cocos
from cocos.director import director
from cocos.sprite import Sprite
import cocos.actions as ac
import pyglet
from pyglet.gl import *
## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()

fastness_green = 60.0
fastness_bullet = 80.0

class ProbeQuad(cocos.cocosnode.CocosNode):
    def __init__(self, r, color4):
        super(ProbeQuad,self).__init__()
        self.color4 = color4
        self.vertexes = [(r,0,0),(0,r,0),(-r,0,0),(0,-r,0)]

    def draw(self):
        glPushMatrix()
        self.transform()
        glBegin(GL_QUADS)
        glColor4ub( *self.color4 )
        for v in self.vertexes:
            glVertex3i(*v)
        glEnd()
        glPopMatrix()

##def random_walk(actor, fastness):
##    width, height = director.get_window_size()
##    x = random.randint(0, width)
##    y = random.randint(0, height)
##    dist = math.hypot(x-actor.position[0], y-actor.position[1])
##    time = dist/(1.0*fastness)
##    move_template = ac.MoveTo((x,y), time)+ac.CallFunc(random_walk, actor, fastness)
##    actor.do(move_template)

class RandomWalk(ac.Action):
    def init(self, fastness):
        self.fastness = fastness

    def start(self):
        self.make_new_leg()

    def make_new_leg(self):
        self._elapsed = 0.0
        x0, y0 = self.target.position
        width, height = director.get_window_size()
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        dx = x1-x0
        dy = y1-y0
        norm = math.hypot(dx, dy)
        try:
            self.t_arrival = norm/(1.0*self.fastness)
        except ZeroDivisionError:
            norm = 1.0
            self.t_arrival = 0.1
        self.dx = dx/norm
        self.dy = dy/norm
        print('dx, dy:',dx, dy)
        self.x0 = x0
        self.y0 = y0

    def step(self, dt):
        self._elapsed += dt
        if self._elapsed > self.t_arrival:
            self.make_new_leg()
        x = self.fastness*self._elapsed*self.dx + self.x0
        y = self.fastness*self._elapsed*self.dy + self.y0
        #print('x,y:', x,y)
        self.target.position = (x,y)


class Chase(ac.Action):
    def init(self, fastness):
        #self.chasee = chasee
        self.fastness = fastness

    def init2(self, chasee, on_bullet_hit):
        self.chasee = chasee
        self.on_bullet_hit = on_bullet_hit

    def step(self, dt):
        if self.chasee is None:
            return
        x0, y0 = self.target.position
        x1, y1 = self.chasee.position
        dx , dy = x1-x0, y1-y0
        mod = math.hypot(dx, dy)
        x = self.fastness*dt*(x1-x0)/mod+x0
        y = self.fastness*dt*(y1-y0)/mod+y0
        self.target.position = (x,y)
        if math.hypot(x1-x, y1-y)<5:
            self._done = True

    def stop(self):
        self.chasee.do(ac.RotateBy(360, 1.0))
        self.on_bullet_hit(self.target)

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.green_obj = ProbeQuad(50, (0,255,0,255))
        self.add( self.green_obj  )
        self.green_obj.do(RandomWalk(fastness_green))
        self.schedule_interval(self.spawn_bullet, 1.0)

    def spawn_bullet(self, dt):
        bullet = ProbeQuad(5, (255, 0, 0, 255))
        bullet.position = (0,0)
        bullet.color = (233, 70, 0)
        chase_worker = bullet.do(Chase(fastness_bullet))
        # workaround deepcopy can't handle a bound method nor a cocosnode
        chase_worker.init2(self.green_obj, self.on_bullet_hit)
        self.add(bullet)

    def on_bullet_hit(self, bullet):
        self.remove(bullet)

description = """
Example actions with duration not known at it start time ( no IntervalAction,
no InstantAction).
It also shows one way of passing non deepcopy-able parameters, like a cocosnode,
to an action.
It should be seen:
    A green quad moving in rectilinear traits.
    A bunch of red dots spawning from left-bottom corner and moving towards
    the green quad.
    Green quad spining when a red dot reach the center of green quad.
"""

def main():
    print(description)
    director.init()
    a = cocos.cocosnode.CocosNode()
    class A(object):
        def __init__(self, x):
            self.x = x
    z = A(a)
    import copy
    b = copy.deepcopy(a)
    print('a:', a)
    print('b:', b)
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
