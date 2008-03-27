# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import ActionSprite, MoveBy, Delay, RandomDelay

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.sprite = ActionSprite( self.image )
        self.add( self.sprite, (0,y/2) )
        self.sprite2 = ActionSprite( self.image )
        self.add( self.sprite2, (0,y/4) )
        self.sprite3 = ActionSprite( self.image )
        self.add( self.sprite3, (0,y/4*3) )
        
        self.sprite.do( Delay(3) + MoveBy( (x, 0) )  )
        self.sprite2.do( RandomDelay(2,4) + MoveBy( (x, 0) )  )
        self.sprite3.do( RandomDelay(2,4) + MoveBy( (x, 0) )  )
        

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
