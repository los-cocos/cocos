from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "tilemap, collide_map"

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer


class PlatformerController(actions.Action, tiles.RectMapCollider):
    on_ground = True
    MOVE_SPEED = 200
    JUMP_SPEED = 500
    GRAVITY = -1500

    def start(self):
        # initial velocity
        self.target.velocity = (0, 0)

    def step(self, dt):
        global keyboard, tilemap, scroller
        dx, dy = self.target.velocity

        # using the player controls, gravity and other acceleration influences
        # update the velocity
        dx = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * self.MOVE_SPEED *dt
        dy = dy + self.GRAVITY * dt
        if self.on_ground and keyboard[key.SPACE]:
            dy = self.JUMP_SPEED

        # get the player's current bounding rectangle
        last = self.target.get_rect()
        new = last.copy()
        new.x += dx
        new.y += dy * dt

        # run the collider
        dx, dy = self.target.velocity = self.collide_map(tilemap, last, new, dx, dy)
        self.on_ground = bool(new.y == last.y)

        # player position is anchored in the center of the image rect
        self.target.position = new.center

        # move the scrolling view to center on the player
        scroller.set_focus(*new.center)

description = """
Shows how to use a tilemap to control collision between actors and the terrain.
Use Left-Right arrows and space to control.
Use D to show cell / tile info
"""

def main():
    global keyboard, tilemap, scroller
    from cocos.director import director
    director.init(width=800, height=600, autoscale=False)

    print(description)
    # create a layer to put the player in
    player_layer = layer.ScrollableLayer()
    # NOTE: the anchor for this sprite is in the CENTER (the cocos default)
    # which means all positioning must be done using the center of its rect
    player = cocos.sprite.Sprite('witch-standing.png')
    player_layer.add(player)
    player.do(PlatformerController())

    # add the tilemap and the player sprite layer to a scrolling manager
    scroller = layer.ScrollingManager()
    tilemap = tiles.load('platformer-map.xml')['level0']
    scroller.add(tilemap, z=0)
    scroller.add(player_layer, z=1)

    # set the player start using the player_start token from the tilemap
    start = tilemap.find_cells(player_start=True)[0]
    r = player.get_rect()

    # align the mid bottom of the player with the mid bottom of the start cell
    r.midbottom = start.midbottom

    # player image anchor (position) is in the center of the sprite
    player.position = r.center

    # construct the scene with a background layer color and the scrolling layers
    platformer_scene = cocos.scene.Scene()
    platformer_scene.add(layer.ColorLayer(100, 120, 150, 255), z=0)
    platformer_scene.add(scroller, z=1)

    # track keyboard presses
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    # allow display info about cells / tiles 
    def on_key_press(key, modifier):
        if key == pyglet.window.key.D:
            tilemap.set_debug(True)
    director.window.push_handlers(on_key_press)

    # run the scene
    director.run(platformer_scene)


if __name__ == '__main__':
    main()
