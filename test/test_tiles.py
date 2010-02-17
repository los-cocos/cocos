# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math

import pyglet
from pyglet.window import key
from pyglet.gl import *

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layers

class CarSprite(cocos.sprite.Sprite):
    motion = actions.Mover(0, 0, max_forward_speed=200,
        max_reverse_speed=-100)
    def update(self, dt):
        # handle input and move the car
        self.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        self.motion.acceleration = (keyboard[key.UP] - keyboard[key.DOWN]) * 400
        if keyboard[key.SPACE]: self.motion.speed = 0
        scroller.set_focus(self.x, self.y)

if __name__ == "__main__":
    from cocos.director import director
    director.init(width=600, height=300, do_not_scale=True, resizable=True)

    car_layer = layers.ScrollableLayer()
    car = CarSprite('car.png')
    car_layer.add(car)
    car.x = 200
    car.y = 100
    car.schedule(car.update)
    car.do(car.motion)

    scroller = layers.ScrollingManager()
    test_layer = tiles.load('road-map.xml')['map0']
    scroller.add(test_layer)
    scroller.add(car_layer)

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
    director.window.push_handlers(on_key_press)

    director.run(main_scene)

