# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import ActionSprite
from cocos.layer import *
import pyglet
from cocos.test_actions import *

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

        sprite1.do( Rotate( 360*5,5 ) )
        sprite2.do( Rotate( -360*5,5 ) )
        sprite3.do( Rotate( -360*5,5 ) )

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()
    child1_scene = cocos.scene.Scene()
    child2_scene = cocos.scene.Scene()
    child3_scene = cocos.scene.Scene()
    child4_scene = cocos.scene.Scene()

    child1_scene.add( ColorLayer( 0.0, 0.0, 1.0, 1.0 ) )
    child1_scene.add( TestLayer() )

    child2_scene.add( ColorLayer( 0.0, 1.0, 0.0, 1.0 ) )
    child2_scene.add( TestLayer() )

    child3_scene.add( ColorLayer( 1.0,0.0, 0.0, 1.0 ) )
    child3_scene.add( TestLayer() )

    child4_scene.add( ColorLayer( 1.0,1.0, 1.0, 1.0 ) )
    child4_scene.add( TestLayer() )

    main_scene.add( child1_scene, scale=0.5, position=(-320,-240) )
    main_scene.add( child2_scene, scale=0.5, position=(320,240) )
    main_scene.add( child3_scene, scale=0.5, position=(-320,240) )
    main_scene.add( child4_scene, scale=0.5, position=(320,-240) )

    child1_scene.do( Rotate(-360,3) )
    child2_scene.do( Rotate(-360,3) )
    child3_scene.do( Rotate(-360,3) )
    child4_scene.do( Rotate(-360,3) )
    main_scene.do( Rotate( 360, 3) )

    director.run (main_scene)
