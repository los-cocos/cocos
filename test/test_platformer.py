from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "tilemap, collide_map, collider"

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer, mapcolliders


class PlatformerController(actions.Action):
    on_ground = True
    MOVE_SPEED = 300
    JUMP_SPEED = 800
    GRAVITY = -1200

    def start(self):
        self.target.velocity = (0, 0)

    def step(self, dt):
        global keyboard, scroller
        vx, vy = self.target.velocity

        # using the player controls, gravity and other acceleration influences
        # update the velocity
        vx = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * self.MOVE_SPEED
        vy += self.GRAVITY * dt
        if self.on_ground and keyboard[key.SPACE]:
            vy = self.JUMP_SPEED

        # with the updated velocity calculate the (tentative) displacement
        dx = vx * dt
        dy = vy * dt

        # get the player's current bounding rectangle
        last = self.target.get_rect()

        # build the tentative displaced rect
        new = last.copy()
        new.x += dx
        new.y += dy

        # account for hitting obstacles, it will adjust new and vx, vy
        self.target.velocity = self.target.collision_handler(last, new, vx, vy)

        # update on_ground status
        self.on_ground = (new.y == last.y)

        # update player position; player position is anchored at the center of the image rect
        self.target.position = new.center

        # move the scrolling view to center on the player
        scroller.set_focus(*new.center)

description = """
Shows how to use a mapcollider to control collision between actors and
the terrain as described by a tilemap.
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

    # add the tilemaps and the player sprite layer to a scrolling manager
    scroller = layer.ScrollingManager()
    fullmap = tiles.load('platformer-map.xml')
    tilemap_walls = fullmap['walls']
    scroller.add(tilemap_walls, z=0)
    tilemap_decoration = fullmap['decoration']
    scroller.add(tilemap_decoration, z=1)
    scroller.add(player_layer, z=2)

    # set the player start using the player_start token from the map
    start = tilemap_decoration.find_cells(player_start=True)[0]
    r = player.get_rect()

    # align the mid bottom of the player with the mid bottom of the start cell
    r.midbottom = start.midbottom

    # player image anchor (position) is in the center of the sprite
    player.position = r.center

    # give a collision handler to the player
    mapcollider = mapcolliders.RectMapCollider(velocity_on_bump='slide')
    player.collision_handler = mapcolliders.make_collision_handler(
        mapcollider, tilemap_walls)

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
