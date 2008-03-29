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

class Scene(IContainer, IActionTarget):
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
        for z,c in self.children:
            if isinstance(c,Layer):
                director.window.push_handlers( c )
            c.on_enter()
            
        
    def on_exit( self ):
        """      
        Called every time just before the scene leaves the stage
        """
        for z,c in self.children:
            c.on_exit()
            if isinstance(c,Layer):
                director.window.pop_handlers()


    def on_draw( self ):                
        """Called every time the scene can be drawn."""

        # Apply transformation to current scene
        glPushMatrix()

        if self.mesh.active:
            self.mesh.before_draw()

        self.transform()

        for z,c in self.children:
            if isinstance(c,Layer):
                c._prepare()

        for z,c in self.children:
            c.on_draw()

        if self.mesh.active:
            self.mesh.after_draw()

        glPopMatrix()


if __name__ == '__main__':
    s = Scene( Layer(), Scene(), Layer() )
    s.on_enter()
