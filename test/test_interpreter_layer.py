# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
import pyglet
        

if __name__ == "__main__":
    director.init( resizable=True )
    interpreter_layer = cocos.layer.PythonInterpreterLayer()
    main_scene = cocos.scene.Scene(interpreter_layer)
    director.run(main_scene)
