#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""
Framework to handle game's logic
"""


from pyglet import window, event
from pyglet import clock
from pyglet import media
from pyglet.gl import *

__all__ = ['director']

class Director(event.EventDispatcher):
    """
    scene = is the scene that is running now
    return_value = the return value of the last scene to finish
    state = a placeholder for the state of the system
    windoow = the current window
    """
    
    def init(self, *args, **kwargs):
        """
        init(size, caption, fullscree, resizable, etc-from-pyglet) -> window
        creates widnow 
        """
        
        self.window = window.Window( *args, **kwargs )
        self.scene_stack = []
        self.show_FPS = True

        # alpha blending
        self.enable_alpha_blending()

        # save resolution and aspect for resize / fullscreen
        self.window.on_resize = self._on_resize
        self._window_original_width = self.window.width
        self._window_original_height = self.window.height
        self._window_aspect =  self.window.width / float( self.window.height )
        self._offset_x = 0
        self._offset_y = 0
        
        return self.window

    def run(self, scene):
        """
        run(scene) -> None
                
        Runs a scene. If another scene is running, an exception is risen
        """
        fps_display = clock.ClockDisplay()

        self.scene = scene
        self.scene_stack.append( scene )

        self.next_scene = None

        self.scene.on_enter()

        while not self.window.has_exit:

            if self.next_scene is not None:
                self._set_scene( self.next_scene )

            if not self.scene_stack:
                break
            
            dt = clock.tick()

            # dispatch pyglet events
            self.window.dispatch_events()
            media.dispatch_events()
#            self.dispatch_events('on_push', 'on_pop')

            # clear pyglets main window
            self.window.clear()

            # step / tick / draw
            self.scene.step( dt )
            
            # show the FPS
            if self.show_FPS:
                fps_display.draw()

            # show all the changes
            self.window.flip()
    
    
    def push(self, scene):
        """
        push(scene) -> None
        
        Adds scene to the scene stack, suspendis the scene thats
        currently executing
        """
        self.dispatch_event("on_push", scene )

    def on_push( self, scene ):
        self.next_scene = scene
        self.scene_stack.append( self.scene )
        
    def pop(self):
        """
        pop() -> scene
        
        Removes a scene from the top of the stack, resuming execution
        of the next one, or ending if the stack is empty
        
        """
        self.dispatch_event("on_pop")
        
    def on_pop(self):
        self.next_scene = self.scene_stack.pop()
        
    def replace(self, scene):
        """
        replace(scene) -> scene
        
        Replaces the active scene with a new one. The replaced scene is returned
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
        """get_window_size() -> (x,y)

        Returns the original window size, and not the resolution.
        In Fullscreen mode the resolution is different from the Window mode
        but the size is emulated.
        """
        return ( self._window_original_width, self._window_original_height)
        
    def enable_alpha_blending( self ):
        """
        enable_alpha_blending() -> None

        Enables alpha blending in Opengl using the GL_ONE_MINUS_SRC_ALPHA algorithm
        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def get_virtual_coordinates( self, x, y ):
        """get_virtual_coordinates( x, y ) -> (int, int)

        Converts real coordinates to virtual (or screen) coordinates.
        If you are working with a window "real" coordinates and "virtual"
        coordinates are the same, but if you are in fullscreen mode, then
        the "real" and "virtual" coordinates might be different since fullscreen mode 
        doesn't change the resolution of the screen. Instead it uses all the screen,
        so the "real" coordinates are the coordinates of all the screen.
        """

        x_diff = self._window_original_width / float( self.window.width - self._offset_x * 2 )
        y_diff = self._window_original_height / float( self.window.height - self._offset_y * 2 )

        adjust_x = (self.window.width * x_diff - self._window_original_width ) / 2
        adjust_y = (self.window.height * y_diff - self._window_original_height ) / 2

        return ( int( x_diff * x) - adjust_x,   int( y_diff * y ) - adjust_y )

    #
    # window resize handler
    #
    def _on_resize( self, width, height):
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


director = Director()
Director.register_event_type('on_push')
Director.register_event_type('on_pop')
