# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos import draw
import pyglet

import random
ri = random.randint

class TestFigure(draw.Canvas):
    def render(self):
        x,y = director.get_window_size()
        ys = y/4
        ye = ys*3
        xs = x/4
        line_width = 50
        self.set_color( (255,255,0,125) )
        self.set_stroke_width( line_width )
        
        # draw lines
        self.set_endcap( draw.ROUND_CAP )
        self.move_to( (x/2, y/2-line_width/2) ); self.line_to( (x/2-300,y/2-300) )        
        
        
            
        
class TestLayer(cocos.layer.Layer):
    is_event_handler = True
    
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        self.add( TestFigure() )        
        self.schedule( lambda x: 0 )

    def on_key_press(self, k, mod):
        self.scale += 1
        
if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

