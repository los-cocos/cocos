# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
"""Pause scene"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene

import pyglet

from pyglet.gl import *

__pause_scene_generator__ = None


def get_pause_scene():
    return __pause_scene_generator__()


def set_pause_scene_generator(generator):
    global __pause_scene_generator__
    __pause_scene_generator__ = generator


def default_pause_scene():
    w, h = director.window.width, director.window.height
    texture = pyglet.image.Texture.create_for_size(
        GL_TEXTURE_2D, w, h, GL_RGBA)
    texture.blit_into(pyglet.image.get_buffer_manager().get_color_buffer(), 0, 0, 0)
    return PauseScene(texture.get_region(0, 0, w, h),
                      ColorLayer(25, 25, 25, 205), PauseLayer())
set_pause_scene_generator(default_pause_scene)


class PauseScene(Scene):
    """Pause Scene"""
    def __init__(self, background, *layers):
        super(PauseScene, self).__init__(*layers)
        self.bg = background
        self.width, self.height = director.get_window_size()

    def draw(self):
        self.bg.blit(0, 0, width=self.width, height=self.height)
        super(PauseScene, self).draw()


class PauseLayer(Layer):
    """Layer that shows the text 'PAUSED'
    """
    is_event_handler = True     #: enable pyglet's events

    def __init__(self):
        super(PauseLayer, self).__init__()

        x, y = director.get_window_size()

        ft = pyglet.font.load('Arial', 36)
        self.text = pyglet.font.Text(ft,
                                     'PAUSED',
                                     halign=pyglet.font.Text.CENTER)
        self.text.x = x // 2
        self.text.y = y // 2

    def draw(self):
        self.text.draw()

    def on_key_press(self, k, m):
        if k == pyglet.window.key.P and m & pyglet.window.key.MOD_ACCEL:
            director.pop()
            return True
