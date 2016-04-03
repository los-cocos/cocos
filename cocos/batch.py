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
"""Batch

Batches
=======

Batches allow you to optimize the number of gl calls using pyglets batch

"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import gl

from cocos.cocosnode import CocosNode

__all__ = ['BatchNode', 'BatchableNode']


def ensure_batcheable(node):
    if not isinstance(node, BatchableNode):
        raise Exception("Children node of a batch must be of class BatchableNode")
    for c in node.get_children():
        ensure_batcheable(c)


class BatchNode(CocosNode):
    def __init__(self):
        super(BatchNode, self).__init__()
        self.batch = pyglet.graphics.Batch()
        self.groups = {}

    def add(self, child, z=0, name=None):
        ensure_batcheable(child)
        child.set_batch(self.batch, self.groups, z)
        super(BatchNode, self).add(child, z, name)

    def visit(self):
        """ All children are placed in to self.batch, so nothing to visit """
        if not self.visible:
            return
        gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        gl.glPopMatrix()

    def remove(self, child):
        if isinstance(child, str):
            child_node = self.get(child)
        else:
            child_node = child
        child_node.set_batch(None)
        super(BatchNode, self).remove(child)

    def draw(self):
        pass  # All drawing done in visit!


class BatchableNode(CocosNode):
    def add(self, child, z=0, name=None):
        batchnode = self.get_ancestor(BatchNode)
        if not batchnode:
            # this node was addded, but theres no batchnode in the
            # hierarchy. so we proceed as normal
            super(BatchableNode, self).add(child, z, name)
            return

        ensure_batcheable(child)
        super(BatchableNode, self).add(child, z, name)
        child.set_batch(self.batch, batchnode.groups, z)

    def remove(self, child):
        if isinstance(child, str):
            child_node = self.get(child)
        else:
            child_node = child
        child_node.set_batch(None)
        super(BatchableNode, self).remove(child)

    def set_batch(self, batch, groups=None, z=0):
        self.batch = batch
        if batch is None:
            self.group = None
        else:
            group = groups.get(z)
            if group is None:
                group = pyglet.graphics.OrderedGroup(z)
                groups[z] = group
            self.group = group
        for childZ, child in self.children:
            child.set_batch(self.batch, groups, z + childZ)
