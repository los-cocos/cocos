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
            'IntervalAction', 'InstantAction',  # Important Subclasses 
            'sequence','spawn','loop', 'Repeat',# Generic Operators
            'Reverse','_ReverseTime',           # Reverse
            ]

class Action(object):
    '''Mother of all actions'''
    def __init__(self, *args, **kwargs):
        self.duration = None # The base action has potentially infinite duration
        self.init(*args, **kwargs)
        self.target = None              #: `CocosNode` object that is the target of the action
        self._elapsed = 0.0
        self._done = False
        self.scheduled_to_remove = False # exclusive use by cocosnode.remove_action

    def init(self):
        """
        Gets called at initialization time, before a target is defined.
        Typical use is store parameters needed by the action.
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
        It will be called from the entity that pumps the action ( cocosnode,
        or a compound action)
        """
        self.target = None        

    def step(self, dt):
        """
        Gets called every frame. `dt` is the number of seconds that elapsed
        since the last call. If there was a pause and resume in the middle,
        the actual elapsed time may be bigger.

        This function will only be called by the `Layer`, but interval actions will
        be updated with the `IntervalAction.update` method.
        """
        self._elapsed += dt

    def done(self):
        """
        False while the step method must be called.
        """
        return self._done

    def __add__(self, action):
        """Sequence Action"""
        return sequence(self, action)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return  Loop_Action(self, other)

    def __or__(self, action):
        """Is the Spawn Action"""
        return spawn(self, action)

    def __reversed__(self):
        raise Exception("Action %s cannot be reversed"%(self.__class__.__name__))


class IntervalAction( Action ):
    """
    IntervalAction()

    Interval Actions are the ones that have fixed duration, known at the
    instantiation time, and, conceptually, the expected duration must be
    positive.
    Degeneratated cases, when a particular instance gets a zero duration are
    allowed for convenience, and .update(1) is guaranted to be called
    
    For example: `MoveTo` , `MoveBy` , `RotateBy` are Interval Actions, while
    `Place`, `Show` and `CallFunc` aren't.

    While
    RotateBy(angle, duration) will usually receive a positive duration, it
    will accept duration = 0, to ease on cases like
    action = RotateBy( angle, a-b )
    """
    def step(self, dt):
        """
        Dont customize this method.
        It is not guaranted to be called when used with special modifiers.
        It is guaranted to be called in the usage cocosnode.do(action).
        You customize the action stepping by overriding .update
        """
        self._elapsed += dt
        try:
            self.update( min(1, self._elapsed/self.duration ) )
        except ZeroDivisionError:
            self.update(1.0)

    def update(self, t):
        """Gets called on every frame
        't' is the time elapsed normalized to [0, 1]
        If this action takes 5 seconds to execute, `t` will be equal to 0
        at 0 seconds. `t` will be 0.5 at 2.5 seconds and `t` will be 1 at 5sec.
        This method must not use self._elapsed, which
        is not guaranted to be updated
        """
        pass

    def done(self):
        """
        In the usage cocosnode.do(action) this method is reliable.
        When the action is used as a component for special modifiers,
        if the modifier code dont call .step then you cant relly on
        this method.
        """
        return self._elapsed >= self.duration

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return  Loop_IntervalAction(self, other)


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
    Instant actions are actions that promises to do nothing when the
    methods step, update, and stop are called.
    Any changes that the action must perform on his target will be done in the
    .start() method
    The interface must be keept compatible with IntervalAction to allow using
    InstantActions with the special operators / modifiers.
    """
    duration = 0.0

    def step(self, dt):
        """does nothing - dont override"""
        pass

    def start(self):
        """
        Here we must do out stuff
        """
        pass

    def done(self):
        return True

    def update(self, t):
        """does nothing - dont override
        """
        pass

    def stop(self):
        """does nothing - dont override
        """

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return  Loop_InstantAction(self, other)

def loop(action, times):
    return action * times
            
class Loop_Action(Action):
    def init(self, one, times):
        self.one = one
        self.times = times

    def start(self):
        self.current_action = copy.deepcopy(self.one)
        self.current_action.target = self.target
        self.current_action.start()

    def step(self, dt):
        self._elapsed += dt
        self.current_action.step(dt)
        if self.current_action.done():
            self.current_action.stop()
            self.times -= 1
            if self.times == 0:
                self._done = True
            else:
                self.current_action = copy.deepcopy(self.one)
                self.current_action.target = self.target
                self.current_action.start()

    def stop(self):
        if not self._done:
            self.current_action.stop()

class Loop_Instant_Action(InstantAction):
    def init(one, times):
        self.one = one
        self.times = times

    def start(self):
        for i in xrange(self.times):
            cpy = copy.deepcopy(self.one)
            cpy.start()

class Loop_IntervalAction(IntervalAction):
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
            
    def stop(self):#todo: need to support early stop 
        self.current_action.update(1)
        self.current_action.stop()
        
    def __reversed__(self):
        return Loop( Reverse(self.one), self.times )

def sequence(action_1, action_2):
    if action_1.duration is None or action_2.duration is None:
        cls = Sequence_Action
    elif (isinstance(action_1,InstantAction) and
          isinstance(action_2, InstantAction)):
        cls = Sequence_InstantAction
    else:
        cls = Sequence_IntervalAction
    return cls(action_1, action_2)

class Sequence_Action(Action):
    """ at least one operand must have duration==None """
    def init(self,  one, two, **kwargs ):
        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)
        self.first = True

    def start(self):
        self.one.target = self.target
        self.two.target = self.target
        self.current_action = self.one
        self.current_action.start()
        if self.current_action.done():
            self._next_action()

    def step(self, dt):
        self._elapsed += dt
        self.current_action.step(dt)
        if self.current_action.done():
            self._next_action()

    def _next_action(self):
        self.current_action.stop()
        if self.first:
            self.first = False
            self.current_action = self.two
            self.current_action.start()
            if self.current_action.done():
                self._done = True
        else:
            self.current_action = None
            self._done = True

    def stop(self):
        if self.current_action:
            self.current_action.stop()

    def __reversed__(self):
        return sequence( Reverse(self.two), Reverse(self.one) )

        
class Sequence_InstantAction(InstantAction):
    """ both operands must be InstantActions """
    def init(self,  one, two, **kwargs ):
        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)

    def start(self):
        self.one.target = self.target
        self.two.target = self.target
        self.one.start()
        self.two.start()
        
    def __reversed__(self):
        return Sequence_InstantAction( Reverse(self.two), Reverse(self.one) )
    


class Sequence_IntervalAction(IntervalAction):
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
        
        self.duration = float(self.one.duration + self.two.duration)
        try:
            self.split = self.one.duration / self.duration
        except ZeroDivisionError:
            self.split = 0.0
        self.last = None

    def start(self):
        self.one.target = self.target
        self.two.target = self.target
        self.one.start()
        self.last = 0 #index in self.actions
        if self.one.duration==0.0:
            self.one.update(1.0)
            self.one.stop()
            self.two.start()
            self.last = 1
####            if self.two.duration==0.0:
####                self.two.update(1.0)
####                self.two.stop()
##        else:
##            self.last = 1


    def __repr__(self):
        return "( %s + %s )" %( self.one, self.two )

    def update(self, t):
        current = t>=self.split
        if current!=self.last:
            self.actions[self.last].update(1.0)
            self.actions[self.last].stop()
            self.last = current
            self.actions[self.last].start()
        if current==0:
            try:
                sub_t = t/self.split
            except ZeroDivisionError:
                sub_t = 1.0
        else:
            try:
                sub_t = (t - self.split) / (1.0 - self.split)
            except ZeroDivisionError:
                sub_t = 1.0
        self.actions[current].update(sub_t)

    def stop(self):
        if self.last:
            self.two.stop()
        else:
            self.one.stop()
        
    def __reversed__(self):
        return Sequence_IntervalAction( Reverse(self.two), Reverse(self.one) )

def spawn(action_1, action_2):
    if action_1.duration is None or action_2.duration is None:
        cls = Spawn_Action
    elif (isinstance(action_1,InstantAction) and
          isinstance(action_2, InstantAction)):
        cls = Spawn_InstantAction
    else:
        cls = Spawn_IntervalAction
    return cls(action_1, action_2)


class Spawn_Action(Action):
    """ at least one operand must have duration==None """
    # el Delay podria ser util para revert
    def init(self, one, two):
        one = copy.deepcopy(one)
        two = copy.deepcopy(two)
        self.actions = [one, two]

    def start(self):
        for action in self.actions:
            action.target = self.target
            action.start()

    def step(self, dt):
        if len(self.actions)==2:
            self.actions[0].step(dt)
            if self.actions[0].done():
                self.actions[0].stop()
                self.actions = self.actions[1:]
        if self.actions:
            self.actions[-1].step(dt)
            if self.actions[-1].done():
                self.actions[-1].stop()
                self.actions = self.actions[:-1]
        self._done = len(self.actions)==0

    def stop(self):
        for e in self.actions:
            print 'en el loop, name:', e.name
            e.stop()

    def __reversed__(self):
        return Reverse( self.actions[0]  ) | Reverse( self.actions[1] )

Spawn_InstantAction = Sequence_InstantAction

class Spawn_IntervalAction(IntervalAction):
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
        self.duration = max(one.duration, two.duration)

        if one.duration > two.duration:
            two = two + Delay( one.duration-two.duration )
        elif two.duration > one.duration:
            one = one + Delay( two.duration-one.duration )

        self.actions = [one, two]

    def start(self):
        for a in self.actions:
            a.target = self.target
            a.start()

    def update(self, t):
        self.actions[0].update(t)
        self.actions[1].update(t)
        self._done = (t >= 1.0)
        if self._done:
            self.actions[0].stop()
            self.actions[1].stop()            

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
        self.duration = None
        self.original = action
        self.action = copy.deepcopy( action )

    def start(self):
        self.action.target = self.target
        self.action.start()

    def step(self, dt):
        self.action.step(dt)
        if self.action.done():
            self.action.stop()
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
