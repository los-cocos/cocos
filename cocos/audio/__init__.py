__all__ = ['SDL', 'pygame']

_working = True

try:
    import pygame.mixer
except ImportError, error:
    _working = False

def initialize(arguments={}):
    if arguments is None:
        assert False # Null audio not implemented yet
    else:
        if _working:
            pygame.mixer.init(**arguments)
