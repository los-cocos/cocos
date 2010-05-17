__all__ = ['SDL', 'pygame']

import cocos
_working = True

try:
    import pygame.mixer
except ImportError, error:
    # set to 0 to debug import errors
    if 1:
        _working = False
    else:
        raise


def initialize(arguments={}):
    global _working
    if arguments is None:
        _working = False
        music.set_control('dummy')
    if _working:
        pygame.mixer.init(**arguments)
        music.set_control('pygame')

