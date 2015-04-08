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
"""Implementation of QuadMoveBy actions

These actions modifies the x and y coordinates of fixed-size grid of (1,1).
The z-coordinate is not modified.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import math

from cocos.director import director
from cocos.euclid import *
from .basegrid_actions import *

__all__ = ['QuadMoveBy',
           'MoveCornerUp',
           'MoveCornerDown',
           'CornerSwap',
           'Flip',
           'FlipX',
           'FlipY',
           'SkewHorizontal',
           'SkewVertical', ]


class QuadMoveBy(Grid3DAction):
    """QuadMoveBy moves each vertex of the grid. The size of the grid is (1,1)

    Vertex positions::

        vertex3 --<-- vertex2
            |            |
            v            ^
            |            |
        vertex0 -->-- vertex1

        The vertices will move from the origin (src parameters) a relative distance (delta parameters) in duration time.

    Example::

       scene.do(QuadMoveBy(src0, src1, src2, src3,
               delta0, delta1, delta2, delta3,
               duration))


       """

    def init(self, src0=(0, 0), src1=(-1, -1), src2=(-1, -1), src3=(-1, -1),
             delta0=(0, 0), delta1=(0, 0), delta2=(0, 0), delta3=(0, 0),
             grid=(1, 1), *args, **kw):
        """Initializes the QuadMoveBy

        :Parameters:
            `src0` : (int, int)
                Initial value for the bottom-left coordinate. Default is (0,0)
            `src1` : (int, int)
                Initial value for the bottom-right coordinate. Default is (win_size_x,0)
            `src2` : (int, int)
                Initial value for the upper-right coordinate. Default is (win_size_x, win_size_y)
            `src3` : (int, int)
                Initial value for the upper-left coordinate. Default is (0, win_size_y)
            `delta0` : (int, int)
                The bottom-left relative coordinate. Default is (0,0)
            `delta1` : (int, int)
                The bottom-right relative coordinate. Default is (0,0)
            `delta2` : (int, int)
                The upper-right relative coordinate. Default is (0,0)
            `delta3` : (int, int)
                The upper-left relative coordinate. Default is (0,0)
        """

        if grid != (1, 1):
            raise GridException("Invalid grid size.")

        super(QuadMoveBy, self).init(grid, *args, **kw)

        x, y = director.get_window_size()

        if src1 == (-1, -1):
            src1 = (x, 0)
        if src2 == (-1, -1):
            src2 = (x, y)
        if src3 == (-1, -1):
            src3 = (0, y)

        self.src0 = Point3(src0[0], src0[1], 0)
        self.src1 = Point3(src1[0], src1[1], 0)
        self.src2 = Point3(src2[0], src2[1], 0)
        self.src3 = Point3(src3[0], src3[1], 0)
        self.delta0 = Point3(delta0[0], delta0[1], 0)
        self.delta1 = Point3(delta1[0], delta1[1], 0)
        self.delta2 = Point3(delta2[0], delta2[1], 0)
        self.delta3 = Point3(delta3[0], delta3[1], 0)

    def update(self, t):
        new_pos0 = self.src0 + self.delta0 * t
        new_pos1 = self.src1 + self.delta1 * t
        new_pos2 = self.src2 + self.delta2 * t
        new_pos3 = self.src3 + self.delta3 * t

        self.set_vertex(0, 0, new_pos0)
        self.set_vertex(1, 0, new_pos1)
        self.set_vertex(1, 1, new_pos2)
        self.set_vertex(0, 1, new_pos3)


class MoveCornerUp(QuadMoveBy):
    """MoveCornerUp moves the bottom-right corner to the upper-left corner in duration time"""
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(MoveCornerUp, self).__init__(delta1=(-x, y), *args, **kw)


class MoveCornerDown(QuadMoveBy):
    """MoveCornerDown moves the upper-left corner to the bottom-right corner in duration time"""
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(MoveCornerDown, self).__init__(delta3=(x, -y), *args, **kw)


class CornerSwap(QuadMoveBy):
    """CornerSwap moves the upper-left corner to the bottom-right corner in vice-versa in duration time.
    The resulting effect is a reflection + rotation.
    """
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(CornerSwap, self).__init__(delta1=(-x, y), delta3=(x, -y), *args, **kw)


class Flip(QuadMoveBy):
    """Flip moves the upper-left corner to the bottom-left corner and vice-versa, and
    moves the upper-right corner to the bottom-left corner and vice-versa, flipping the
    window upside-down, and right-left.
    """
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(Flip, self).__init__(delta0=(x, y), delta1=(-x, y), delta2=(-x, -y), delta3=(x, -y), *args, **kw)


class FlipX(QuadMoveBy):
    """FlipX flips the screen horizontally, moving the left corners to the right, and vice-versa.
    """
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(FlipX, self).__init__(delta0=(x, 0), delta1=(-x, 0), delta2=(-x, 0), delta3=(x, 0), *args, **kw)


class FlipY(QuadMoveBy):
    """FlipY flips the screen vertically, moving the upper corners to the bottom, and vice-versa.
    """
    def __init__(self, *args, **kw):
        x, y = director.get_window_size()
        super(FlipY, self).__init__(delta0=(0, y), delta1=(0, y), delta2=(0, -y), delta3=(0, -y), *args, **kw)


class SkewHorizontal(QuadMoveBy):
    """SkewHorizontal skews the screen horizontally. default skew: x/3"""
    def __init__(self, delta=None, *args, **kw):
        x, y = director.get_window_size()
        if delta is None:
            delta = x // 3
        super(SkewHorizontal, self).__init__(delta1=(-delta, 0), delta3=(delta, 0), *args, **kw)


class SkewVertical(QuadMoveBy):
    """SkewVertical skews the screen vertically. default skew: y/3"""
    def __init__(self, delta=None, *args, **kw):
        x, y = director.get_window_size()
        if delta is None:
            delta = y // 3
        super(SkewVertical, self).__init__(delta0=(0, delta), delta2=(0, -delta), *args, **kw)
