#
# Cocos
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *
from pyglet.window import key


from cocos.actions import *

from cocos.director import director
from cocos.layer import Layer 
from cocos.scene import Scene



class SampleLayer(Layer):
    def on_key_press(self, keys, modifiers ):
        print "key: press", keys, modifiers
        director.push( Scene( SampleLayer2() ) )
        
    def on_key_release( self, keys, modifiers ):
        print "key: release: %s %s" % (keys, modifiers )
               

class SampleLayer2(Layer):
    def on_key_press(self, keys, modifiers ):
        print "key2: press", keys, modifiers
 
    def on_key_release( self, keys, modifiers ):
        print "key2: release: %s %s" % (keys, modifiers )
        director.scene.end( "me mori" )
    

class HiScoreLayer( Layer ):

    def on_key_release( self, keys, mod ):
        if keys == key.ENTER:
            director.scene.end("chau")
            return True

    def on_enter( self ):
        print '**** HI SCORE ****'

class AboutLayer ( Layer ):
    def on_key_release( self, keys, mod ):
        if keys == key.ENTER:
            director.scene.end("chau about")
            return True

    def on_enter( self ):
        print '**** ABOUT ****'

class Nivel( Layer ):
    def __init__( self, l ):
        super( Nivel, self ).__init__()
        self.l = l

    def on_enter( self ):
        print " **** Nivel %d**** " % self.l

    def on_key_release( self, k, m ):
        if k == key.ENTER:
            director.scene.end(True)
        elif k == key.Q:
            director.scene.end(None)
        else:
            director.scene.end(False)
        return True

class GameLayer( Layer ):

    def __init__( self ):
        super( GameLayer, self ).__init__()
        self.first_time = True
        self.next_level = 0

    def on_enter( self ):
        print " **** START GAME **** "

        if self.first_time:
            director.push( Scene( Nivel(1) ) )
            self.first_time = False

        else:
            rv = director.return_value
            if rv == True:
                self.next_level += 1

            elif rv == False:
                self.next_level -= 1

            if rv == None:
                if self.next_level > 10:
                    director.replace( Scene( HiScoreLayer() ) )
                else:
                    director.scene.end("QUIT")

            else:
                director.push( Scene( Nivel( self.next_level ) ) )

class MenuLayer(Layer):
    def on_enter( self ):
        print '**** MENU LAYER ****'

    def on_key_release( self, keys, mod ):
        if keys ==  key.H:
            director.push( Scene( HiScoreLayer() ) )
            return True

        elif keys ==  key.A:
            director.push( Scene( AboutLayer() ) )
            return True

        elif keys ==  key.G:
            director.push( Scene(  GameLayer() ) )
            return True

        elif keys == key.Q:
            director.scene.end("GAME OVER")


class Intro( Layer ):
    def on_enter( self ):
        print '**** INTRO ****'

    def on_key_release( self, keys, mod ):
        if keys ==  key.ENTER:
            director.push( Scene( MenuLayer() ) )
            return True

        elif keys == key.Q:
            director.scene.end("GAME OVER")


if __name__ == "__main__":
    director.init()
    director.run( Scene( Intro()) )
