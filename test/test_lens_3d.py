# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import *
from cocos.actions import *
from cocos.layer import *
import pyglet
import random

from cocos.mesh import *

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        image = pyglet.resource.image('grossini.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        sprite1 = ActionSprite( image )

        image = pyglet.resource.image('grossinis_sister1.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        sprite2 = ActionSprite( image )

        image = pyglet.resource.image('grossinis_sister2.png')
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        sprite3 = ActionSprite( image )

        ju_right = Jump( y=100, x=600, jumps=4, duration=5 )
        ju_left = Jump( y=100, x=-600, jumps=4, duration=5 )
        rot1 = Rotate( 180 * 4, duration=5)

        self.add( sprite1, (320,240) )
        self.add( sprite2, (620,100) )
        self.add( sprite3, (20,100) )

        sc = ScaleBy( 9, 5 )
        rot = Rotate( 180, 5 )
        

#        sprite1.do( Repeat( sc + Reverse(sc) ) )
#        sprite1.do( Repeat( rot + Reverse(rot) ) )
        sprite2.do( Repeat( ju_left + Reverse(ju_left) ) )
        sprite2.do( Repeat( Reverse(rot1) + rot1 ) )
        sprite3.do( Repeat( ju_right + Reverse(ju_right) ) )
        sprite3.do( Repeat( rot1 + Reverse(rot1) ) )


if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    for i in range(32):
        l = ColorLayer(random.random(), random.random(), random.random(), 1.0)
        scale = (32-i)/32.0
        main_scene.add( l, z=i, scale=scale )

    tl1 = TestLayer()
    main_scene.add( tl1, z=33 )

    e = Lens3D( radius=240, grid=(32,32), duration=100 )
    main_scene.do( e )

    director.run (main_scene)
