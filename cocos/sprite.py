#
# Cocos
# http://code.google.com/p/los-cocos/
#
'''Action Sprite

Animating a sprite
==================

To execute any action you need to create an action::

    move = MoveBy( (50,0), 5 )

In this case, ``move`` is an action that will move the sprite
50 pixels to the right (``x`` coordinate), 0 pixel in the ``y`` coordinate,
and 0 pixels in the ``z`` coordinate in 5 seconds.

And now tell the sprite to execute it::

    sprite.do( move )
'''

__docformat__ = 'restructuredtext'

import rect
from director import director
import cocosnode
from batch import *

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionSprite',                     # Sprite class
            ]


        
class ActionSprite( BatchableNode, pyglet.sprite.Sprite):
    '''ActionSprites are sprites that can execute actions.

    Example::

        sprite = ActionSprite('grossini.png')
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
        
        if anchor is None:
            if isinstance(image, pyglet.image.Animation):
                xa = image.frames[0].image.width / 2
                ya = image.frames[0].image.height / 2
                for img in image.frames:
                    img.image.anchor_x = xa
                    img.image.anchor_y = ya
            else:
                image.anchor_x = image.width / 2
                image.anchor_y = image.height / 2
        else:
            image.anchor = anchor
            
        pyglet.sprite.Sprite.__init__(self, image)
        cocosnode.CocosNode.__init__(self)
        self.group = None
        self.children_group = None

        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.opacity = opacity
        self.color = color
        

    def on_draw(self):
        self._group.set_state()
        if self._vertex_list is not None:
            self._vertex_list.draw(GL_QUADS)
        self._group.unset_state()
        
ActionSprite.supported_classes = ActionSprite
