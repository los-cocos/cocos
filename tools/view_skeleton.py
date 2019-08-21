"""Usage:
    python %s file_with_skeleton.py

An example of input file is ../test/sample_skeleton.py

Should show a cocos window drawing the skeleton defined in said file, red over white.
"""
from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import imp

## import all the stuff we need from cocos
import cocos
from cocos.director import director
from cocos.sprite import Sprite


class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()
        
        # create a ColorSkin for our skeleton
        sk_file = imp.load_source("user_skeleton", sys.argv[1])
        self.skin = cocos.skeleton.ColorSkin(sk_file.skeleton,
                                        (255,0,0,255))
        
        # add the skin to the scene
        self.add( self.skin )
        x, y = director.get_window_size()
        self.skin.position = x // 2, y // 2
   
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__ % sys.argv[0])
        sys.exit()

    # usual cocos setup
    director.init()
    test_layer = TestLayer()
    bg_layer = cocos.layer.ColorLayer(255,255,255,255)
    main_scene = cocos.scene.Scene()
    main_scene.add(bg_layer, z=-10)
    main_scene.add(test_layer, z=10)
    director.run(main_scene)
