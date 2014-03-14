from __future__ import division, print_function, unicode_literals

from colors import *

class Level( object ):
    pass

class LevelLens( Level ):
    speed = 0.5
    blocks = [ Colors.LENS ]
    lines = 10
    prob = 0.07

class LevelScale( Level ):
    speed = 0.5
    blocks = [ Colors.SCALE ]
    lines = 10
    prob = 0.07

class LevelLiquid( Level ):
    speed = 0.45
    blocks = [ Colors.LIQUID ]
    lines = 12
    prob = 0.07

class LevelWaves( Level ):
    speed = 0.4
    blocks = [ Colors.WAVES ]
    lines = 14
    prob = 0.09

class LevelTwirl( Level ):
    speed = 0.35
    blocks = [ Colors.TWIRL ]
    lines = 16
    prob = 0.11

class LevelRotate( Level ):
    speed = 0.3
    blocks = [ Colors.ROTATE ]
    lines = 18
    prob = 0.13

class LevelTwirlZoom( Level ):
    speed = 0.25
    blocks = [ Colors.TWIRL, Colors.SCALE ]
    lines = 20
    prob = 0.15

class LevelWavesRot( Level ):
    speed = 0.2
    blocks = [ Colors.WAVES, Colors.ROTATE]
    lines = 22
    prob = 0.17

levels = [ LevelLens, LevelScale, LevelLiquid, LevelWaves, LevelTwirl, LevelRotate, LevelTwirlZoom, LevelWavesRot ]
