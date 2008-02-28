#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
# To see some examples, see:
#    test/test_sprite.py
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

            'Place',                            # placement action
            'Goto','Move',                      # movement actions
            'Jump','Bezier',                    # complex movement actions
            'Rotate','Scale',                   # object modification
            'Spawn','Sequence','Repeat',        # queueing actions
            'CallFunc','CallFuncS',             # Calls a function
            'Delay','RandomDelay',              # Delays
            'Hide','Show','Blink',              # Hide or Shows the sprite
            'Animate',                          # Animates the sprite
            'FadeOut','FadeIn',                 # Fades out the sprite

            'Animation',                        # class that holds the frames to animate

            'ForwardDir','BackwardDir',         # Movement Directions
            'RepeatMode','PingPongMode',        # Repeat modes
            ]


class ForwardDir: pass 
class BackwardDir: pass
class PingPongMode: pass
class RepeatMode: pass

class ActionSprite( object ):
    """An sprite that supports **Actions**

    To execute an action use the **do** method.

    **sprite.do( Action )**"""

    
    def __init__( self, img ):
        self.frame = image.load( img )
        self.actions = []
        self.to_remove = []
        self.translate = Point3(0,0,0)
        self.scale = 1.0
        self.angle = 0.0
        self.show = True
        self.animations = {}
        self.color = [1.0,1.0,1.0,1.0]

    def do( self, action ):
        try:
            # HACK:
            # deepcopy is needed to run the same sequence of actions
            # in different sprites at the same time
            a = copy.deepcopy( action )
        except Exception, e:
            # but deepcopy fails when copying the CallFunc calling an instance
            # method.
            print "WARNING: Running this action with various sprites at the time has an unpredictable behaviour"
            print "CallFunc / CallFuncS actions can't be deep-copied when they are calling instance methods."
            print "Workaround: Make it call a free function instead."
            print action
            a = copy.copy( action )

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
        if self.show:
            glPushMatrix()
            glLoadIdentity()

            glColor4f(*self.color)
            glTranslatef(self.translate.x, self.translate.y, self.translate.z )

            # comparison is cheaper than an OpenGL matrix multiplication
            if self.angle != 0.0:
                glRotatef(self.angle, 0, 0, 1)
            if self.scale != 1.0:
                glScalef(self.scale, self.scale, 1)

            # hotspot is in the center of the sprite.
            # TODO: hotspot shall be customizable
            self.frame.blit( -self.frame.width / 2, - self.frame.height / 2 )

            glPopMatrix()

    def place( self, coords ):
        self.translate = Point3( *coords )

    def get_box( self ):
        """get_box() -> (x1,y1,x2,y2)

        Returns the box that continas the srpite in Screen coordinates"""
        x2 = self.frame.width / 2
        y2 = self.frame.height / 2
        return (self.translate.x - x2, self.translate.y - x2,
                self.translate.x +  x2, self.translate.y + y2 )

    def add_animation( self, animation ):
        self.animations[ animation.name ] = animation

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
        """Returns the runtime.
        IntervalActions can modify this value. Don't access self.runtime directly"""
        return self.runtime

    def __add__(self, action):
        """Is the Sequence Action"""
        return Sequence(self, action)

    def __or__(self, action):
        """Is the Spawn Action"""
        return Spawn(self, action)


class IntervalAction( Action ):
    """IntervalAction( dir=ForwardDir, mode=PingPongMode )

    Abstract Class that defines the direction of any Interval
    Action. Interval Actions are the ones that can go forward or
    backwards in time. 
    
    For example: Goto, Move, Rotate are Interval Actions.
    CallFunc is not.

    dir can be: ForwardDir or BackwardDir
    mode can be: PingPongMode or RepeatMode
    """
    
    def __init__( self, *args, **kwargs ):

        self.direction = ForwardDir
        self.mode = PingPongMode

        if kwargs.has_key('dir'):
            self.direction = kwargs['dir']
            del(kwargs['dir'])
        if kwargs.has_key('mode'):
            self.mode = kwargs['mode']
            del(kwargs['mode'])

        super( IntervalAction, self ).__init__( *args, **kwargs )


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


class Place( Action ):
    """Place( (x,y,0) )

    Creates and action that will place the sprite in the position x,y.

    Example: Place( (320,240,0) )
    """
    def init(self, position):
        self.position = Point3(*position)
        
    def start(self):
        self.target.translate = self.position

    def done(self):
        return True


class Hide( Action ):
    """Hide()

    Hides the sprite. To show it again call the Show() action"""
    def start(self):
        self.target.show = False

    def done(self):
        return True

class Show( Action ):
    """Show()

    Show the sprite. To hide it call the Hide() action"""
    def start(self):
        self.target.show = True

    def done(self):
        return True

class Blink( IntervalAction ): 
    """Blink( number_of_times, duration)

    Blinks the sprite a Number_of_Times, for Duration seconds"""
    def init(self, times, duration):
        self.times = times
        self.duration = duration
        
    def step(self, dt):
        slice = self.duration / float( self.times )
        m =  self.get_runtime() % slice
        self.target.show = (m  >  slice / 2.0)

class Rotate( IntervalAction ):
    """Rotate( degrees, duration )

    Rotates a sprite counter-clockwise"""
    def init(self, angle, duration=5 ):
        self.angle = angle
        self.duration = duration

    def start( self ):       
        self.start_angle = self.target.angle

    def step(self, dt):
        self.target.angle = (self.start_angle +
                    self.angle * (
                        min(1,float(self.get_runtime())/self.duration)
                    )) % 360 


class Scale(IntervalAction):
    """Scale( zoom_factor, duration )

    Scales an sprite with a given zoom_factor"""
    def init(self, end, duration=5 ):
        self.end_scale = end
        self.duration = duration

    def start( self ):
        self.start_scale = self.target.scale

    def step(self, dt):
        delta = self.end_scale-self.start_scale

        self.target.scale = (self.start_scale +
                    delta * (
                        min(1,float(self.get_runtime() )/self.duration)
                    ))

class Goto( IntervalAction ):
    """Goto( (x,y,0), duration)

    Creates an action that will move a sprite to the position x,y
    x and y are absolute coordinates.
    Duration is is seconds.

    Example: Goto( (50,10,0), 8 )
    It will move a sprite to the position x=50, y=10 in 8 seconds."""
    def init(self, end, duration=5):
        self.end_position = Point3( *end )
        self.duration = duration

    def start( self ):
        self.start_position = self.target.translate

    def step(self,dt):
        delta = self.end_position-self.start_position
        self.target.translate = (self.start_position +
                    delta * (
                        min(1,float(self.get_runtime() )/self.duration)
                    ))


class Move( Goto ):
    """Move( (x,y,0), duration)

    Creates an action that will move a sprite x,y pixels.
    x and y are relative to the position of the sprite.
    Duration is is seconds.

    Example: Move( (50,10,0), 8 )
    It will move a sprite 50 pixels to the right and 10 pixels to the top
    for 8 seconds."""
    def init(self, delta, duration=5):
        self.delta = Point3( *delta)
        self.duration = duration

    def start( self ):
        self.start_position = self.target.translate
        self.end_position = self.start_position + self.delta


class Jump(IntervalAction):
    """Jump( y, x, quantity_of_jumps, duration )

    Creates an actions that moves a sprite Width pixels doing
    the number of Quanitty_Of_Jumps jumps with a height of Height pixels,
    for Duration seconds.

    Example: Jump(50,200, 5, 6)
    It will do 5 jumps travelling 200 pixels to the right for 6 seconds.
    The height of each jump will be 50 pixels each."""
    
    def init(self, y=150, x=120, jumps=1, duration=5):
        self.y = y
        self.x = x
        self.duration = duration
        self.jumps = jumps

    def start( self ):
        self.start_position = self.target.translate

    def step(self, dt):
        y = int( self.y * ( math.sin( (self.get_runtime()/self.duration) * math.pi * self.jumps ) ) )
        y = abs(y)

        x = self.x * min(1,float(self.get_runtime())/self.duration)
        self.target.translate = self.start_position + (x,y,0)

class Bezier( IntervalAction ):
    """Bezier( bezier_configuration, duration )

    Moves a sprite through a bezier path"""
    def init(self, bezier, duration=5):
        self.duration = duration
        self.bezier = bezier

    def start( self ):
        self.start_position = self.target.translate

    def step(self,dt):
        at = self.get_runtime() / self.duration
        p = self.bezier.at( at )

        self.target.translate = ( self.start_position +
            Point3( p[0], p[1], 0 ) )


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
        self.actions = [ copy.copy(a) for a in actions]
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
        self.action = copy.copy( action )
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
    def init(self, func, *args, **kwargs):
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


class FadeOut( IntervalAction ):
    """FadeOut(duration)

    Fades out an sprite"""
    def init( self, duration ):
        self.duration = duration

    def start( self ):
        self.sprite_color = copy.copy( self.target.color )

    def step( self, dt ):
        p = self.get_runtime() / self.duration
        c = self.sprite_color[3] - self.sprite_color[3] * p
        self.target.color[3] = c


class FadeIn( FadeOut):
    """FadeIn(duration)

    Fades in an sprite"""
    def step( self, dt ):
        p = self.get_runtime() / self.duration
        c = self.sprite_color[3] * p
        self.target.color[3] = c


class Animate( IntervalAction ):
    """Animates a sprite given the name of an Animation"""
    def init( self, animation_name ):
        self.animation_name = animation_name

    def start( self ):
        self.animation = self.target.animations[self.animation_name]
        self.duration = len( self.animation.frames ) * self.animation.delay

    def step( self, dt ):
        i =  self.get_runtime() / self.animation.delay
        i = min(int(i), len(self.animation.frames)-1)
        self.target.frame = self.animation.frames[i]


class Animation( object ):
    """Creates an animation with a name, a delay per frames and a list of images"""
    def __init__( self, name, delay, *frames):
        self.name = name
        self.delay = delay
        self.frames = [ image.load(i) for i in frames]
        
    def add_frame( self, frame ):
        self.frames.append( image.load( frame ) )
