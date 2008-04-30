#
# Cocos
# http://code.google.com/p/los-cocos/
#
"""Layer class and subclasses

A `Layer` has as size the whole drawable area (window or screen),
and knows how to draw itself. It can be semi transparent (having holes
and/or partial transparency in some/all places), allowing to see other layers
behind it. Layers are the ones defining appearance and behavior, so most
of your programming time will be spent coding Layer subclasses that do what
you need. The layer is where you define event handlers.
Events are propagated to layers (from front to back) until some layer catches
the event and accepts it.
"""

__docformat__ = 'restructuredtext'

from cocos.director import *
from cocos import cocosnode
from cocos import scene

__all__ = [ 'Layer', 'MultiplexLayer']

class Layer(cocosnode.CocosNode, scene.EventHandlerMixin):
    """Class that handles events and other important game's behaviors"""

    is_event_handler = False #! if true, the event handlers of this layer will be registered. defaults to false.
    
    def __init__( self ):
        super( Layer, self ).__init__()
        self.scheduled_layer = False
        x,y = director.get_window_size()
        self.transform_anchor_x = x/2
        self.transform_anchor_y = y/2
        
    def push_handlers(self):
        if self.is_event_handler:
            director.window.push_handlers( self )
        for child in self.get_children():
            if isinstance(child, Layer):
                child.push_handlers()
                
    def remove_handlers(self):
        if self.is_event_handler:
            director.window.remove_handlers( self )
        for child in self.get_children():
            if isinstance(child, Layer):
                child.remove_handlers()
           
    def on_enter(self):
        super(Layer, self).on_enter()
        
        scn = self.get_ancestor(scene.Scene)
        if not scene: return
        
        if scn._handlers_enabled:
            director.window.push_handlers( self )
        
    def on_exit(self):
        super(Layer, self).on_exit()
        
        scn = self.get_ancestor(scene.Scene)
        if not scene: return
        
        if scn._handlers_enabled:
            director.window.remove_handlers( self )

#
# MultiplexLayer
class MultiplexLayer( Layer ):
    """A Composite layer that only enables one layer at the time.

     This is useful, for example, when you have 3 or 4 menus, but you want to
     show one at the time"""

    
    def __init__( self, *layers ):
        super( MultiplexLayer, self ).__init__()

        self.layers = layers 
        self.enabled_layer = 0

        self.add( self.layers[ self.enabled_layer ] )

    def switch_to( self, layer_number ):
        """Switches to another Layer that belongs to the Multiplexor.

        :Parameters:
            `layer_number` : Integer
                MUST be a number between 0 and the quantities of layers - 1.
                The running layer will receive an "on_exit()" call, and the
                new layer will receive an "on_enter()" call.
        """
        if layer_number < 0 or layer_number >= len( self.layers ):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        self.remove( self.layers[ self.enabled_layer ] )

        self.enabled_layer = layer_number
        self.add( self.layers[ self.enabled_layer ] )
