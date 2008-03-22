#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Interfaces uses internally by Sprites, Layers and Scenes"""

class Container( object ):
    def add( self, child, *args, **kwargs ):
        raise Exception("Not Implemented")

    def remove( self, reference ): 
        raise Exception("Not Implemented")
