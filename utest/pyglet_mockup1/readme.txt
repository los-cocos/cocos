
pyglet mockup 1


This is work in progress.
Grown from an empty package to the current form in the spirit of TDD: just
adding the minimal code that allows to run tests related to actions.


Overview:

Keep the most near to do-nothing, remember-nothing as possible.
Thus, it accepts the most basic calls from cocos and does nothing nor remembers
nothing for this calls.
The only exception is pyglet.window.Window which stores the width, size passed
by director.init, because director.window.width and director.window.height are
widely used in cocos code.

As of 2014 06 I prefer to let pyglet mockup modules be empty and inject
necessary content in pyglet/__init__.py


What not to add:

pyglet objects, functions or methods with low count usage from cocos.
In general, code that effectively does or memorize something.
In particular, do not capture or do anything with glZzz calls; it is fine to
add a signature/pass, but only for commonly used functions.


Capabilities:

 pyglet.window.Window can be instantiated, it only provides width and height
 and accepts call to 'clear' method
 
 pyglet.event.EventHandler accepts calls to method
 dispatch_event(self, event_type, *args)
 and it will record the call with
        self._utest_recorded_events.append((event_type, args))
(remember to clear the record before the critical section you want to test)

 pyglet.version will return "1.1.4"
 Director can be instantiated
 from cocos.director import director works
 director.get_window_size() works
 CocosNode and all the actions in BaseActions can be instantiated
 pyglet.clock.schedule ( also unschedule, etc) accepted (non memorized)
 some GL constants and gl functions are accepted (if you load them with
 from pyglet.gl import *).
 you can 'import cocos.layer'; the classes ScrollingManager and ScrollableLayer
 can be imported


 
