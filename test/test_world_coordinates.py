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

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        sprite1 = Sprite('grossini.png')
        self.add( sprite1  )
        sprite1.position = 300,300

        sprite2 = Sprite('grossini.png')
        sprite1.add( sprite2  )
        sprite2.position = -50,-50

        sprite3 = Sprite('grossini.png')
        sprite2.add( sprite3 )
        sprite3.position = 150,150
        sprite3.rotation = 0
        sprite3.opacity = 128

        self.sprite3 = sprite3

        print sprite1.point_to_world( (0,0) )
        print sprite1.get_world_transform()

        print sprite2.point_to_world( (0,0) )
        print sprite2.get_world_transform()

        print sprite3.point_to_world( (0,0) )
        print sprite3.get_world_transform()

        sprite3.do( RotateBy(360,20) )

    def draw( self ):

        p = self.sprite3.point_to_world( (0,0) )
   
        glPointSize(5)
        glBegin(GL_POINTS)
        glColor4f(1, 0, 0, 1)
        glVertex3f(p.x, p.y, 0)
        glEnd()


if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
