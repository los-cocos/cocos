from gamectrl import *

class Level( object ):
    pass

class Level1( Level ):
    speed = 0.5
    blocks = [ Colors.LIQUID ]
    lines = 7
    nro = 0
    prob = 0.05

class Level2( Level ):
    speed = 0.45
    blocks = [ Colors.LENS, Colors.SCALE]
    lines = 8
    nro = 1
    prob = 0.07

class Level3( Level ):
    speed = 0.4
    blocks = [ Colors.WAVES, Colors.SPEED_UP, Colors.SPEED_DOWN]
    lines = 9
    nro = 2
    prob = 0.09

class Level4( Level ):
    speed = 0.35
    blocks = [ Colors.TWIRL, Colors.SCALE, Colors.ROTATE, Colors.SPEED_DOWN, Colors.SPEED_UP]
    lines = 11
    nro = 3
    prob = 0.11

class Level5( Level ):
    speed = 0.3
    blocks = [ Colors.TWIRL, Colors.LIQUID, Colors.SCALE, Colors.ROTATE, Colors.SPEED_DOWN, Colors.SPEED_UP]
    lines = 13
    nro = 4
    prob = 0.13

class Level6( Level ):
    speed = 0.25
    blocks = [ Colors.WAVES, Colors.TWIRL, Colors.LIQUID, Colors.SCALE, Colors.ROTATE, Colors.SPEED_DOWN, Colors.SPEED_UP]
    lines = 15
    nro = 5
    prob = 0.15

class Level7( Level ):
    speed = 0.2
    blocks = [ Colors.LIQUID, Colors.WAVES, Colors.TWIRL, Colors.LIQUID, Colors.SCALE, Colors.ROTATE, Colors.SPEED_DOWN, Colors.SPEED_UP]
    lines = 17
    nro = 6
    prob = 0.17

levels = [Level1, Level2, Level3, Level4, Level5, Level6, Level7]
