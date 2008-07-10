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
'''Singleton that handles the logic behind the Scenes

Director
========

Initializing
------------

The director is the singleton that creates and handles the main ``Window``
and manages the logic behind the ``Scenes``. 

The first thing to do, is to initialize the ``director``::

    from cocos.director import *
    director.init( list_of_arguments )

This will initialize the director, and will create a display area 
(a 640x480 window by default).
The parameters that are supported by director.init() are the same
parameters that are supported by pyglet.window.Window().

Some of the supported parameters are:

    * ``fullscreen``: Boolean. Window is created in fullscreen. Default is False
    * ``resizable``: Boolean. Window is resizable. Default is False
    * ``vsync``: Boolean. Sync with the vertical retrace. Default is True
    * ``width``: Integer. Window width size. Default is 640
    * ``height``: Integer. Window height size. Default is 480
    * ``caption``: String. Window title.
    * ``visible``: Boolean. Window is visible or not. Default is True.

The full list of valid arguments can be found here:

    - http://www.pyglet.org/doc/1.1/api/pyglet.window.Window-class.html


Example::

    director.init( caption="Hello World", fullscreen=True )

For a complete list of the supported parameters, see the pyglet Window
documentation.

Running a Scene
----------------

Once you have initialized the director, you can run your first ``Scene``::

    director.run( Scene( MyLayer() ) )

This will run a scene that has only 1 layer: ``MyLayer()``. You can run a scene
that has multiple layers. For more information about ``Layers`` and ``Scenes``
refer to the ``Layers`` and ``Scene`` documentation.

`cocos.director.Director`

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
            
'''

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import window, event
from pyglet import clock
from pyglet import media
from pyglet.gl import *

import cocos

__all__ = ['director', 'DefaultHandler']

class DefaultHandler( object ):
    def __init__(self):
        super(DefaultHandler,self).__init__()
        self.wired = False

    def on_key_press( self, symbol, modifiers ):
        if symbol == pyglet.window.key.F and (modifiers & pyglet.window.key.MOD_ACCEL):
            director.window.set_fullscreen( not director.window.fullscreen )
            return True

        elif symbol == pyglet.window.key.P and (modifiers & pyglet.window.key.MOD_ACCEL):
            import scenes.pause as pause
            pause_sc = pause.get_pause_scene() 
            if pause:
                director.push( pause_sc )
            return True

        elif symbol == pyglet.window.key.W and (modifiers & pyglet.window.key.MOD_ACCEL):
#            import wired
            if self.wired == False:
                glDisable(GL_TEXTURE_2D);
                glPolygonMode(GL_FRONT, GL_LINE);
                glPolygonMode(GL_BACK, GL_LINE);
#                wired.wired.install()
#                wired.wired.uset4F('color', 1.0, 1.0, 1.0, 1.0 )
                self.wired = True
            else:
                glEnable(GL_TEXTURE_2D);
                glPolygonMode(GL_FRONT, GL_FILL);
                glPolygonMode(GL_BACK, GL_FILL);
                self.wired = False 
#                wired.wired.uninstall()
            return True

        elif symbol == pyglet.window.key.X and (modifiers & pyglet.window.key.MOD_ACCEL):
            director.show_FPS = not director.show_FPS 
            return True

        elif symbol == pyglet.window.key.I and (modifiers & pyglet.window.key.MOD_ACCEL):
            from layer import PythonInterpreterLayer

            if not director.show_interpreter:
                if director.python_interpreter == None:
                    director.python_interpreter = cocos.scene.Scene( PythonInterpreterLayer() )
                    director.python_interpreter.enable_handlers( True )
                director.python_interpreter.on_enter()
                director.show_interpreter = True
            else:
                director.python_interpreter.on_exit()
                director.show_interpreter= False
            return True

        elif symbol == pyglet.window.key.S and (modifiers & pyglet.window.key.MOD_ACCEL):
            import time
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot-%d.png' % (int( time.time() ) ) )
            return True

        if symbol == pyglet.window.key.ESCAPE:
            director.pop()
            return True

class Director(event.EventDispatcher):
    """Class that creates and handle the main Window and manages how
       and when to execute the Scenes"""
    #: a dict with locals for the interactive python interpreter (fill with what you need)
    interpreter_locals = {}

    def init(self, *args, **kwargs):
        """Initializes the Director creating the main window.
        Keyword arguments are passed to pyglet.window.Window().

        All the valid arguments can be found here:

            - http://www.pyglet.org/doc/1.1/api/pyglet.window.Window-class.html
        
        :rtype: pyglet.window.Window                    
        :returns: The main window, an instance of pyglet.window.Window class.
        """

        # pop out the Cocos-specific flag
        do_not_scale_window = kwargs.pop('do_not_scale', False)
       
        #: pyglet's window object
        self.window = window.Window( *args, **kwargs )

        #: whether or not the FPS are displayed
        self.show_FPS = False 

        #: stack of scenes
        self.scene_stack = []

        #: scene that is being run
        self.scene = None

        #: this is the next scene that will be shown
        self.next_scene = None

        # save resolution and aspect for resize / fullscreen
        if do_not_scale_window:
            self.window.push_handlers(on_resize=self.unscaled_resize_window)
        else:
            self.window.push_handlers(on_resize=self.scaled_resize_window)
        self.window.push_handlers(self.on_draw)
        self._window_original_width = self.window.width
        self._window_original_height = self.window.height
        self._window_aspect =  self.window.width / float( self.window.height )
        self._offset_x = 0
        self._offset_y = 0
        
        # opengl settings
        self.set_alpha_blending()

        # init fps
        self.fps_display = clock.ClockDisplay()

        # python interpreter
        self.python_interpreter = None

        #: whether or not to show the python interpreter
        self.show_interpreter = False

        # default handler
        self.window.push_handlers( DefaultHandler() )

        return self.window

    def run(self, scene):
        """Runs a scene, entering in the Director's main loop.

        :Parameters:   
            `scene` : `Scene`
                The scene that will be run.
        """

        self.scene_stack.append( self.scene )
        self._set_scene( scene )

        event_loop.run()


    def on_draw( self ):
        """Callback to draw the window.
        It propagates the event to the running scene."""
         
        self.window.clear()

        if self.next_scene is not None:
            self._set_scene( self.next_scene )

        if not self.scene_stack:
            pyglet.app.exit()

        # draw all the objects
        self.scene.visit()

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
        self.dispatch_event("on_push", scene )

    def on_push( self, scene ):
        self.next_scene = scene
        self.scene_stack.append( self.scene )
        
    def pop(self):
        """Pops out a scene from the queue. This scene will replace the running one.
           The running scene will be deleted. If there are no more scenes in the stack
           the execution is terminated.
        """
        self.dispatch_event("on_pop")
        
    def on_pop(self):
        self.next_scene = self.scene_stack.pop()
        
    def replace(self, scene):
        """Replaces the running scene with a new one. The running scene is terminated.

        :Parameters:   
            `scene` : `Scene`
                It is the scene that will be run.
        """  
        self.next_scene = scene

    def _set_scene(self, scene ):
        """Change to a new scene.
        """

        self.next_scene = None

        if self.scene is not None:
            self.scene.on_exit()
            self.scene.enable_handlers( False )
            
        old = self.scene
        
        self.scene = scene
        self.scene.enable_handlers( True )
        scene.on_enter()

        return old


    #
    # Window Helper Functions
    #
    def get_window_size( self ):
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
        return ( self._window_original_width, self._window_original_height)
        

    def get_virtual_coordinates( self, x, y ):
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

        x_diff = self._window_original_width / float( self.window.width - self._offset_x * 2 )
        y_diff = self._window_original_height / float( self.window.height - self._offset_y * 2 )

        adjust_x = (self.window.width * x_diff - self._window_original_width ) / 2
        adjust_y = (self.window.height * y_diff - self._window_original_height ) / 2

        return ( int( x_diff * x) - adjust_x,   int( y_diff * y ) - adjust_y )


    def scaled_resize_window( self, width, height):
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
        self.set_projection()
        self.dispatch_event("on_resize", width, height)
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
        self.dispatch_event("on_resize", width, height)

    def set_projection(self):
        '''Sets a 3D projection mantaining the aspect ratio of the original window size'''

        width, height = self.window.width, self.window.height
        ow, oh = self.get_window_size()

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1.0*width/height, 0.1, 3000.0)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()
        gluLookAt( ow/2.0, oh/2.0, oh/1.1566,       # eye
                   ow / 2.0, oh / 2.0, 0,           # center
                   0.0, 1.0, 0.0                    # up vector
                   )
        
    #
    # Misc functions
    #
    def set_alpha_blending( self, on=True ):
        """
        Enables/Disables alpha blending in OpenGL 
        using the GL_ONE_MINUS_SRC_ALPHA algorithm.
        On by default.
        """
        if on:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            glDisable(GL_BLEND)

    def set_depth_test( sefl, on=True ):
        '''Enables z test. On by default
        '''
        if on:
            glClearDepth(1.0)
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)
            glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        else:
            glDisable( GL_DEPTH_TEST )


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
