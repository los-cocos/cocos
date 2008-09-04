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

        self.batch = cocos.sprite.BatchNode()
        self.add( self.batch )

        self.sprite = Sprite('grossini.png')
        self.sprite.position = x/2, y/2

        self.sprite2 = Sprite('grossini.png')
        self.sprite2.position = 20, 30

        self.sprite5 = Sprite('grossini.png')
        self.sprite5.position = -20, 30

        self.sprite3 = Sprite('grossini.png')
        self.sprite3.position = -20, -30

        self.sprite4 = Sprite('grossini.png')
        self.sprite4.position = 20, -30

        self.sprite.add( self.sprite2, z=-1, name="temp" )
        self.sprite3.add( self.sprite4, z=1 )
        self.batch.add( self.sprite  )
        self.sprite.add( self.sprite3, z=-1 )
        self.sprite2.add( self.sprite5, z=1 )
        self.sprite.remove("temp")


if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
