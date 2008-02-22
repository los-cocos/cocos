#
# Based on actions.py from Grossini's Hell
#

import time, random
from euclid import *

from pyglet import image
from pyglet.gl import *

class ActionSprite( object ):
    def __init__( self, img ):
        self.sprite = image.load( img )
        self.actions = []
        self.to_remove = []
        self.translate = Point3(0,0,0)
        self.scale = 1.0
        self.angle = 0.0

    def do( self, what ):
        action = what( self )
        action._start()
        self.actions.append( action )

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
        glRotatef(self.angle, 0, 0, 1)
        glScalef(self.scale, self.scale, 1)
        self.sprite.blit( -self.sprite.width / 2, - self.sprite.height / 2 )
        glPopMatrix()


class ActionCreator:
    def __init__(self, creator):
        self.creator = creator
        
    def __call__(self, *args, **kwargs):
        return self.creator(*args, **kwargs)
        
    def __add__(self, other):
        return sequence(self, other)

    def __or__(self, other):
        return spawn(self, other)

class Action(object):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.init(*args, **kwargs)
        
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

    def end(self):
        pass

    def step(self, dt):
        pass

class DecoratorAction(Action):
    def __getattr__( self, k):
        if k in ( 'runtime', 'duration' ):
            return getattr( self.action, k )
        else:
            return self.__dict__[ k ]

    def __setattr__( self, k, v ):
        if k in ( 'runtime', 'duration' ):
            setattr( self.action, k, v)
        else:
            self.__dict__[ k ] = v

    def _step(self, dt):
        """ override. don't increment runtime"""
        self.step(dt)

class GotoAction( Action ):
    def init(self, start, end, duration=1000):
        self.start_position = start
        self.end_position = end
        self.duration = duration

    def step(self,dt):
        delta = self.end_position-self.start_position
        self.target.translate = (self.start_position +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))

    def done(self):
        return (self.runtime > self.duration)

def goto(goal, duration=1000):
    def create(target):
        return GotoAction( target, 
                start=target.translate, 
                end=goal, duration=duration)
    return ActionCreator(create)

def move(delta, duration=1000):
    def create(target):
        return GotoAction(target, 
                start=target.translate, 
                end=target.translate+delta, duration=duration)
    return ActionCreator(create)

class ScaleAction(Action):
    def init(self, start, end, duration=1000):
        self.start_scale = start
        self.end_scale = end
        self.duration = duration
        
    def step(self, dt):
        delta = self.end_scale-self.start_scale

        self.target.scale = (self.start_scale +
                    delta * (
                        min(1,float(self.runtime)/self.duration)
                    ))
        
    def done(self):
        return (self.runtime > self.duration)


def scale(amount, duration=1000):
    def create(target):
        return ScaleAction(target, 
                start=target.scale, 
                end=amount, duration=duration)
    return ActionCreator(create)

class RotateAction(Action):
    def init(self, start, angle, duration=1000):
        self.start_angle = start
        self.angle = angle
        self.duration = duration
        
    def step(self, dt):
        self.target.angle = (self.start_angle +
                    self.angle * (
                        min(1,float(self.runtime)/self.duration)
                    )) % 360 

    def done(self):
        return (self.runtime > self.duration)


def rotate(angle, duration=1000):
    def create(target):
        return RotateAction(target, 
                start=target.angle, 
                angle=angle, duration=duration)
    return ActionCreator(create)


class ActionSequencer(Action):
    def init(self, actions):
        self.actions = actions
        self.count = 0
        
    def instantiate(self):
        self.current = self.actions[self.count](self.target)
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
        
def sequence(*actions):
    def create(target):
        return ActionSequencer( target, actions)
    return ActionCreator(create)


class SpawnAction(Action):
    def init(self, actions, target):
        self.actions = actions
        if target is None:
            self.spawn_target = self.target
        else:
            self.spawn_target = target
        
    def done(self):
        return True
        
    def start(self):
        for a in self.actions:
            self.spawn_target.do(a)

def spawn(*actions, **kwargs):
    def create(target):
        return SpawnAction(target, 
            actions, kwargs.get("target",None))
    return ActionCreator(create)    


class PlaceAction(Action):
    def init(self, position):
        self.position = position
        
    def done(self):
        return True
        
    def start(self):
        self.target.translate = self.position

def place(position):
    def create(target):
        return PlaceAction(target, 
            position)
    return ActionCreator(create)       


class CallAction(Action):
    def init(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def done(self):
        return True
        
    def start(self):
        self.func(*self.args, **self.kwargs)

def call(func, *args, **kwargs):
    def create(target):
        return CallAction(target, 
            func, args, kwargs)
    return ActionCreator(create)        


class DelayAction(Action):
    def init(self, delta):
        self.delta = delta
        
    def done(self):
        return ( self.delta <= self.runtime )

def delay(delta):
    def create(target):
        return DelayAction(target, 
            delta)
    return ActionCreator(create)        

def random_delay(low, hi):
    def create(target):
        return DelayAction(target, 
            random.randint(low, hi))
    return ActionCreator(create)  
   
class RepeatAction(Action):
    def init(self, action, times=-1):
        self.action = action
        self.times = times
        self.count = 0
        self.instantiate()
        
    def instantiate(self):
        self.current = self.action(self.target)
        self.current._start()
        
    def done(self):
        return (self.times != -1) and (self.count>=self.times)
        
    def step(self, dt):
        if self.current.done():
            if self.times==-1 or self.count < self.times:
                self.count += 1
                self.instantiate()
            else:
                return
        self.current._step(dt)
        

        
def repeat(action, times=-1):
    def create(target):
        return RepeatAction(target, 
            action, times)
    return ActionCreator(create)
   
class RandomRepeatAction(Action):
    def init(self, actions, times=-1):
        self.actions = actions
        self.pending = self.actions[:]
        self.times = times
        self.count = 0
        self.instantiate()
        
    def instantiate(self):
        if not self.pending:
            self.pending = self.actions[:]
        c = random.choice(self.pending)
        self.current = c(self.target)
        self.pending.remove(c)
        self.current._start()
        
    def done(self):
        return (self.times != -1) and (self.count>=self.times)
        
    def step(self, dt):
        if self.current.done():
            if self.times==-1 or self.count < self.times:
                self.count += 1
                self.instantiate()
            else:
                return
        self.current._step(dt)
        

        
def random_repeat(actions, times=-1):
    def create(target):
        return RandomRepeatAction(target, 
            actions, times)
    return ActionCreator(create)


class TimeWarperAction(Action):
    def init(self, warper, action):
        self.action = action(self.target)
        self.warper = warper
                
    def start(self):
        self.action._start()
        
    def done(self):
        return self.action.done()
        
    def step(self, dt):
        self.action._step(self.warper(self.runtime + dt) - self.warper(self.runtime))
        
def timewarp(warper, action):
    def create(target):
        return TimeWarperAction(target, 
            warper, action)
    return ActionCreator(create)
 
def linear(factor):
    def warper(value):
        return value*factor
    return warper


class ReverseAction(Action):
    def init(self, action):
        self.action = action(self.target)
                
    def start(self):
        self.action._start()
        
    def done(self):
        return ( self.runtime >= self.action.duration )
        
    def step(self, dt):
        self.action.runtime = self.action.duration - self.runtime
        self.action._step( dt )
        
def reverse(action):
    def create(target):
        return ReverseAction(target, 
            action)
    return ActionCreator(create)
 

class BezierAction( Action ):
    def init(self, start, bezier, duration=1000):
        self.start_position = start
        self.duration = duration
        self.bezier = bezier

    def step(self,dt):
        at = self.runtime / self.duration
        p = self.bezier.at( at )

        self.target.translate = ( self.start_position +
            Point3( p[0], p[1], 0 ) )

    def done(self):
        return (self.runtime > self.duration)

def bezier(goal, duration=1000):
    def create(target):
        return BezierAction( target, 
                start=target.translate, 
                bezier=goal, duration=duration)
    return ActionCreator(create)


class SinAction(DecoratorAction):
    import math

    def init(self, action, height=150, freq=4, negative=True):
        self.action = action(self.target)
        self.height = height
        self.freq = freq
        self.negative = negative
                
    def start(self):
        self.action._start()
        
    def done(self):
        return self.action.done()
        
    def step(self, dt):
        self.action._step( dt )
        y = int( self.height * ( math.sin( (self.runtime/self.action.duration) * math.pi * self.freq ) ) )
        if not self.negative:
            y = abs(y)
        self.action.target.translate.y += y
        
def sin(action, height=150, freq=5):
    def create(target):
        return SinAction(target, 
            action, height, freq, negative=True)
    return ActionCreator(create)


def jump(action, height=150, freq=5):
    def create(target):
        return SinAction(target, 
            action, height, freq, negative=False)
    return ActionCreator(create)
