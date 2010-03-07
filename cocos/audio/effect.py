from cocos.audio.pygame.mixer import Sound
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
            `filename` : path of a WAV or Ogg audio file
        """
        self.sound = Sound(filename)
        self.action = actions.PlayAction(self.sound)

    def play(self):
        self.sound.play()
