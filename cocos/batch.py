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
"""Batch

Batches
=======

Batches allow you to optimize the number of gl calls using pygllets batch

"""

__docformat__ = 'restructuredtext'

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

    def draw(self):
        pass#self.batch.draw()

class BatchableNode( cocosnode.CocosNode ):
    def add(self, child, z=0, name=None):
        batchnode = self.get_ancestor(BatchNode)
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
        if isinstance(child, str):
            child = self.get(child)
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
