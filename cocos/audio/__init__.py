__all__ = ['SDL', 'pygame']

import pygame.mixer

def initialize(arguments={}):
    if arguments is None:
        assert False # Null audio not implemented yet
    else:
        pygame.mixer.init(**arguments)
