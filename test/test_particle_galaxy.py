from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "f 10 0.033, s, f 20 0.033, s, f 30 0.033, s, f 30 0.033, s, q"
tags = "particles, Galaxy"

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
#        p = Sun()
#        p = Spiral()
#        p = Meteor()
        p = Galaxy()

        p.position = (320,240)
        self.add( p )

def main():
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    main_scene.add( L() )

    director.run( main_scene )

if __name__ == '__main__':
    main()
