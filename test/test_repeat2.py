# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import Repeat, Rotate, MoveBy, Place
from cocos.sprite import ActionSprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.sprite = ActionSprite( self.image )
        self.add( self.sprite, (x/2, y/2) )
        move = MoveBy((100,0), 1)
        rot = Rotate(360, 1)
        seq = Place((x/4,y/2)) + rot+move+rot+move
        print seq
        self.sprite.do( Repeat ( seq ) )
        

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
