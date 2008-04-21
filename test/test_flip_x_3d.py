# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.sprite import *
from cocos.layer import *
import pyglet

class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        x,y = director.get_window_size()

        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.image_sister1 = pyglet.resource.image('grossinis_sister1.png')
        self.image_sister1.anchor_x = self.image_sister1.width / 2
        self.image_sister1.anchor_y = self.image_sister1.height / 2

        self.image_sister2 = pyglet.resource.image('grossinis_sister2.png')
        self.image_sister2.anchor_x = self.image_sister2.width / 2
        self.image_sister2.anchor_y = self.image_sister2.height / 2

        sprite1 = ActionSprite( self.image )
        sprite2 = ActionSprite( self.image_sister1 )
        sprite3 = ActionSprite( self.image_sister2 )

        self.add( sprite1, (x/2, y/2) )
        self.add( sprite2, (3*x/4, y/2) )
        self.add( sprite3, (1*x/4, y/2) )

if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    red = ColorLayer(1.0, 0.0, 0.0, 1.0)
    blue = ColorLayer(0.0, 0.0, 1.0, 1.0)
    green = ColorLayer(0.0, 1.0, 0.0, 1.0)
    white = ColorLayer(1.0, 1.0, 1.0, 1.0)

    main_scene.add( red, z=0 )
    main_scene.add( blue, z=1, scale=0.75 )
    main_scene.add( green, z=2, scale=0.5 )
    main_scene.add( white, z=3, scale=0.25 )

    main_scene.add( SpriteLayer(), z=4 )

    main_scene.do( FlipX3D(duration=2) )
    director.run (main_scene)
