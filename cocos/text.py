# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2011 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
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
    """
    Base class for all cocos text
    Provides the CocosNode interfase and a pyglet Batch to store parts
    """
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

class PygletRichLabel(pyglet.text.DocumentLabel):
    '''Rich text label.
    '''
    def __init__(self, text='',
                 font_name=None, font_size=None, bold=False, italic=False,
                 color=None,
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 halign='left',
                 multiline=False, dpi=None, batch=None, group=None):
        '''Create a rich text label.

        :Parameters:
            `text` : str
                Pyglet attributed (rich) text to display.
            `font_name` : str or list
                Font family name(s).  If more than one name is given, the
                first matching name is used.
            `font_size` : float
                Font size, in points.
            `bold` : bool
                Bold font style.
            `italic` : bool
                Italic font style.
            `color` : (int, int, int, int) or None
                Font colour, as RGBA components in range [0, 255].
                None to use font colors defined by text attributes.
            `x` : int
                X coordinate of the label.
            `y` : int
                Y coordinate of the label.
            `width` : int
                Width of the label in pixels, or None
            `height` : int
                Height of the label in pixels, or None
            `anchor_x` : str
                Anchor point of the X coordinate: one of ``"left"``,
                ``"center"`` or ``"right"``.
            `anchor_y` : str
                Anchor point of the Y coordinate: one of ``"bottom"``,
                ``"baseline"``, ``"center"`` or ``"top"``.
            `halign` : str
                Horizontal alignment of text on a line, only applies if
                a width is supplied. One of ``"left"``, ``"center"``
                or ``"right"``.
            `multiline` : bool
                If True, the label will be word-wrapped and accept newline
                characters.  You must also set the width of the label.
            `dpi` : float
                Resolution of the fonts in this layout.  Defaults to 96.
            `batch` : `Batch`
                Optional graphics batch to add the label to.
            `group` : `Group`
                Optional graphics group to use.

        '''

        text = '{color (255, 255, 255, 255)}' + text
        document = pyglet.text.decode_attributed(text)
        super(PygletRichLabel, self).__init__(document, x, y, width, height,
                                    anchor_x, anchor_y,
                                    multiline, dpi, batch, group)
        style = dict(halign=halign)

        if font_name:
            style['font_name'] = font_name
        if font_size:
            style['font_size'] = font_size
        if bold:
            style['bold'] = bold
        if italic:
            style['italic'] = italic
        if color:
            style['color'] = color

        self.document.set_style(0, len(self.document.text), style)

class RichLabel(TextElement):
    '''CocosNode RichLabel element. It is a wrapper of a custom Pyglet Rich Label
    using rich text attributes with the benefits of being of a CocosNode
    '''
    klass = PygletRichLabel
