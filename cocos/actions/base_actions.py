#
# Base Actions
#

'''Classes to manipulate sprites.

Base Actions
============

'''

__docformat__ = 'restructuredtext'

import copy

__all__ = [ 
            'Action',                           # Base Class
            'IntervalAction', 'InstantAction',  # Important Base classes 
            'Sequence','Spawn','Repeat',        # Basic behaviours
            'Reverse',
            ]


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

def Reverse( action ):
    """Reverses the behaviour of the action

    Example::
        # rotates the sprite 180 degrees in 2 seconds counter clockwise
        action = Reverse( Rotate( 180, 2 ) )
        sprite.do( action )
    """
    return action.__reversed__()

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
