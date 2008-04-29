# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
import random

rr = random.randrange

if __name__ == "__main__":
    director.init( resizable=True, fullscreen=False )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()
    
    for i in range(16):
        l = ColorLayer(rr(0,255), rr(0,255), rr(0,255), 255)
        scale = (16-i)/16.0
        l.scale = scale
        main_scene.add( l, z=i )

    e = ShuffleTiles( grid=(16,8), duration=2, seed=2 )
    main_scene.do( e + Reverse(e) )

    director.run (main_scene)
