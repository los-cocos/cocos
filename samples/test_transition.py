import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.transitions import *
from cocos.actions import *
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
            valign=font.Text.TOP,
            batch=self.batch)

        self.text_subtitle = pyglet.text.Label( transition_list[current_transition].__name__,
            font_size=18,
            multiline=True,
            x=5,
            y=director.get_window_size()[1] - 80,
            halign=font.Text.LEFT,
            valign=font.Text.TOP,
            batch=self.batch )

        self.text_help = pyglet.text.Label("Press LEFT / RIGHT for prev/next test, ENTER to restart demo",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER,
            batch=self.batch )


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

        image = pyglet.resource.image('grossini.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        g = ActionSprite( image )

        self.add( g, position=(320,240) )

        rot = Rotate( 360, 4 )

        g.do( Repeat( rot + Reverse(rot) ) )

#    def on_exit( self ):
#        for o in self.objects:
#            o.stop()

class GrossiniLayer2(Layer):
    def __init__( self ):
        super( GrossiniLayer2, self ).__init__()

        rot = Rotate( 360, 5 )

        image = pyglet.resource.image('grossinis_sister1.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        g1 = ActionSprite( image )

        image = pyglet.resource.image('grossinis_sister2.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        g2 = ActionSprite( image )

        self.add( g1, position=(490,240) )
        self.add( g2, position=(140,240) )

        g1.do( Repeat( rot + Reverse(rot) ) )
        g2.do( Repeat( rot + Reverse(rot) ) )

#    def on_exit( self ):
#        for o in self.objects:
#            o.stop()

if __name__ == "__main__":
    director.init(resizable=True)
#    director.window.set_fullscreen(True)

    transition_list = [
        SlideLRTransition,
        SlideRLTransition,
        GrowTransition,
        FadeTransition,
        ShrinkAndGrow,
        SlideBTTransition,
        SlideTBTransition,
        MoveInTTransition,
        MoveInBTransition,
        MoveInLTransition,
        MoveInRTransition,
        CornerMoveTransition,
        ]
    current_transition = 0

    g = GrossiniLayer()
    g2 = GrossiniLayer2()
    c2 = ColorLayer(0.5,0.1,0.1,1)
    c1 = ColorLayer(0,1,1,1)
    control = ControlLayer()
    controlScene1 = Scene(c2, g, control)
    controlScene2 = Scene(c1, g2, control)
    control_p = 0
    control_list = [controlScene1, controlScene2]
    
    
    director.run( controlScene1 )
    
