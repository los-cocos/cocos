import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, AnimationLayer, ColorLayer
from cocos.scene import Scene
from cocos.transitions import *
from cocos.actions import ActionSprite, Rotate, Repeat
import pyglet
from pyglet import gl, font

from pyglet.window import key

    
class ControlLayer(Layer):
    def on_enter( self ):
        ft_title = font.load( "Arial", 32 )
        ft_subtitle = font.load( "Arial", 18 )
        ft_help = font.load( "Arial", 16 )

        self.text_title = font.Text(ft_title, "Transition Demos",
            x=5,
            y=480,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)

        self.text_subtitle = font.Text(ft_subtitle, transition_list[current_transition].__name__,
            x=5,
            y=400,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)
        
        self.text_help = font.Text(ft_help,"Press LEFT / RIGHT for prev/next example, ENTER to restart example",
            x=320,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)

    def step( self, df ):
        self.text_help.draw()

        self.text_subtitle.text = transition_list[current_transition].__name__
        self.text_subtitle.draw()
        self.text_title.draw()

    def on_key_press( self, k , m ):
        global current_transition, control_p
        if k == key.LEFT:
            current_transition = (current_transition-1)%len(transition_list)
        if k == key.RIGHT:
            current_transition = (current_transition+1)%len(transition_list)
        if k == key.ENTER:
            director.replace( transition_list[current_transition](
                        control_list[control_p],
                        (control_list[(control_p+1)%len(control_list)] ),
                        2)                                
                    )
            control_p = (control_p + 1) % len(control_list)
            return True
        if k == key.ESCAPE:
            director.scene.end()

class GrossiniLayer(AnimationLayer):
    def __init__( self ):
        super( GrossiniLayer, self ).__init__()

        g = ActionSprite('grossini.png')

        g.place( (320,240,0) )

        self.add( g )

        rot = Rotate( 180, 5 )

        g.do( Repeat( rot ) )

class GrossiniLayer2(AnimationLayer):
    def __init__( self ):
        super( GrossiniLayer2, self ).__init__()

        rot = Rotate( 180, 5 )

        g = ActionSprite('grossini.png')
        g.place( (490,240,0) )
        self.add( g )
        g.do( Repeat( rot ) )

        g = ActionSprite('grossini.png')
        g.place( (150,240,0) )
        self.add( g )
        g.do( Repeat( rot ) )

if __name__ == "__main__":
    director.init(resizable=True)
    director.window.set_fullscreen(True)
    g = GrossiniLayer()
    g2 = GrossiniLayer2()
    c2 = ColorLayer(0.5,0.1,0.1,1)
    c1 = ColorLayer(0,1,1,1)
    control = ControlLayer()
    controlScene1 = Scene(c2, g, control)
    controlScene2 = Scene(c1, g2, control)
    control_p = 0
    control_list = [controlScene1, controlScene2]
    
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
    
    director.run( controlScene1 )
    
