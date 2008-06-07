#
# Cocos: 
# http://code.google.com/p/los-cocos/
#
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import pyglet
from pyglet.gl import *

import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    l = ColorLayer( 255,128,64,64 )
    main_scene.add( l, z=0 )

    l.do( FadeOut( duration=2) )
#    l.do( FadeIn( duration=2) )

    director.run (main_scene)
