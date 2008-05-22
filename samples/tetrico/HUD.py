# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from cocos.layer import *


class HUD( Layer ):
    def __init__( self ):
        super( HUD, self).__init__()
