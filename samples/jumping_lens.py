#
# cocos2d
# http://python.cocos2d.org
#

from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer
from cocos.actions import JumpBy, Lens3D, Reverse

# create a layer with an image


class BackgroundLayer(Layer):

    def __init__(self):
        # always call super()
        super(BackgroundLayer, self).__init__()

        # load the image form file
        self.image = pyglet.resource.image('flag.png')

    def draw(self):
        # blit the image on every frame
        self.image.blit(0, 0)

if __name__ == "__main__":
    # initialize the director,
    # enabling to resize the main window
    director.init(resizable=True)

    # enable opengl depth test
    # since we are using z-values
    director.set_depth_test()

    # create an Scene with 1 layer: BackgroundLayer
    scene = Scene(BackgroundLayer())

    # create a Lens effect action
    #  radius: 150 pixels
    #  lens_effect: 0.7, a strong "lens". 0 means no effect at all. 1 means very strong
    #  center: center of the lens
    #  grid=(20,16): create a grid of 20 tiles x 16 tiles. More tiles will
    #     look better but the performance will decraese
    #  duration=10: 10 seconds
    lens = Lens3D(radius=150, lens_effect=0.7, center=(150, 150), grid=(20, 16), duration=50)

    # create a Jump action
    # Jump to the right 360 pixels doing:
    #   3 jumps
    #   of height 170 pixels
    #  in 4 seconds
    jump = JumpBy((360, 0), 170, 3, 4)

    # do and get the cloned action of lens'
    action = scene.do(lens)

    # perform the Jump action using as target the lens effect.
    # the Jump action will modify the 'position' attribute, and
    # the lens action uses the 'position' attribute as the center of the lens
    #
    # The action Jump + Reverse(Jump) will be repeated 5 times
    scene.do((jump + Reverse(jump)) * 5, target=action)

    # Run!
    director.run(scene)
