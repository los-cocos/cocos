"""This is a wrapper to the low level music API. You shouldn't use this in
your cocos applications; but instead use the music control functions in the
Scene class
"""

from cocos import audio
try:
    import pygame.music
except ImportError:
    audio._working = False

class MusicControl(object):
    def load(self, filename):
        pygame.music.load(filename)

    def play(self):
        pygame.music.play()

    def stop(self):
        pygame.music.stop()

class DummyMusicControl(object):
    def load(self,filename):
        pass
    def play(self):
        pass
    def stop(self):
        pass

def set_control(name):
    global control
    assert name in ('dummy', 'pygame')
    control = globals()["_" + name] 

_dummy = DummyMusicControl()
_pygame = MusicControl()

set_control('dummy')

