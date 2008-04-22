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

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    rr = random.randrange

    for i in range(8):
        l = ColorLayer(rr(0,255), rr(0,255), rr(0,255), 255)
        l.scale = (8-i)/8.0
        main_scene.add( l, z=i )

    e = MoveCornerUp( duration=1 )
    main_scene.do( e )

    director.run( main_scene )
