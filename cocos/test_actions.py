#
# An implementation of Cocos' ActionObject for Pyglet 1.1
#
# Based on actions.py from Grossini's Hell:
#    http://www.pyweek.org/e/Pywiii/
#
# Based on actions.py from Pygext:
#     http://opioid-interactive.com/~shang/projects/pygext/
#

'''Classes to manipulate sprites.

Animating a sprite
==================

To animate an sprite you need to execute an action.

Actions that modifies the sprite's properties:

    * `MoveBy` ( (x,y), duration)
    * `MoveTo` ( (x,y), duration )
    * `Rotate` ( degrees, duration )
    * `Scale` ( zoom_factor, duration )
    * `Jump` ( height, x, number_of_jumps, duration )
    * `Bezier` ( bezier_configuration, duration )
    * `Place` ( (x,y) )
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

    move = MoveBy( (50,0), 5 )

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
        It can be `PingPongMode` or `RestartMode` . Default is : `PingPongMode` .
    ``time_func`` : a function. The format of the function is f( runtime, duration )
        If you want to alter the speed of time, you should provide your onw time_func or use the `accelerate` function.
        Default : None. No alter-time function is used.

Available IntervalActions
=========================

  * `MoveTo`
  * `MoveBy`
  * `Jump`
  * `Bezier`
  * `Blink`
  * `Rotate`
  * `Scale`
  * `FadeOut`
  * `FadeIn`

Examples::

    move = MoveBy( (200,0), 5 )  # Moves 200 pixels to the right in 5 seconds.
                                 # Direction: ForwardDir (default)
                                 # RestartMode:  PingPongMode (default)
                                 # time_func:  No alter function (default)

    rmove = Repeat( move )       # Will repeat the action *move* forever
                                 # The repetitions are in PingPongMode
                                 # times: -1 (default)

    move2 = MoveBy( (200,0), 5, time_func=accelerate )
                                # Moves 200 pixels to the right in 5 seconds
                                # time_func=accelerate. This means that the
                                # speed is not linear. It will start to action
                                # very slowly, and it will increment the speed
                                # in each step. The total running time will be
                                # 5 seconds.

    move3 = MoveBy( (200,0), 5, dir=BackwardDir )
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

import pyglet
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionObject',                     # Sprite class

            'Action','IntervalAction',          # Action classes

            'Place',                            # placement action
            'MoveTo','MoveBy',                      # movement actions
            'Jump','Bezier',                    # complex movement actions
            'Rotate','ScaleTo',                 # object modification
            'Spawn','Sequence','Repeat',        # queueing actions
            'CallFunc','CallFuncS',             # Calls a function
            'Delay','RandomDelay',              # Delays
            'Hide','Show','Blink',              # Hide or Shows the sprite
            'FadeOut','FadeIn',                 # Fades out the sprite

            'ForwardDir','BackwardDir',         # Movement Directions
            'RestartMode','PingPongMode',        # Repeat modes

            'Accelerate',                       # a function that gives the time acceleration
            ]


class ForwardDir: pass
class BackwardDir: pass
class PingPongMode: pass
class RestartMode: pass

class ActionObject( object ):
    '''ActionObjects are sprites that can execute actions.

    Example::
    
        sprite = ActionObject('grossini.png')
    '''
    
    def __init__( self ):

        print "__init__: ActionObject"

        super( ActionObject, self ).__init__()

        self.actions = []
        self.to_remove = []
        self.scheduled = False

        self.color = (255,255,255)
        self.opacity = 255
        self.position = (0,0)
        self.scale = 1.0
        self.rotation = 0.0
        self.anchor_x = 0.5
        self.anchor_y = 0.5

    def do( self, action ):
        '''Executes an *action*.
        When the action finished, it will be removed from the sprite's queue.

        :Parameters:
            `action` : an `Action` instance
                Action that will be executed.
        :rtype: `Action` instance
        :return: A clone of *action*
        '''
        a = copy.deepcopy( action )

        a.target = self
        a.start()
        self.actions.append( a )

        if not self.scheduled:
            self.scheduled = True
            pyglet.clock.schedule( self.step )
        return a

    def remove_action(self, action ):
        """Removes an action from the queue

        :Parameters:
            `action` : Action
                Action to be removed
        """
        self.to_remove.append( action )

    def pause(self):
        pass
    def resume(self):
        pass
        
    def flush(self):
        """Removes running actions from the queue"""
        for action in self.actions:
            self.to_remove.append( action )

    def step(self, dt):
        """This method is called every frame.

        :Parameters:
            `dt` : delta_time
                The time that elapsed since that last time this functions was called.
        """
        for x in self.to_remove:
            self.actions.remove( x )
        self.to_remove = []

        if len( self.actions ) == 0:
            self.scheduled = False
            pyglet.clock.unschedule( self.step )

        for action in self.actions:
            action.step(dt)
            if action.done():
                self.remove( action )
                


class Action(object):
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.target = None
              
    def init(self):
        """ 
        Gets called at initialization time, before a target it defined
        """
        pass

    def start(self):
        """
        Gets called as soon as a target is asigned to this instance
        """
        pass
                    
    def step(self, dt):
        """
        Gets called every frame. `dt` is the number of seconds that elapsed
        since the last call. If there was a pause and resume in the middle, 
        the actual elapsed time may be bigger.
        
        This function will only be called byt the layer. Not other sprites.
        """
        pass
        
        
    def __add__(self, action):
        """Is the Sequence Action"""
        return Sequence(self, action)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        return Repeat( self, other )
        
    def __or__(self, action):
        """Is the Spawn Action"""
        return Spawn(self, action)


class IntervalAction( Action ):
    """
    IntervalAction()

    Abstract Class that defines the direction of any Interval
    Action. Interval Actions are the ones that have a fixed duration,
    so we can make them go forward or backwards in time. 
    
    For example: `MoveTo` , `MoveBy` , `Rotate` are Interval Actions.
    `CallFunc` is not.

    subclasses must ensure that instances have a duration attribute.
    """
    
    def __init__( self, *args, **kwargs ):
        super( IntervalAction, self ).__init__( *args, **kwargs )
        self.elapsed = 0
        
    def update(self, t):
        """
        Gets called on every frame.
        `t` is in [0,1]
        If this action takes 5 seconds to execute, `t` will be equal to 0
        at 0 seconds. `t` will be 0.5 at 2.5 seconds and `t` will be 1 at 5sec.
        """
        pass
                    
    def step(self, dt):
        self.elapsed += dt
        if self.duration:
            self.update( min(1, self.elapsed/self.duration ) )
        else:
            self.update( 1 )
            
    def done(self):
        return self.elapsed >= self.duration
        
class Rotate( IntervalAction ):
    """Rotates a sprite clockwise in degrees

    Example::
        # rotates the sprite 180 degrees in 2 seconds
        action = Rotate( 180, 2 )       
        sprite.do( action )
    """
    def init(self, angle, duration ):
        """Init method.
        
        :Parameters:
            `angle` : float
                Degrees that the sprite will be rotated. 
                Positive degrees rotates the sprite clockwise.
            `duration` : float
                Duration time in seconds
        """
        self.angle = angle
        self.duration = duration

    def start( self ): 
        self.start_angle = self.target.rotation

    def update(self, t):
        self.target.rotation = (self.start_angle + self.angle * t ) % 360 


class Reverse( IntervalAction ):
    """Reverses the behaviour of the action

    Example::
        # rotates the sprite 180 degrees in 2 seconds counter clockwise
        action = Reverse( Rotate( 180, 2 ) )
        sprite.do( action )
    """
    def init(self, other ):
        """Init method.
        
        :Parameters:
            `other` : IntervalAction
                The action that will be reversed
        """
        self.other = other
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()
        
    def update(self, t):
        self.other.update( 1-t ) 

class Speed( IntervalAction ):
    """
    Changes the speed of an action, making it take longer (speed>1)
    or less (speed<1)

    Example::
        # rotates the sprite 180 degrees in 1 secondclockwise
        action = Speed( Rotate( 180, 2 ), 2 )
        sprite.do( action )
    """
    def init(self, other, speed ):
        """Init method.
        
        :Parameters:
            `other` : IntervalAction
                The action that will be affected
            `speed`: float
                The speed change. 1 is no change. 
                2 means twice as fast, takes half the time
                0.5 means half as fast, takes double the time
        """
        self.other = other
        self.speed = speed
        self.duration = other.duration/speed

    def start(self):
        self.other.target = self.target
        self.other.start()
        
    def update(self, t):
        self.other.update( t ) 

class Accelerate( IntervalAction ):
    """
    Changes the acceleration of an action
    
    Example::
        # rotates the sprite 180 degrees in 2 seconds clockwise
        # it starts slow and ends fast
        action = Accelerate( Rotate( 180, 2 ), 4 )
        sprite.do( action )
    """
    def init(self, other, rate ):
        """Init method.
        
        :Parameters:
            `other` : IntervalAction
                The action that will be affected
            `rate`: float
                The acceleration rate. 1 is linear.
                the new t is t**rate 
        """
        self.other = other
        self.rate = rate
        self.duration = other.duration

    def start(self):
        self.other.target = self.target
        self.other.start()
        
    def update(self, t):
        self.other.update( t**self.rate ) 


class MoveTo( IntervalAction ):
    """Moves a sprite to the position x,y. x and y are absolute coordinates.

    Example::
        # Move the sprite to coords x=50, y=10 in 8 seconds
        
        action = MoveTo( (50,10), 8 )       
        sprite.do( action )
    """
    def init(self, dst_coords, duration=5):
        """Init method.

        :Parameters:
            `dst_coords` : (x,y)
                Coordinates where the sprite will be placed at the end of the action
            `duration` : float
                Duration time in seconds
        """

        self.end_position = Point2( *dst_coords )
        self.duration = duration

    def start( self ):
        self.start_position = self.target.position
        self.delta = self.end_position-self.start_position

    def update(self,t):
        self.target.position = self.start_position + self.delta * t

class MoveBy( MoveTo ):
    """Mve a sprite x,y pixels.
    x and y are relative to the position of the sprite.
    Duration is is seconds.

    Example::
        # Move the sprite 50 pixels to the left in 8 seconds
        action = MoveBy( (-50,0), 8 )  
        sprite.do( action )
    """
    def init(self, delta, duration=5):
        """Init method.

        :Parameters:
            `delta` : (x,y)
                Delta coordinates
            `duration` : float
                Duration time in seconds
        """
        self.delta = Point2( *delta)
        self.duration = duration

    def start( self ):
        self.start_position = self.target.position
        self.end_position = self.start_position + self.delta

class FadeOut( IntervalAction ):
    """FadeOut(duration)
    Fades out an sprite
   
    Example::

        action = FadeOut( 2 )
        sprite.do( action )
    """
    def init( self, duration ):
        """Init method.

        :Parameters:
            `duration` : float
                Seconds that it will take to fade
        """
        self.duration = duration

    def update( self, t ):
        self.target.opacity = 255 * (1-t)


class FadeIn( FadeOut):
    """FadeIn(duration)
    Fades in an sprite
   
    Example::

        action = FadeIn( 2 )
        sprite.do( action )
    """
    def update( self, t ):
        self.target.opacity = 255 * t
        
class ScaleTo(IntervalAction):
    """Scales the sprite

    Example::
        # scales the sprite to 5x in 2 seconds
        action = ScaleTo( 5, 2 )       
        sprite.do( action )
    """
    def init(self, scale, duration=5 ):
        """Init method.
        
        :Parameters:
            `scale` : float
                scale factor
            `duration` : float
                Duration time in seconds
        """
        self.end_scale = scale
        self.duration = duration

    def start( self ):
        self.start_scale = self.target.scale
        self.delta = self.end_scale-self.start_scale

    def update(self, t):
        self.target.scale = self.start_scale + self.delta * t

class ScaleBy(ScaleTo):
    """Scales the sprite

    Example::
        # scales the sprite by 5x in 2 seconds
        action = ScaleBy( 5, 2 )       
        sprite.do( action )
    """

    def start( self ):
        self.start_scale = self.target.scale
        self.delta = self.start_scale*self.end_scale


class Blink( IntervalAction ): 
    """Blinks the sprite a Number_of_Times, for Duration seconds

    Example::
        # Blinks 10 times in 2 seconds
        action = Blink( 10, 2 ) 
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
        
    def update(self, t):
        slice = 1 / float( self.times )
        m =  t % slice
        self.target.visible = (m  >  slice / 2.0)


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
            `bezier` : bezier_configuration instance
                A bezier configuration
            `duration` : float
                Duration time in seconds
        """
        self.duration = duration
        self.bezier = bezier

    def start( self ):
        self.start_position = self.target.position

    def update(self,t):
        p = self.bezier.at( t )
        self.target.position = ( self.start_position +Point2( *p ) )

class Jump(IntervalAction):
    """Moves a sprite simulating a jump movement.

    Example::

        action = Jump(50,200, 5, 6)    # Move the sprite 200 pixels to the right
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
        self.start_position = self.target.position

    def step(self, dt):
        y = int( self.y * ( math.sin( ( max(0,min(1, self.get_runtime()/self.duration)) * math.pi * self.jumps ) ) ) )
        y = abs(y)

        x = self.x * max(0,min(1,float(self.get_runtime())/self.duration))
        self.target.position = self.start_position + Point2(x,y)





# -----8<----- not done below this line

class Place( Action ):
    """Place the sprite in the position x,y.

    Example::

        action = Place( (320,240,0) )
        sprite.do( action )
    """
    def init(self, position):
        """Init method.

        :Parameters:
            `position` : (x,y)
                Coordinates where the sprite will be placed
        """
        self.position = position
        
    def start(self):
        self.target.position = self.position

    def done(self):
        return True


class Hide( Action ):
    """Hides the sprite. To show it again call the `Show` () action

    Example::

        action = Hide()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = False

    def done(self):
        return True

class Show( Action ):
    """Shows the sprite. To hide it call the `Hide` () action

    Example::

        action = Show()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = True

    def done(self):
        return True


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
        self.cloned_actions = []

    def done(self):
        ret = True
        for i in self.cloned_actions:
            ret = ret and i.done()

        return ret

    def start(self):
        for a in self.actions:
            c = self.target.do( a )
            self.cloned_actions.append( c )


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
    """Repeats an action. It is is similar to Sequence, but it runs the same action every time

    Example::

        action = Jump( 50,200,3,5)
        repeat = Repeat( action, times=5 )
        sprite.do( repeat )
    """
    def init(self, action, times=-1):
        """Init method.

        :Parameters:
            `action` : `Action` instance
                The action that will be repeated
            `times` : integer
                The number of times that the action will be repeated. -1, which is the default value, means *repeat forever*
        """
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
    """An action that will call a function.

    Example::

        def my_func():        
            print "hello baby"

        action = CallFunc( my_func )
        sprite.do( action )
    """
    def init(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def done(self):
        return True
        
    def start(self):
        self.func(*self.args, **self.kwargs)
        
    def __deepcopy__(self, memo):
        return copy.copy( self )


class CallFuncS(CallFunc):
    """An action that will call a funtion with the target as the first argument

    Example::

        def my_func( sprite ):
            print "hello baby"
        
        action = CallFuncS( my_func )
        sprite.do( action )
        """
    def start(self):
        self.func( self.target, *self.args, **self.kwargs)

        
class Delay(Action):
    """Delays the action a certain ammount of seconds
   
   Example::

        action = Delay(2.5)
        sprite.do( action )
    """
    def init(self, delay):
        """Init method

        :Parameters:
            `delay` : float
                Seconds of delay 
        """
        self.delay = delay
        
    def done(self):
        return ( self.delay <= self.runtime )


class RandomDelay(Delay):
    """Delays the actions between *min* and *max* seconds
   
   Example::

        action = RandomDelay(2.5, 4.5)      # delays the action between 2.5 and 4.5 seconds
        sprite.do( action )
    """
    def init(self, low, hi):
        """Init method

        :Parameters:
            `low` : float
                Minimun seconds of delay
            `hi` : float
                Maximun seconds of delay
        """
        self.delay = low + (random.random() * (hi - low))



