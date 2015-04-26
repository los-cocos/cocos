# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "tmx, hexmap, mouse hit"

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
import cocos.layer
from cocos import tiles, actions, layer
import cocos.sprite

class DriveCar(actions.Driver):
    def step(self, dt):
        # handle input and move the car
        self.target.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        self.target.acceleration = (keyboard[key.UP] - keyboard[key.DOWN]) * 400
        if keyboard[key.SPACE]: self.target.speed = 0
        super(DriveCar, self).step(dt)
        scroller.set_focus(self.target.x, self.target.y)

def tint_green_hexmap_borders(hexmap):
    columns = len(hexmap.cells)
    rows = len(hexmap.cells[0])
    ## leftmost and rightmost colums
    for col in [0, columns-1]:
        for j in range(rows):
            hexmap.set_cell_color(col, j, (0, 255, 0))
    ## upper and lower cells
    for col in range(columns):
        for k in [0, rows-1]:
            hexmap.set_cell_color(col, k, (0, 255, 0))
    
def main():
    global keyboard, scroller, old_ij, old_cell, old_highlighted_color
    from cocos.director import director
    director.init(width=600, height=300, autoscale=False, resizable=True)

    car_layer = layer.ScrollableLayer()
    car = cocos.sprite.Sprite('car.png')
    car_layer.add(car)
    car.position = (200, 100)
    car.max_forward_speed = 200
    car.max_reverse_speed = -100
    car.do(DriveCar())

    scroller = layer.ScrollingManager()
    map_loaded = tiles.load('hexmap.tmx')
    # In Tiled we named 'tile_layer_1' our sample layer 
    test_layer = map_loaded['tile_layer_1']
    tint_green_hexmap_borders(test_layer)
    scroller.add(test_layer)
    scroller.add(car_layer)

    old_ij = 'nonexist'
    old_highlighted_color = None
    old_cell = None
    
    main_scene = cocos.scene.Scene(scroller)

    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    def on_key_press(key, modifier):
        if key == pyglet.window.key.Z:
            if scroller.scale == .75:
                scroller.do(actions.ScaleTo(1, 2))
            else:
                scroller.do(actions.ScaleTo(.75, 2))
        elif key == pyglet.window.key.D:
            test_layer.set_debug(True)
        elif key == pyglet.window.key.Q:
            tint_red_hexmap_borders(test_layer)
    director.window.push_handlers(on_key_press)

    def on_mouse_motion(x, y, dx, dy ):
        global scroller, old_ij, old_cell, old_highlighted_color
        #vh, vy = director.get_virtual_coordinates(x, y)
        vx, vy = scroller.pixel_from_screen(x,y)
        ij = test_layer.get_key_at_pixel(vx, vy)
        if ij == old_ij:
            return
        # restore color
        if old_cell:
            p, q = old_ij
            if old_highlighted_color is None:
                test_layer.set_cell_color(p, q, (255, 255, 255))
                del old_cell.properties['color4']
            else:
                test_layer.set_cell_color(p, q, old_highlighted_color[:3])

        # record info and set color
        old_ij = ij
        i, j = ij
        print(i,j)
        old_cell = test_layer.get_cell(i, j)
        if old_cell is None:
            return
        old_highlighted_color = old_cell.properties.get('color4', None)
        test_layer.set_cell_color(i, j, (255, 0, 0))
    director.window.push_handlers(on_mouse_motion)
            
        
    director.run(main_scene)

description = """
Shows a tmx map with hexagonal tiles.

The tiles in the map border are programatically tinted green.

Moving the mouse over the window will highlight in red the tile
under the mouse cursor.

The tile waterHex.png was derived from the same named in the tileset
'Pastel Resources Hex' by 'qubodup', found at
http://opengameart.org/content/pastel-resources-hex-tiles-55x64-and-64x55
"""

if __name__ == '__main__':
    print(description)
    main()
