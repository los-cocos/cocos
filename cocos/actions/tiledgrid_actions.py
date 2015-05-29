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
"""Implementation of TiledGrid3DAction actions
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import random
from cocos.euclid import *
from .basegrid_actions import *
from cocos.director import director

rr = random.randrange

__all__ = ['FadeOutTRTiles',            # actions that don't modify the z coordinate
           'FadeOutBLTiles',
           'FadeOutUpTiles',
           'FadeOutDownTiles',
           'ShuffleTiles',
           'TurnOffTiles',
           'SplitRows',
           'SplitCols',
           'ShakyTiles3D',              # actions that modify the z coordinate
           'ShatteredTiles3D',
           'WavesTiles3D',
           'JumpTiles3D', ]


# Don't export this class
class Tile(object):
    def __init__(self, position=(0, 0), start_position=(0, 0), delta=(0, 0)):
        super(Tile, self).__init__()
        self.position = position
        self.start_position = start_position
        self.delta = delta

    def __repr__(self):
        return "(start_pos: %s  pos: %s   delta:%s)" % (self.start_position, self.position, self.delta)


class ShakyTiles3D(TiledGrid3DAction):
    """Simulates a shaky floor composed of tiles

    Example::

       scene.do(ShakyTiles3D(randrange=6, grid=(4,4), duration=10))
    """

    def init(self, randrange=6, *args, **kw):
        """
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange(-randrange, randrange) to do the effect
        """
        super(ShakyTiles3D, self).init(*args, **kw)
        self.randrange = randrange

    def update(self, t):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                    coords = self.get_original_tile(i, j)
                    for k in range(0, len(coords), 3):
                        x = rr(-self.randrange, self.randrange + 1)
                        y = rr(-self.randrange, self.randrange + 1)
                        z = rr(-self.randrange, self.randrange + 1)
                        coords[k] += x
                        coords[k+1] += y
                        coords[k+2] += z
                    self.set_tile(i, j, coords)


class ShatteredTiles3D(TiledGrid3DAction):
    """ShatterTiles shatters the tiles according to a random value.
    It is similar to shakes (see `ShakyTiles3D`) the tiles just one frame, and then continue with
    that state for duration time.

    Example::

        scene.do(ShatteredTiles3D(randrange=12))
    """

    def init(self, randrange=6, *args, **kw):
        """
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange(-randrange, randrange) to do the effect
        """
        super(ShatteredTiles3D, self).init(*args, **kw)
        self.randrange = randrange
        self._once = False

    def update(self, t):
        if not self._once:
            for i in range(0, self.grid.x):
                for j in range(0, self.grid.y):
                    coords = self.get_original_tile(i, j)
                    for k in range(0, len(coords), 3):
                        x = rr(-self.randrange, self.randrange + 1)
                        y = rr(-self.randrange, self.randrange + 1)
                        z = rr(-self.randrange, self.randrange + 1)
                        coords[k] += x
                        coords[k+1] += y
                        coords[k+2] += z
                    self.set_tile(i, j, coords)
            self._once = True


class ShuffleTiles(TiledGrid3DAction):
    """ShuffleTiles moves the tiles randomly across the screen.
    To put them back use: Reverse(ShuffleTiles()) with the same seed parameter.

    Example::

       scene.do(ShuffleTiles(grid=(4,4), seed=1, duration=10))
    """

    def init(self, seed=-1, *args, **kw):
        """
        :Parameters:
            `seed` : float
                Seed for the random in the shuffle.
        """
        super(ShuffleTiles, self).init(*args, **kw)
        self.seed = seed

    def start(self):
        super(ShuffleTiles, self).start()

        self.tiles = {}
        self._once = False

        if self.seed != -1:
            random.seed(self.seed)

        # random positions
        self.nr_of_tiles = self.grid.x * self.grid.y
        self.tiles_order = list(range(self.nr_of_tiles))
        random.shuffle(self.tiles_order)

        for i in range(self.grid.x):
            for j in range(self.grid.y):
                self.tiles[(i, j)] = Tile(position=Point2(i, j),
                                          start_position=Point2(i, j),
                                          delta=self._get_delta(i, j))

    def place_tile(self, i, j):
        t = self.tiles[(i, j)]
        coords = self.get_original_tile(i, j)

        for k in range(0, len(coords), 3):
            coords[k] += int(t.position.x * self.target.grid.x_step)
            coords[k+1] += int(t.position.y * self.target.grid.y_step)
        self.set_tile(i, j, coords)

    def update(self, t):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                self.tiles[(i, j)].position = self.tiles[(i, j)].delta * t
                self.place_tile(i, j)

    # private method
    def _get_delta(self, x, y):
        idx = x * self.grid.y + y
        i, j = divmod(self.tiles_order[idx], self.grid.y)
        return Point2(i, j)-Point2(x, y)


class FadeOutTRTiles(TiledGrid3DAction):
    """Fades out each tile following a diagonal Top-Right path until all the tiles are faded out.

    Example::

       scene.do(FadeOutTRTiles(grid=(16,12), duration=10))
    """

    def update(self, t):

        # direction right - up
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                distance = self.test_func(i, j, t)
                if distance == 0:
                    self.turn_off_tile(i, j)
                elif distance < 1:
                    self.transform_tile(i, j, distance)
                else:
                    self.turn_on_tile(i, j)

    def turn_on_tile(self, x, y):
        self.set_tile(x, y, self.get_original_tile(x, y))

    def transform_tile(self, x, y, t):
        coords = self.get_original_tile(x, y)
        for c in range(len(coords)):

            # x
            if c == 0 * 3 or c == 3 * 3:
                coords[c] = coords[c] + (self.target.grid.x_step / 2.0)*(1 - t)
            elif c == 1 * 3 or c == 2 * 3:
                coords[c] = coords[c] - (self.target.grid.x_step / 2.0)*(1 - t)

            # y
            if c == 0*3 + 1 or c == 1*3 + 1:
                coords[c] = coords[c] + (self.target.grid.y_step / 2.0)*(1 - t)
            elif c == 2*3 + 1 or c == 3*3 + 1:
                coords[c] = coords[c] - (self.target.grid.y_step / 2.0)*(1 - t)

        self.set_tile(x, y, coords)

    def turn_off_tile(self, x, y):
        self.set_tile(x, y, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_func(self, i, j, t):
        x, y = self.grid * t
        if x + y == 0:
            return 1
        return pow((i + j) / (x + y), 6)


class FadeOutBLTiles(FadeOutTRTiles):
    """Fades out each tile following an Bottom-Left path until all the tiles are faded out.

    Example::

       scene.do(FadeOutBLTiles(grid=(16,12), duration=5))
    """

    def test_func(self, i, j, t):
        x, y = self.grid * (1 - t)
        if i + j == 0:
            return 1
        return pow((x + y) / (i + j), 6)


class FadeOutUpTiles(FadeOutTRTiles):
    """Fades out each tile following an upwards path until all the tiles are faded out.

    Example::

       scene.do(FadeOutUpTiles(grid=(16,12), duration=5))
    """

    def test_func(self, i, j, t):
        x, y = self.grid * t
        if y == 0:
            return 1
        return pow(j / y, 6)

    def transform_tile(self, x, y, t):
        coords = self.get_original_tile(x, y)
        for c in range(len(coords)):

            # y
            if c == 0*3 + 1 or c == 1*3 + 1:
                coords[c] = coords[c] + (self.target.grid.y_step / 2.0)*(1 - t)
            elif c == 2*3 + 1 or c == 3*3 + 1:
                coords[c] = coords[c] - (self.target.grid.y_step / 2.0)*(1 - t)

        self.set_tile(x, y, coords)


class FadeOutDownTiles(FadeOutUpTiles):
    """Fades out each tile following an downwards path until all the tiles are faded out.

    Example::

       scene.do(FadeOutDownTiles(grid=(16,12), duration=5))
    """

    def test_func(self, i, j, t):
        x, y = self.grid * (1 - t)
        if j == 0:
            return 1
        return pow(y / j, 6)


class TurnOffTiles(TiledGrid3DAction):
    """TurnOffTiles turns off each in random order

    Example::

       scene.do(TurnOffTiles(grid=(16,12), seed=1, duration=10))
    """

    def init(self, seed=-1, *args, **kw):
        super(TurnOffTiles, self).init(*args, **kw)
        self.seed = seed

    def start(self):
        super(TurnOffTiles, self).start()

        if self.seed != -1:
            random.seed(self.seed)

        self.nr_of_tiles = self.grid.x * self.grid.y
        self.tiles_order = list(range(self.nr_of_tiles))
        random.shuffle(self.tiles_order)

    def update(self, t):
        l = int(t * self.nr_of_tiles)
        for i in range(self.nr_of_tiles):
            t = self.tiles_order[i]
            if i < l:
                self.turn_off_tile(t)
            else:
                self.turn_on_tile(t)

    def get_tile_pos(self, idx):
        return divmod(idx, self.grid.y)

    def turn_on_tile(self, t):
        x, y = self.get_tile_pos(t)
        self.set_tile(x, y, self.get_original_tile(x, y))

    def turn_off_tile(self, t):
        x, y = self.get_tile_pos(t)
        self.set_tile(x, y, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


class WavesTiles3D(TiledGrid3DAction):
    """Simulates waves using the math.sin() function in the z-axis of each tile

    Example::

       scene.do(WavesTiles3D(waves=5, amplitude=120, grid=(16,16), duration=10))
    """

    def init(self, waves=4, amplitude=120, *args, **kw):
        """
        :Parameters:
            `waves` : int
                Number of waves (2 * pi) that the action will perform. Default is 4
            `amplitude` : int
                Wave amplitude (height). Default is 20
        """
        super(WavesTiles3D, self).init(*args, **kw)

        #: Total number of waves to perform
        self.waves = waves

        #: amplitude rate. Default: 1.0
        #: This value is modified by other actions like `AccelAmplitude`.
        self.amplitude_rate = 1.0
        self.amplitude = amplitude

    def update(self, t):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                coords = self.get_original_tile(i, j)

                x = coords[0]
                y = coords[1]

                z = (math.sin(t*math.pi*self.waves*2 + (y + x)*.01)*self.amplitude*self.amplitude_rate)

                for k in range(0, len(coords), 3):
                    coords[k+2] += z

                self.set_tile(i, j, coords)


class JumpTiles3D(TiledGrid3DAction):
    """Odd tiles will perform a jump in the z-axis using the sine function,
    while the even tiles will perform a jump using sine+pi function

    Example::

       scene.do(JumpTiles3D(jumps=5, amplitude=40, grid=(16,16), duration=10))
    """

    def init(self, jumps=4, amplitude=20, *args, **kw):
        """
        :Parameters:
            `jumps` : int
                Number of jumps(2 * pi) that the action will perform. Default is 4
            `amplitude` : int
                Wave amplitude (height). Default is 20
        """
        super(JumpTiles3D, self).init(*args, **kw)

        #: Total number of jumps to perform
        self.jumps = jumps

        #: amplitude rate. Default: 1.0
        #: This value is modified by other actions like `AccelAmplitude`.
        self.amplitude_rate = 1.0
        self.amplitude = amplitude

    def update(self, t):

        phase = t * math.pi * self.jumps * 2
        amplitude = self.amplitude * self.amplitude_rate
        sinz = math.sin(phase) * amplitude
        sinz2 = math.sin(math.pi + phase) * amplitude

        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                coords = self.get_original_tile(i, j)

                for k in range(0, len(coords), 3):
                    if (i + j) % 2 == 0:
                        coords[k+2] += sinz
                    else:
                        coords[k+2] += sinz2

                self.set_tile(i, j, coords)


class SplitRows(TiledGrid3DAction):
    """Split the screen in a number of rows, and move
    these rows away from the screen.

    The odds rows are moved to the left, while the even rows are moved to
    the right.

    Example::

       scene.do(SplitRows(rows=3, duration=2))
    """

    def init(self, rows=9, grid=(-1, -1), *args, **kw):
        """
        :Parameters:
            `rows` : int
                Number of rows that will have the effect. Default: 9
        """
        if grid != (-1, -1):
            raise Exception("This action doesn't receives the grid argument")

        grid = (1, rows)
        self.rows = rows
        super(SplitRows, self).init(grid, *args, **kw)

    def update(self, t):

        x, y = director.get_window_size()

        for j in range(0, self.grid.y):
            coords = self.get_original_tile(0, j)

            for c in range(0, len(coords), 3):
                direction = 1
                if j % 2 == 0:
                    direction = -1
                coords[c] += direction * x * t

            self.set_tile(0, j, coords)


class SplitCols(TiledGrid3DAction):
    """Split the screen in a number of columns, and move
    these columns away from the screen.

    The odds columns are moved to the upwards, while the even
    columns are moved to the downwards.

    Example::

       scene.do(SplitCols(cols=3, duration=2))
    """

    def init(self, cols=9, grid=(-1, -1), *args, **kw):
        """
        :Parameters:
            `cols` : int
                Number of columns that will have the effect. Default: 9
        """
        if grid != (-1, -1):
            raise Exception("This action doesn't receives the grid argument")

        grid = (cols, 1)
        self.cols = cols
        super(SplitCols, self).init(grid, *args, **kw)

    def update(self, t):

        x, y = director.get_window_size()

        for i in range(0, self.grid.x):
            coords = self.get_original_tile(i, 0)

            for c in range(0, len(coords), 3):
                direction = 1
                if i % 2 == 0:
                    direction = -1
                coords[c+1] += direction * y * t

            self.set_tile(i, 0, coords)
