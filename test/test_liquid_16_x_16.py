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

        self.add( sprite2, (x/4, y/2) )
        self.add( sprite1, (x/2, y/2) )
        self.add( sprite3, (x/(4/3.0), y/2) )


if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)
    green = ColorLayer(0.0, 1.0, 0.0, 1.0)
    white = ColorLayer(1.0, 1.0, 1.0, 1.0)
    tl1 = TestLayer()

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1, scale=0.75 )
    main_scene.add( green, z=2, scale=0.5 )
    main_scene.add( white, z=3, scale=0.25 )
    main_scene.add( tl1, z=4 )

    main_scene.do( Liquid( grid=(16,16), duration=100) )

    director.run (main_scene)
