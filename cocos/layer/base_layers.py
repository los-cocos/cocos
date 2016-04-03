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
"""Layer class and subclasses

A `Layer` has as size the whole drawable area (window or screen),
and knows how to draw itself. It can be semi transparent (having holes
and/or partial transparency in some/all places), allowing to see other layers
behind it. Layers are the ones defining appearance and behavior, so most
of your programming time will be spent coding Layer subclasses that do what
you need. The layer is where you define event handlers.
Events are propagated to layers (from front to back) until some layer catches
the event and accepts it.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from cocos.director import director
from cocos import cocosnode
from cocos import scene

__all__ = ['Layer', 'MultiplexLayer']


class Layer(cocosnode.CocosNode, scene.EventHandlerMixin):
    """a CocosNode that automatically handles listening to director.window events"""

    #: if True the layer will listen to director.window events
    #: Default: False
    is_event_handler = False  #: if true, the event handlers of this layer will be registered. defaults to false.

    def __init__(self):
        super(Layer, self).__init__()
        self.scheduled_layer = False
        x, y = director.get_window_size()
        self.transform_anchor_x = x // 2
        self.transform_anchor_y = y // 2

    def push_all_handlers(self):
        """ registers itself to receive director.window events and propagates
            the call to childs that are layers.
            class member is_event_handler must be True for this to work"""
        if self.is_event_handler:
            director.window.push_handlers(self)
        for child in self.get_children():
            if isinstance(child, Layer):
                child.push_all_handlers()

    def remove_all_handlers(self):
        """ de-registers itself to receive director.window events and propagates
            the call to childs that are layers.
            class member is_event_handler must be True for this to work"""
        if self.is_event_handler:
            director.window.remove_handlers(self)
        for child in self.get_children():
            if isinstance(child, Layer):
                child.remove_all_handlers()

    def on_enter(self):
        super(Layer, self).on_enter()

        scn = self.get_ancestor(scene.Scene)
        if not scn:
            return

        if scn._handlers_enabled:
            if self.is_event_handler:
                director.window.push_handlers(self)

    def on_exit(self):
        super(Layer, self).on_exit()

        scn = self.get_ancestor(scene.Scene)
        if not scn:
            return

        if scn._handlers_enabled:
            if self.is_event_handler:
                director.window.remove_handlers(self)


# MultiplexLayer
class MultiplexLayer(Layer):
    """A Composite layer that only enables one layer at the time.

     This is useful, for example, when you have 3 or 4 menus, but you want to
     show one at the time"""

    def __init__(self, *layers):
        super(MultiplexLayer, self).__init__()

        self.layers = layers
        self.enabled_layer = 0

        self.add(self.layers[self.enabled_layer])

    def switch_to(self, layer_number):
        """Switches to another Layer that belongs to the Multiplexor.

        :Parameters:
            `layer_number` : Integer
                MUST be a number between 0 and the quantities of layers - 1.
                The running layer will receive an "on_exit()" call, and the
                new layer will receive an "on_enter()" call.
        """
        if layer_number < 0 or layer_number >= len(self.layers):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        self.remove(self.layers[self.enabled_layer])

        self.enabled_layer = layer_number
        self.add(self.layers[self.enabled_layer])
