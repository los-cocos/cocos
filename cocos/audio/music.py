"""This is a wrapper to the low level music API. You shouldn't use this in
your cocos applications; but instead use the music control functions in the
Scene class
"""

import pygame.music

class MusicControl(object):
    def load(self, filename):
        pygame.music.load(filename)

    def play(self):
        pygame.music.play()
        
    def stop(self):
        pygame.music.stop()

# Shared singleton
control = MusicControl()

