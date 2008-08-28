# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        sprite1 = Sprite('grossini.png')
        sprite1.position = x/2, y/2
        sprite1.children_anchor = 0,-100
        self.add( sprite1  )

        sprite2 = Sprite('grossini.png')
        sprite2.position = 50,0
        sprite1.add( sprite2  )

        sprite3 = Sprite('grossini.png')
        sprite3.position = -50,0
        sprite1.add( sprite3 )
        
        

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
