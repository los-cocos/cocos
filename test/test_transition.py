import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, AnimationLayer
from cocos.scene import Scene
from cocos import transitions
from cocos.actions import ActionSprite, Rotate, Repeat
import pyglet
from pyglet import gl

class GrossiniLayer(AnimationLayer):
    def __init__( self ):
        super( GrossiniLayer, self ).__init__()

        g = ActionSprite('grossini.png')

        g.place( (320,240,0) )

        self.add( g )

        rot = Rotate( 180, 5 )

        g.do( Repeat( rot ) )


class ColorLayer(Layer):
    def __init__(self, *color):
        self.color = color
        super(ColorLayer, self).__init__()
        
    def step(self, dt):
        gl.glColor4f(*self.color)
        x, y = director.window.width, director.window.height
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( 0, 0 )
        gl.glVertex2f( 0, y )
        gl.glVertex2f( x, y )
        gl.glVertex2f( x, 0 )
        gl.glEnd()
        gl.glColor4f(1,1,1,1)    

if __name__ == "__main__":
    director.init()
    g = GrossiniLayer()
    c1 = ColorLayer(1,0,0,1)
    c2 = ColorLayer(0,1,1,1)
    s1 = Scene(c1, g) 
    s2 = Scene(c2, g) 
    director.run( transitions.SlideLRTransition2(
                        Scene (c2, g), Scene(c1, g), 5 )
                        )
    