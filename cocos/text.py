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
'''Text cocos nodes
'''
__docformat__ = 'restructuredtext'

from director import director
import cocosnode
from batch import *

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet import image
from pyglet.gl import *

from batch import *

class TextElement(cocosnode.CocosNode):
    def __init__(self, text='', position=(0,0), **kwargs):
        super(TextElement, self).__init__()
        self.position = position
        self.args = []
        self.kwargs = kwargs
        kwargs['text']=text
        self.group = None
        self.batch = None
        
        self.batch = pyglet.graphics.Batch()
        self.create_element()
        
    def create_element(self):
        self.element = self.klass(group=self.group, batch=self.batch, **self.kwargs)
        
    def draw(self):
        glPushMatrix()
        self.transform()
        self.element.draw()
        glPopMatrix()
        
    def _get_opacity(self):
        return self.element.color[3]
    def _set_opacity(self, value):
        self.element.color = tuple(self.element.color[:3]) + (int(value),)
    opacity = property(_get_opacity, _set_opacity)
        
class Label(TextElement):
    '''CocosNode Label element. It is a wrapper of pyglet.text.Label with the benefits
    of being of a CocosNode
    '''
    klass = pyglet.text.Label
    
    
    
class HTMLLabel(TextElement):
    '''CocosNode HTMLLabel element. It is a wrapper of pyglet.text.HTMLLabel with the benefits
    of being of a CocosNode
    '''
    klass = pyglet.text.HTMLLabel
