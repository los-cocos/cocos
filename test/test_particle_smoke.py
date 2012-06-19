# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1, s, t 2, s, t 3, s, t 4, s, q"
tags = "particles, Smoke"

import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from cocos.particle_systems import *

class L(Layer):
    def __init__(self):
        super( L, self).__init__()

#        p = Fireworks()
#        p = Explosion()
#        p = Fire()
#        p = Flower()
        p = Smoke()
#        p = Sun()
#        p = Spiral()
#        p = Meteor()
#        p = Galaxy()

        p.position = (320,100)
        self.add( p )

def main():
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()
    main_scene.add( ColorLayer(0,0,0,255), z=0 )
    main_scene.add( L(), z=1 )

    director.run( main_scene )

if __name__ == '__main__':
    main()
