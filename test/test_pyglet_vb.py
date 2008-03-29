import pyglet
from pyglet.gl import *
# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

from cocos.actions import MeshSprite

window = pyglet.window.Window()

grossini = pyglet.resource.image("grossini.png")
grossini.anchor_x = grossini.width / 2
grossini.anchor_y = grossini.height / 2
ms = MeshSprite( grossini, 5,5 )
def update(dt):
    window.clear()
    ms.on_draw(dt)
    
pyglet.clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    pass
    
pyglet.app.run()