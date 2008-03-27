#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#

"""
Scene class and subclasses
"""
__docformat__ = 'restructuredtext'

__all__ = ['Scene']

from pyglet.gl import *

from interfaces import *
from director import director
from layer import *
from test_actions import *

class Scene(IContainer, ActionObject):
    """
    """
   
#    supported_classes = (Layer, Scene) 

    def __init__(self, *children):
        """
        Creates a Scene with layers and / or scenes.
        
        :Parameters:
            `children` : list of `Layer` or `Scene`
                Layers or Scenes that will be part of the scene.
        """

        self.supported_classes = (Layer, Scene)

        super(Scene,self).__init__( *children )


    def end(self, value=None):
        """Ends the current scene setting director.return_value with `value`
        
        :Parameters:
            `value` : anything
                The return value. It can be anything. A type or an instance.
        """
        director.return_value = value
        director.pop()

    def on_enter( self ):
        """
        Called every time just before the scene is run.
        """        
        for z,c,p in self.children:
            if isinstance(c,Layer):
                director.window.push_handlers( c )
            c.on_enter()
            
        
    def on_exit( self ):
        """      
        Called every time just before the scene leaves the stage
        """
        for z,c,p in self.children:
            c.on_exit()
            if isinstance(c,Layer):
                director.window.pop_handlers()


    def on_draw( self ):                
        """Called every time the scene can be drawn."""

        # Apply transformation to current scene
        glPushMatrix()

        x,y = director.get_window_size()

        color = self.color + (self.opacity,)
        if color != (255,255,255,255):
            glColor4ub( * color )

        if self.anchor_x != 0 and self.anchor_y != 0:
            rel_x = self.anchor_x * x
            rel_y = self.anchor_x * y
            glTranslatef( rel_x, rel_y, 0 )

        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)

        if self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )

        if self.anchor_x != 0 and self.anchor_y != 0:
            rel_x = self.anchor_x * x
            rel_y = self.anchor_x * y
            glTranslatef( -rel_x, -rel_y, 0 )

        for z,c,p in self.children:
            if isinstance(c,Layer):
                c._prepare()

        for z,c,p in self.children:
            glPushMatrix()
            self.apply_transformation( **p )
            c.on_draw()
            glPopMatrix()


        glPopMatrix()



if __name__ == '__main__':
    s = Scene( Layer(), Scene(), Layer() )
    s.on_enter()
