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

from cocos.mesh import *

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        image1 = pyglet.resource.image('grossini.png')
        image1.anchor_x = image1.width / 2
        image1.anchor_y = image1.height / 2

        image2 = pyglet.resource.image('grossinis_sister1.png')
        image2.anchor_x = image2.width / 2
        image2.anchor_y = image2.height / 2

        image3 = pyglet.resource.image('grossinis_sister2.png')
        image3.anchor_x = image3.width / 2
        image3.anchor_y = image3.height / 2


        sprite1 = ActionSprite( image1 )
        sprite2 = ActionSprite( image2 )
        sprite3 = ActionSprite( image3 )

        self.add( sprite1, (x/2, y/2) )
        self.add( sprite2, (3*x/4, y/2) )
        self.add( sprite3, (1*x/4, y/2) )

if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)
    green = ColorLayer(0.0, 1.0, 0.0, 1.0)
    white = ColorLayer(1.0, 1.0, 1.0, 1.0)

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1, scale=0.75 )
    main_scene.add( green, z=2, scale=0.5 )
    main_scene.add( white, z=3, scale=0.25 )
    main_scene.add( TestLayer(), z=10 )

    a = Flip( duration=1 )
    main_scene.do( a )

    director.run (main_scene)
