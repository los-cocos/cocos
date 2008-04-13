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

        sprite1.do( Rotate( 360,1 ) * 16 )
        sprite2.do( Rotate( -360,1 ) * 16 )
        sprite3.do( Rotate( -360,1 ) * 16 )

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

    main_scene.add( child1_scene, scale=1.5, position=(-160,-120) )
    main_scene.add( child2_scene, scale=1.5, position=(160,120) )
    main_scene.add( child3_scene, scale=1.5, position=(-160,120) )
    main_scene.add( child4_scene, scale=1.5, position=(160,-120) )

    rot = Rotate(-360,2)
    sleep = Delay(2)

    sleep2 = Delay(2)

    sc1 = ScaleTo(0.5, 0.5) + Delay(1.5)
    sc2 = Delay(0.5) + ScaleTo(0.5, 0.5) + Delay(1.0)
    sc3 = Delay(1.0) + ScaleTo(0.5, 0.5) + Delay(0.5)
    sc4 = Delay(1.5) + ScaleTo(0.5, 0.5)

    child1_scene.do( sc4 + sleep + rot + sleep + rot + rot  )
    child2_scene.do( sc3 + sleep + rot + sleep + rot + Reverse(rot) )
    child3_scene.do( sc2 + sleep + rot + sleep + rot + Reverse(rot) ) 
    child4_scene.do( sc1 + sleep + rot + sleep + rot + rot)

    main_scene.do( sleep + Reverse(rot) *2 + rot * 2 + sleep)

    director.run (main_scene)
