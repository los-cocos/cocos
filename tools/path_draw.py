#
# framework libs
#

from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet.window import mouse, key
from pyglet.gl import *
from pyglet import font

from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.path import Path, Bezier

from primitives import Circle, Line
import threading, string
import time, cmd, math,random


def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
    
class PathView:
    def __init__(self, name, path):
        self.name = name
        self.a = Point(*path.a)
        self.b = Point(*path.b)+self.a
        self.ac = Point(*path.ac)+self.a
        self.bc = Point(*path.bc)+self.a
        
    def render(self):
        c = Circle(
            self.a[0],self.a[1],
            width=10,color=(0.,.9,0.,1.)
            )
        c.render()
        c = Circle(
            self.ac[0],self.ac[1],
            width=10,color=(0.,.9,0.5,1.)
            )
        c.render()
        l = Line(self.a,self.ac,stroke=2,color=(0,1.,1.,1.))
        l.render()
        
        c = Circle(
            self.b[0],self.b[1],
            width=10,color=(0.,.9,1.,1.)
            )
        c.render()
        c = Circle(
            self.bc[0],self.bc[1],
            width=10,color=(0.,.9,1.,0.5)
            )
        c.render()
        l = Line(self.b,self.bc,stroke=2,color=(0,1.,1.,1.))
        l.render()
        
        steps=100.0
        bz = self.bezier()
        last = self.a
        for i in range(int(steps)):
            t = (i+1) / steps
            val = bz.at( t )
            val = val[0] + self.a.x, val[1] + self.a.y
            
            glBegin(GL_LINES);
            glVertex2f(last[0], last[1]); 
            glVertex2f(val[0], val[1]); 
            glEnd( );

            last = val
            
    def get_nearest(self, x, y):
        mind = 10000
        near = self.a
        for p in [self.a, self.b, self.ac, self.bc]:
            if dist(p, (x,y)) < mind:
                mind = dist(p, (x,y))
                near = p
                
        return near
        
    def bezier(self):
        return Bezier( 
                (self.a.x, self.a.y),
                (self.b.x-self.a.x, self.b.y-self.a.y),
                (self.ac.x-self.a.x, self.ac.y-self.a.y),
                (self.bc.x-self.a.x, self.bc.y-self.a.y),

            )
            
    def repr(self):
        return self.bezier().__repr__()
        
class Point:
    def __init__(self, x, y):
        self.set(x, y)
        
    def set(self, x, y):
        self.x = x
        self.y = y
        
    def __getitem__(self, item):
        if item == 0: return self.x
        elif item == 1: return self.y
        raise IndexError("No such attr")

    def __setitem__(self, item, value):
        if item == 0: self.x = value
        elif item == 1: self.y = value
        raise IndexError("No such attr")
    
    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)
    
    
class PathDraw(Layer):
    SWITCH, SHOW, CREATE_A, CREATE_B, DRAG, ANIMATE = range(6)
    
    @property
    def path(self):
        return self.paths[self.pathp]

    def __init__(self, module, filepath):
        Layer.__init__(self)
        self.module = module
        self.filepath = filepath
        self.paths = []
        self.pathp = 0
        self.near = None
        for name in dir(module):
            what = getattr(module, name)
            if isinstance(what, Bezier):
                p = PathView( name, what )
                self.paths.append( p )
        if len(self.paths)==0:
            self.new_path()
        self.state = self.SHOW
        self.stop = False
        self.mouse = Point(0,0)

        self.font = font.load('Arial', 18)
        self.duration = 3
        self.time_warp = 1
        self.number = ""
        
    def save(self):
        text = "from cocos.path import Bezier\n\n"
        for p in self.paths:
            text += p.name + " = "
            text += p.bezier().__repr__()
            text += "\n"
            
        
        f = open(self.filepath, "w")
        f.write( text )
        f.close()
        
    def on_text(self, text):
        if self.state in ( self.SHOW, self.SWITCH ):
            if text in string.digits:
                self.state = self.SWITCH
                self.number += text
        
        
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse.set(x,y)
        if self.state == self.SHOW:
            near = self.path.get_nearest(x,y)
            if dist(near, (x,y)) < 8:
                self.near = near
            else:
                self.near = None
        if self.state == self.DRAG:
            self.near.set(x,y)       
                
    def on_key_press(self, symbol, modifiers):
        if self.state == self.SHOW:
            if symbol == key.S:
                self.save()
            if symbol == key.N:
                self.new_path()
            if symbol == key.A:
                self.state = self.ANIMATE
                self.anim_start = time.time()
            if symbol == key.D:
                if (modifiers & key.LSHIFT or modifiers & key.RSHIFT):
                    self.duration /= 1.1
                else:
                    self.duration *= 1.1
                
            if symbol == key.T:
                if (modifiers & key.LSHIFT or modifiers & key.RSHIFT):
                    self.time_warp /= 1.1
                else:
                    self.time_warp *= 1.1
        elif self.state == self.SWITCH:
            if symbol == key.ENTER:
                try:
                    newp = int(self.number)
                    if newp < len(self.paths):
                        self.pathp = newp
                except ValueError:
                    pass
                self.state = self.SHOW
                self.number = ""
                       
                    
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse.x = x
        self.mouse.y = y
        
        if self.state == self.SHOW:
            if button == mouse.LEFT:
                if self.near:
                    self.state = self.DRAG
                    
        elif self.state == self.DRAG:
            if button == mouse.LEFT:
                self.state = self.SHOW       
        
    def draw(self):
        if self.stop:
            director.scene.end()
            
        if self.state == self.SWITCH:
            text = font.Text(self.font, 'switch to:',color=(0.,0.5,0.5,0.5))
            text.x = 20
            text.y = 300
            text.draw()
            text = font.Text(self.font, self.number ,color=(0.,0.5,0.5,0.5))
            text.x = 20
            text.y = 250
            text.draw()
            
        elif self.state in (self.SHOW, self.DRAG):
            self.path.render()
            if self.near:
                c = Circle(
                    self.near.x,self.near.y,
                    width=15,color=(0.,1.,1.,1.)
                    )
                c.render()
                
        elif self.state == self.ANIMATE:
            dt = time.time() - self.anim_start
            bz = self.path.bezier()
            if dt >= self.duration:
                self.state = self.SHOW
            else:
                x,y = bz.at( (dt / self.duration)**self.time_warp )
                c = Circle(
                        x+self.path.a.x,y+self.path.a.y,
                        width=45,color=(0.,1.,1.,1.)
                        )
                c.render()
                    
                
        text = font.Text(self.font, '[%i,%i] t**%0.2f d=%0.2f n=%d p=%d'%(
                    self.mouse.x, self.mouse.y,
                    self.time_warp,
                    self.duration,
                    len(self.paths), self.pathp
                ),
                color=(0.,0.5,0.5,0.5))
        text.x = 100
        text.y = 20
        text.draw()

                 
    def new_path(self):
        self.paths.append(
            PathView("new"+str(random.randint(1,1000000)),
                     Bezier( (297,297), (13,286), (-192, 272), (89,84) )
                     )
            )
        self.pathp = len(self.paths)-1
        
def usage():
    text = """Usage:
    python %s file_with_paths.py

An example of input file is tools/foo.py
"""
    return text
  
if __name__ == "__main__":
    import imp, sys
    
    if len(sys.argv) < 2:
        print(usage() % sys.argv[0])
        sys.exit()
        
    path = sys.argv[1]
    client = imp.load_source("client", path)
    director.init()
    draw = PathDraw(client, path)
    director.run( Scene( draw ) )
