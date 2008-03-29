# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import ActionSprite, SpriteGroup, Rotate, MoveBy, ScaleBy
import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.image2 = pyglet.resource.image('grossinis_sister1.png')
        self.image2.anchor_x = self.image2.width / 2
        self.image2.anchor_y = self.image2.height / 2

        self.image3 = pyglet.resource.image('grossinis_sister2.png')
        self.image3.anchor_x = self.image3.width / 2
        self.image3.anchor_y = self.image3.height / 2

        self.sprite = ActionSprite( self.image )
        self.add( self.sprite, (x/2, y/2) )
        
        self.sprite2 = ActionSprite( self.image2  )
        self.sprite.add( self.sprite2, (0, 101) )

        self.sprite3 = ActionSprite( self.image3  )
        self.sprite2.add( self.sprite3, (0, 102) )

        self.sprite.do( Rotate(360,10) ) 
        self.sprite2.do( ScaleBy(2,5)+ScaleBy(0.5,5) ) 
        self.sprite2.do( Rotate(360,10) ) 
        self.sprite3.do( Rotate(360,10) ) 
        self.sprite3.do( ScaleBy(2,5)+ScaleBy(0.5,5) ) 
        
        

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
