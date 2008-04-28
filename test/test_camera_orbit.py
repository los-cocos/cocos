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
import random


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        sprite1 = ActionSprite( 'grossini.png' )
        sprite2 = ActionSprite( 'grossinis_sister1.png')
        sprite3 = ActionSprite( 'grossinis_sister2.png')

        sprite1.position = (320,240)
        sprite2.position = (620,100)
        sprite3.position = (20,100)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

        ju_right = Jump( y=100, x=600, jumps=4, duration=5 )
        ju_left = Jump( y=100, x=-600, jumps=4, duration=5 )
        rot1 = Rotate( 180 * 4, duration=5)

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
    main_scene = cocos.scene.Scene()

    rr = random.randrange
    for i in range(8):
        l = ColorLayer(rr(0,255),rr(0,255), rr(0,255),255)
        l.scale = (8-i)/8.0
        main_scene.add( l, z=i )

    tl1 = TestLayer()
    main_scene.add( tl1, z=33 )

    # set a 3d grid with a grid3d action
#    e = Waves3D( amplitude=25, waves=15, grid=(32,24), duration=4)
    e = Lens3D( radius=200, grid=(32,24), duration=4)

    # use the remaining grid and move it's camera
    rot = OrbitCamera( radius=1, delta_radius=2, angle_x=0, delta_x=-90, angle_z=0, delta_z=180, duration=2 )

    main_scene.do( e )
    main_scene.do( rot + Reverse( rot ) )

    director.run (main_scene)
