"""Batch

Batches
=======

Batches allow you to optimize the number of gl calls using pygllets batch

"""

from director import director
import cocosnode
from batch import *

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet import image
from pyglet.gl import *

__all__ = ['BatchNode','BatchableNode','NodeGroup' ]


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
        sprite_group = NodeGroup(self, group)
        self.pre_group = NodeGroup(self, OrderedGroup(-1, parent=group))
        self.group = OrderedGroup(0, parent=group)
        self.same_group = NodeGroup(self, self.group)
        self.post_group = NodeGroup(self, OrderedGroup(1, parent=group))
        self.batch = batch
        
        for z, child in self.children:
            if z < 0:
                group = self.pre_group
            elif z == 0:
                group = self.same_group
            else:
                group = self.post_group
            child.set_batch( self.batch, group )
        
        
class NodeGroup(pyglet.graphics.Group):
    def __init__(self, sprite, group):
        super(NodeGroup, self).__init__(parent=group)
        self.sprite = sprite

    def set_state(self):
        glPushMatrix()
        self.sprite.transform()

    def unset_state(self):
        glPopMatrix()
