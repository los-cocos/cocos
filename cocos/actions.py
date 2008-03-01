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

'''Classes to manipulate sprites.

Sprites
=======

Creating sprites
================

An sprite is created instantiating the ActionSprite class::

    from cocos.actions import *

    sprite = ActionSprite('sprite_texture.png')

``sprite_texture.png`` is an image file with the shape of the sprite


Animating a sprite
==================

To animate an sprite you need to execute an action.

Actions that modifies the sprite's properties:

    * `Move` ( (x,y,0), duration)
    * `Goto` ( (x,y,0), duration )
    * `Rotate` ( degrees, duration )
    * `Scale` ( zoom_factor, duration )
    * `Jump` ( height, x, number_of_jumps, duration )
    * `Bezier` ( bezier_configuration, duration )
    * `Place` ( (x,y,0) )
    * `Animate` ( animation_name )
    * `FadeIn` ( duration )
    * `FadeOut` ( duration )
    * `Blink` ( times_to_blink, duration )
    * `Show` ()
    * `Hide` ()

Composite actions:

    * `Repeat` ( action )
    * `Spawn` ( list_of_actions )
    * `Sequence` ( list_of_actions )

Misc actions:

    * `CallFunc` ( function )
    * `CallFuncS` ( function )
    * `Delay` ( seconds )
    * `RandomDelay` ( lo_seconds, hi_seconds )


To execute any action you need to create an action::

    move = Move( (50,0,0), 5 )

In this case, ``move`` is an action that will move the sprite
50 pixels to the right (``x`` coordinate), 0 pixel in the ``y`` coordinate,
and 0 pixels in the ``z`` coordinate in 5 seconds.


And now tell the sprite to execute it::

    sprite.do( move )


Interval Actions
================

An interval action is an action that takes place within a certain period of time.
It has an start time, and a finish time. The finish time is the parameter
``duration`` plus the start time.

These `IntervalAction` have some interesting properties, like:

  * They can run Forward (default)
  * They can run Backwards
  * They can alter the speed of time

For example, if you run an action in a Forward direction and the you run it again in
a Backward direction, then you are simulation a PingPong movement.

These actions has 3 special parameters:

    ``dir`` : direction
        It can be `ForwardDir` or `BackwardDir` . Default is: `ForwardDir`
    ``mode`` : repeat mode
        It can be `PingPongMode` or `RepeatMode` . Default is : `PingPongMode` .
    ``time_func`` : a function. The format of the function is f( runtime, duration )
        If you want to alter the speed of time, you should provide your onw time_func or use the `accelerate` function.
        Default : None. No alter-time function is used.

Available IntervalActions
=========================

  * `Goto`
  * `Move`
  * `Jump`
  * `Bezier`
  * `Blink`
  * `Rotate`
  * `Scale`
  * `Animate`
  * `FadeOut`
  * `FadeIn`

Examples::

    move = Move( (200,0,0), 5 )  # Moves 200 pixels to the right in 5 seconds.
                                 # Direction: ForwardDir (default)
                                 # RepeatMode:  PingPongMode (default)
                                 # time_func:  No alter function (default)

    rmove = Repeat( move )       # Will repeat the action *move* forever
                                 # The repetitions are in PingPongMode
                                 # times: -1 (default)

    move2 = Move( (200,0,0), 5, time_func=accelerate )
                                # Moves 200 pixels to the right in 5 seconds
                                # time_func=accelerate. This means that the
                                # speed is not linear. It will start to action
                                # very slowly, and it will increment the speed
                                # in each step. The total running time will be
                                # 5 seconds.

    move3 = Move( (200,0,0), 5, dir=BackwardDir )
                                # Moves 200 pixels to the **left** in 5 seconds
                                # But when you use this direction (BackwardDir)
                                # the starting coords and the finishing coords
                                # are inverted
                                
'''

__docformat__ = 'restructuredtext'

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

            'accelerate',                       # a function that gives the time acceleration
            ]


class ForwardDir: pass
class BackwardDir: pass
class PingPongMode: pass
class RepeatMode: pass

class ActionSprite( object ):
    '''ActionSprite( image_filenaem )

    Creates an instance of ActionSprite. ActionSprites can execute actions.

    Example::
    
        sprite = ActionSprite('grossini.png')
    '''
    
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
        '''Executes an *action*.
        When the action finished, it will be removed from the sprite's queue.

        :Parameters:
            `action` : an Action instance
                Action that will be executed.
        :rtype: Action instance
        :return: A clone of *action*
        '''
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
        return a

    def done(self, action ):
        self.to_remove.append( action )
        
    def step(self, dt):
        """This functions is called *n* times per second, where
        *n* are the FPS.

        :Parameters:
            `dt` : delta_time
                The time that ellapsed since that last time this functions was called.
        """
        for action in self.actions:
            action._step(dt)
            if action.done():
                self.done( action )
                
        for x in self.to_remove:
            self.actions.remove( x )
        self.to_remove = []

        self.draw()

    def draw( self ):
        '''
        '''
 
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
        '''Places the sprite in the coordinates *coords*.

        :Parameters:
            `coords` : (x,y,0)
                Coordinates where the sprite will be translated.'''
        self.translate = Point3( *coords )

    def get_box( self ):
        ''' Returns the box that continas the sprite in Screen coordinates

        :rtype: (x1,x2,y1,y2)
        :returns: Returns the box that contains the sprite in screen coordinates'''

        x2 = self.frame.width / 2
        y2 = self.frame.height / 2
        return (self.translate.x - x2, self.translate.y - x2,
                self.translate.x +  x2, self.translate.y + y2 )

    def add_animation( self, animation ):
        '''Adds a new *Animation* instance to the sprite. These Animations can be animated
        using the *Animate* action.

        :Parameters:
            `animation` : Animation instance
                Animation that will be executed.'''
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
        self.runtime += dt
        self.step(dt)
        
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
    """IntervalAction( dir=ForwardDir, mode=PingPongMode, time_func=None )

    Abstract Class that defines the direction of any Interval
    Action. Interval Actions are the ones that can go forward or
    backwards in time. 
    
    For example: `Goto` , `Move` , `Rotate` are Interval Actions.
    `CallFunc` is not.

    dir can be: `ForwardDir` or `BackwardDir`
    mode can be: `PingPongMode` or `RepeatMode`
    time_func can be any function that alters the time.
    `accelerate` , a time-alter function, is provided with this lib.
    """
    
    def __init__( self, *args, **kwargs ):

        self.direction = ForwardDir
        self.mode = PingPongMode
        self.time_func = None

        if kwargs.has_key('dir'):
            self.direction = kwargs['dir']
            del(kwargs['dir'])
        if kwargs.has_key('mode'):
            self.mode = kwargs['mode']
            del(kwargs['mode'])
        if kwargs.has_key('time_func'):
            self.time_func= kwargs['time_func']
            del(kwargs['time_func'])
    
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
        rt = 0
        if self.direction == ForwardDir:
            rt = self.runtime
        elif self.direction== BackwardDir:
            rt = self.duration - self.runtime
        else:
            raise Exception("Unknown Interval Mode: %s" % (str( self.mode) ) )

        if self.time_func:
            rt = self.time_func( rt, self.duration )
        return rt

def accelerate( t, duration ):
    return t * (t/duration)

class Place( Action ):
    """Place( (x,y,0) )

    Creates and action that will place the sprite in the position x,y.

    Example::

        action = Place( (320,240,0) )
        sprite.do( action )
    """
    def init(self, position):
        """Init method.

        :Parameters:
            `position` : (x,y,0)
                Coordinates where the sprite will be placed
        """
        self.position = Point3(*position)
        
    def start(self):
        self.target.translate = self.position

    def done(self):
        return True


class Hide( Action ):
    """Hide()

    Hides the sprite. To show it again call the `Show` () action

    Example::

        action = Hide()
        sprite.do( action )
    """
    def start(self):
        self.target.show = False

    def done(self):
        return True

class Show( Action ):
    """Show()

    Shows the sprite. To hide it call the `Hide` () action

    Example::

        action = Show()
        sprite.do( action )
    """
    def start(self):
        self.target.show = True

    def done(self):
        return True

class Blink( IntervalAction ): 
    """Blink( number_of_times, duration)

    Blinks the sprite a Number_of_Times, for Duration seconds

    Example::

        action = Blink( 10, 2 ) # Blinks 10 times in 2 seconds
        sprite.do( action )
    """


    def init(self, times, duration):
        """Init method.

        :Parameters:
            `times` : integer
                Number of times to blink
            `duration` : float
                Duration time in seconds
        """
        self.times = times
        self.duration = duration
        
    def step(self, dt):
        slice = self.duration / float( self.times )
        m =  min( self.duration, self.get_runtime()) % slice
        self.target.show = (m  >  slice / 2.0)

class Rotate( IntervalAction ):
    """Rotates a sprite counter-clockwise

    Example::

        action = Rotate( 180, 2 )       # rotates the sprite 180 degrees in 2 seconds
        sprite.do( action )
    """
    def init(self, angle, duration=5 ):
        """Init method.
        
        :Parameters:
            `angle` : float
                Degrees that the sprite will be rotated. Positive degrees rotates the sprite conter-clockwise.
            `duration` : float
                Duration time in seconds
        """
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
    """Scales the sprite

    Example::

        action = Scale( 5, 2 )       # scales the sprite 5x in 5 seconds
        sprite.do( action )
    """
    def init(self, zoom, duration=5 ):
        """Init method.
        
        :Parameters:
            `zoom` : float
                scale factor
            `duration` : float
                Duration time in seconds
        """
        self.end_scale = zoom
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
    """Creates an action that will move a sprite to the position x,y
    x and y are absolute coordinates.

    Example::

        action = Goto( (50,10,0), 8 )       # Move the sprite to coords x=50, y=10 in 8 seconds
        sprite.do( action )
    """
    def init(self, dst_coords, duration=5):
        """Init method.

        :Parameters:
            `dst_coords` : (x,y,0)
                Coordinates where the sprite will be placed at the end of the action
            `duration` : float
                Duration time in seconds
        """

        self.end_position = Point3( *dst_coords )
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
    """Creates an action that will move a sprite x,y pixels.
    x and y are relative to the position of the sprite.
    Duration is is seconds.

    Example::

        action = Move( (-50,0,0), 8 )  # Move the sprite 50 pixels to the left in 8 seconds
        sprite.do( action )
    """
    def init(self, delta, duration=5):
        """Init method.

        :Parameters:
            `delta` : (x,y,0)
                Delta coordinates
            `duration` : float
                Duration time in seconds
        """
        self.delta = Point3( *delta)
        self.duration = duration

    def start( self ):
        self.start_position = self.target.translate
        self.end_position = self.start_position + self.delta


class Jump(IntervalAction):
    """Jump( y, x, quantity_of_jumps, duration )

    Creates an actions that moves a sprite Width pixels doing
    the number of Quanitty_Of_Jumps jumps with a height of Height pixels,
    in Duration seconds.

    Example::

        action = Jump(50,200, 5, 6)    # Move the sprite 200 pixels to the left
        sprite.do( action )            # in 6 seconds, doing 5 jumps
                                       # of 50 pixels of height
    """
    
    def init(self, y=150, x=120, jumps=1, duration=5):
        """Init method

        :Parameters:
            `y` : integer
                Height of jumps
            `x` : integer
                horizontal movement relative to the startin position
            `jumps` : integer
                quantity of jumps
            `duration` : float
                Duration time in seconds
        """
        self.y = y
        self.x = x
        self.duration = duration
        self.jumps = jumps

    def start( self ):
        self.start_position = self.target.translate

    def step(self, dt):
        y = int( self.y * ( math.sin( (min(1, self.get_runtime()/self.duration)) * math.pi * self.jumps ) ) )
        y = abs(y)

        x = self.x * min(1,float(self.get_runtime())/self.duration)
        self.target.translate = self.start_position + (x,y,0)

class Bezier( IntervalAction ):
    """Moves a sprite through a bezier path

    Example::

        action = Bezier( bezier_conf.path1, 5 )   # Moves the sprite using the
        sprite.do( action )                       # bezier path 'bezier_conf.path1'
                                                  # in 5 seconds
    """
    def init(self, bezier, duration=5):
        """Init method

        :Parameters:
            `bezier` : Bezier instance
                A bezier configuration
            `duration` : float
                Duration time in seconds
        """
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
    """Spawn a  new action immediately.
    You can spawn actions using:
        
        * the Spanw() class
        * the overriden *|* operator
        * call sprite.do() many times

    Example::

        action = Spawn( action1, action2, action3 )
        sprite.do( action )

        or:

        sprite.do( action1 | action2 | action3 )

        or:

        sprite.do( action1 )
        sprite.do( action2 )
        sprite.do( action3 )
    """
    def init(self, *actions):
        """Init method

        :Parameters:
            `actions` : list of actions
                The list of actions that will be spawned
        """
        self.actions = actions

    def done(self):
        return True
        
    def start(self):
        for a in self.actions:
            self.target.do( a )


class Sequence(Action):
    """Run actions sequentially: One after another
    You can sequence actions using:
        
        * the Sequence() class
        * the overriden *+* operator

    Example::

        action = Sequence( action1, action2, action3 )
        sprite.do( action )

        or:

        sprite.do( action1 + action2 + action3 )
        """
    def init(self,  *actions, **kwargs ):
        """Init method

        :Parameters:
            `actions` : list of actions
                List of actions to be sequenced
        """
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
        p = min(1, self.get_runtime() / self.duration )
        c = self.sprite_color[3] - self.sprite_color[3] * p
        self.target.color[3] = c


class FadeIn( FadeOut):
    """FadeIn(duration)

    Fades in an sprite"""
    def step( self, dt ):
        p = min(1, self.get_runtime() / self.duration )
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
