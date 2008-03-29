#
# An implementation of Cocos' ActionSprite for Pyglet 1.1
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

import interfaces
from director import director

import pyglet
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionSprite',                     # Sprite class

            'Action','IntervalAction',          # Action classes

            'Place',                            # placement action
            'MoveTo','MoveBy',                  # movement actions
            'Jump','Bezier',                    # complex movement actions
            'Rotate','ScaleTo','ScaleBy',       # object modification
            'Spawn','Sequence','Repeat',        # queueing actions
            'CallFunc','CallFuncS',             # Calls a function
            'Delay','RandomDelay',              # Delays
            'Hide','Show','Blink',              # Hide or Shows the sprite
            'FadeOut','FadeIn',                 # Fades out the sprite


            'Accelerate',                       # a function that gives the time acceleration
            'Reverse',
            'Speed',
            ]

class SpriteGroup(pyglet.graphics.Group):
    def __init__(self, sprite):
        super(SpriteGroup, self).__init__(parent=sprite.group)
        self.sprite = sprite
        
    def set_state(self):
        glPushMatrix()
        self.sprite.transform()
        
    def unset_state(self):
        glPopMatrix()

class ActionSprite( pyglet.sprite.Sprite, interfaces.IActionTarget, interfaces.IContainer ):
    '''ActionSprites are sprites that can execute actions.

    Example::
    
        sprite = ActionSprite('grossini.png')
    '''
    def __init__( self, *args, **kwargs ):

        pyglet.sprite.Sprite.__init__(self, *args, **kwargs)
        interfaces.IActionTarget.__init__(self)
        interfaces.IContainer.__init__(self)
        self.group = None
        self.children_group = None
        
    def add( self, child, position=(0,0), rotation=0.0, scale=1.0, color=(255,255,255), opacity=255, anchor_x=0.5, anchor_y=0.5, z=0,name='',):  
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `name` : str
                Name of the child
            `position` : tuple
                 this is the lower left corner by default
            `rotation` : int
                the rotation (degrees)
            `scale` : int
                the zoom factor
            `opacity` : int
                the opacity (0=transparent, 255=opaque)
            `color` : tuple
                the color to colorize the child (RGB 3-tuple)
            `anchor_x` : float
                x-point from where the image will be rotated / scaled. Value goes from 0 to 1
            `anchor_y` : float
                y-point from where the image will be rotated / scaled. Value goes from 0 to 1
        """
        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        properties = {'position' : position,
                      'rotation' : rotation,
                      'scale' : scale,
                      'color' : color,
                      'opacity' : opacity,
                      'anchor_x' : anchor_x,
                      'anchor_y' : anchor_y,
                      }
        for k,v in properties.items():
            setattr(child, k, v)

        if self.group is None:
            self.children_group = SpriteGroup( self )
        child.set_parent( self )
            
        self.children.append( child )
        
    def set_parent(self, parent):
        self.group = parent.children_group
        self.batch = parent.batch
        
        self.children_group = SpriteGroup( self )
        for c in self.children:
            c.set_parent( self )
            
    def transform( self ):
        """Apply ModelView transformations"""

        x,y = director.get_window_size()

        color = tuple(self.color) + (self.opacity,)
        if color != (255,255,255,255):
            glColor4ub( * color )

        if self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )

        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)

        

        
ActionSprite.supported_classes = ActionSprite
    

        
class Action(object):
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.target = None
        self.elapsed = None
              
    def init(self):
        """ 
        Gets called at initialization time, before a target it defined
        """
        pass

    def start(self):
        """
        Before we start executing an action, self.target is assigned and this method is called.
        it will be called for every excecution of the action.
        """
        pass
                    
    def step(self, dt):
        """
        Gets called every frame. `dt` is the number of seconds that elapsed
        since the last call. If there was a pause and resume in the middle, 
        the actual elapsed time may be bigger.
        
        This function will only be called by the layer. Not other sprites.
        """
        if self.elapsed is None:
            self.elapsed = 0
            
            
        self.elapsed += dt

        if self.duration:
            self.update( min(1, self.elapsed/self.duration ) )
        else:
            self.update( 1 )
                
        
    def __add__(self, action):
        """Is the Sequence Action"""
        return Sequence(self, action)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return  Sequence(self, self*(other-1))
        
    def __or__(self, action):
        """Is the Spawn Action"""
        return Spawn(self, action)

    def __reversed__(self):
        raise Exception("Action %s cannot be reversed"%(self.__class__.__name__))
    

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
    
        
    def update(self, t):
        """
        Gets called on every frame.
        `t` is in [0,1]
        If this action takes 5 seconds to execute, `t` will be equal to 0
        at 0 seconds. `t` will be 0.5 at 2.5 seconds and `t` will be 1 at 5sec.
        
        """
        pass
                    
    
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

    def __reversed__(self):
        return Rotate(-self.angle, self.duration)
    
def Reverse( action ):
    """Reverses the behaviour of the action

    Example::
        # rotates the sprite 180 degrees in 2 seconds counter clockwise
        action = Reverse( Rotate( 180, 2 ) )
        sprite.do( action )
    """
    return action.__reversed__()

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
        
    def __reversed__(self):
        return Speed( Reverse( self.other ), self.speed )

class Accelerate( IntervalAction ):
    """
    Changes the acceleration of an action
    
    Example::
        # rotates the sprite 180 degrees in 2 seconds clockwise
        # it starts slow and ends fast
        action = Accelerate( Rotate( 180, 2 ), 4 )
        sprite.do( action )
    """
    def init(self, other, rate = 2):
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

    def __reversed__(self):
        return Accelerate(Reverse(self.other), 1.0/self.rate)

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
        self.delta = Point2( *delta )
        self.duration = duration

    def start( self ):
        self.start_position = self.target.position
        self.end_position = self.start_position + self.delta
        
    def __reversed__(self):
        return MoveBy(-self.delta, self.duration)
        
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
        
    def __reversed__(self):
        return FadeIn( self.duration )
    


class FadeIn( FadeOut):
    """FadeIn(duration)
    Fades in an sprite
   
    Example::

        action = FadeIn( 2 )
        sprite.do( action )
    """
    def update( self, t ):
        self.target.opacity = 255 * t

    def __reversed__(self):
        return FadeOut( self.duration )

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
        self.delta =  self.start_scale*self.end_scale - self.start_scale

    def __reversed__(self):
        return ScaleBy( 1.0/self.end_scale, self.duration )


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

    def __reversed__(self):
        return self


class Bezier( IntervalAction ):
    """Moves a sprite through a bezier path

    Example::

        action = Bezier( bezier_conf.path1, 5 )   # Moves the sprite using the
        sprite.do( action )                       # bezier path 'bezier_conf.path1'
                                                  # in 5 seconds
    """
    def init(self, bezier, duration=5, forward=True):
        """Init method

        :Parameters:
            `bezier` : bezier_configuration instance
                A bezier configuration
            `duration` : float
                Duration time in seconds
        """
        self.duration = duration
        self.bezier = bezier
        self.forward = forward

    def start( self ):
        self.start_position = self.target.position

    def update(self,t):
        if self.forward:
            p = self.bezier.at( t )
        else:
            p = self.bezier.at( 1-t )
        self.target.position = ( self.start_position +Point2( *p ) )

    def __reversed__(self):
        return Bezier(self.bezier, self.duration, not self.forward)
    
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

    def update(self, t):
        y = int( self.y * ( math.sin( t * math.pi * self.jumps ) ) ) 
        y = abs(y)

        x = self.x * t
        self.target.position = self.start_position + Point2(x,y)

    def __reversed__(self):
        return Jump(self.y, -self.x, self.jumps, self.duration)


class InstantAction( Action ):
    """
    Instant actions are actions that happen just one call.
    """
    duration = 0
    
    def start(self):
        """
        Here we must do out stuff
        """
        pass
    
    def done(self):
        return True
    
    def update(self, t):
        pass

    
class Place( InstantAction ):
    """Place the sprite in the position x,y.

    Example::

        action = Place( (320,240) )
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
        
class Hide( InstantAction ):
    """Hides the sprite. To show it again call the `Show` () action

    Example::

        action = Hide()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = False

    def __reversed__(self):
        return Show()

class Show( InstantAction ):
    """Shows the sprite. To hide it call the `Hide` () action

    Example::

        action = Show()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = True

    def __reversed__(self):
        return Hide()

class ToggleVisibility( InstantAction ):
    """Toggles the visible attribute of a sprite

    Example::

        action = ToggleVisibility()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = not self.target.visible

    def __reversed__(self):
        return self
    
class CallFunc(InstantAction):
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
              
    def start(self):
        self.func(*self.args, **self.kwargs)
        
    def __deepcopy__(self, memo):
        return copy.copy( self )

    def __reversed__(self):
        return self

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

class Sequence(IntervalAction):
    """Run actions sequentially: One after another
    You can sequence actions using:
        
        * the Sequence() class
        * the overriden *+* operator

    Example::

        action = Sequence( one, two )
        sprite.do( action )

        or:

        sprite.do( one+two )
        """
    def init(self,  one, two, **kwargs ):
        """Init method

        :Parameters:
            `actions` : list of actions
                List of actions to be sequenced
        """
        
        if not hasattr(one, "duration") or not hasattr(one, "duration"):
            raise Exception("You can only sequence actions with finite duration, not repeats or others like that")
        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)
        self.actions = [self.one, self.two]
        
        self.duration = self.one.duration + self.two.duration
        self.split = self.one.duration / float(self.duration)
        
        self.last = None

    def start(self):
        self.one.target = self.target
        self.two.target = self.target

    def __repr__(self):
        return "( %s + %s )" %( self.one, self.two )
    
    def update(self, t):
        start_t = 0
        found = None
        if t >= self.split:
            found = 1
            if self.split == 1:
                new_t = 1
            else:
                new_t = (t-self.split) / (1 - self.split )
        elif t < self.split:
            found = 0
            if self.split != 0:
                new_t = t / self.split
            else:
                new_t = 1
                
                
        # now we can execute the action and save the state
        if self.last is None and found == 1:
            self.one.start()
            self.one.update(1)
            
        if self.last != found:
            if self.last is not None:
                self.actions[self.last].update(1)
            self.actions[ found ].start()
            
        self.actions[ found ].update( new_t )
        self.last = found
        
    def __reversed__(self):
        return Sequence( Reverse(self.two), Reverse(self.one) )

class Delay(IntervalAction):
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
        self.duration = delay
        
    def __reversed__(self):
        return self
    

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
        self.low = low
        self.hi = hi
        
    def __deepcopy__(self, memo):
        new = copy.copy(self)
        new.duration = self.low + (random.random() * (self.hi - self.low))
        return new





class Spawn(IntervalAction):
    """Spawn a  new action immediately.
    You can spawn actions using:
        
        * the Spanw() class
        * the overriden *|* operator
        * call sprite.do() many times

    Example::

        action = Spawn( action1, action2 )
        sprite.do( action )

        or:

        sprite.do( action1 | action2  )

        or:

        sprite.do( action1 )
        sprite.do( action2 )
    """
    def init(self, one, two):
        """Init method

        :Parameters:
            `actions` : list of actions
                The list of actions that will be spawned
        """
        one = copy.deepcopy(one)
        two = copy.deepcopy(two)
        if one.duration > two.duration:
            two = two + Delay( one.duration-two.duration )
        elif two.duration > one.duration:
            one = one + Delay( two.duration-one.duration )

        self.duration = one.duration
        
        self.actions = [one, two]
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
            

    def __reversed__(self):
        return Reverse( self.actions[0]  ) | Reverse( self.actions[1] )
    
class DoAction(InstantAction):
    """Calls the action when executed.
    Usefull if you want to sequence actions of infinite duration.
    
    Example::

        action = Repeat( dance )
        sprite.do( go_home + DoAction( dance ) )
    """
    def init(self, action):
        self.action = action
        
    def start(self):
        self.target.do( self.action )

    def __reversed__(self):
        return self
    
    
class Repeat(Action):
    """Repeats an action forever. 

    Example::

        action = Jump( 50,200,3,5)
        repeat = Repeat( action )
        sprite.do( repeat )
        
    Note::
        To repeat just a finite amount of time, just do action * times .
    """
    def init(self, action):
        """Init method.

        :Parameters:
            `action` : `Action` instance
                The action that will be repeated
        """
        self.original = action
        self.action = copy.deepcopy( action )
        self.elapsed = 0
        
    def start(self):
        self.action.target = self.target
        self.action.start()
        
    def step(self, dt):
        self.action.step(dt)
        if self.action.done():
            self.action = copy.deepcopy(self.original)
            self.start()
            
    def done(self):
        return False
            


        
