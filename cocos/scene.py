"""
Scene class and subclasses
"""

import bisect

from director import director

class Scene(object):
    """
    """
    
    def __init__(self, *layers):
        """
        Creates a Scene with layers, from bottom to top, giving a 
        z-value from 1.0 to len(layers)
        """
        self.layers = []
        self.layers_name = {}
        
        for i,l in enumerate(layers):
            self.add( i, l )

    def add( self, zvalue, layer, layer_name = None ):
        """
        add(zvalue, layer, layer_name) -> None
        
        Adds a layer at z-value depth, naming it 'name' if given.
        (name can be used later to remove the layer)
        """
        elem = zvalue, layer
        self.layers.insert( bisect.bisect( elem, self.layers ), elem )
        
    def remove( self, layer_name ):
        """
        remove(layer_name or layer_reference) -> None
        
        Removes a layer from the scene given the layer_name or the layer.
        If the layer can't be removed, and exception will be risen
        """
        if layer_name in self.layers_name:
            layer = self.layers_name[ layer_name ]
            self.remove_layer( layer )
            del self.layers_name[ layer_name ]
            
    def remove_layer(self, layer ):
        """
        remove_layer(layer) -> None
        
        Removes a layer from the scene
        """
        self.layers = [ (z, l) for (z,l) in self.layers if l != layer ]
        
    def end(self, value=None):
        """
        end(value) -> None
        
        Ends the current scene setting director.return_value with value
        """
        director.return_value = value
        director.pop()

    def on_enter( self ):
        """
        Called every time the scene is shown. The scene also registers the layer's events.
        """        
        for z,l in self.layers:
            director.window.push_handlers( l )
            l.on_enter()
            
        
    def on_exit( self ):
        """
        on_exit() -> None
        
        Called every time the scene is not longer shown
        """
        for z,l in self.layers:
            l.on_exit()
            director.window.pop_handlers()

            
    def step( self, dt ):
        """
        step(dt) -> None
        
        Calls step(dt) in all the layers
        """
        for i, l in self.layers:
            l._prepare(dt)
        for i, l in self.layers:
            l._step(dt)
        
        
class TransitionScene(Scene):
    """
    A Scene that takes two scenes and makes a transition
    """
        

