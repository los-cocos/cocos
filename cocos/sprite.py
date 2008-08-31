# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
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
'''Action Sprite

Animating a sprite
==================

To execute any action you need to create an action::

    move = MoveBy( (50,0), 5 )

In this case, ``move`` is an action that will move the sprite
50 pixels to the right (``x`` coordinate) and  0 pixel in the ``y`` coordinate
in 5 seconds.

And now tell the sprite to execute it::

    sprite.do( move )
'''

__docformat__ = 'restructuredtext'

import cocosnode
from batch import *

import pyglet
from pyglet import image
from pyglet.gl import *

__all__ = [ 'Sprite',                     # Sprite class
            ]



class Sprite( BatchableNode, pyglet.sprite.Sprite):
    '''Sprites are sprites that can execute actions.

    Example::

        sprite = Sprite('grossini.png')
    '''

    def __init__( self, image, position=(0,0), rotation=0, scale=1, opacity = 255, color=(255,255,255), anchor = None ):
        '''Initialize the sprite

        :Parameters:
                `image` : string or image
                    name of the image resource or a pyglet image.
                `position` : tuple
                    position of the anchor. Defaults to (0,0)
                `rotation` : float
                    the rotation (degrees). Defaults to 0.
                `scale` : float
                    the zoom factor. Defaults to 1.
                `opacity` : int
                    the opacity (0=transparent, 255=opaque). Defaults to 255.
                `color` : tuple
                    the color to colorize the child (RGB 3-tuple). Defaults to (255,255,255).
                `anchor` : (float, float)
                    (x,y)-point from where the image will be positions, rotated and scaled in pixels. For example (image.width/2, image.height/2) is the center (default).
        '''

        if isinstance(image, str):
            image = pyglet.resource.image(image)


        pyglet.sprite.Sprite.__init__(self, image)
        cocosnode.CocosNode.__init__(self)

        if anchor is None:
            if isinstance(self.image, pyglet.image.Animation):
                anchor = (image.frames[0].image.width / 2,
                    image.frames[0].image.height / 2)
            else:
                anchor = image.width / 2, image.height / 2


        self.image_anchor = anchor
        self.anchor = (0, 0)

        #: group.
        #: XXX what is this?
        self.group = None

        #: children group.
        #: XXX what is this ?
        self.children_group = None

        #: position of the sprite in (x,y) coordinates
        self.position = position

        #: rotation degrees of the sprite. Default: 0 degrees
        self.rotation = rotation

        #: scale of the sprite where 1.0 the default value
        self.scale = scale

        #: opacity of the sprite where 0 is transparent and 255 is solid
        self.opacity = opacity

        #: color of the sprite in R,G,B format where 0,0,0 is black and 255,255,255 is white
        self.color = color


    def _set_anchor_x(self, value):
        if isinstance(self.image, pyglet.image.Animation):
            for img in self.image.frames:
                img.image.anchor_x = value
            self._texture.anchor_x = value
        else:
            self.image.anchor_x = value
        self._update_position()

    def _get_anchor_x(self):
        if isinstance(self.image, pyglet.image.Animation):
            return self.image.frames[0].image.anchor_x
        else:
            return self.image.anchor_x
    image_anchor_x = property(_get_anchor_x, _set_anchor_x)

    def _set_anchor_y(self, value):
        if isinstance(self.image, pyglet.image.Animation):
            for img in self.image.frames:
                img.image.anchor_y = value
            self._texture.anchor_y = value
        else:
            self.image.anchor_y = value
        self._update_position()

    def _get_anchor_y(self):
        if isinstance(self.image, pyglet.image.Animation):
            return self.image.frames[0].image.anchor_y
        else:
            return self.image.anchor_y
    image_anchor_y = property(_get_anchor_y, _set_anchor_y)

    def _set_anchor(self, value):
        self._set_anchor_x(value[0])
        self._set_anchor_y(value[1])

    def _get_anchor(self):
        return (self._get_anchor_x(), self._get_anchor_y())

    image_anchor = property(_get_anchor, _set_anchor)

    def draw(self):
        self._group.set_state()
        if self._vertex_list is not None:
            self._vertex_list.draw(GL_QUADS)
        self._group.unset_state()

Sprite.supported_classes = Sprite
