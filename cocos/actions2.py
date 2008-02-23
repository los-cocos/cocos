#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
#
# Based on actions.py from Grossini's Hell
#

import time, random
import copy

from euclid import *

from pyglet import image
from pyglet.gl import *


__all__ = [ 'ActionSprite',                     # base class
            'Goto','Move',                      # movement actions
            'Rotate','Scale',                   # object modification
            'Spawn', 'Sequence',                # queueing actions
            ]

class ActionSprite( object ):
    def __init__( self, img ):
        self.sprite = image.load( img )
        self.actions = []
        self.to_remove = []
        self.translate = Point3(0,0,0)
        self.scale = 1.0
        self.angle = 0.0

    def do( self, action ):
        a = copy.deepcopy( action )
        a.target = self
        a._start()
        self.actions.append( a )


    def done(self, what):
        self.to_remove.append( what )
        
    def step(self, dt):
        for action in self.actions:
            action._step(dt)
            if action.done():
                self.done( action )
                
        for x in self.to_remove:
            self.actions.remove( x )
        self.to_remove = []

        self.draw()

    def draw( self ):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.translate.x, self.translate.y, self.translate.z )

        # comparison is cheaper than a matrix multiplication
        if self.angle != 0.0:
            glRotatef(self.angle, 0, 0, 1)
        if self.scale != 1.0:
            glScalef(self.scale, self.scale, 1)

        self.sprite.blit( -self.sprite.width / 2, - self.sprite.height / 2 )
        glPopMatrix()

    def place( self, coords ):
        self.translate = Point3( *coords )


class Action(object):
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.target = None
        
    def _start(self):
        self.runtime = 0
        self.start()
        
    def _step(self, dt):
        self.step(dt)
        self.runtime += dt
        
    def init(self):
        pass

    def done(self):
        return True
            
    def start(self):
        pass

    def step(self, dt):
        pass

    def __add__(self, action):
        return Sequence(self, action)

    def __or__(self, action):
        return Spawn(self, action)

class Rotate( Action ):
    def init(self, angle, duration=5):
        self.angle = angle
        self.duration = duration

    def start( self ):       
        self.start_angle = self.target.angle

    def step(self, dt):
        self.target.angle = (self.start_angle +
                    self.angle * (
                        min(1,float(self.runtime)/self.duration)
                    )) % 360 

    def done(self):
        return (self.runtime > self.duration)


class Scale(Action):
    def init(self, end, duration=5):
        self.end_scale = end
        self.duration = duration

    def start( self ):
        self.start_scale = self.target.scale

    def step(self, dt):
        delta = self.end_scale-self.start_scale

        self.target.scale = (self.start_scale +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))
        
    def done(self):
        return (self.runtime > self.duration)

class Goto( Action ):
    def init(self, end, duration=5):
        self.end_position = Point3( *end )
        self.duration = duration

    def start( self ):
        self.start_position = self.target.translate


    def step(self,dt):
        delta = self.end_position-self.start_position
        self.target.translate = (self.start_position +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))

    def done(self):
        return (self.runtime > self.duration)


class Move( Goto ):
    def start( self ):
        self.start_position = self.target.translate
        self.end_position = self.start_position + self.end_position


class Spawn(Action):
    """Spawn a  new action immediately"""
    def init(self, *actions):
        self.actions = actions

    def done(self):
        return True
        
    def start(self):
        for a in self.actions:
            self.target.do( a )


class Sequence(Action):
    """Queues 1 action after the other. One the 1st action finishes, then the next one will start"""
    def init(self, *actions):
        self.actions = actions
        self.count = 0
        
    def instantiate(self):
        self.current = self.actions[self.count]
        self.current.target = self.target
        self.current._start()
    
    def start(self):
        self.instantiate()
        
    def done(self):
        return ( self.count >= len(self.actions) )
        
    def step(self, dt):
        self.current._step(dt)
        if self.current.done():
            self.count += 1
            if not self.done():
                self.instantiate()            
