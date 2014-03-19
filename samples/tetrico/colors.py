from __future__ import division, print_function, unicode_literals

import pyglet

class Colors( object ):
    colors = ['black','orange','red','yellow','cyan','magenta','green','blue',
            'black',        # don't remove
            'rotate','scale','liquid','waves','twirl','lens',
            'black' ]       # don't remove

    BLACK,ORANGE,RED,YELLOW,CYAN,MAGENTA,GREEN,BLUE, LAST_COLOR,  \
        ROTATE, SCALE, LIQUID, WAVES, TWIRL, LENS, LAST_SPECIAL = range( len(colors) )

    images = [ pyglet.resource.image('block_%s.png' % color) for color in colors ]
    
    specials = [ k for k in range( LAST_COLOR+1, LAST_SPECIAL) ]

