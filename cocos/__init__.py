"""
Los Cocos: An extension for Pyglet 

http://code.google.com/p/los-cocos/
"""

__version__ = "0.1.2"
__author__ = "PyAr Team"
version = __version__

import actions
import director
import effect
import euclid
import layer
import menu
import path
import scene
import particle
import transitions

import pyglet
if pyglet.version.find( '1.0' ) == -1:
    print "*" * 80
    print "\ncocos v%s does not work properly with pyglet v%s" % (__version__, pyglet.version )
    print "\nUse pyglet v1.0 or upgrade to cocos-0.2.x\n"
    print "*" * 80
    
