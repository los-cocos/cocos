# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.audio.effect import Effect

if __name__ == "__main__":
    director.init(audio_backend='sdl')
    effect = Effect('powerup.wav')
    effect.play()
    import time
    time.sleep(2)
