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

from __future__ import division, print_function, unicode_literals

import math
from math import pi, atan

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos import euclid

import pyglet
from pyglet.gl import *
from pyglet.window import key

def circle(radius, color):
    circumference = 2*math.pi*radius
    step_size = 5
    steps = max(4, int(circumference / step_size))

    adelta = 2 * math.pi / steps
    points = [0,0,radius,0]
    for step in range(1,steps+1):
        x = radius*math.cos(step*adelta)
        y = radius*math.sin(step*adelta)
        points += [x,y]

    num_points = steps+2
    vertex_list = pyglet.graphics.vertex_list(num_points,
        ('v2f', points),
        ('c4B', list(color)*num_points)
        )
    return vertex_list

def rectangle(x1, y1, x2, y2, color):
    return pyglet.graphics.vertex_list(4,
            ('v2f', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', color*4)
        )

def up_triange(x,y, h, w, color):
    return pyglet.graphics.vertex_list(3,
            ('v2f', [x, y, x-w/2, y+h, x+w/2, y+h]),
            ('c4B', color*3)
        )

def down_triange(x,y, h, w, color):
    return pyglet.graphics.vertex_list(3,
            ('v2f', [x, y, x-w/2, y-h, x+w/2, y-h]),
            ('c4B', color*3)
        )

class Widget(cocos.cocosnode.CocosNode):
    def __init__(self):
        super(Widget, self).__init__()
        self.selected = False
        self.hovered = False

    def set_hover(self, value):
        self.hovered = value

    def set_selected(self, position):
        pass

    def on_dragged(self, dx, dy):
        self.x += dx
        self.y += dy

    def is_mouse_over(self, position):
        return False

class BallWidget(Widget):
    def __init__(self, radius, color):
        super(BallWidget, self).__init__()
        self.radius = radius
        self.color = color
        self.body = circle(radius, color)
        self.hover_envelope = circle(radius*1.2, (255,255,0,100))
        self.selected_envelope = circle(radius*1.5, (255,255,255,200))

    def draw(self):
        glPushMatrix()
        self.transform()
        if self.selected:
            self.selected_envelope.draw(GL_TRIANGLE_FAN)
        elif self.hovered:
            self.hover_envelope.draw(GL_TRIANGLE_FAN)
        self.body.draw(GL_TRIANGLE_FAN)
        glPopMatrix()

    def is_mouse_over(self, position):
        px, py = position
        x, y = self.position
        if (px-x)**2+(py-y)**2 < self.radius**2:
            return True
        return False

class UILayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(UILayer, self).__init__()
        self.hovering = None
        self.hovering_all = []
        self.mouse_down = False
        self.dragging = False

    def on_mouse_motion(self, x, y, dx, dy):
        selected = None
        self.hovering_all = []

        for c in self.get_children():
            if isinstance(c, Widget):
                if c.is_mouse_over((x,y)):
                    selected = c
                    self.hovering_all.append( c )
                c.set_hover(False)

        if selected:
            if self.hovering not in self.hovering_all:
                selected.set_hover(True)
                self.hovering = selected
            else:
                self.hovering.set_hover(True)
        else:
            self.hovering = None

    def on_mouse_press(self, *args):
        self.mouse_down = True

    def on_mouse_release(self, *args):
        self.mouse_down = False
        self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.dragging = True
        if self.hovering:
            self.hovering.on_dragged(dx,dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.hovering_all and not self.mouse_down:
            top = self.hovering_all.pop(0)
            self.hovering_all.append(top)
            self.hovering.set_hover(False)
            self.hovering = self.hovering_all[0]
            self.hovering.set_hover(True)

class TimelineModel(object):
    def get_markers(self):
        pass
    def get_duration(self):
        pass
    def get_position(self):
        pass

class TimeLine(Widget):
    def __init__(self, model):
        super(TimeLine, self).__init__()
        self.model = model

        x, y = director.get_window_size()
        self.x_margin = xm = 20
        self.y_margin = ym = 20
        self.height = h = 10
        self.width = x-2*xm
        self.color = 125,0,0,125
        self.bar = rectangle( xm, y-ym, x-xm, y-ym-h, self.color)

    def draw(self):
        # draw bar
        self.bar.draw(GL_QUADS)
        # draw ticks
        d = self.model.get_duration()
        if d != 0:
            step = 2** ( int(math.log(d, 2)-2) )
            p = 0
            while p <= d:
                self.show_tick( p )
                p += step

        markers = self.model.get_markers()
        markers_pxs = [ self.map_to_pixel(m) for m in markers ]
        x, y = director.get_window_size()
        ym = self.y_margin
        h = self.height
        for pixel in markers_pxs:
            t = up_triange(pixel, y - ym - h / 2, 10, 10, (100,100,255,255))
            t.draw(GL_TRIANGLES)

        pixel = self.map_to_pixel( self.model.get_position() )
        t = down_triange(pixel, y - ym - h / 2, 10, 10, (255,255,0,255))
        t.draw(GL_TRIANGLES)

    def map_to_pixel(self, when):
        d = self.model.get_duration()
        xm = self.x_margin

        if d == 0:
            return xm
        w = self.width
        p = (when / d) * w

        return xm + p

    def show_tick(self, when):
        l = self.height + 5
        x,y = director.get_window_size()
        ym = self.y_margin
        p = self.map_to_pixel( when )

        # draw line
        glColor4ub(128, 128, 128,100)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f( p, y-ym )
        glVertex2f( p, y-ym-l )
        glEnd()

        # draw label
        label = pyglet.text.Label(str(when),
                          font_name='Monotype',
                          #font_name='Times New Roman',
                          font_size=8,
                          x=p, y=y-ym-l-7,
                          anchor_x='center', anchor_y='center')
        label.draw()
