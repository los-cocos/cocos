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

"""
"""

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *
import pyglet.graphics

from layer import *
from director import *
from cocosnode import *
from actions import *
from sprite import Sprite

__all__ = [ 'Widget','WidgetButton'
            ]


#
# Interfaces
#

class Widget(object):

    SELECTED, UNSELECTED, DISABLED = range(3)

    '''returns the width'''
    width = 0

    '''returns the height'''
    height = 0

    def get_rect( self ):
        '''returns bounding box'''
        pass

    def on_select( self ):
        '''was selected'''
        pass

    def on_unselect(self):
        '''widget was unselected'''
        pass

    def on_activate(self):
        '''widget was activated'''
        pass

    def on_disable(self):
        '''widget was disabled'''
        pass


class WidgetButton( CocosNode ):
    def __init__(self, selected_image, unselected_image=None, disabled_image=None, **kw):
        super(WidgetButton,self).__init__(**kw)

        self._images = []

        self._load_image( 0, selected_image )
        self._load_image( 1, unselected_image )
        self._load_image( 2, disabled_image )

        self._state = Widget.SELECTED

        self._rect = [0,0, self._images[0].width, self._images[0].height ]

    def _load_image( self, idx, image ):
        if image:
            if isinstance(image, str):
                image = pyglet.resource.image(image)
            else:
                image = selected_image
            self._images.append( image )
        else:
            self._images.append( self._images[0] )

    def draw (self):
        glPushMatrix()
        self.transform()
        self._images[ self._state].blit(0,0,0)
        glPopMatrix()


    # implements protocol Widget
    def _get_width( self ):
        return self._images[ self._state ].width
    width = property(_get_width, None, doc='')

    def _get_height( self ):
        return self._images[ self._state ].height
    height = property(_get_height, None, doc='')

    def get_rect(self):
        return [self.x, self.y, self.width, self.height]

    def on_select( self ):
        print 'on select'

    def on_unselect( self ):
        print 'on unselect'

    def on_activate( self ):
        print 'on activate'
