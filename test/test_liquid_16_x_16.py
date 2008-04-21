# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.sprite import *
from cocos.layer import *
import pyglet


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        sprite1 = ActionSprite( 'grossini.png', (x/2, y/2) )
        sprite2 = ActionSprite( 'grossinis_sister1.png', (x/4, y/2) )
        sprite3 = ActionSprite( 'grossinis_sister2.png', (x/4*3, y/2) )

        self.add( sprite2 )
        self.add( sprite1 )
        self.add( sprite3 )


if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(255, 0, 0, 255)
    blue = ColorLayer(0, 0, 255, 255)
    blue.scale = 0.75
    green = ColorLayer(0, 255, 0, 255)
    green.scale = 0.5
    white = ColorLayer(255, 255, 255, 255)
    white.scale = 0.25
    tl1 = TestLayer()

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1 )
    main_scene.add( green, z=2 )
    main_scene.add( white, z=3 )
    main_scene.add( tl1, z=4 )

    main_scene.do( Liquid( waves=50, grid=(16,16), duration=100) )

    director.run (main_scene)
