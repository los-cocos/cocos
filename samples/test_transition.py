#
# Cocos:
# http://code.google.com/p/los-cocos/
#
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import ActionSprite
import pyglet
from pyglet import gl, font

from pyglet.window import key

    
class ControlLayer(Layer):
    def __init__( self ):

        super(ControlLayer, self).__init__()

        self.text_title = pyglet.text.Label("Transition Demos",
            font_size=32,
            x=5,
            y=director.get_window_size()[1],
            halign=font.Text.LEFT,
            valign=font.Text.TOP )

        self.text_subtitle = pyglet.text.Label( transition_list[current_transition].__name__,
            font_size=18,
            multiline=True,
            width=600,
            x=5,
            y=director.get_window_size()[1] - 80,
            halign=font.Text.LEFT,
            valign=font.Text.TOP )

        self.text_help = pyglet.text.Label("Press LEFT / RIGHT for prev/next test, ENTER to restart demo",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)

    def on_draw( self ):
        self.text_title.draw()
        self.text_subtitle.draw()
        self.text_help.draw()

    def on_key_press( self, k , m ):
        global current_transition, control_p
        if k == key.LEFT:
            current_transition = (current_transition-1)%len(transition_list)
        elif k == key.RIGHT:
            current_transition = (current_transition+1)%len(transition_list)
        elif k == key.ENTER:
            director.replace( transition_list[current_transition](
                        control_list[control_p],
                        (control_list[(control_p+1)%len(control_list)] ),
                        2)                                
                    )
            control_p = (control_p + 1) % len(control_list)
            return True

        if k in (key.LEFT, key.RIGHT ):
            self.text_subtitle.text = transition_list[current_transition].__name__


class GrossiniLayer(Layer):
    def __init__( self ):
        super( GrossiniLayer, self ).__init__()

        g = ActionSprite( 'grossini.png')
        g.position = (320,240)

        rot = RotateBy( 360, 4 )
        g.do( Repeat( rot + Reverse(rot) ) )

        self.add( g )

class GrossiniLayer2(Layer):
    def __init__( self ):
        super( GrossiniLayer2, self ).__init__()

        rot = Rotate( 360, 5 )
        g1 = ActionSprite( 'grossinis_sister1.png' )
        g1.position = (490,240)

        g2 = ActionSprite( 'grossinis_sister2.png' )
        g2.position = (140,240)

        g1.do( Repeat( rot + Reverse(rot) ) )
        g2.do( Repeat( rot + Reverse(rot) ) )

        self.add( g1 )
        self.add( g2 )


if __name__ == "__main__":
    director.init(resizable=True)
#    director.window.set_fullscreen(True)

    transition_list = [
        # ActionTransitions
        RotoZoomTransition,
        JumpZoomTransition,
        MoveInLTransition,
        MoveInRTransition,
        MoveInBTransition,
        MoveInTTransition,
        SlideInLTransition,
        SlideInRTransition,
        SlideInBTransition,
        SlideInTTransition,
        FlipX3DTransition,
        FlipY3DTransition,
        FlipAngular3DTransition,
        ShuffleTilesTransition,
        ShrinkAndGrowTransition,
        CornerMoveTransition,
        EnvelopeTransition,
        CurtainTransition,
        TurnOffTilesTransition,

        ]
    current_transition = 0

    g = GrossiniLayer()
    g2 = GrossiniLayer2()
    c2 = ColorLayer(128,16,16,255)
    c1 = ColorLayer(0,255,255,255)
    control1 = ControlLayer()
    control2 = ControlLayer()
    controlScene1 = Scene( c2, g, control2 )
    controlScene2 = Scene( c1, g2, control2 )

    control_p = 0
    control_list = [controlScene1, controlScene2]
    
    director.run( controlScene1 )
