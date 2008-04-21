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

import rect
from director import director
import cocosnode

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionSprite',                     # Sprite class
            'SpriteGroup',
            ]

class SpriteGroup(pyglet.graphics.Group):
    def __init__(self, sprite, group):
        super(SpriteGroup, self).__init__(parent=group)
        self.sprite = sprite

    def set_state(self):
        glPushMatrix()
        self.sprite.transform()

    def unset_state(self):
        glPopMatrix()

def ensure_batcheable(node):
    if not isinstance(node, BatchableNode):
        raise Exception("Children node of a batch must be have the batch mixin")
    for c in  node.get_children():
        ensure_batcheable(c)

class BatchNode( cocosnode.CocosNode ):
    def __init__(self):
        super(BatchNode, self).__init__()
        self.batch = pyglet.graphics.Batch()
        
    def add(self, child, z=0, name=None):
        ensure_batcheable(child)
        group = pyglet.graphics.OrderedGroup( z )
        child.set_batch( self.batch, group )
         
        super(BatchNode, self).add(child, z, name)
    
    def visit(self):
        self.batch.draw()
        
    def on_draw(self):
        pass#self.batch.draw()
        
class BatchableNode( cocosnode.CocosNode ):
    def add(self, child, z=0, name=None):
        batchnode = self.get(BatchNode)
        if not batchnode: 
            # this node was addded, but theres no batchnode in the
            # hierarchy. so we proceed as normal
            super(BatchableNode, self).add(child, z, name)
            return
            
        # we are being batched, so we set groups and batch
        # pre/same/post will be set, because if we have a
        # batchnode parent, we already executed set_batch on self
        ensure_batcheable(child)
        if z < 0:
            group = self.pre_group
        elif z == 0:
            group = self.same_group
        else:
            group = self.post_group
            
        super(BatchableNode, self).add(child, z, name)
        child.set_batch( self.batch, group )
        
                 
    def remove(self, child):
        child.set_batch( None, None )
        super(BatchableNode, self).remove(child)
        
    def set_batch(self, batch, group):
        sprite_group = SpriteGroup(self, group)
        self.pre_group = SpriteGroup(self, OrderedGroup(-1, parent=group))
        self.group = OrderedGroup(0, parent=group)
        self.same_group = SpriteGroup(self, self.group)
        self.post_group = SpriteGroup(self, OrderedGroup(1, parent=group))
        self.batch = batch
        
        for z, child in self.children:
            if z < 0:
                group = self.pre_group
            elif z == 0:
                group = self.same_group
            else:
                group = self.post_group
            child.set_batch( self.batch, group )
        
        
class ActionSprite( BatchableNode, pyglet.sprite.Sprite):
    '''ActionSprites are sprites that can execute actions.

    Example::

        sprite = ActionSprite('grossini.png')
        
    :Parameters:
            `image_name` : string or image
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
    
    def __init__( self, image, position=(0,0), rotation=0, scale=1, opacity = 255, color=(255,255,255), anchor = None ):
        if isinstance(image, str):
            image = pyglet.resource.image(image)
        
        if anchor is None:
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
