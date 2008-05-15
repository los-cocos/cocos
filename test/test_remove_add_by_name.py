# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director
from cocos.layer import *



if __name__ == "__main__":
    director.init( resizable=True )

    main_scene = cocos.scene.Scene()
    color = ColorLayer(255,0,0,255)
    main_scene.add( color, name='color' )

    # this one doesn't remove it's name
    main_scene.remove(color)

    # this one works
#    main_scene.remove('color')
    main_scene.add( color, name='color' )
