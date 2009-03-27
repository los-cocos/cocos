# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''Base actions

Base Actions
============

These actions are the 'mother' of all actions.
They are the building blocks.

'''

__docformat__ = 'restructuredtext'

import copy

__all__ = [ 
            'Action',                           # Base Class
            'IntervalAction', 'InstantAction',  # Important Base classes 
            'Sequence','Spawn','Repeat',        # Basic behaviors
            'Reverse','_ReverseTime',           # Reverse
            ]





class Action(object):
    '''Mother of all actions'''
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)
        self.target = None              #: `CocosNode` object that is the target of the action
        self._elapsed = None

    def init(self):
        """
        Gets called at initialization time, before a target is defined
        """
        pass

    def start(self):
        """
        Before we start executing an action, self.target is assigned and this method is called.
        It will be called for every execution of the action.
        """
        pass

    def stop(self):
        """
        After we finish executing an action this method is called.
        It will be called for every execution of the action.
        """
        pass
        
    def step(self, dt):
        """
        Gets called every frame. `dt` is the number of seconds that elapsed
        since the last call. If there was a pause and resume in the middle,
        the actual elapsed time may be bigger.

        This function will only be called by the `Layer`, but interval actions will
        be updated with the `IntervalAction.update` method.
        """
        if self._elapsed is None:
            self._elapsed = 0


        self._elapsed += dt

        if self.duration:
            self.update( min(1, self._elapsed/self.duration ) )
        else:
            self.update( 1 )
            self.stop()


    def __add__(self, action):
        """Is the Sequence Action"""
        return Sequence(self, action)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return  Loop(self, other)

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

    For example: `MoveTo` , `MoveBy` , `RotateBy` are Interval Actions, while
    `Place`, `Show` and `CallFunc` aren't.

    Subclasses must ensure that instances have a duration attribute.
    """


    def update(self, t):
        """Gets called on every frame.
        `t` is in [0,1]
        If this action takes 5 seconds to execute, `t` will be equal to 0
        at 0 seconds. `t` will be 0.5 at 2.5 seconds and `t` will be 1 at 5sec.
        """
        pass


    def done(self):
        return self._elapsed >= self.duration

def Reverse( action ):
    """Reverses the behavior of the action

    Example::

        # rotates the sprite 180 degrees in 2 seconds counter clockwise
        action = Reverse( RotateBy( 180, 2 ) )
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
class Loop(IntervalAction):
    """Repeat one action for n times
    You can loop actions using:

        * the Loop() class
        * the overriden * operator

    Example::

        action = Loop( one, 10 )
        sprite.do( action )

        or:

        sprite.do( one * 10 )
    """
    def init(self,  one, times ):
        """Init method

        :Parameters:
            `one` : `Action`
                Action to be repeated
            `times` : int
                Number of times that the action will be repeated
        """

        self.one = one
        self.times = times

        if not hasattr(self.one, "duration"):
            raise Exception("You can only loop actions with finite duration, not repeats or others like that")
        
        self.duration = self.one.duration * times
        
        self.current = None
        self.last = None
        
    def start(self):
        self.duration = self.one.duration * self.times
        self.last = 0
        self.current_action = copy.deepcopy(self.one)
        self.current_action.target = self.target
        self.current_action.start()
        
    def __repr__(self):
        return "( %s * %i )" %( self.one, self.times )

    def update(self, t):
        current = int(t * float(self.times))
        new_t = (t - (current * (1./self.times) ) ) * self.times


        if current >= self.times: # we are done
            return
        # just more dt for the current action
        elif current == self.last:
            self.current_action.update(new_t)
        else:
            # finish the last action
            self.current_action.update(1)
            self.current_action.stop()
            
            for i in range(self.last+1, current):
                # fast forward the jumped actions            
                self.current_action = copy.deepcopy(self.one)
                self.current_action.target = self.target
                self.current_action.start()
                self.current_action.update(1)
                self.current_action.stop()
            
            # set new current action
            self.current_action = copy.deepcopy(self.one)
            self.current_action.target = self.target
            self.last = current
            
            # start a new action
            self.current_action.start()
            
            # feed dt
            self.current_action.update(new_t)
            
    def stop(self):
        self.current_action.update(1)
        self.current_action.stop()
        
    def __reversed__(self):
        return Loop( Reverse(self.one), self.times )
        
        
class Sequence(IntervalAction):
    """Run actions sequentially: One after another
    You can sequence actions using:

        * the Sequence() class
        * the overriden *+* operator

    Example::

        action = Sequence( one, Sequence( two, three) )
        sprite.do( action )

        or:

        sprite.do( one + two + three )
        """
    def init(self,  one, two, **kwargs ):
        """Init method

        :Parameters:
            `one` : `Action`
                The first action to execute
            `two` : `Action`
                The second action to execute
        """

        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)
        self.actions = [self.one, self.two]

        if not hasattr(self.one, "duration") or not hasattr(self.two, "duration"):
            raise Exception("You can only sequence actions with finite duration, not repeats or others like that")
        
        self.duration = self.one.duration + self.two.duration
        self.split = self.one.duration / float(self.duration)

        self.last = None

    def start(self):
        self.duration = self.one.duration + self.two.duration
        self.split = self.one.duration / float(self.duration)

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
            self.one.stop()

        if self.last != found:
            if self.last is not None:
                self.actions[self.last].update(1)
                self.actions[self.last].stop()
                
            self.actions[ found ].start()

        self.actions[ found ].update( new_t )
        self.last = found

    def stop(self):
        self.two.stop()
        
    def __reversed__(self):
        return Sequence( Reverse(self.two), Reverse(self.one) )

class Spawn(IntervalAction):
    """Spawn a  new action immediately.
    You can spawn actions using:

        * the Spawn() class
        * the overriden *|* operator
        * call sprite.do() many times

    Example::

        action = Spawn( action1, Spawn( action2, action3 ) )
        sprite.do( action )

        or:

        sprite.do( action1 | action2 | action3 )

        or:

        sprite.do( action1 )
        sprite.do( action2 )
        sprite.do( action3 )
    """

    def init(self, one, two):
        """Init method

        :Parameters:
            `one` : `Action`
                The first action to execute in parallel
            `two` : `Action`
                The second action to execute in parallel
        """
        from cocos.actions.interval_actions import Delay

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
        for i in self.actions:
            ret = ret and i.done()
        return ret

    def start(self):
        for a in self.actions:
            a.target = self.target
            a.start()

    def update(self, t):
        self.actions[0].update(t)
        self.actions[1].update(t)
        

    def __reversed__(self):
        return Reverse( self.actions[0]  ) | Reverse( self.actions[1] )

class Repeat(Action):
    """Repeats an action forever.

    Example::

        action = JumpBy( (200,0), 50,3,5)
        repeat = Repeat( action )
        sprite.do( repeat )

    Note: To repeat just a finite amount of time, just do action * times .
    """
    def init(self, action):
        """Init method.

        :Parameters:
            `action` : `Action` instance
                The action that will be repeated
        """
        self.original = action
        self.action = copy.deepcopy( action )

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


class _ReverseTime( IntervalAction ):
    """Executes an action in reverse order, from time=duration to time=0

    WARNING: Use this action carefully. This action is not
    sequenceable. Use it as the default ``__reversed__`` method
    of your own actions, but using it outside the ``__reversed``
    scope is not recommended.

    The default ``__reversed__`` method for all the `Grid3DAction` actions
    and `Camera3DAction` actions is ``_ReverseTime()``.
    """
    def init(self, other, *args, **kwargs):
        super(_ReverseTime, self).init(*args, **kwargs)
        self.other = other
        self.duration = self.other.duration
        
    def start(self):
        self.other.target = self.target
        super(_ReverseTime, self).start()
        self.other.start()
        
    def stop(self):
        super(_ReverseTime,self).stop()
    
    def update(self, t):
        self.other.update(1-t)
    
    def __reversed__(self):
        return self.other
