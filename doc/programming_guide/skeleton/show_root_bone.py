# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
#

## import all the stuff we need from cocos
import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos import skeleton

# import the skeleton we have created
import root_bone

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        
        # create a ColorSkin for our skeleton
        self.skin = skeleton.ColorSkin(root_bone.skeleton,
                                        (255,0,0,255))
        
        # add the skin to the scene
        self.add( self.skin )
        x, y = director.get_window_size()
        self.skin.position = x/2, y/2
   
    
if __name__ == "__main__":
    # usual cocos setup
    director.init()
    test_layer = TestLayer()
    bg_layer = cocos.layer.ColorLayer(255,255,255,255)
    main_scene = cocos.scene.Scene()
    main_scene.add(bg_layer, z=-10)
    main_scene.add(test_layer, z=10)
    director.run(main_scene)
