# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import *
from cocos.utils import SequenceScene
from cocos.text import *
from cocos.layer import *

from pyglet import font
from pyglet.window import key

def main():
    # This simple test shows the usage of the SequenceScene.
    # It creates two simple scenes and adds them a ColorLayer.
    # Then the director is called with the SequenceScene of this two scenes.
    # Instead of using classes to create the scenes we will use the default
    # key to exit the scene which is ESCAPE.
    # The ESCAPE key is the default key to do a director.pop()

    director.init( resizable=True, width=640, height=480 )
    scene1 = Scene()
    scene2 = Scene()

    colorLayer1 = ColorLayer(32,32,255,255)
    colorLayer2 = ColorLayer(32,32,0,0)

    scene1.add( colorLayer1, z=0 )
    scene2.add( colorLayer2, z=0 )

    director.run( SequenceScene(scene1, scene2) )

if __name__ == '__main__':
    main()
