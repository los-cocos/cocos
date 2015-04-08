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
"""Instant Actions

Instant Actions
===============

Instant actions are immediate actions. They don't have a duration like
the Interval Actions.


"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import copy
from .base_actions import *

__all__ = ['Place',                               # placement action
           'CallFunc', 'CallFuncS',               # Calls a function
           'Hide', 'Show', 'ToggleVisibility', ]  # Visibility actions


class Place(InstantAction):
    """Place the `CocosNode` object in the position x,y.

    Example::

        action = Place((320,240))
        sprite.do(action)
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


class Hide(InstantAction):
    """Hides the `CocosNode` object. To show it again call the `Show` () action

    Example::

        action = Hide()
        sprite.do(action)
    """
    def start(self):
        self.target.visible = False

    def __reversed__(self):
        return Show()


class Show(InstantAction):
    """Shows the `CocosNode` object. To hide it call the `Hide` () action

    Example::

        action = Show()
        sprite.do(action)
    """
    def start(self):
        self.target.visible = True

    def __reversed__(self):
        return Hide()


class ToggleVisibility(InstantAction):
    """Toggles the visible attribute of a `CocosNode` object

    Example::

        action = ToggleVisibility()
        sprite.do(action)
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

        action = CallFunc(my_func)
        sprite.do(action)
    """
    def init(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def start(self):
        self.func(*self.args, **self.kwargs)

    def __deepcopy__(self, memo):
        return copy.copy(self)

    def __reversed__(self):
        return self


class CallFuncS(CallFunc):
    """An action that will call a funtion with the target as the first argument

    Example::

        def my_func(sprite):
            print "hello baby"

        action = CallFuncS(my_func)
        sprite.do(action)
        """
    def start(self):
        self.func(self.target, *self.args, **self.kwargs)
