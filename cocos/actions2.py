#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
#
# Based on actions.py from Grossini's Hell:
#    http://www.pyweek.org/e/Pywiii/
#
# Based on actions.py from Pygext:
#     http://opioid-interactive.com/~shang/projects/pygext/
#

import random
import copy
import math

from euclid import *

from pyglet import image
from pyglet.gl import *


__all__ = [ 'ActionSprite',                     # Sprite class

            'Action','IntervalAction',          # Action classes

            'Goto','Move','Jump',               # movement actions
            'Rotate','Scale',                   # object modification
            'Spawn', 'Sequence', 'Repeat',      # queueing actions
            'CallFunc','CallFuncS',             # Calls a function
            'Delay', 'RandomDelay',             # Delays

            'ForwardDir','BackwardDir',         # Movement Directions
            'RepeatMode', 'PingPongMode',       # Repeat modes
            ]


class ForwardDir: pass 
class BackwardDir: pass
class PingPongMode: pass
class RepeatMode: pass

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

        # comparison is cheaper than an OpenGL matrix multiplication
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
        self.start_count = 1
        self.runtime = 0
        self.start()
        
    def _restart(self):
        self.start_count +=1
        self.restart()

    def _step(self, dt):
        self.step(dt)
        self.runtime += dt
        
    def init(self):
        pass

    def done(self):
        return True
            
    def start(self):
        pass

    def restart( self ):
        """IntervalAction and other subclasses shall override this method"""
        self._start()

    def step(self, dt):
        pass

    def get_runtime( self ):
        """Returns the runtime. IntervalActions can modify this value."""
        return self.runtime

    def __add__(self, action):
        return Sequence(self, action)

    def __or__(self, action):
        return Spawn(self, action)


class IntervalAction( Action ):

    def restart( self ):
        self.runtime=0
        if self.mode == PingPongMode:
            if self.direction == ForwardDir:
                self.direction = BackwardDir
            else:
                self.direction = ForwardDir 
 
    def done(self):
        # It doesn't matter the mode, this is always valid
        return (self.runtime > self.duration)

    def get_runtime( self ):
        if self.direction == ForwardDir:
            return self.runtime
        elif self.direction== BackwardDir:
            return self.duration - self.runtime
        else:
            raise Exception("Unknown Interval Mode: %s" % (str( self.mode) ) )


class Rotate( IntervalAction ):
    def init(self, angle, duration=5, dir=ForwardDir, mode=PingPongMode):
        self.angle = angle
        self.duration = duration
        self.mode = mode
        self.direction = dir

    def start( self ):       
        self.start_angle = self.target.angle

    def step(self, dt):
        self.target.angle = (self.start_angle +
                    self.angle * (
                        min(1,float(self.get_runtime())/self.duration)
                    )) % 360 


class Scale(IntervalAction):
    def init(self, end, duration=5, dir=ForwardDir, mode=PingPongMode):
        self.end_scale = end
        self.duration = duration
        self.mode = mode
        self.direction = dir

    def start( self ):
        self.start_scale = self.target.scale

    def step(self, dt):
        delta = self.end_scale-self.start_scale

        self.target.scale = (self.start_scale +
                    delta * (
                        min(1,float(self.get_runtime() )/self.duration)
                    ))

class Goto( IntervalAction ):
    def init(self, end, duration=5, dir=ForwardDir, mode=PingPongMode):
        self.end_position = Point3( *end )
        self.duration = duration
        self.mode = mode
        self.direction = dir

    def start( self ):
        self.start_position = self.target.translate

    def step(self,dt):
        delta = self.end_position-self.start_position
        self.target.translate = (self.start_position +
                    delta * (
                        min(1,float(self.get_runtime() )/self.duration)
                    ))


class Move( Goto ):
    def init(self, delta, duration=5, dir=ForwardDir, mode=PingPongMode):
        self.delta = Point3( *delta)
        self.duration = duration
        self.mode = mode
        self.direction = dir

    def start( self ):
        self.start_position = self.target.translate
        self.end_position = self.start_position + self.delta


class Jump(IntervalAction):
    def init(self, height=150, width=120, jumps=1, duration=5, dir=ForwardDir, mode=PingPongMode ):
        self.height = height
        self.width = width
        self.duration = duration
        self.jumps = jumps
        self.mode = mode
        self.direction = dir

    def start( self ):
        self.start_position = self.target.translate

    def step(self, dt):
        y = int( self.height * ( math.sin( (self.get_runtime()/self.duration) * math.pi * self.jumps ) ) )
        y = abs(y)

        x = self.width * min(1,float(self.get_runtime())/self.duration)
        self.target.translate = self.start_position + (x,y,0)

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
    def init(self,  *actions, **kwargs ):
        self.actions = actions
        self.direction = ForwardDir
        self.mode = PingPongMode
        if kwargs.has_key('dir'):
            self.direction = kwargs['dir']
        if kwargs.has_key('mode'):
            self.mode = kwargs['mode']


    def restart( self ):
        if self.mode == PingPongMode:
            if self.direction == ForwardDir:
                self.direction = BackwardDir
            else:
                self.direction = ForwardDir
        self.start()


    def instantiate(self):
        index = self.count

        if self.direction == BackwardDir:
            index = len( self.actions ) - index - 1

        self.current = self.actions[index]
        self.current.target = self.target
        if self.start_count == 1:
            self.current._start()
        else:
            self.current._restart()
    
    def start(self):
        self.count = 0
        self.instantiate()
        
    def done(self):
        return ( self.count >= len(self.actions) )
        
    def step(self, dt):
        self.current._step(dt)
        if self.current.done():
            self.count += 1
            if not self.done():
                self.instantiate()            


class Repeat(Action):
    """Repeats an action. It is is similar to Sequence, but it runs the same action every time"""
    def init(self, action, times=-1):
        self.action = action
        self.times = times

    def restart( self ):
        self.start()
        
    def start(self):
        self.count = 0
        self.instantiate()

    def instantiate(self):
        self.action.target = self.target
        if self.start_count == 1 and self.count == 0:
            self.action._start()
        else:
            self.action._restart()
        
    def done(self):
        return (self.times != -1) and (self.count>=self.times)
        
    def step(self, dt):
        self.action._step(dt)
        if self.action.done():
            self.count += 1
            if not self.done():
                self.instantiate()            


class CallFunc(Action):
    """An action that will call a funtion."""
    def init(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def done(self):
        return True
        
    def start(self):
        self.func(*self.args, **self.kwargs)


class CallFuncS(CallFunc):
    """An action that will call a funtion with the target as the first argument"""
    def start(self):
        self.func( self.target, *self.args, **self.kwargs)

        
class Delay(Action):
    """Delays the actions in seconds"""
    def init(self, delta):
        self.delta = delta
        
    def done(self):
        return ( self.delta <= self.runtime )


class RandomDelay(Delay):
    """Delays the actions in random seconds between low and hi"""
    def init(self, low, hi):
        self.delta = random.randint(low, hi)
        
    def done(self):
        return ( self.delta <= self.runtime )
