from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 0.5, s, t 1, s, t 1.5, s, q"
tags = "Sprite, bounding box"

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import *
import pyglet
from pyglet.gl import *
import cocos.euclid

## the following is in case we want to get the images
## from other directories:
# pyglet.resource.path.append("/data/other/directory")
# pyglet.resource.reindex()


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        parent = Sprite('grossinis_sister1.png')
        self.add( parent )
        parent.position = ( x//2, y//2 )

        sprite = Sprite('grossinis_sister2.png')
        sprite.position = 100,140
        sprite.do( RotateBy( duration=2, angle=360 ) )
        sprite.do( ScaleBy( duration=2, scale=2 ) )
        sprite.do( MoveBy( duration=2, delta=(200,0) ) )
        parent.add( sprite )
        sprite.opacity = 128
        self.sprite1 = sprite

        sprite = Sprite('grossini.png')
        self.add( sprite )
        sprite.position = 100,140
        sprite.do( RotateBy( duration=2, angle=360 ) )
        sprite.do( ScaleBy( duration=2, scale=2 ) )
        sprite.do( MoveBy( duration=2, delta=(200,0) ) )

        self.sprite2 = sprite


    def draw( self ):
        # local coords
        r = self.sprite2.get_AABB()

        left,bottom = r.left,r.bottom
        right,top = r.right,r.top

        glBegin(GL_LINE_LOOP)
        glColor4f(1, 0, 0, 1)
        glVertex3f(left, bottom, 0)
        glVertex3f(right, bottom, 0)
        glVertex3f(right, top, 0)
        glVertex3f(left, top, 0)
        glEnd()

        # world coords

        bl = self.sprite1.point_to_world( (0,0) )
        x,y = self.sprite1.width, self.sprite2.height
        tr = self.sprite1.point_to_world( (x,y) )

        left,bottom = bl.x, bl.y
        right,top = tr.x, tr.y

        bl = self.sprite1.point_to_world( (0,0) )
        glPointSize(16)
        glBegin(GL_POINTS)
        glColor4f(1, 1, 0, 1)
        glVertex3f(bl.x, bl.y, 0)
        glEnd()

#        glBegin(GL_LINE_LOOP)
#        glColor4f(1, 1, 0, 1)
#        glVertex3f(left, bottom, 0)
#        glVertex3f(right, bottom, 0)
#        glVertex3f(right, top, 0)
#        glVertex3f(left, top, 0)
#        glEnd()

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
