# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math

import pyglet
from pyglet.window import key
from pyglet.gl import *

import cocos
from cocos import tiles, actions

class CarSprite(cocos.sprite.Sprite):
    speed = 0
    def update(self, dt):
        # handle input and move the car
        self.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        speed = self.speed
        speed += (keyboard[key.UP] - keyboard[key.DOWN]) * 50
        if keyboard[key.SPACE]: speed = 0
        if speed > 200: speed = 200
        if speed < -100: speed = -100
        self.speed = speed
        r = math.radians(self.rotation)
        s = dt * speed
        self.x += math.sin(r) * s
        self.y += math.cos(r) * s
        scroller.set_focus(self.x, self.y)

if __name__ == "__main__":
    from cocos.director import director
    director.init(width=600, height=300, do_not_scale=True)

    car_layer = tiles.ScrollableLayer()
    car = CarSprite('car.png')
    car.x=200
    car.y=100
    car.schedule(car.update)
    car_layer.add(car)

    scroller = tiles.ScrollingManager()
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

