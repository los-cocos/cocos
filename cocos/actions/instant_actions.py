#
# cocos2d Instant Actions
#
'''Instant Actions

Instant Actions
===============

Instant actions are immediate actions. They don't have a duration like
the Interval Actions.


'''

__docformat__ = 'restructuredtext'
import copy
from base_actions import *

__all__ = [
            'Place',                            # placement action
            'CallFunc','CallFuncS',             # Calls a function
            'Hide','Show','ToggleVisibility',   # Visibility actions
            'DoAction',
            ]

class Place( InstantAction ):
    """Place the `CocosNode` object in the position x,y.

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
    """Hides the `CocosNode` object. To show it again call the `Show` () action

    Example::

        action = Hide()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = False

    def __reversed__(self):
        return Show()

class Show( InstantAction ):
    """Shows the `CocosNode` object. To hide it call the `Hide` () action

    Example::

        action = Show()
        sprite.do( action )
    """
    def start(self):
        self.target.visible = True

    def __reversed__(self):
        return Hide()

class ToggleVisibility( InstantAction ):
    """Toggles the visible attribute of a `CocosNode` object

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


