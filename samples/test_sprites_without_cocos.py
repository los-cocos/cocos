#
# Los Cocos: Sprite Test
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from cocos.actions import *


batch = pyglet.graphics.Batch()
window = pyglet.window.Window()
fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
    fps_display.draw()
    batch.draw()

image = pyglet.resource.image('grossini.png')
image.anchor_x = image.width / 2
image.anchor_y = image.height / 2
sprite = ActionSprite(image, x=window.width/2, y=window.height/2, batch=batch)

image = pyglet.resource.image('grossinis_sister1.png')
image.anchor_x = image.width / 2
image.anchor_y = image.height / 2
sprite_sister1 = ActionSprite(image, x=20, y=window.height/2, batch=batch)

image = pyglet.resource.image('grossinis_sister2.png')
image.anchor_x = image.width / 2
image.anchor_y = image.height / 2
sprite_sister2 = ActionSprite(image, x=20, y=window.height/2, batch=batch)

goto = MoveTo( (400,50), 2 )
move = MoveBy( (150,0), 2 )
rot = Rotate( 360, 1, time_func=accelerate )
scale = Scale( 8, 1 )
scale2 = Scale( 3, 5, time_func=accelerate  )
jump = Jump( 50, 600, 6, 5, time_func=accelerate )
blink = Blink( 10, 2 )
fadein = FadeIn( 2 )
fadeout = FadeOut( 2 )
place = Place( (20,50) )
import foo
bz = Bezier( foo.curva, 3, time_func=accelerate )

sprite.do( place + blink + Repeat(bz,2) + fadeout + Repeat( fadein + rot + move + scale + move + rot) )
sprite_sister1.do( Delay(0.4) + Repeat(jump) | Repeat(scale2) )
sprite_sister2.do( Repeat(jump) | Repeat(scale2)  ) 


pyglet.app.run()

