#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""
Layer class and subclasses
"""

from cocos.director import *

__all__ = [ 'Layer', 'MultiplexLayer', 'AnimationLayer' ]

class Layer(object):
    """
    """
    effects = ()

    def step(self, dt):
        """
        step(dt) -> None
        
        Called once per cycle. Use this method to draw/animate your objects
        """
        pass


    def set_effect (self, e):
        """
        set_effect(e) -> None
        
        Apply effect e to this layer. if e is None, current effect (if any)
        is removed
        """
        if e is None:
            del self.effects
        else:
            self.effects = (e,)

    def _prepare (self, dt):
        for e in self.effects:
            e.prepare (self, dt)

    def _step(self, dt):
        if not self.effects:
            self.step (dt)
        else:
            for e in self.effects:
                e.show ()

    def on_enter( self ):
       pass 

    def on_exit( self ):
       pass 

#
# MultiplexLayer
# 
# A Composite layer that only enables one layer at the time
# This is useful, for example, when you have 3 or 4 menus, but you want to
# show one at the time
#
class MultiplexLayer( Layer ):
    def __init__( self, *layers ):
        super( MultiplexLayer, self ).__init__()

        self.layers = layers 
        self.enabled_layer = 0

        for l in self.layers:
            l.switch_to = self.switch_to

    def switch_to( self, layer_number ):
        """switch_to( layer_nubmer ) -> None

        Switches to another Layer that belongs to the Multiplexor.
        layer_number MUST be a number between 0 and the quantities of layers - 1.
        The running layer will receive an "on_exit()" call, and the new layer will receive an "on_enter()" call.
        """
        if layer_number < 0 or layer_number >= len( self.layers ):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        director.window.pop_handlers()
        self.layers[ self.enabled_layer ].on_exit()

        self.enabled_layer = layer_number
        director.window.push_handlers( self.layers[ self.enabled_layer ] )
        self.layers[ self.enabled_layer ].on_enter()

    def step( self, dt):
        self.layers[ self.enabled_layer ].step( dt )

    def on_enter( self ):
        director.window.push_handlers( self.layers[ self.enabled_layer ] )
        self.layers[ self.enabled_layer ].on_enter()

    def on_exit( self ):
        director.window.pop_handlers()
        self.layers[ self.enabled_layer ].on_exit()


class AnimationLayer(Layer):

    def __init__( self ):
        super( AnimationLayer, self ).__init__()

        self.objects = []

    def add( self, o ):
        self.objects.append( o )

    """
    dt animations
    """
    def step( self, dt ):
        [ o.step(dt) for o in self.objects ]
