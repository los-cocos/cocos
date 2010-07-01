__docformat__ = 'restructuredtext'

from cocos import audio
try:
    from cocos.audio.pygame.mixer import Sound
except ImportError:
    audio._working = False


import actions

class Effect(object):
    """Effects are sounds effect loaded in memory

    Example ::

        shot = Effect('bullet.wav')
        shot.play() # Play right now
        sprite.do(shot.action)
    """

    def __init__(self, filename):
        """Initialize the effect

        :Parameters:
            `filename` : fullpath
                path of a WAV or Ogg audio file
        """
        if audio._working:
            self.sound = Sound(filename)
        else:
            self.sound = None
        self.action = actions.PlayAction(self.sound)

    def play(self):
        if audio._working:
            self.sound.play()
