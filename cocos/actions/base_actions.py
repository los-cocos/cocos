# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
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
"""Foundation for all actions

Actions
=======

Actions purpose is to modify along the time some trait of an object.
The object that the action will modify is the action's target.
Usually the target will be an instance of some CocosNode subclass.

Example::

    MoveTo(position, duration)

the target will move smoothly over the segment
(target.position, action position parameter), reaching the final position
after duration seconds have elapsed.

Cocos also provide some powerful operators to combine or modify actions, the
more important s being:

**sequence operator:**   action_1 + action_2 -> action_result

where action_result performs by first doing all that action_1 would do and
then perform all that action_2 would do

Example use::

    move_2 = MoveTo((100, 100), 10) + MoveTo((200, 200), 15)

When activated, move_2 will move the target first to (100, 100), it will
arrive there 10 seconds after departure; then it will move to (200, 200),
and will arrive there 10 seconds after having arrived to (100, 100)

**spawn operator:**  action_1 | action_2 -> action_result

where action_result performs by doing what would do action_1 in parallel with
what would perform action_2

Example use::

    move_rotate = MoveTo((100,100), 10) | RotateBy(360, 5)

When activated, move_rotate will move the target from the position at the
time of activation to (100, 100); also in the first 5 seconds target will
be rotated 360 degrees

**loop operator:**   action_1 * n -> action_result

Where n non negative integer, and action result would repeat n times in a
row the same that action_1 would perform.

Example use::

    rotate_3 = RotateBy(360, 5) * 3

When activated, rotate_3 will rotate target 3 times, spending 5 sec in each
turn.


Action instance roles
+++++++++++++++++++++

Action subclass: a detailed cualitative description for a change

An Action instance can play one of the following roles

Template Role
-------------

The instance knows all the details to perform,
except a target has not been set.
In this role only __init__ and init should be called.
It has no access to the concrete action target.
The most usual way to obtain an action in the template mode is
by calling the constructor of some Action subclass.

Example::

    position = (100, 100); duration = 10
    move = MoveTo(position, duration)
    move is playing here the template role.


Worker role
-----------

Carry on with the changes desired when the action is initiated.
You obtain an action in the worker role by calling the method
do in a cocosnode instance, like::

    worker_action = cocosnode.do(template_action, target=...)

The most usual is to call without the target kw-param, thus by default
setting target to the same cocosnode that performs the do.
The worker action begins to perform at the do call, and will carry on
with the desired modifications to target in subsequent frames.
If you want the capabilty to stop the changes midway, then you must
retain the worker_action returned by the do and then, when you want stop
the changes, call::

    cocosnode.remove_action(worker_action)
    ( the cocosnode must be the same as in the do call )

Also, if your code need access to the action that performs the changes,
have in mind that you want the worker_action (but this is discouraged,

Example::

     position = (100, 100); duration = 10
     move = MoveTo(position, duration)
     blue_bird = Bird_CocosNode_subclass(...)
     blue_move = blue_bird.do(move)

Here move plays the template role and blue_move plays the worker role.
The target for blue_move has been set for the do method.
When the do call omits the target parameter it defaults to the cocosnode where
the do is called, so in the example the target for blue_move is blue_bird.
In subsequents frames after this call, the blue_bird will move to the position
(100, 100), arriving there 10 seconds after the do was executed.

From the point of view of a worker role action, the actions life
can be mimicked by::

    worker_action = deepcopy(template_action)
    worker_action.target = some_obj
    worker_action.start()
    for dt in frame.next():
        worker_action.step(dt)
        if premature_termination() or worker_action.done():
            break
    worker_action.stop()

Component role
--------------

Such an instance is created and stored into an Action class instance
that implements an Action operator (a composite action).
Carries on with the changes desired on behalf of the composite action.
When the composite action is not instance of IntervalAction, the
perceived life can be mimicked as in the worker role.
When the composite action is instance of IntervalAction, special rules apply.
For examples look at code used in the implementation of any operator, like
Sequence_Action or Sequence_IntervalAction.

Restrictions and Capabilities for the current design and implementation
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Worker Independence
-------------------

Multiple worker actions can be obtained from a single template action, and
they wont interfere between them when applied to different targets.

Example::

     position = (100, 0); duration = 10
     move = MoveBy(position, duration)

     blue_bird = Sprite("blue_bird.png")
     blue_bird.position = (0, 100)
     blue_move = blue_bird.do(move)

     red_bird = Sprite("red_bird.png")
     red_bird.position = (0, 200)
     red_move = blue_bird.do(move)

    Here we placed two birds at the left screen border, separated vertically
    by 100.
    move is the template_action: full details on changes, still no target
    blue_move, red_move are worker_action 's: obtained by a node.do, have all
    the details plus the target; they will perform the changes along the time.
    What we see is both birds moving smooth to right by 100, taking 10 seconds
    to arrive at final position.
    Note that even if both worker actions derive for the same template, they
    don't interfere one with the other.


A worker action instance should not be used as a template
---------------------------------------------------------

You will not get tracebacks, but the second worker action most surelly will
have a corrupt workspace, that will produce unexpected behavior.

Posible fights between worker actions over a target member
----------------------------------------------------------

If two actions that are active at the same time try to change the same
target's member(s), the resulting change is computationally well defined, but
can be somewhat unexpected by the programmer.

Example::

    guy = Sprite("grossini.png")
    guy.position = (100, 100)
    worker1 = guy.do(MoveTo((400, 100), 3))
    worker2 = guy.do(MoveBy((0, 300), 3))
    layer.add(guy)

Here the worker1 action will try to move to (400, 100), while the worker2 action
will try to move 300 in the up direction.
Both are changing guy.position in each frame.

What we see on screen, in the current cocos implementation, is the guy moving up,
like if only worker2 were active.
And, by physics, the programmer expectation probably guessed more like a
combination of both movements.

Note that the unexpected comes from two actions trying to control the same target
member. If the actions were changing diferent members, like position and
rotation, then no unexpected can happen.

The fighting can result in a behavior that is a combination of both workers, not one
a 'winning' one. It entirely depends on the implementation from each action.
It is possible to write actions than in a fight will show additive behavoir,
by example::

    import cocos.euclid as eu
    class MoveByAdditive(ac.Action):
        def init( self, delta_pos, duration ):
            try:
                self.delta_pos = eu.Vector2(*delta_pos)/float(duration)
            except ZeroDivisionError:
                duration = 0.0
                self.delta_pos = eu.Vector2(*delta_pos)
            self.duration = duration

        def start(self):
            if self.duration==0.0:
                self.target.position += self.delta_pos
                self._done = True

        def step(self, dt):
            old_elapsed = self._elapsed
            self._elapsed += dt
            if self._elapsed > self.duration:
                dt = self.duration - old_elapsed
                self._done = True
            self.target.position += dt*self.delta_pos

    guy = Sprite("grossini.png")
    guy.position = (100, 100)
    worker1 = guy.do(MoveByAdditive((300, 0), 3))
    worker2 = guy.do(MoveByAdditive((0, 300), 3))
    layer.add(guy)

Here the guy will mode in diagonal, ending 300 right and 300 up, the two
actions have combined.


Action's instances in the template role must be (really) deepcopyiable
----------------------------------------------------------------------

Beginers note: if you pass in init only floats, ints, strings, dicts or tuples
of the former you can skip this section and revisit later.

If the action template is not deepcopyiable, you will get a deepcopy exception,
complaining it can't copy something

If you cheat deepcopy by overriding __deepcopy__ in your class like::

    def __deepcopy__(self):
        return self

you will not get a traceback, but the Worker Independence will broke, the Loop
and Repeat operators will broke, and maybe some more.

The section name states a precise requeriment, but it is a bit concise. Let see
some common situations where you can be in trouble and how to manage them.

  - you try to pass a CocosNode instance in init, and init stores that in an
    action member

  - you try to pass a callback f = some_cocosnode.a_method, with the idea that
    it shoud be called when some condition is meet, and init stores it in an
    action member

  - You want the action access some big decision table, static in the sense it
    will not change over program execution. Even if is deepcopyable, there's
    no need to deepcopy.

Workarounds:

    - store the data that you do not want to deepcopy in some member in the
      cocosnode

    - use an init2 fuction to pass the params you want to not deepcopy::

        worker = node.do(template)
        worker.init2(another_cocosnode)

      (see test_action_non_interval.py for an example)


Future:
Next cocos version probably will provide an easier mechanism to designate some
parameters as references.


Overview main subclasses
++++++++++++++++++++++++

All action classes in cocos must be subclass of one off the following:

    - Action
    - IntervalAction (is itself subclass of Action)
    - InstantAction  (is itself subclass of IntervalAction)

InstantAction
-------------

The task that must perform happens in only one call, the start method.
The duration member has the value zero.
Examples::

    Place(position) : does target.position <- position
    CallFunc(f, *args, **kwargs) : performs the call f(*args,**kwargs)

IntervalAction
--------------

The task that must perform is spanned over a number of frames.
The total time needed to complete the task is stored in the member duration.
The action will cease to perform when the time elapsed from the start call
reachs duration.
A proper IntervalAction must adhere to extra rules, look in the details section
Examples::

    MoveTo(position, duration)
    RotateBy(angle, duration)

Action
------

The most general posible action class.
The task that must perform is spanned over a number of frames.
The time that the action would perfom is undefined, and member duration has
value None.
Examples::

    RandomWalk(fastness)

Performs:

  - selects a random point in the screen
  - moves to it with the required fastness
  - repeat

This action will last forever.

::

    Chase(fastness, chasee)

Performs:

  - at each frame, move the target toward the chasee with the specified
    fastness.
  - Declare the action as done when the distance from target to
    chasee is less than 10.

If fastness is greather than the chasee fastness this action will certainly
terminate, but we dont know how much time when the action starts.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import copy

__all__ = ['Action',                               # Base Class
           'IntervalAction', 'InstantAction',      # Important Subclasses
           'sequence', 'spawn', 'loop', 'Repeat',  # Generic Operators
           'Reverse', '_ReverseTime', ]            # Reverse


class Action(object):
    """The most general action"""
    def __init__(self, *args, **kwargs):
        """dont override - use init"""
        self.duration = None  # The base action has potentially infinite duration
        self.init(*args, **kwargs)
        self.target = None              #: `CocosNode` object that is the target of the action
        self._elapsed = 0.0
        self._done = False
        self.scheduled_to_remove = False  # exclusive use by cocosnode.remove_action

    def init(*args, **kwargs):
        """
        Gets called by __init__ with all the parameteres received,
        At this time the target for the action is unknown.
        Typical use is store parameters needed by the action.
        """
        pass

    def start(self):
        """
        External code sets self.target and then calls this method.
        Perform here any extra initialization needed.
        """
        pass

    def stop(self):
        """
        When the action must cease to perform this function is called by
        external code; after this call no other method should be called.
        """
        self.target = None

    def step(self, dt):
        """
        Gets called every frame. `dt` is the number of seconds that elapsed
        since the last call.
        """
        self._elapsed += dt

    def done(self):
        """
        False while the step method must be called.
        """
        return self._done

    def __add__(self, action):
        """sequence operator - concatenates actions
            action1 + action2 -> action_result
            where action_result performs as:
            first do all that action1 would do; then
            perform all that action2 would do
        """
        return sequence(self, action)

    def __mul__(self, other):
        """repeats ntimes the action
        action * n -> action_result
        where action result performs as:
        repeat n times the changes that action would do
        """
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return Loop_Action(self, other)

    def __or__(self, action):
        """spawn operator -  runs two actions in parallel
        action1 | action2 -> action_result
        """
        return spawn(self, action)

    def __reversed__(self):
        raise Exception("Action %s cannot be reversed" % self.__class__.__name__)


class IntervalAction(Action):
    """
    IntervalAction()

    Interval Actions are the ones that have fixed duration, known when the
    worker instance is created, and, conceptually, the expected duration must
    be positive.
    Degeneratated cases, when a particular instance gets a zero duration, are
    allowed for convenience.

    IntervalAction adds the method update to the public interfase, and it
    expreses the changes to target as a function of the time elapsed, relative
    to the duration, ie f(time_elapsed/duration).
    Also, it is guaranted that in normal termination .update(1.0) is called.
    Degenerate cases, when a particular instance gets a zero duration, also
    are guaranted to call .update(1.0)
    Note that when a premature termination happens stop will be called but
    update(1.0) is not called.

    Examples: `MoveTo` , `MoveBy` , `RotateBy` are strictly Interval Actions,
    while `Place`, `Show` and `CallFunc` aren't.

    While
    RotateBy(angle, duration) will usually receive a positive duration, it
    will accept duration = 0, to ease on cases like
    action = RotateBy( angle, a-b )
    """
    def step(self, dt):
        """
        Dont customize this method: it will not be called when in the component
        role for certain composite actions (like Sequence_IntervalAction).
        In such situation the composite will calculate the suitable t and
        directly call .update(t)
        You customize the action stepping by overriding .update
        """
        self._elapsed += dt
        try:
            self.update(min(1, self._elapsed / self.duration))
        except ZeroDivisionError:
            self.update(1.0)

    def update(self, t):
        """Gets called on every frame
        't' is the time elapsed normalized to [0, 1]
        If this action takes 5 seconds to execute, `t` will be equal to 0
        at 0 seconds. `t` will be 0.5 at 2.5 seconds and `t` will be 1 at 5sec.
        This method must not use self._elapsed, which is not guaranted to be
        updated.
        """
        pass

    def done(self):
        """
        When in the worker role, this method is reliable.
        When in the component role, if the composite spares the call to
        step this method cannot be relied (an then the composite must decide
        by itself when the action is done).
        Example of later situation is Sequence_IntervalAction.
        """
        return self._elapsed >= self.duration

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return Loop_IntervalAction(self, other)


def Reverse(action):
    """Reverses the behavior of the action

    Example::

        # rotates the sprite 180 degrees in 2 seconds counter clockwise
        action = Reverse( RotateBy( 180, 2 ) )
        sprite.do( action )
    """
    return action.__reversed__()


class InstantAction(IntervalAction):
    """
    Instant actions are actions that promises to do nothing when the
    methods step, update, and stop are called.
    Any changes that the action must perform on his target will be done in the
    .start() method
    The interface must be keept compatible with IntervalAction to allow the
    basic operators to combine an InstantAction with an IntervalAction and
    give an IntervalAction as a result.
    """
    def __init__(self, *args, **kwargs):
        super(IntervalAction, self).__init__(*args, **kwargs)
        self.duration = 0.0

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
        pass

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply actions by ints")
        if other <= 1:
            return self
        return Loop_InstantAction(self, other)


def loop(action, times):
    return action * times


class Loop_Action(Action):
    """Repeats one Action for n times
    """
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


class Loop_InstantAction(InstantAction):
    """Repeats one InstantAction for n times
    """
    def init(self, one, times):
        self.one = one
        self.times = times

    def start(self):
        for i in range(self.times):
            cpy = copy.deepcopy(self.one)
            cpy.start()


class Loop_IntervalAction(IntervalAction):
    """Repeats one IntervalAction for n times
    """
    def init(self, one, times):
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
        return "( %s * %i )" % (self.one, self.times)

    def update(self, t):
        current = int(t * float(self.times))
        new_t = (t - (current * (1. / self.times))) * self.times

        if current >= self.times:  # we are done
            return
        # just more dt for the current action
        elif current == self.last:
            self.current_action.update(new_t)
        else:
            # finish the last action
            self.current_action.update(1)
            self.current_action.stop()

            for i in range(self.last + 1, current):
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

    def stop(self):  # todo: need to support early stop
        self.current_action.update(1)
        self.current_action.stop()

    def __reversed__(self):
        return Loop_IntervalAction(Reverse(self.one), self.times)


def sequence(action_1, action_2):
    """Returns an action that runs first action_1 and then action_2
       The returned action will be instance of the most narrow class
       posible in InstantAction, IntervalAction, Action
    """

    if isinstance(action_1, InstantAction) and isinstance(action_2, InstantAction):
        cls = Sequence_InstantAction
    elif (isinstance(action_1, IntervalAction) and
          isinstance(action_2, IntervalAction)):
        cls = Sequence_IntervalAction
    else:
        cls = Sequence_Action
    return cls(action_1, action_2)


class Sequence_Action(Action):
    """implements sequence when the result cannot be expresed as IntervalAction
        At least one operand must have duration==None """
    def init(self,  one, two, **kwargs):
        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)
        self.first = True

    def start(self):
        self.one.target = self.target
        self.two.target = self.target
        self.current_action = self.one
        self.current_action.start()

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
        return sequence(Reverse(self.two), Reverse(self.one))


class Sequence_InstantAction(InstantAction):
    """implements sequence when the result can be expresed as InstantAction
        both operands must be InstantActions """
    def init(self,  one, two, **kwargs):
        self.one = copy.deepcopy(one)
        self.two = copy.deepcopy(two)

    def start(self):
        self.one.target = self.target
        self.two.target = self.target
        self.one.start()
        self.two.start()

    def __reversed__(self):
        return Sequence_InstantAction(Reverse(self.two), Reverse(self.one))


class Sequence_IntervalAction(IntervalAction):
    """implements sequence when the result can be expresed as IntervalAction but
        not as InstantAction
    """
    def init(self,  one, two, **kwargs):
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
        self.last = 0  # index in self.actions
        if self.one.duration == 0.0:
            self.one.update(1.0)
            self.one.stop()
            self.two.start()
            self.last = 1

    def __repr__(self):
        return "( %s + %s )" % (self.one, self.two)

    def update(self, t):
        current = t >= self.split
        if current != self.last:
            self.actions[self.last].update(1.0)
            self.actions[self.last].stop()
            self.last = current
            self.actions[self.last].start()
        if current == 0:
            try:
                sub_t = t / self.split
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
        return Sequence_IntervalAction(Reverse(self.two), Reverse(self.one))


def spawn(action_1, action_2):
    """Returns an action that runs action_1 and action_2 in paralel.
       The returned action will be instance of the most narrow class
       posible in InstantAction, IntervalAction, Action
    """
    if isinstance(action_1, InstantAction) and isinstance(action_2, InstantAction):
        cls = Spawn_InstantAction
    elif (isinstance(action_1, IntervalAction) and
          isinstance(action_2, IntervalAction)):
        cls = Spawn_IntervalAction
    else:
        cls = Spawn_Action
    return cls(action_1, action_2)


class Spawn_Action(Action):
    """implements spawn when the result cannot be expresed as IntervalAction
        At least one operand must have duration==None """
    def init(self, one, two):
        one = copy.deepcopy(one)
        two = copy.deepcopy(two)
        self.actions = [one, two]

    def start(self):
        for action in self.actions:
            action.target = self.target
            action.start()

    def step(self, dt):
        if len(self.actions) == 2:
            self.actions[0].step(dt)
            if self.actions[0].done():
                self.actions[0].stop()
                self.actions = self.actions[1:]
        if self.actions:
            self.actions[-1].step(dt)
            if self.actions[-1].done():
                self.actions[-1].stop()
                self.actions = self.actions[:-1]
        self._done = len(self.actions) == 0

    def stop(self):
        for e in self.actions:
            e.stop()

    def __reversed__(self):
        return Reverse(self.actions[0]) | Reverse(self.actions[1])


class Spawn_IntervalAction(IntervalAction):
    """implements spawn when the result cannot be expresed as InstantAction
    """

    def init(self, one, two):
        from cocos.actions.interval_actions import Delay

        one = copy.deepcopy(one)
        two = copy.deepcopy(two)
        self.duration = max(one.duration, two.duration)

        if one.duration > two.duration:
            two = two + Delay(one.duration - two.duration)
        elif two.duration > one.duration:
            one = one + Delay(two.duration - one.duration)

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
        return Reverse(self.actions[0]) | Reverse(self.actions[1])


class Spawn_InstantAction(InstantAction):
    """implements spawn when the result can be expresed as InstantAction"""
    def init(self, one, two):
        one = copy.deepcopy(one)
        two = copy.deepcopy(two)
        self.actions = [one, two]

    def start(self):
        for action in self.actions:
            action.target = self.target
            action.start()


class Repeat(Action):
    """Repeats an action forever.
        Applied to InstantAction s means once per frame.

    Example::

        action = JumpBy( (200,0), 50,3,5)
        repeat = Repeat( action )
        sprite.do( repeat )

    Note: To repeat just a finite amount of time, just do action * times.
    """
    def init(self, action):
        """Init method.

        :Parameters:
            `action` : `Action` instance
                The action that will be repeated
        """
        self.duration = None
        self.original = action
        self.action = copy.deepcopy(action)

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


class _ReverseTime(IntervalAction):
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
        super(_ReverseTime, self).stop()

    def update(self, t):
        self.other.update(1 - t)

    def __reversed__(self):
        return self.other
