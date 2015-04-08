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
"""Transitions between Scenes"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import pyglet
from pyglet.gl import *

from cocos.actions import *
import cocos.scene as scene
from cocos.director import director
from cocos.layer import ColorLayer
from cocos.sprite import Sprite

__all__ = ['TransitionScene',
           'RotoZoomTransition', 'JumpZoomTransition',
           'MoveInLTransition', 'MoveInRTransition',
           'MoveInBTransition', 'MoveInTTransition',
           'SlideInLTransition', 'SlideInRTransition',
           'SlideInBTransition', 'SlideInTTransition',
           'FlipX3DTransition', 'FlipY3DTransition', 'FlipAngular3DTransition',
           'ShuffleTransition',
           'TurnOffTilesTransition',
           'FadeTRTransition', 'FadeBLTransition',
           'FadeUpTransition', 'FadeDownTransition',
           'ShrinkGrowTransition',
           'CornerMoveTransition',
           'EnvelopeTransition',
           'SplitRowsTransition', 'SplitColsTransition',
           'FadeTransition',
           'ZoomTransition', ]


class TransitionScene(scene.Scene):
    """TransitionScene
    A Scene that takes two scenes and makes a transition between them.

    The input scenes are put into envelopes (Scenes) that are made childs to
    the transition scene.
    Proper transitions are allowed to modify any parameter for the envelopes,
    but must not modify directly the input scenes; that would corrupt the input
    scenes in the general case.
    """

    def __init__(self, dst, duration=1.25, src=None):
        """Initializes the transition

        :Parameters:
            `dst` : Scene
                Incoming scene, the one that remains visible when the transition ends.
            `duration` : float
                Duration of the transition in seconds. Default: 1.25
            `src` : Scene
                Outgoing scene. Default: current scene
        """
        super(TransitionScene, self).__init__()

        if src is None:
            src = director.scene

            # if the director is already running a transition scene then terminate
            # it so we may move on
            if isinstance(src, TransitionScene):
                tmp = src.in_scene.get('dst')
                src.finish()
                src = tmp

        if src is dst:
            raise Exception("Incoming scene must be different from outgoing scene")

        envelope = scene.Scene()
        envelope.add(dst, name='dst')
        self.in_scene = envelope   #: envelope with scene that will replace the old one

        envelope = scene.Scene()
        envelope.add(src, name='src')
        self.out_scene = envelope   #: envelope with scene that will be replaced
        self.duration = duration    #: duration in seconds of the transition
        if not self.duration:
            self.duration = 1.25

        self.start()

    def start(self):
        """Adds the incoming scene with z=1 and the outgoing scene with z=0"""
        self.add(self.in_scene, z=1)
        self.add(self.out_scene, z=0)

    def finish(self):
        """Called when the time is over.
        Envelopes are discarded and the dst scene will be the one runned by director.
        """
        # devs:
        # try to not override this method
        # if you should, try to remain compatible with the recipe TransitionsWithPop
        # if you can't, add in the docstring for your class that is not usable
        # for that recipe, and bonus points if you add to the recipe that
        # your class is not elegible for pop transitions
        dst = self.in_scene.get('dst')
        src = self.out_scene.get('src')
        director.replace(dst)

    def hide_out_show_in(self):
        """Hides the outgoing scene and shows the incoming scene"""
        self.in_scene.visible = True
        self.out_scene.visible = False

    def hide_all(self):
        """Hides both the incoming and outgoing scenes"""
        self.in_scene.visible = False
        self.out_scene.visible = False

    def visit(self):
        # preserve modelview matrix
        glPushMatrix()
        super(TransitionScene, self).visit()
        glPopMatrix()


class RotoZoomTransition(TransitionScene):
    """Rotate and zoom out the outgoing scene, and then rotate and zoom in the incoming
    """

    def __init__(self, *args, **kwargs):
        super(RotoZoomTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1.0

        self.in_scene.transform_anchor = (width // 2, height // 2)
        self.out_scene.transform_anchor = (width // 2, height // 2)

        rotozoom = (ScaleBy(0.001, duration=self.duration / 2.0) |
                    Rotate(360 * 2, duration=self.duration / 2.0)) + Delay(self.duration / 2.0)

        self.out_scene.do(rotozoom)
        self.in_scene.do(Reverse(rotozoom) + CallFunc(self.finish))


class JumpZoomTransition(TransitionScene):
    """Zoom out and jump the outgoing scene, and then jump and zoom in the incoming
    """

    def __init__(self, *args, **kwargs):
        super(JumpZoomTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.5
        self.in_scene.position = (width, 0)
        self.in_scene.transform_anchor = (width // 2, height // 2)
        self.out_scene.transform_anchor = (width // 2, height // 2)

        jump = JumpBy((-width, 0), width // 4, 2, duration=self.duration / 4.0)
        scalein = ScaleTo(1, duration=self.duration / 4.0)
        scaleout = ScaleTo(0.5, duration=self.duration / 4.0)

        jumpzoomout = scaleout + jump
        jumpzoomin = jump + scalein

        delay = Delay(self.duration / 2.0)
        self.out_scene.do(jumpzoomout)
        self.in_scene.do(delay + jumpzoomin + CallFunc(self.finish))


class MoveInLTransition(TransitionScene):
    """Move in from to the left the incoming scene.
    """
    def __init__(self, *args, **kwargs):
        super(MoveInLTransition, self).__init__(*args, **kwargs)

        self.init()
        a = self.get_action()

        self.in_scene.do((Accelerate(a, 0.5)) + CallFunc(self.finish))

    def init(self):
        width, height = director.get_window_size()
        self.in_scene.position = (-width, 0)

    def get_action(self):
        return MoveTo((0, 0), duration=self.duration)


class MoveInRTransition(MoveInLTransition):
    """Move in from to the right the incoming scene.
    """
    def init(self):
        width, height = director.get_window_size()
        self.in_scene.position = (width, 0)

    def get_action(self):
        return MoveTo((0, 0), duration=self.duration)


class MoveInTTransition(MoveInLTransition):
    """Move in from to the top the incoming scene.
    """
    def init(self):
        width, height = director.get_window_size()
        self.in_scene.position = (0, height)

    def get_action(self):
        return MoveTo((0, 0), duration=self.duration)


class MoveInBTransition(MoveInLTransition):
    """Move in from to the bottom the incoming scene.
    """
    def init(self):
        width, height = director.get_window_size()
        self.in_scene.position = (0, -height)

    def get_action(self):
        return MoveTo((0, 0), duration=self.duration)


class SlideInLTransition(TransitionScene):
    """Slide in the incoming scene from the left border.
    """
    def __init__(self, *args, **kwargs):
        super(SlideInLTransition, self).__init__(*args, **kwargs)

        self.width, self.height = director.get_window_size()
        self.init()

        move = self.get_action()

        self.in_scene.do(Accelerate(move, 0.5))
        self.out_scene.do(Accelerate(move, 0.5) + CallFunc(self.finish))

    def init(self):
        self.in_scene.position = (-self.width, 0)

    def get_action(self):
        return MoveBy((self.width, 0), duration=self.duration)


class SlideInRTransition(SlideInLTransition):
    """Slide in the incoming scene from the right border.
    """
    def init(self):
        self.in_scene.position = (self.width, 0)

    def get_action(self):
        return MoveBy((-self.width, 0), duration=self.duration)


class SlideInTTransition(SlideInLTransition):
    """Slide in the incoming scene from the top border.
    """
    def init(self):
        self.in_scene.position = (0, self.height)

    def get_action(self):
        return MoveBy((0, -self.height), duration=self.duration)


class SlideInBTransition(SlideInLTransition):
    """Slide in the incoming scene from the bottom border.
    """
    def init(self):
        self.in_scene.position = (0, -self.height)

    def get_action(self):
        return MoveBy((0, self.height), duration=self.duration)


class FlipX3DTransition(TransitionScene):
    """Flips the screen horizontally.
    The front face is the outgoing scene and the back face is the incoming scene.
    """
    def __init__(self, *args, **kwargs):
        super(FlipX3DTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D(amplitude=0, duration=0, grid=(1, 1), waves=2)
        flip90 = OrbitCamera(angle_x=0,  delta_z=90, duration=self.duration / 2.0)
        flipback90 = OrbitCamera(angle_x=0, angle_z=90, delta_z=90, duration=self.duration / 2.0)

        self.in_scene.visible = False
        flip = turnongrid + \
            flip90 + \
            CallFunc(self.hide_all) + \
            FlipX3D(duration=0) + \
            CallFunc(self.hide_out_show_in) + \
            flipback90

        self.do(flip +
                CallFunc(self.finish) +
                StopGrid())


class FlipY3DTransition(TransitionScene):
    """Flips the screen vertically.
    The front face is the outgoing scene and the back face is the incoming scene.
    """
    def __init__(self, *args, **kwargs):
        super(FlipY3DTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D(amplitude=0, duration=0, grid=(1, 1), waves=2)
        flip90 = OrbitCamera(angle_x=90, delta_z=-90, duration=self.duration / 2.0)
        flipback90 = OrbitCamera(angle_x=90, angle_z=90, delta_z=90, duration=self.duration / 2.0)

        self.in_scene.visible = False
        flip = turnongrid + \
            flip90 + \
            CallFunc(self.hide_all) + \
            FlipX3D(duration=0) + \
            CallFunc(self.hide_out_show_in) + \
            flipback90

        self.do(flip +
                CallFunc(self.finish) +
                StopGrid())


class FlipAngular3DTransition(TransitionScene):
    """Flips the screen half horizontally and half vertically.
    The front face is the outgoing scene and the back face is the incoming scene.
    """
    def __init__(self, *args, **kwargs):
        super(FlipAngular3DTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D(amplitude=0, duration=0, grid=(1, 1), waves=2)
        flip90 = OrbitCamera(angle_x=45,  delta_z=90, duration=self.duration / 2.0)
        flipback90 = OrbitCamera(angle_x=45, angle_z=90, delta_z=90, duration=self.duration / 2.0)

        self.in_scene.visible = False
        flip = turnongrid + \
            flip90 + \
            CallFunc(self.hide_all) + \
            FlipX3D(duration=0) + \
            CallFunc(self.hide_out_show_in) + \
            flipback90

        self.do(flip +
                CallFunc(self.finish) +
                StopGrid())


class ShuffleTransition(TransitionScene):
    """Shuffle the outgoing scene, and then reorder the tiles with the incoming scene.
    """
    def __init__(self, *args, **kwargs):
        super(ShuffleTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / height
        x, y = int(12*aspect), 12

        shuffle = ShuffleTiles(grid=(x, y), duration=self.duration / 2.0, seed=15)
        self.in_scene.visible = False

        self.do(shuffle +
                CallFunc(self.hide_out_show_in) +
                Reverse(shuffle) +
                CallFunc(self.finish) +
                StopGrid())


class ShrinkGrowTransition(TransitionScene):
    """Shrink the outgoing scene while grow the incoming scene
    """
    def __init__(self, *args, **kwargs):
        super(ShrinkGrowTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1

        self.in_scene.transform_anchor = (2*width / 3.0, height / 2.0)
        self.out_scene.transform_anchor = (width / 3.0, height / 2.0)

        scale_out = ScaleTo(0.01, duration=self.duration)
        scale_in = ScaleTo(1.0, duration=self.duration)

        self.in_scene.do(Accelerate(scale_in, 0.5))
        self.out_scene.do(Accelerate(scale_out, 0.5) + CallFunc(self.finish))


class CornerMoveTransition(TransitionScene):
    """Moves the bottom-right corner of the incoming scene to the top-left corner
    """
    def __init__(self, *args, **kwargs):
        super(CornerMoveTransition, self).__init__(*args, **kwargs)

        self.out_scene.do(MoveCornerUp(duration=self.duration) +
                          CallFunc(self.finish) +
                          StopGrid())

    def start(self):
        # don't call super. overriding order
        self.add(self.in_scene, z=0)
        self.add(self.out_scene, z=1)


class EnvelopeTransition(TransitionScene):
    """From the outgoing scene:
        - moves the top-right corner to the center
        - moves the bottom-left corner to the center

      From the incoming scene:
        - performs the reverse action of the outgoing scene
    """
    def __init__(self, *args, **kwargs):
        super(EnvelopeTransition, self).__init__(*args, **kwargs)

        self.in_scene.visible = False

        move = QuadMoveBy(delta0=(320, 240), delta1=(-630, 0),
                          delta2=(-320, -240), delta3=(630, 0),
                          duration=self.duration / 2.0)
        # move = Accelerate(move)
        self.do(move +
                CallFunc(self.hide_out_show_in) +
                Reverse(move) +
                CallFunc(self.finish) +
                StopGrid())


class FadeTRTransition(TransitionScene):
    """Fade the tiles of the outgoing scene from the left-bottom corner the to top-right corner.
    """
    def __init__(self, *args, **kwargs):
        super(FadeTRTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / height
        x, y = int(12 * aspect), 12

        a = self.get_action(x, y)

#        a = Accelerate(a)
        self.out_scene.do(a +
                          CallFunc(self.finish) +
                          StopGrid())

    def start(self):
        # don't call super. overriding order
        self.add(self.in_scene, z=0)
        self.add(self.out_scene, z=1)

    def get_action(self, x, y):
        return FadeOutTRTiles(grid=(x, y), duration=self.duration)


class FadeBLTransition(FadeTRTransition):
    """Fade the tiles of the outgoing scene from the top-right corner to the bottom-left corner.
    """
    def get_action(self, x, y):
        return FadeOutBLTiles(grid=(x, y), duration=self.duration)


class FadeUpTransition(FadeTRTransition):
    """Fade the tiles of the outgoing scene from the bottom to the top.
    """
    def get_action(self, x, y):
        return FadeOutUpTiles(grid=(x, y), duration=self.duration)


class FadeDownTransition(FadeTRTransition):
    """Fade the tiles of the outgoing scene from the top to the bottom.
    """
    def get_action(self, x, y):
        return FadeOutDownTiles(grid=(x, y), duration=self.duration)


class TurnOffTilesTransition(TransitionScene):
    """Turn off the tiles of the outgoing scene in random order
    """
    def __init__(self, *args, **kwargs):
        super(TurnOffTilesTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / height
        x, y = int(12 * aspect), 12

        a = TurnOffTiles(grid=(x, y), duration=self.duration)
#        a = Accelerate(a)
        self.out_scene.do(a +
                          CallFunc(self.finish) +
                          StopGrid())

    def start(self):
        # don't call super. overriding order
        self.add(self.in_scene, z=0)
        self.add(self.out_scene, z=1)


class FadeTransition(TransitionScene):
    """Fade out the outgoing scene and then fade in the incoming scene.

    Optionally supply the color to fade to in-between as an RGB color tuple.
    """
    def __init__(self, *args, **kwargs):
        color = kwargs.pop('color', (0, 0, 0)) + (0,)
        super(FadeTransition, self).__init__(*args, **kwargs)

        self.fadelayer = ColorLayer(*color)

        self.in_scene.visible = False
        self.add(self.fadelayer, z=2)

    def on_enter(self):
        super(FadeTransition, self).on_enter()
        self.fadelayer.do(FadeIn(duration=self.duration / 2.0) +
                          CallFunc(self.hide_out_show_in) +
                          FadeOut(duration=self.duration / 2.0) +
                          CallFunc(self.finish))

    def on_exit(self):
        super(FadeTransition, self).on_exit()
        self.remove(self.fadelayer)


class SplitColsTransition(TransitionScene):
    """Splits the screen in columns.
    The odd columns goes upwards while the even columns goes downwards.
    """
    def __init__(self, *args, **kwargs):
        super(SplitColsTransition, self).__init__(*args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.visible = False
        flip_a = self.get_action()
        flip = flip_a + \
            CallFunc(self.hide_out_show_in) + \
            Reverse(flip_a)

        self.do(AccelDeccel(flip) +
                CallFunc(self.finish) +
                StopGrid())

    def get_action(self):
        return SplitCols(cols=3, duration=self.duration / 2.0)


class SplitRowsTransition(SplitColsTransition):
    """Splits the screen in rows.
    The odd rows goes to the left while the even rows goes to the right.
    """
    def get_action(self):
        return SplitRows(rows=3, duration=self.duration / 2.0)


class ZoomTransition(TransitionScene):
    """Zoom and FadeOut the outgoing scene."""

    def __init__(self, *args, **kwargs):
        if 'src' in kwargs or len(args) == 3:
            raise Exception("ZoomTransition does not accept 'src' parameter.")

        super(ZoomTransition, self).__init__(*args, **kwargs)
        # fixme: if scene was never run and some drawable need to initialize
        # in scene on enter the next line will render bad
        self.out_scene.visit()

    def start(self):
        screensprite = self._create_out_screenshot()
        zoom = ScaleBy(2, self.duration) | FadeOut(self.duration)
        restore = CallFunc(self.finish)
        screensprite.do(zoom + restore)

        self.add(screensprite, z=1)
        self.add(self.in_scene, z=0)

    def finish(self):
        # tested with the recipe TransitionsWithPop, works.
        dst = self.in_scene.get('dst')
        director.replace(dst)

    def _create_out_screenshot(self):
        # TODO: try to use `pyglet.image.get_buffer_manager().get_color_buffer()`
        #       instead of create a new BufferManager... note that pyglet uses
        #       a BufferManager singleton that fail when you change the window
        #       size.
        buffer = pyglet.image.BufferManager()
        image = buffer.get_color_buffer()

        width, height = director.window.width, director.window.height
        actual_width, actual_height = director.get_window_size()

        out = Sprite(image)
        out.position = actual_width // 2, actual_height // 2
        out.scale = max(actual_width / width, actual_height / height)

        return out
