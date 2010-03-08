__all__ = ['SDL', 'pygame']

_working = True

try:
    import pygame.mixer
except ImportError, error:
    _working = False

def initialize(arguments={}):
    global _working
    if arguments is None:
        _working = False

    if _working:
         pygame.mixer.init(**arguments)

