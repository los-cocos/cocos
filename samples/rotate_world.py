# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from cocos.sprite import ActionSprite
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

        sprite1.do( Rotate( 360,1 ) * 10 )
        sprite2.do( Rotate( -360,1 ) * 10 )
        sprite3.do( Rotate( -360,1 ) * 10 )

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()
    child1_scene = cocos.scene.Scene()
    child2_scene = cocos.scene.Scene()

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)

    tl1 = TestLayer()
    tl2 = TestLayer()

    child1_scene.add( red )
    child1_scene.add( tl1 )

    child2_scene.add( blue )
    child2_scene.add( tl2 )

    main_scene.add( child1_scene, scale=0.5, position=(-160,-120) )
    main_scene.add( child2_scene, scale=0.5, position=(160,120) )

    red.do( Rotate(-360,2) *5 )
    blue.do( Rotate(-360,2) *5 )

    tl1.do( Rotate(360,2) *5 )
    tl2.do( Rotate(360,2) *5 )

    child1_scene.do( Rotate(360,5) )
    child2_scene.do( Rotate(360,5) )

    main_scene.do( Rotate( 360,6) )

    director.run (main_scene)
