# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2019  Richard Jones, Claudio Canepa
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
# Ideas borrowed from:
#    Artificial Ineptitude : http://www.pyweek.org/e/0AI/
#
""" """

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from cocos.scene import Scene
from cocos.director import director

__all__ = ['SequenceScene', ]


class SequenceScene(Scene):
    """A Scene used to play a sequence of scenes one after another.

    Arguments:
        *scenes (Scene): argument list with the scenes to play.

    The playing goes from first arg to last arg.

    For each scene, scene.on_enter is not called until it becomes active.

    Use director.pop to advance to the next scene.

    director.pop when the last scene is playing removes that scene and the
    SequenceScene from the scene stack.

    Example use case: running a intro scene before the main menu scene::

        director.run(SequenceScene(intro(), menuGame()))

    """
    def __init__(self, *scenes):
        super(SequenceScene, self).__init__()
        self.scenes = scenes
        self.p = 0

    def on_enter(self):
        if self.p >= len(self.scenes):
            director.pop()
        else:
            director.push(self.scenes[self.p])

        self.p += 1
