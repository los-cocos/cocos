#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#

"""
Scene class and subclasses
"""
__docformat__ = 'restructuredtext'

__all__ = ['Scene']

import bisect

from director import director

class Scene(object):
    """
    """
    
    def __init__(self, *layers):
        """
        Creates a Scene with layers, from bottom to top, giving a 
        z-value from 0.0 to len(layers)-1
        
        :Parameters:
            `layers` : list of `Layer`
                Layers that will be part of the scene.
        """
        self.layers = []
        self.layers_name = {}
        
        for i,l in enumerate(layers):
            self.add( i, l )

    def add( self, zvalue, layer, layer_name = None ):
        """
        add(zvalue, layer [, layer_name]) -> None
        
        Adds a layer at z-value depth, naming it 'name' if given.
        (name can be used later to remove the layer)
        """
        elem = zvalue, layer
        bisect.insort( self.layers,  elem )
        
    def remove( self, layer_name ):
        """Removes a layer from the scene given the layer_name.
        If the layer can't be removed, and exception will be risen
        
        :Parameters:
            `layer_name` : string
                `Layer` name       
        """
        if layer_name in self.layers_name:
            layer = self.layers_name[ layer_name ]
            self.remove_layer( layer )
            del self.layers_name[ layer_name ]
        else:
            raise Exception("Layer not found: %s" % layer_name)
            
    def remove_layer(self, layer ):
        """Removes a layer from the scene given a layer's reference.
        
        :Parameters:
            `layer` : `Layer`
                `Layer` reference"""
        self.layers = [ (z, l) for (z,l) in self.layers if l != layer ]
        
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
        for z,l in self.layers:
            director.window.push_handlers( l )
            l.on_enter()
            
        
    def on_exit( self ):
        """      
        Called every time just before the scene leaves the stage
        """
        for z,l in self.layers:
            l.on_exit()
            director.window.pop_handlers()


    def on_draw( self ):                
        """Called every time the scene can be drawn."""
        for i, l in self.layers:
            l._prepare()
        for i, l in self.layers:
            l.on_draw()
