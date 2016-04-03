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
"""
cocos.director.director is the singleton that creates and handles the main ``Window``
and manages the logic behind the ``Scenes``.

Initializing
------------

The first thing to do, is to initialize the ``director``::

    from cocos.director import director
    director.init( parameters )

This will initialize the director, and will create a display area
(a 640x480 window by default).
The parameters that are supported by director.init() are the same
parameters that are supported by pyglet.window.Window(), plus a few
cocos exclusive ones. They are all named parameters (kwargs).
See ``Director.init()`` for details.

Example::

    director.init( width=800, height=600, caption="Hello World", fullscreen=True )

Running a Scene
----------------

Once you have initialized the director, you can run your first ``Scene``::

    director.run( Scene( MyLayer() ) )

This will run a scene that has only 1 layer: ``MyLayer()``. You can run a scene
that has multiple layers. For more information about ``Layers`` and ``Scenes``
refer to the ``Layers`` and ``Scene`` documentation.

Once a scene is running you can do the following actions:

    * ``director.replace( new_scene ):``
        Replaces the running scene with the new_scene
        You could also use a transition. For example:
        director.replace( SplitRowsTransition( new_scene, duration=2 ) )

    * ``director.push( new_scene ):``
        The running scene will be pushed to a queue of scenes to run,
        and new_scene will be executed.

    * ``director.pop():``
        Will pop out a scene from the queue, and it will replace the running scene.

    * ``director.scene.end( end_value ):``
        Finishes the current scene with an end value of ``end_value``. The next scene
        to be run will be popped from the queue.

Other functions you can use are:

    * ``director.get_window_size():``
      Returns an (x,y) pair with the _logical_ dimensions of the display.
      The display might have been resized, but coordinates are always relative
      to this size. If you need the _physical_ dimensions, check the dimensions
      of ``director.window``


    * ``get_virtual_coordinates(self, x, y):``
      Transforms coordinates that belongs the real (physical) window size, to
      the coordinates that belongs to the virtual (logical) window. Returns
      an x,y pair in logical coordinates.

The director also has some useful attributes:

    * ``director.return_value``: The value returned by the last scene that
      called ``director.scene.end``. This is useful to use scenes somewhat like
      function calls: you push a scene to call it, and check the return value
      when the director returns control to you.

    * ``director.window``: This is the pyglet window handled by this director,
      if you happen to need low level access to it.

    * ``self.show_FPS``: You can set this to a boolean value to enable, disable
      the framerate indicator.

    * ``self.scene``: The scene currently active

"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import sys
from os import getenv
import warnings

import pyglet
from pyglet import window, event
from pyglet import clock
# from pyglet import media
from pyglet import gl

import cocos
import cocos.audio
import cocos.custom_clocks

if hasattr(sys, 'is_cocos_sphinx') and sys.is_cocos_sphinx:
    __all__ = ['director', 'Director', 'DefaultHandler']
else:
    __all__ = ['director', 'DefaultHandler']


class DefaultHandler(object):
    def __init__(self):
        super(DefaultHandler, self).__init__()
        self.wired = False

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.F and (modifiers & pyglet.window.key.MOD_ACCEL):
            director.window.set_fullscreen(not director.window.fullscreen)
            return True

        elif symbol == pyglet.window.key.P and (modifiers & pyglet.window.key.MOD_ACCEL):
            import cocos.scenes.pause as pause
            pause_sc = pause.get_pause_scene()
            if pause:
                director.push(pause_sc)
            return True

        elif symbol == pyglet.window.key.W and (modifiers & pyglet.window.key.MOD_ACCEL):
            # import wired
            if not self.wired:
                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glPolygonMode(gl.GL_FRONT, gl.GL_LINE)
                gl.glPolygonMode(gl.GL_BACK, gl.GL_LINE)
                # wired.wired.install()
                # wired.wired.uset4F('color', 1.0, 1.0, 1.0, 1.0 )
                self.wired = True
            else:
                gl.glEnable(gl.GL_TEXTURE_2D)
                gl.glPolygonMode(gl.GL_FRONT, gl.GL_FILL)
                gl.glPolygonMode(gl.GL_BACK, gl.GL_FILL)
                self.wired = False
                # wired.wired.uninstall()
            return True

        elif symbol == pyglet.window.key.X and (modifiers & pyglet.window.key.MOD_ACCEL):
            director.show_FPS = not director.show_FPS
            return True

        elif symbol == pyglet.window.key.I and (modifiers & pyglet.window.key.MOD_ACCEL):
            from .layer import PythonInterpreterLayer

            if not director.show_interpreter:
                if director.python_interpreter is None:
                    director.python_interpreter = cocos.scene.Scene(PythonInterpreterLayer())
                    director.python_interpreter.enable_handlers(True)
                director.python_interpreter.on_enter()
                director.show_interpreter = True
            else:
                director.python_interpreter.on_exit()
                director.show_interpreter = False
            return True

        elif symbol == pyglet.window.key.S and (modifiers & pyglet.window.key.MOD_ACCEL):
            import time
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot-%d.png' % (int(time.time())))
            return True

        if symbol == pyglet.window.key.ESCAPE:
            director.pop()
            return True


class Director(event.EventDispatcher):
    """Class that creates and handle the main Window and manages how
       and when to execute the Scenes

       You should not directly instantiate the class, instead you do::

            from cocos.director import director

       to access the only one Director instance.
       """
    #: a dict with locals for the interactive python interpreter (fill with what you need)
    interpreter_locals = {}

    def init(self, *args, **kwargs):
        """
        Initializes the Director creating the main window.

        There are a few cocos exclusive parameters, the rest are the
        standard pyglet parameters for pyglet.window.Window.__init__
        This docstring only partially list the pyglet parameters; a full
        list is available at pyglet Window API Reference at
        http://pyglet.org/doc/api/pyglet.window.Window-class.html

        :Parameters:
            `autoscale` : bool
                True: on window resizes, cocos will scale the view so that your
                app don't need to handle resizes.
                False: your app must include logic to deal with different window
                sizes along the session.
                Defaults to False
            `do_not_scale` : bool
                Deprecated. The logical negation of autoscale
            `audio_backend` : string
                one in ['pyglet','sdl']. Defaults to 'pyglet' for legacy support.
            `audio` : dict or None
                None or a dict providing parameters for the sdl audio backend.
                None: in this case a "null" audio system will be used, where all the
                sdl sound operations will be no-ops. This may be useful if you do not
                want to depend on SDL_mixer
                A dictionary with string keys; these are the arguments for setting up
                the audio output (sample rate and bit-width, channels, buffer size).
                The key names/values should match the positional arguments of
                http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.init
                The default value is {}, which means sound enabled with default
                settings


            `fullscreen` : bool
                Window is created in fullscreen. Default is False
            `resizable` : bool
                Window is resizable. Default is False
            `vsync` : bool
                Sync with the vertical retrace. Default is True
            `width` : int
                Window width size. Default is 640
            `height` : int
                Window height size. Default is 480
            `caption` : string
                Window title.
            `visible` : bool
                Window is visible or not. Default is True.

        :rtype: pyglet.window.Window
        :returns: The main window, an instance of pyglet.window.Window class.
        """

        #: whether or not the FPS are displayed
        self.show_FPS = False

        #: stack of scenes
        self.scene_stack = []

        #: scene that is being run
        self.scene = None

        #: this is the next scene that will be shown
        self.next_scene = None

        # python interpreter
        self.python_interpreter = None

        #: whether or not to show the python interpreter
        self.show_interpreter = False

        #: flag requesting app termination
        self.terminate_app = False

        # pop out the Cocos-specific flags

        # 'autoscale' / 'do_not_scale' - Scheduled for cleanup at v0.7
        if 'do_not_scale' in kwargs:
            warnings.warn("'do_not_scale' kw-param in director.init is deprecated, use 'autoscale'")
            if 'autoscale' in kwargs:
                warnings.warn("Conflict between deprecated 'do_not_scale' and 'autoscale', " +
                              "'autoscale' wins")
                self.autoscale = kwargs.pop('autoscale')
            else:
                self.autoscale = not kwargs.pop('do_not_scale')
        else:
            self.autoscale = kwargs.pop('autoscale', True)

        def _get_do_not_scale_window():
            warnings.warn('Access to deprecated director.do_not_scale_window')
            return not self.autoscale

        def _set_do_not_scale_window(v):
            warnings.warn('Access to deprecated director.do_not_scale_window')
            self.autoscale = not v
        do_not_scale_window = property(_get_do_not_scale_window, _set_do_not_scale_window)

        audio_backend = kwargs.pop('audio_backend', 'pyglet')
        audio_settings = kwargs.pop('audio', {})

        # handle pyglet 1.1.x vs 1.2dev differences in fullscreen
        self._window_virtual_width = kwargs.get('width', None)
        self._window_virtual_height = kwargs.get('height', None)
        if pyglet.version.startswith('1.1') and kwargs.get('fullscreen', False):
            # pyglet 1.1.x dont allow fullscreen with explicit width or height
            kwargs.pop('width', 0)
            kwargs.pop('height', 0)

        #: pyglet's window object
        self.window = window.Window(*args, **kwargs)

        # complete the viewport geometry info, both virtual and real,
        # also set the appropriate on_resize handler
        if self._window_virtual_width is None:
            self._window_virtual_width = self.window.width
        if self._window_virtual_height is None:
            self._window_virtual_height = self.window.height

        self._window_virtual_aspect = (
            self._window_virtual_width / float(self._window_virtual_height))

        self._offset_x = 0
        self._offset_y = 0

        if self.autoscale:
            resize_handler = self.scaled_resize_window
            self.set_projection = self.set_projection3D
        else:
            resize_handler = self.unscaled_resize_window
            self.set_projection = self.set_projection2D
        # the offsets and size for the viewport will be proper after this
        self._resize_no_events = True
        resize_handler(self.window.width, self.window.height)
        self._resize_no_events = False

        self.window.push_handlers(on_resize=resize_handler)

        self.window.push_handlers(self.on_draw)

        # opengl settings
        self.set_alpha_blending()

        # default handler
        self.window.push_handlers(DefaultHandler())

        # Environment variable COCOS2d_NOSOUND=1 overrides audio settings
        if getenv('COCOS2D_NOSOUND', None) == '1' or audio_backend == 'pyglet':
            audio_settings = None
        # if audio is not working, better to not work at all. Except if
        # explicitly instructed to continue
        if not cocos.audio._working and audio_settings is not None:
            from cocos.audio.exceptions import NoAudioError
            msg = "cocos.audio isn't able to work without needed dependencies. " \
                  "Try installing pygame for fixing it, or forcing no audio " \
                  "mode by calling director.init with audio=None, or setting the " \
                  "COCOS2D_NOSOUND=1 variable in your env."
            raise NoAudioError(msg)

        # Audio setup:
        # TODO: reshape audio to not screw unittests
        import os
        if not os.environ.get('cocos_utest', False):
            cocos.audio.initialize(audio_settings)

        return self.window

    fps_display = None

    def set_show_FPS(self, value):
        if value and self.fps_display is None:
            self.fps_display = clock.ClockDisplay()
        elif not value and self.fps_display is not None:
            self.fps_display.unschedule()
            self.fps_display = None

    show_FPS = property(lambda self: self.fps_display is not None, set_show_FPS)

    def run(self, scene):
        """Runs a scene, entering in the Director's main loop.

        :Parameters:
            `scene` : `Scene`
                The scene that will be run.
        """

        self._set_scene(scene)

        event_loop.run()

    def set_recorder(self, framerate, template="frame-%d.png", duration=None):
        """Will replace the app clock so that now we can ensure a steady
        frame rate and save one image per frame

        :Parameters
            `framerate`: int
                the number of frames per second
            `template`: str
                the template that will be completed with an in for the name of the files
            `duration`: float
                the amount of seconds to record, or 0 for infinite
        """
        clock = cocos.custom_clocks.get_recorder_clock(framerate, template, duration)
        cocos.custom_clocks.set_app_clock(clock)

    def on_draw(self):
        """Handles the event 'on_draw' from the pyglet.window.Window

            Realizes switch to other scene and app termination if needed
            Clears the window area
            The windows is painted as:

                - Render the current scene by calling it's visit method
                - Eventually draw the fps metter
                - Eventually draw the interpreter

            When the window is minimized any pending switch to scene will be
            delayed to the next de-minimizing time.
        """

        # typically True when window minimized
        if (self.window.width == 0 or self.window.height == 0) and not self.terminate_app:
            # if surface area is zero, we don't need to draw; also
            # we don't want to allow scene changes in this situation: usually
            # on_enter does some scaling, which would lead to division by zero
            return

        # handle scene changes and app termination
        if self.terminate_app:
            self.next_scene = None

        if self.next_scene is not None or self.terminate_app:
            self._set_scene(self.next_scene)

        if self.terminate_app:
            pyglet.app.exit()
            return

        self.window.clear()

        # draw all the objects
        gl.glPushMatrix()
        self.scene.visit()
        gl.glPopMatrix()

        # finally show the FPS
        if self.show_FPS:
            self.fps_display.draw()

        if self.show_interpreter:
            self.python_interpreter.visit()

    def push(self, scene):
        """Suspends the execution of the running scene, pushing it
        on the stack of suspended scenes. The new scene will be executed.

        :Parameters:
            `scene` : `Scene`
                It is the scene that will be run.
           """
        self.dispatch_event("on_push", scene)

    def on_push(self, scene):
        self.next_scene = scene
        self.scene_stack.append(self.scene)

    def pop(self):
        """If the scene stack is empty the appication is terminated.
            Else pops out a scene from the stack and sets as the running one.
        """
        self.dispatch_event("on_pop")

    def on_pop(self):
        if len(self.scene_stack) == 0:
            self.terminate_app = True
        else:
            self.next_scene = self.scene_stack.pop()

    def replace(self, scene):
        """Replaces the running scene with a new one. The running scene is terminated.

        :Parameters:
            `scene` : `Scene`
                It is the scene that will be run.
        """
        self.next_scene = scene

    def _set_scene(self, scene):
        """Makes scene the current scene

            Operates on behalf of the public scene switching methods
            User code must not call directly
        """
        # Even library code should not call it directly: instead set
        # ._next_scene and let 'on_draw' call here at the proper time

        self.next_scene = None

        # always true except for first scene in the app
        if self.scene is not None:
            self.scene.on_exit()
            self.scene.enable_handlers(False)

        old = self.scene
        self.scene = scene

        # always true except when terminating the app
        if self.scene is not None:
            # active scene is the top node
            self.scene.parent = None
            self.scene.enable_handlers(True)
            scene.on_enter()

        return old

    #
    # Window Helper Functions
    #
    def get_window_size(self):
        """Returns the size of the window when it was created, and not the
        actual size of the window.

        Usually you don't want to know the current window size, because the
        Director() hides the complexity of rescaling your objects when
        the Window is resized or if the window is made fullscreen.

        If you created a window of 640x480, the you should continue to place
        your objects in a 640x480 world, no matter if your window is resized or not.
        Director will do the magic for you.

        :rtype: (x,y)
        :returns: The size of the window when it was created
        """
        return self._window_virtual_width, self._window_virtual_height

    def get_virtual_coordinates(self, x, y):
        """Transforms coordinates that belongs the *real* window size, to the
        coordinates that belongs to the *virtual* window.

        For example, if you created a window of 640x480, and it was resized
        to 640x1000, then if you move your mouse over that window,
        it will return the coordinates that belongs to the newly resized window.
        Probably you are not interested in those coordinates, but in the coordinates
        that belongs to your *virtual* window.

        :rtype: (x,y)
        :returns: Transformed coordinates from the *real* window to the *virtual* window
        """

        x_diff = self._window_virtual_width / float(self.window.width - self._offset_x * 2)
        y_diff = self._window_virtual_height / float(self.window.height - self._offset_y * 2)

        adjust_x = (self.window.width * x_diff - self._window_virtual_width) / 2
        adjust_y = (self.window.height * y_diff - self._window_virtual_height) / 2

        return int(x_diff * x) - adjust_x, int(y_diff * y) - adjust_y

    def scaled_resize_window(self, width, height):
        """One of two possible methods that are called when the main window is resized.

        This implementation scales the display such that the initial resolution
        requested by the programmer (the "logical" resolution) is always retained
        and the content scaled to fit the physical display.

        This implementation also sets up a 3D projection for compatibility with the
        largest set of Cocos transforms.

        The other implementation is `unscaled_resize_window`.

        :Parameters:
            `width` : Integer
                New width
            `height` : Integer
                New height
        """
        # physical view size
        pw, ph = width, height
        # virtual (desired) view size
        vw, vh = self.get_window_size()
        # desired aspect ratio
        v_ar = vw / float(vh)
        # usable width, heigh
        uw = int(min(pw, ph * v_ar))
        uh = int(min(ph, pw / v_ar))
        ox = (pw-uw) // 2
        oy = (ph-uh) // 2
        self._offset_x = ox
        self._offset_y = oy
        self._usable_width = uw
        self._usable_height = uh
        self.set_projection()

        if self._resize_no_events:
            # setting viewport geometry, not handling an event
            return

        # deprecated - see issue 154
        self.dispatch_event("on_resize", width, height)

        self.dispatch_event("on_cocos_resize", self._usable_width, self._usable_height)

        # dismiss the pyglet BaseWindow default 'on_resize' handler
        return pyglet.event.EVENT_HANDLED

    def unscaled_resize_window(self, width, height):
        """One of two possible methods that are called when the main window is resized.

        This implementation does not scale the display but rather forces the logical
        resolution to match the physical one.

        This implementation sets up a 2D projection, resulting in the best pixel
        alignment possible. This is good for text and other detailed 2d graphics
        rendering.

        The other implementation is `scaled_resize_window`.

        :Parameters:
            `width` : Integer
                New width
            `height` : Integer
                New height
        """
        self._usable_width = width
        self._usable_height = height

        if self._resize_no_events:
            # setting viewport geometry, not handling an event
            return

        # deprecated - see issue 154
        self.dispatch_event("on_resize", width, height)

        self.dispatch_event("on_cocos_resize", self._usable_width, self._usable_height)

    def set_projection(self):
        """
        placeholder, will be set to one of set_projection2D or set_projection3D
        when director.init is called
        """
        pass

    def set_projection3D(self):
        """Sets a 3D projection mantaining the aspect ratio of the original window size"""
        # virtual (desired) view size
        vw, vh = self.get_window_size()

        gl.glViewport(self._offset_x, self._offset_y, self._usable_width, self._usable_height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(60, self._usable_width / float(self._usable_height), 0.1, 3000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glLoadIdentity()
        gl.gluLookAt(vw / 2.0, vh / 2.0, vh / 1.1566,   # eye
                  vw / 2.0, vh / 2.0, 0,             # center
                  0.0, 1.0, 0.0                      # up vector
                  )

    def set_projection2D(self):
        """Sets a 2D projection (ortho) covering all the window"""
        # called only for the side effect of setting matrices in pyglet
        self.window.on_resize(self._usable_width, self._usable_height)

    #
    # Misc functions
    #
    def set_alpha_blending(self, on=True):
        """
        Enables/Disables alpha blending in OpenGL
        using the GL_ONE_MINUS_SRC_ALPHA algorithm.
        On by default.
        """
        if on:
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        else:
            gl.glDisable(gl.GL_BLEND)

    def set_depth_test(self, on=True):
        """Enables z test. On by default"""
        if on:
            gl.glClearDepth(1.0)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
        else:
            gl.glDisable(gl.GL_DEPTH_TEST)

event_loop = pyglet.app.event_loop
if not hasattr(event_loop, "event"):
    event_loop = pyglet.app.EventLoop()
director = Director()
director.event = event_loop.event
"""The singleton; check `cocos.director.Director` for details on usage.
Don't instantiate Director(). Just use this singleton."""

director.interpreter_locals["director"] = director
director.interpreter_locals["cocos"] = cocos

Director.register_event_type('on_push')
Director.register_event_type('on_pop')
Director.register_event_type('on_resize')
Director.register_event_type('on_cocos_resize')
