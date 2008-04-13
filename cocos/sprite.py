#
# ActionSprite
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

import interfaces
import rect
from director import director

import pyglet
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionSprite',                     # Sprite class
            'SpriteGroup',
            ]

class SpriteGroup(pyglet.graphics.Group):
    def __init__(self, sprite):
        super(SpriteGroup, self).__init__(parent=sprite.group)
        self.sprite = sprite

    def set_state(self):
        glPushMatrix()
        self.sprite.transform()

    def unset_state(self):
        glPopMatrix()

class ActionSprite( pyglet.sprite.Sprite, interfaces.IActionTarget, interfaces.IContainer ):
    '''ActionSprites are sprites that can execute actions.

    Example::

        sprite = ActionSprite('grossini.png')
    '''
    def __init__( self, *args, **kwargs ):

        pyglet.sprite.Sprite.__init__(self, *args, **kwargs)
        interfaces.IActionTarget.__init__(self)
        interfaces.IContainer.__init__(self)
        self.group = None
        self.children_group = None

    def add( self, child, position=(0,0), rotation=0.0, scale=1.0, color=(255,255,255), opacity=255, anchor_x=0.5, anchor_y=0.5, z=0,name='',):
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `name` : str
                Name of the child
            `position` : tuple
                 this is the lower left corner by default
            `rotation` : int
                the rotation (degrees)
            `scale` : int
                the zoom factor
            `opacity` : int
                the opacity (0=transparent, 255=opaque)
            `color` : tuple
                the color to colorize the child (RGB 3-tuple)
            `anchor_x` : float
                x-point from where the image will be rotated / scaled. Value goes from 0 to 1
            `anchor_y` : float
                y-point from where the image will be rotated / scaled. Value goes from 0 to 1
        """
        # child must be a subclass of supported_classes
        if not isinstance( child, self.supported_classes ):
            raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        properties = {'position' : position,
                      'rotation' : rotation,
                      'scale' : scale,
                      'color' : color,
                      'opacity' : opacity,
                      'anchor_x' : anchor_x,
                      'anchor_y' : anchor_y,
                      }
        for k,v in properties.items():
            setattr(child, k, v)

        if self.group is None:
            self.children_group = SpriteGroup( self )
        child.set_parent( self )

        self.children.append( child )

    def set_parent(self, parent):
        self.group = parent.children_group
        self.batch = parent.batch

        self.children_group = SpriteGroup( self )
        for c in self.children:
            c.set_parent( self )

    def get_children(self):
        return self.children[:]

    def get_rect(self):
        x, y = self.position
        return rect.Rect(x, y, self.width, self.height)

    def transform( self ):
        """Apply ModelView transformations"""

        x,y = director.get_window_size()

        color = tuple(self.color) + (self.opacity,)
        if color != (255,255,255,255):
            glColor4ub( * color )

        if self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )

        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)


    def on_exit(self):
        self.pause()

    def on_removed(self):
        self.batch = None
        for c in self.children:
            c.set_parent( self )

    def on_added(self):
        for c in self.children:
            c.set_parent( self )

    def on_enter(self):
        self.resume()

ActionSprite.supported_classes = ActionSprite
