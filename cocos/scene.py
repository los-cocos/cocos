# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2017  Richard Jones, Claudio Canepa
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
Scene class.
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

__all__ = ['Scene']


import cocos
from cocos.director import director
import cocos.cocosnode as cocosnode

try:
    import cocos.audio.music
except Exception:
    pass


class Scene(cocosnode.CocosNode):
    """
        Creates a Scene with layers and / or scenes.

        Responsibilities:
            Control the dispatching of events to its layers; and background 
            music playback.

        Arguments:
            children (list[Layer or Scene]):
                Layers or Scenes that will be part of the scene.
                They are automatically assigned a z-level from 0 to
                num_children.
        """

    def __init__(self, *children):
        
        super(Scene, self).__init__()
        self._handlers_enabled = False
        for i, c in enumerate(children):
            self.add(c, z=i)

        x, y = director.get_window_size()

        self.transform_anchor_x = x // 2
        self.transform_anchor_y = y // 2
        self.music = None
        self.music_playing = False

    def on_enter(self):
        """Called every time the Scene enters the stage."""
        for c in self.get_children():
            c.parent = self
        super(Scene, self).on_enter()
        if self.music is not None:
            cocos.audio.music.control.load(self.music)
        if self.music_playing:
            cocos.audio.music.control.play()

    def on_exit(self):
        """Called every time the :class:`Scene` exits the stage."""
        super(Scene, self).on_exit()
        # _apply_music after super, because is_running must be already False
        if self.music_playing:
            cocos.audio.music.control.stop()

    def end(self, value=None):
        """Ends the current scene.

        This is accomplished by calling :meth:`.Director.pop`.
        Also sets ``director.return_value`` to ``value``.

        Arguments:
            value(anything):
                The return value. It can be anything. A type or an instance.
        """
        director.return_value = value
        director.pop()

    def load_music(self, filename):
        """This prepares a streamed music file to be played in this scene.

        Music will be stopped after calling this (even if it was playing before).

        Arguments:
            filename (str): Filename of music to load.
                Depending on installed libraries, supported formats may be
                WAV, MP3, OGG, MOD. You can also use ``None`` to unset music.
        """
        self.music = filename
        self.music_playing = False
        if self.is_running:
            if filename is not None:
                cocos.audio.music.control.load(filename)
            else:
                cocos.audio.music.control.stop()

    def play_music(self):
        """Enable music playback for this scene. Nothing happens if music was 
        already playing.

        Note that if you call this method on an inactive scene, the music will
        start playing back only if/when the scene gets activated.
        """
        if self.music is not None and not self.music_playing:
            self.music_playing = True
            if self.is_running:
                cocos.audio.music.control.play()

    def stop_music(self):
        """Stops music playback for this scene.
        """
        self.load_music(None)
