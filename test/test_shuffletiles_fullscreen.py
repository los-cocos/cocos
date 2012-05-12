# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 0.49, s, t 0.51, s, t 2.49, s, t 2.51, s, t 2.99, s, t 3.1 s, q"

import pyglet
import cocos
from cocos.director import director
import cocos.actions as ac
from cocos.layer import *

class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        self.img.blit(0,0)

def toggle_fullscreen():
    director.window.set_fullscreen( not director.window.fullscreen )

def main():
    director.init( resizable=True, fullscreen=False )
    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    action1 = ac.ShuffleTiles( grid=(16,8), seed=2, duration=3 )
    action2 = ( ac.Delay(0.5) +
                ac.CallFunc(toggle_fullscreen) +
                ac.Delay(2.0) +
                ac.CallFunc(toggle_fullscreen))
    combo_action = action1 | action2

    main_scene.do( combo_action )
    director.run (main_scene)

if __name__ == '__main__':
    main()
