"""
Layer class and subclasses
"""

class Layer(object):
    """
    """
    effects = ()

    def step(self, dt):
        """
        step(dt) -> None
        
        Called once per cycle. Use this method to draw/animate your objects
        """

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


class MenuLayer(Layer):
    """
    A layer that implements a basic menu
    """

