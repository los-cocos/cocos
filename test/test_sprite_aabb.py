# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
import pyglet
from pyglet.gl import *

## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        sprite = Sprite('grossini.png')
        sprite.position = x/2, y/2
        sprite.do( RotateBy( duration=2, angle=360 ) )
        self.add( sprite )


        self.sprite = sprite


    def draw( self ):
        r = self.sprite.get_AABB()
        left = r.left
        bottom = r.bottom
        right = r.right
        top = r.top
        glBegin(GL_LINE_LOOP)
        glColor4f(1, 0, 0, 1)
        glVertex3f(left, bottom, 0)
        glVertex3f(right, bottom, 0)
        glVertex3f(right, top, 0)
        glVertex3f(left, top, 0)
        glEnd()



if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
