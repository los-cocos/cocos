#
# Los Cocos: Particle Example
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import *
from cocos.particle import *
from cocos.layer import *
from cocos.scene import *

class ParticleLayer( AnimationLayer ):

    def __init__( self ):
        super( ParticleLayer, self ).__init__()

        self.particle = ParticleEngine( 120 )

        self.add( self.particle )


if __name__ == "__main__":
    director.init( resizable=True)
    director.run( Scene( ParticleLayer()) )
