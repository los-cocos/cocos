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
        
        sprite1 = ActionSprite( 'grossini.png' )
        sprite2 = ActionSprite( 'grossinis_sister1.png' )
        sprite3 = ActionSprite( 'grossinis_sister2.png' )

        sprite1.position = (x/2, y/2 )
        sprite2.position = (x/4, y/2 )
        sprite3.position = (3*x/4.0, y/2 )

        self.add( sprite2 )
        self.add( sprite1 )
        self.add( sprite3 )

        sprite1.do( Rotate( 360,1 ) * 16 )
        sprite2.do( Rotate( -360,1 ) * 16 )
        sprite3.do( Rotate( -360,1 ) * 16 )

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()
    main_scene.transform_anchor = (320,240)
    child1_scene = cocos.scene.Scene()
    child2_scene = cocos.scene.Scene()

    red = ColorLayer(255,0,0,255)
    blue = ColorLayer(0,0,255,255)

    tl1 = TestLayer()
    tl2 = TestLayer()

    child1_scene.add( red )
    child1_scene.add( tl1 )
    child1_scene.scale = 0.5
    child1_scene.transform_anchor = (320,240)
    child1_scene.position = (-160,-120)

    child2_scene.add( blue )
    child2_scene.add( tl2 )
    child2_scene.scale = 0.5
    child2_scene.transform_anchor = (320,240)
    child2_scene.position = (160,120)

    main_scene.add( child1_scene )
    main_scene.add( child2_scene )

    red.do( Rotate(-360,2) *5 )
    blue.do( Rotate(-360,2) *5 )

    tl1.do( Rotate(360,2) *5 )
    tl2.do( Rotate(360,2) *5 )

    child1_scene.do( Rotate(360,5) )
    child2_scene.do( Rotate(360,5) )

    main_scene.do( Rotate( 360,6) )

    director.run (main_scene)
