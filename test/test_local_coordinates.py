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

    is_event_handler = True

    def __init__(self):

        super( TestLayer, self ).__init__()
       
        self.mouse_x = self.mouse_y = 0

        x,y = director.get_window_size()
        
        sprite1 = Sprite('grossini.png')
        self.add( sprite1  )
        sprite1.position = 300,300
        sprite1.opacity = 128

        sprite2 = Sprite('grossini.png')
        sprite1.add( sprite2  )
        sprite2.position = -50,-50
        sprite2.opacity = 128

        sprite3 = Sprite('grossini.png')
        sprite2.add( sprite3 )
        sprite3.position = 150,150
        sprite3.rotation = 90
        sprite3.scale = 2
        sprite3.opacity = 128


        sprite1.do( ScaleBy(1.5, 10) )
        sprite2.do( MoveBy((100,-150),5) )
        sprite3.do( RotateBy(360,20) )

        self.sprites = [sprite1, sprite2, sprite3]

    def draw( self ):
        glPointSize(16)

        glBegin(GL_POINTS)
        glColor4f(1, 0, 0, 1)
        glVertex3f(self.mouse_x, self.mouse_y, 0)

        glColor4f(1,1,0,1)
        for s in self.sprites:
            p = s.point_to_world( (0,0) )
            glVertex3f(p.x, p.y, 0)

        glEnd()

    def test_collisions( self, x, y ):
        for s in self.sprites:
            rect = s.get_rect()
            p = s.point_to_local( (x, y) )
            if rect.contains( p.x, p.y ):
                s.color = (255,0,0)
            else:
                s.color = (255,255,255)

    def on_mouse_press(self, x, y, buttons, modifiers):
        x, y = director.get_virtual_coordinates (x, y)
        self.mouse_x,self.mouse_y = x,y
        self.test_collisions(x,y)

    def on_mouse_drag( self, x, y, dx, dy, buttons, modifiers ):
        x, y = director.get_virtual_coordinates (x, y)
        self.mouse_x,self.mouse_y = x,y
        self.test_collisions(x,y)

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
