from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, t 1.1, s, t 2.1, s, t 3.1, s, t 4.1, s, t 5.1, s, t 6.1, s, q"
tags = "scrolling, ScrollingManager, autoscale"
autotest = 0

import math

import pyglet
from pyglet.window import key
from pyglet.gl import *

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer
from cocos.director import director
import cocos.euclid as eu
from cocos.actions import Delay, CallFunc, ScaleTo

view_width = 640
view_height = 480

world_width = 1000 + 4*98 #1392
world_height = 1000

class ProbeQuad(cocos.cocosnode.CocosNode):
    def __init__(self, r, color4):
        super(ProbeQuad,self).__init__()
        self.color4 = color4
        self.vertexes = [(r,0,0),(0,r,0),(-r,0,0),(0,-r,0)]

    def draw(self):
        glPushMatrix()
        self.transform()
        glBegin(GL_QUADS)
        glColor4ub( *self.color4 )
        for v in self.vertexes:
            glVertex3i(*v)
        glEnd()
        glPopMatrix()


class SquareLand(cocos.layer.ScrollableLayer):
    is_event_handler = True
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        super(SquareLand,self).__init__()
        self.px_width = world_width
        self.px_height = world_height

        #dummy objects in the world: a big framed background and squares
        bg = cocos.layer.ColorLayer(170,170,0,255,width=world_width, height=world_height)
        self.add(bg, z=0)
        margin = int(world_width*0.01)
        #print 'margin',margin
        self.margin = margin
        bg = cocos.layer.ColorLayer(0,170,170,255,width=world_width-2*margin,height=world_height-2*margin)
        bg.position = (margin,margin)
        self.add(bg, z=1)

        mod = (world_width-2.0*margin)/10.0
        #print mod
        y = margin+mod
        self.marks_positions = []
        while y<world_height-mod:
            x = margin+mod
            while x<world_width-mod:
                red = 55+int(200.0*x/world_width)
                blue = 55+int(200.0*y/world_height)
                actor = cocos.layer.ColorLayer( red, 0, blue, 255,
                                        width = 2*int(mod), height = 2*int(mod))
                actor.position = x,y
                self.marks_positions.append((x,y))
                self.add(actor, z=3)
                x += 3*mod
            y += 3*mod
        self.marks_positions = self.marks_positions[:3]

        self.player = cocos.sprite.Sprite( 'grossinis_sister1.png' )
        self.player.scale = 0.4
        self.player.model_width = self.player.width
        self.player.model_height = self.player.height

        self.player.position = (mod/2+margin, mod/2+margin)#(200,200)
        self.player.fastness = 200
        self.add(self.player, z=4)

        self.bindings = { #key constant : button name
            key.LEFT:'left',
            key.RIGHT:'right',
            key.UP:'up',
            key.DOWN:'down',
            key.PLUS:'zoomin',
            key.MINUS:'zoomout'
            }
        self.buttons = { #button name : current value, 0 not pressed, 1 pressed
            'left':0,
            'right':0,
            'up':0,
            'down':0,
            'zoomin':0,
            'zoomout':0
            }
        self.schedule(self.step)

    def on_enter(self):
        super(SquareLand,self).on_enter()
        self.scroller = self.get_ancestor(cocos.layer.ScrollingManager)
        self.scene = self.get_ancestor(cocos.scene.Scene)
        self.scene.f_refresh_marks = self.refresh_marks

    #tracking of keys : keys updates self.buttons, model uses buttons
    def on_key_press(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m ):
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            return True
        return False

    def on_mouse_press(self,x,y,button,modifiers):
        # test from screen coords
        print('on_mouse_press:')
        vx, vy = self.scroller.pixel_from_screen(x,y)
        print('\tpixel_from_screen(x, y):', vx, vy)

    def clamp(self, actor, new_pos):
        x,y = new_pos
        if  x-actor.model_width//2<self.margin:
            x = self.margin + actor.model_width//2
        elif x+actor.model_width//2>self.world_width-self.margin:
            x = self.world_width-self.margin-actor.model_width//2
        if  y-actor.model_height//2<self.margin:
            y = self.margin + actor.model_height//2
        elif y+actor.model_height//2>self.world_height-self.margin:
            y = self.world_height-self.margin-actor.model_height//2
        return x,y

    def step( self, dt ):
        buttons = self.buttons
        move_dir = eu.Vector2(buttons['right']-buttons['left'],
                              buttons['up']-buttons['down'])
        changed = False
        if move_dir:
            new_pos = self.player.position + self.player.fastness*dt*move_dir.normalize()
            new_pos = self.clamp(self.player, new_pos)

            self.player.position = new_pos
            changed = True

        new_zoom = self.scroller.scale + (buttons['zoomin']-buttons['zoomout'])*0.2*dt
        if new_zoom < 0.3:
            new_zoom = 0.3
        elif new_zoom > 2.0:
            new_zoom = 2.0
        if new_zoom != self.scroller.scale:
            self.scroller.scale = new_zoom
            changed = True

        if changed:
            self.update_after_change()

    def update_after_change(self):
        self.scroller.set_focus(*self.player.position)
        self.refresh_marks()

    def refresh_marks(self):
        for mark, position in zip(self.scene.marks, self.marks_positions):
            screen_pos = self.scroller.pixel_to_screen(*position)
            mark.position = screen_pos

    def teleport_player(self, x, y):
        """ only used by autotest """
        self.player.position = x, y
        self.update_after_change()


class TestScene(cocos.scene.Scene):
    def __init__(self):
        super(TestScene,self).__init__()
        self.marks = []
        for i in range(1,4):
            mark = ProbeQuad(3,(0,255//i, 0, 255))
            mark.position = (-20, -20)
            self.marks.append(mark)
            self.add(mark, z=2)

    def on_enter(self):
        director.push_handlers(self.on_cocos_resize)
        super(TestScene, self).on_enter()

    def on_cocos_resize(self, usable_width, usable_height):
        self.f_refresh_marks()

def show_common_text():
    print("""
tests ScrollingManager and ScrollableLayer when the contents are not provided
by a tilemap.

You can run the test in the two available modes:'autoscale' True/False
Look near the script begin to choose the mode; the instructions and expected
results text will match the mode.

use arrows to move, +- in the main keyboard (not the keypad) for zoom,
ctrl-f to toggle fullscreen status.

You will need grossinis_sister1.png , to be found in the test directory.

You will need cocos r966+ ( for 'cocos_on_resize' event and supresion of
NotImplementedError in pixel_to_screen)

For clarity set view_width, view_height to respect your desktop aspect
ratio; look near the script begin

""")

def show_mode_1_text():
    print("""
Mode: autoscale, that is autoscale=True

1. scroll constraits works:
    verify that moving the player you can make the view scroll to reveal all
    of the world, and not more than that.

2. resize maps the correct area and the scroll constraits work ok after a
resize:
    a. move the player to bottom left corner. Use ctrl-f to repeatedly switch
    between windowed and fullscreen.
    Both screens should show the same world area, only at different scale.

    b. Repeat at the top-right corner.

    c. when in fullscreen,  verify that moving the player you can make the
    view scroll to reveal all of the world, and not more than that.

3. zooming ( ScrollerManager scale) works:
    zoom in or out using key '+' or '-', not so much that all the world shows
    in a single screen, then repeat 1), 2)

4. consistency screen to world coordinates conversion(aka pixel_from_screen):
    a. restart the script, mouse click the inner bottom left corner, do ctrl-f
    click again over the inner bottom left corner, zoom a little, click again
    over the the inner bottom left corner.
    Now look at the console: the pixel_from_screen values must all be near a
    common value.

    b. restart the script, scroll to the top right corner, repeat a. replacing
    'botton left' by 'top left'

5. world to screen coordinate changes (aka pixel_to_screen) correctness:
    restart the script; move a bit. Look at the lower left corners in the lower
    row of squares; you should see a small square in the shades of green.
    moving, zomming, resizing (ctrl-f) should not alter the relative position of
    small green squeares with respect to the world.

6. good behavior when world small that the view:
    scale down (zoom out) to the max. When the world becomes smaller than the
    view, it should nicely center in the screen.
    Moving the player from left to right border should not produce 'jumps' on
    the view.
""")

def show_mode_2_text():
    print("""
Mode: not autoscale, that is autoscale=False

1. scroll constraits works:
    verify that moving the player you can make the view scroll to reveal all
    of the world, and not more than that.

2. resize maps the correct area and the scroll constraits work ok after a
resize:
    a. move the player to bottom left corner. Use ctrl-f to repeatedly switch
    between windowed and fullscreen.
    Both screens should depict the world at the same scale, thus the bigger
    view will more area in the world.
    When going from big to small, the player must be visible n the small view.
    When going small to big, the bg should show all showed in the small plus
    some extra area.

    b. Repeat at the top-right corner.

    c. when in fullscreen,  verify that moving the player you can make the
    view scroll to reveal all of the world, and not more than that.

3. zooming ( ScrollerManager scale) works:
    zoom in or out using key '+' or '-', not so much that all the world shows
    in a single screen, then repeat 1), 2)

4. consistency screen to world coordinates conversion(aka pixel_from_screen):
    a. restart the script, mouse click the inner bottom left corner, do ctrl-f
    click again over the inner bottom left corner, zoom a litle, click again
    over the the inner bottom left corner.
    Now look at the console: the pixel_from_screen values must all be near a
    common value.

    b. restart the script, scroll to the top right corner, repeat a. replacing
    'botton left' by 'top left'

5. world to screen coordinate changes (aka pixel_to_screen) correctness:
    restart the script; move a bit. Look at the lower left corners in the lower
    row of squares; you should see a small square in the shades of green.
    moving, zomming, resizing (ctrl-f) should not alter the relative position of
    small green squeares with respect to the world.

6. good behavior when world small that the view:
    scale down (zoom out) to the max. When the world becomes smaller than the
    view, it should nicely center in the screen.
    Moving the player from left to right border should not produce 'jumps' on
    the view.
""")

def main():
    show_common_text()
    autoscale = True
    if autoscale:
        show_mode_1_text()
    else:
        show_mode_2_text()
    director.init(view_width, view_height, autoscale=autoscale)

    scene = TestScene()
    world_layer = SquareLand(world_width, world_height)
    scroller = cocos.layer.ScrollingManager()
    if autotest:
        def resize_scroller():
            scroller.scale = 0.75
        w, h = world_width, world_height
        template_action = (
            Delay(0.05) + 
            CallFunc(world_layer.teleport_player, 0, 0) + Delay(1) +
            CallFunc(world_layer.teleport_player, w//2, 0) + Delay(1) +
            CallFunc(world_layer.teleport_player, w//2, h) +Delay(1) +
            CallFunc(world_layer.teleport_player, w, h) + Delay(1) +
            CallFunc(resize_scroller) + Delay(1) +
            CallFunc(director.window.set_size, 800, 600) + CallFunc(world_layer.update_after_change)
            )
        world_layer.do(template_action)
    scroller.add(world_layer)
    scene.add(scroller)
    director.run(scene)

if __name__ == '__main__':
    main()
