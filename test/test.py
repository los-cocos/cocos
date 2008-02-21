
#
# framework libs
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image
from pyglet.gl import *

from cocos.actions import *

from cocos.director import director
from cocos.layer import Layer, AnimationLayer
from cocos.scene import Scene



class SampleLayer(Layer):
    def on_key_press(self, keys, modifiers ):
        print "tecla press", keys, modifiers
        director.push( Scene( SampleLayer2() ) )
        
    def on_key_release( self, keys, modifiers ):
        print "tecla release: %s %s" % (keys, modifiers )
               
    def step(self, dt):
        pass

class SampleLayer2(Layer):
    def on_key_press(self, keys, modifiers ):
        print "tecla2 press", keys, modifiers
 
    def on_key_release( self, keys, modifiers ):
        print "tecla2 release: %s %s" % (keys, modifiers )
        director.scene.end( "me mori" )
    
    def step(self, dt):
        pass

class SampleLayer3( AnimationLayer ):
    def __init__( self ):
        super( AnimationLayer, self ).__init__()


from pyglet.window import key

class HiScoreLayer ( AnimationLayer ):

    def __init__( self ):
        super( HiScoreLayer, self ).__init__()
        sprite1 = ActionSprite('grossini.png')
        sprite2 = ActionSprite('grossinis_sister2.png')
        sprite3 = ActionSprite('grossinis_sister2.png')
        sprite4 = ActionSprite('grossinis_sister1.png')
        sprite5 = ActionSprite('grossinis_sister1.png')

        sprite1.translate = Point3( 320,240,0)

        sprite2.translate = Point3( 20,180,0)
        sprite3.translate = Point3( 20,180,0)

        sprite4.translate = Point3( 20,180,0)
        sprite5.translate = Point3( 20,180,0)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )
        self.add( sprite4 )
        self.add( sprite5 )

        go = goto( Point3(320,240,0), 5 )
        go2 = goto( Point3(40,80,0), 5 )

        mo = move( Point3(600,0,0), 10 )

        ro = rotate( 300, 5 )
        ro2 = rotate( -300, 5 )

        sc_up = scale( 15, 5 )
        sc_down = scale( 0.1, 5 )

        import foo
        bz = bezier( foo.curva, 5 )
        bz2 = bezier( foo.new228555, 5 )

        sprite1.do( repeat( sc_up + sc_down ) )
        sprite1.do( repeat( ro + ro2 ) )
#        sprite3.do( timewarp( linear(0.8), bz2) )
        sprite4.do( jump( mo ) )
        sprite5.do( reverse( jump( mo ) ) )
        sprite2.do( bz )
        sprite3.do( reverse( bz ) )


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
        super( GameLayer, self ).__init__(self)
        self.first_time = True
        self.next_level = 0

    def step( self, dt ):
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
#    director.run( Scene( HiScoreLayer()) )
