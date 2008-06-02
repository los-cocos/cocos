# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
import random


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        self.sprite = Sprite('grossini.png')
        self.sprite.position = x/2, y/2
        self.add( self.sprite  )
        
        self.schedule( self.change_x )
        self.schedule_interval( self.change_y, 1 )
        
    def change_x(self, dt):
        self.sprite.x = random.random()*director.get_window_size()[0]
    def change_y(self, dt):
        self.sprite.y = random.random()*director.get_window_size()[1]
        
        

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
