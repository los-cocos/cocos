#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
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

For example::

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

__all__ = ['director']

class Director(event.EventDispatcher):
    """Class that creates and handle the main Window and manages how
       and when to execute the Scenes"""
    
    def init(self, *args, **kwargs):
        """Initializes the Director creating the main window.
        Keyword arguments are passed to pyglet.window.Window().
        
        :rtype: pyglet.window.Window                    
        :returns: The main window, an instance of pyglet.window.Window class.
        """
        
        self.window = window.Window( *args, **kwargs )
        self.show_FPS = True

        # scene related
        self.scene_stack = []
        self.scene = None
        self.next_scene = None


        # save resolution and aspect for resize / fullscreen
        self.window.on_resize = self.on_resize
        self.window.on_draw = self.on_draw
        self._window_original_width = self.window.width
        self._window_original_height = self.window.height
        self._window_aspect =  self.window.width / float( self.window.height )
        self._offset_x = 0
        self._offset_y = 0
        
        # opengl settings
        self.set_alpha_blending()

        # init fps
        self.fps_display = clock.ClockDisplay()
    
        return self.window


    def run(self, scene):
        """Runs a scene, entering in the Director's main loop.

        :Parameters:   
            `scene` : `Scene`
                The scene that will be run.
        """

        self.scene_stack.append( self.scene )
        self._set_scene( scene )

        pyglet.app.run()


    def on_draw( self ):
        """Callback to draw the window.
        It propagates the event to the running scene."""
         
        self.window.clear()

        if self.next_scene is not None:
            self._set_scene( self.next_scene )

        if not self.scene_stack:
            pyglet.app.exit()

        # draw all the objects
        self.scene.on_draw()

        # finally show the FPS
        if self.show_FPS:
            self.fps_display.draw()

    
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

        old = self.scene
        
        self.scene = scene
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


    def on_resize( self, width, height):
        """Method that is called every time the main window is resized.
        
        :Parameters:
            `width` : Integer
                New width
            `height` : Integer
                New height
        """
        width_aspect = width
        height_aspect = int( width / self._window_aspect)

        if height_aspect > height:
            width_aspect = int( height * self._window_aspect )
            height_aspect = height

        self._offset_x = (width - width_aspect) / 2
        self._offset_y =  (height - height_aspect) / 2

        glViewport(self._offset_x, self._offset_y, width_aspect, height_aspect )
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self._window_original_width, 0, self._window_original_height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        
    #
    # Misc functions
    #
    def set_alpha_blending( self, on=True ):
        """
        Enables/Disables alpha blending in OpenGL 
        using the GL_ONE_MINUS_SRC_ALPHA algorithm."""
        if on:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            glDisable(GL_BLEND)
        
        

director = Director()
"""The singleton; check `cocos.director.Director` for details on usage.
Don't instantiate Director(). Just use this singleton."""

Director.register_event_type('on_push')
Director.register_event_type('on_pop')
