# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2020  Richard Jones, Claudio Canepa
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
"""Layer class and subclasses.

Layers are typically thought as event handlers and / or as containers that help
to organize the scene visuals or logic.

The transform_anchor is set by default to the window's center, which most of the
time provides the desired behavior on rotation and scale.

By default a layer will not listen to events, his `is_event_handler` must be set
to True before the layer enters the stage to enable the automatic registering as
event handler.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from cocos.director import director
from cocos import cocosnode
from cocos import scene

__all__ = ['Layer', 'MultiplexLayer']


class Layer(cocosnode.CocosNode):
    """A CocosNode that can automatically register to listen to director.window events"""

    is_event_handler = False  #: If ``True``, the event handlers of this layer will be registered. Defaults to ``False``.

    def __init__(self):
        super(Layer, self).__init__()
        self.scheduled_layer = False
        x, y = director.get_window_size()
        self.transform_anchor_x = x // 2
        self.transform_anchor_y = y // 2

    def on_enter(self):
        "Called every time just before the node enters the stage."
        super(Layer, self).on_enter()
        if self.is_event_handler:
            director.window.push_handlers(self)

    def on_exit(self):
        "Called every time just before the node exits the stage."
        super(Layer, self).on_exit()
        if self.is_event_handler:
            director.window.remove_handlers(self)


# MultiplexLayer
class MultiplexLayer(Layer):
    """A Composite layer that only enables one layer at a time.

    This is useful, for example, when you have 3 or 4 menus, but you want to
    show one at the time.

    After instantiation the enabled layer is layers[0]

    Arguments:
        *layers : iterable with the layers to be managed.
    """

    def __init__(self, *layers):
        super(MultiplexLayer, self).__init__()

        self.layers = layers
        self.enabled_layer = 0

        self.add(self.layers[self.enabled_layer])

    def switch_to(self, layer_number):
        """Switches to another of the layers managed by this instance.

        Arguments:
            layer_number (int) :
                **Must** be a number between 0 and the (number of layers - 1).
                The running layer will receive an ``on_exit()`` call, and the
                new layer will receive an ``on_enter()`` call.

        Raises:
            Exception: layer_number was out of bound.
        """
        if layer_number < 0 or layer_number >= len(self.layers):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        self.remove(self.layers[self.enabled_layer])

        self.enabled_layer = layer_number
        self.add(self.layers[self.enabled_layer])
