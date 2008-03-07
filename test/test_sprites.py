#
# Los Cocos: Sprite Test
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyglet import image, font
from pyglet.gl import *
from pyglet.window import key

from cocos.actions import *
from cocos.director import director
from cocos.layer import Layer 
from cocos.scene import Scene

import foo      # Bezier configurations


def get_sprite_test( index ):
    d = tests[index]
    return Scene( FontLayer( title = d[0], subtitle=d[1]), d[2]( index ) )


class FontLayer( Layer ):
    def __init__( self, title="Sprite Exmaple #", subtitle ="Goto()"  ):
        super( FontLayer, self ).__init__()

        self.title = title
        self.subtitle = subtitle

        self.text_title = pyglet.text.Label(self.title,
            font_size=32,
            x=5,
            y=director.get_window_size()[1],
            halign=font.Text.LEFT,
            valign=font.Text.TOP,
            batch=self.batch)

        self.text_subtitle = pyglet.text.Label(self.subtitle,
            font_size=18,
            x=5,
            y=director.get_window_size()[1] - 80,
            halign=font.Text.LEFT,
            valign=font.Text.TOP,
            batch=self.batch )

        self.text_help = pyglet.text.Label("Press LEFT / RIGHT for prev/next test, ENTER to restart test",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER,
            batch=self.batch )


class SpriteLayer( Layer ):

    def __init__( self, index=1 ):
        super(SpriteLayer, self ).__init__()
        self.index = index

        self.image = pyglet.resource.image('grossini.png')
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.image_sister1 = pyglet.resource.image('grossinis_sister1.png')
        self.image_sister1.anchor_x = self.image_sister1.width / 2
        self.image_sister1.anchor_y = self.image_sister1.height / 2

        self.image_sister2 = pyglet.resource.image('grossinis_sister2.png')
        self.image_sister2.anchor_x = self.image_sister2.width / 2
        self.image_sister2.anchor_y = self.image_sister2.height / 2

    def on_key_release( self, keys, mod ):
        # LEFT: go to previous scene
        # RIGTH: go to next scene
        # ENTER: restart scene
        if keys == key.LEFT:
            self.index -= 1
            if self.index < 1:
                self.index = len( tests )
        elif keys == key.RIGHT:
            self.index += 1
            if self.index > len( tests ):
                self.index = 1

        if keys in (key.LEFT, key.RIGHT, key.ENTER):
            director.replace( get_sprite_test( self.index ) )
            return True

    def on_exit( self ):
        for o in self.objects:
            o.stop()

class SpriteGoto( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=320, y=100 )

        self.add( sprite )

        sprite.do( Goto( (620,100), 5 ) )


class SpriteMove( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=320, y=100 )

        self.add( sprite )

        move = Move( (150,0), 3 )
        sprite.do( move )


class SpriteRepeatMove( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        move = Move( (150,0), 0.5 )
        rot = Rotate( 360, 0.5 )

        sprite.do( Repeat( Sequence( rot + move , rot , move , rot , move , rot) ) )

class SpriteScale( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=320, y=240 )

        self.add( sprite )

        sprite.do( Scale( 10, 5 ) )

class SpriteRotate( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=320, y=100 )

        self.add( sprite )

        sprite.do( Rotate( 360, 2 ) )

class SpriteJump( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        sprite.do( Jump(y=100, x=400, jumps=4, duration=3 ) )

class SpriteBezier( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        sprite.do( Bezier( foo.curva, 5 ) )

class SpriteSpawn( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        jump = Jump(100,400,4,5)
        rotate = Rotate( 720, 5 )
        sprite.do( jump | rotate )

class SpriteSequence( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )
        
        bz = Bezier( foo.curva, 3 )
        move = Move( (0,-250), 3 )
        jump = Jump(100,-400,4,3)

        sprite.do( bz + move + jump )

class SpriteDelay( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        move = Move( (250,0), 3 )
        jump = Jump(100,-250,4,3)

        sprite.do( move + Delay(5) + jump )

class SpriteBlink( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=320, y=240 )

        self.add( sprite )

        blink = Blink( 10, 2 )

        sprite.do( blink )

class SpriteFadeOut( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite( self.image_sister1, x=200, y=240 )
        sprite2 = ActionSprite( self.image_sister2, x=440, y=240 )

        self.add( sprite1, sprite2 )

        fadeout = FadeOut( 2 )
        fadein = FadeIn( 2 )

        sprite1.opacity = 0
        sprite1.do( fadein )
        sprite2.do( fadeout )

class SpriteRepeat( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )

        jump = Jump(100,400,4,3, mode=RepeatMode )

        sprite.do( Repeat( jump ) )

class SpriteRepeat2( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )
        
        jump = Jump(100,400,4,3, mode=PingPongMode )

        sprite.do( Repeat( jump ) )


class SpriteRepeatSeq( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )
        
        jump = Jump(100,400,4,2)
        move = Move( (0,100), 1 )
        jump2 = Jump(50,-200,4,2)

        sprite.do( Repeat( jump + move + jump2 , 4 ) )


class SpriteRepeatSeq2( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )

        self.add( sprite )
        
        jump = Jump(50,200,4,1)
        move = Move( (0,100), 0.5 )
        jump2 = Jump(50,-200,4,1)

        sprite.do( Repeat( Repeat(jump,3) + Repeat(move,3) + Repeat(jump2,3) ) )


class SpriteTrigger( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite( self.image, x=120, y=100 )
        self.add( sprite )
        
        move = Move( (100,0), 2 )

        sprite.do( move + CallFunc( self.say_hello )  )

    def say_hello( self ):
        print "HELLO BABY"

        sprite2 = ActionSprite( self.image_sister1, x=270, y=110 )
        self.add( sprite2 )


class SpriteReuseAction( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite( self.image_sister1, x=120, y=250 )
        sprite2 = ActionSprite( self.image_sister2, x=20, y=100 )

        self.add( sprite1, sprite2 )

        jump = Jump( 150, 400, 4, 4 )
        sprite1.do( jump )
        sprite2.do( jump )


class SpriteReuseSequence( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite( self.image_sister1, x=120, y=250 )
        sprite2 = ActionSprite( self.image_sister2, x=20, y=100 )

        self.add( sprite1, sprite2 )

        jump = Jump(50,200,4,2)
        move = Move( (0,100), 2)
        jump2 = Jump(50,-200,4, 2)

        rotate = Rotate( 360, 2 )

        seq = Repeat(jump + move + jump2 )

        sprite1.do( seq )
        sprite2.do( seq )
        sprite2.do( Repeat( rotate) )


class SpriteAlterTime( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite( self.image_sister1, x=20, y=100 )
        sprite2 = ActionSprite( self.image_sister2, x=20, y=300 )

        self.add( sprite1, sprite2 )

        move1 = Move( (500,0), 3 )
        move2 = Move( (500,0), 3, time_func=accelerate)

        sprite1.do( move1 )
        sprite2.do( move2 )


class SpriteRepeatAlterTime( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite( self.image_sister1, x=20, y=100 )
        sprite2 = ActionSprite( self.image_sister2, x=20, y=300 )

        self.add( sprite1, sprite2 )

        move1 = Move( (500,0), 3 )
        move2 = Move( (500,0), 3, time_func=accelerate)

        sprite1.do( Repeat(move1) )
        sprite2.do( Repeat(move2) )


# accelerate() is a function that is part of actions.py
# It is really simple. Look at it:
# and it is very simple:
#
#def accelerate( t, duration ):
#    return t * (t/duration)
#
# To try some cool effects, create your own alter-time function!
   
tests = {
 1: ("Test #1 - Goto", "sprite.do( Goto( (x,y), duration ) )", SpriteGoto ),
 2: ("Test #2 - Move", "sprite.do( Move( (delta_x,delta_y), duration ) )", SpriteMove ),
 3: ("Test #3 - Scale", "sprite.do( Scale( zoom_factor, duration) )", SpriteScale ),
 4: ("Test #4 - Rotate", "sprite.do( Rotate( degrees, duration) )", SpriteRotate ),
 5: ("Test #5 - Jump", "sprite.do( Jump( y, x, jumps, duration) )", SpriteJump),
 6: ("Test #6 - Bezier", "sprite.do( Bezier( bezier_conf, duration) )", SpriteBezier),
 7: ("Test #7 - Spawn", "Run 2 (or more) actions at the same time:\n\nsprite.do( Jump() | Rotate() )\nor:\nsprite.do( Spawn( Jump(), Rotate() ) )\nor:\nsprite.do( Jump() )\nsprite.do( Rotate() )", SpriteSpawn),
 8: ("Test #8 - Sequence", "Run actions sequentialy:\n\nsprite.do( Bezier() + Move() + Jump() )\nor:\nsprite.do( Sequence( Bezier(), Move(), Jump() ) )", SpriteSequence),
 9: ("Test #9 - Blink", "Show and hide an sprite\nsprite.do( Blink( times, duration ) )\n\nShow() and Hide() are actions too.", SpriteBlink),
 10: ("Test #10 - FadeIn and FadeOut", "Fades in and out and sprite\nsprite1.do( FadeIn( duration ) )\nsprite2.do( FadeOut(duration)).", SpriteFadeOut),
 11: ("Test #11 - Delay","Delays between actions\nsprite.do(Move() + Delay( seconds ) + Jump() )\n\nRandomDelay() is an action too.", SpriteDelay ),
 12: ("Test #12 - Repeat", "Run the same action in 'RepeatMode'\nsprite.do( Repeat( Jump( mode=RepeatMode) )", SpriteRepeat),
 13: ("Test #13 - Repeat a-la PingPong", "Run the same action in 'PingPongMode' (default mode)\nsprite.do( Repeat( Jump( mode=PingPongMode) )", SpriteRepeat2),
 14: ("Test #14 - Repeat a Sequence", "Repeat a sequence 4 times\nsprite.do( Repeat( jump + move + jump2, 4 )", SpriteRepeatSeq),
 15: ("Test #15 - Repeat a Sequence #2", "Repeat a sequence of duplicate Actions\nsprite.do( Repeat( rot + move + rot + move + rot + move + rot ) )", SpriteRepeatMove ),
 16: ("Test #16 - Repeat Sequence of Repeats", "Repeat a sequence of repeats\nsprite.do( Repeat( Repeat(jump,3) + Repeat(move,3) + Repeat(jump2,3) )", SpriteRepeatSeq2),
 17: ("Test #17 - Triggers","Call a python function\nsprite.do( move + CallFunc( self.say_hello) )\n\nCallFuncS(), another action, passes the sprite as the 1st parameter", SpriteTrigger ),
 18: ("Test #18 - Reusable Actions","Run the same action in different sprites\njump = Jump(150,400,4,4)\nsprite1.do( jump )\nsprite2.do( jump )", SpriteReuseAction),
 19: ("Test #19 - Reusable Actions #2","Run a sequence of actions in different sprites\nThe other sprites can run other actions in parallel.\nseq=Repeat(action1+action2+action3)\nsprite1.do(seq)\nsprite2.do(seq)\nsprite2.do( Repeat( rotate) )", SpriteReuseSequence),
 20: ("Test #20 - Alter time", "You can change the speed of time:\n\ndef accelerate(t, duration):\n\treturn t * (t/duration)\n\nmove = Move( (300,0), 5, time_func=accelerate)\nsprite.do(move)\n\nThe other sprite is doing the same action without altering the time", SpriteAlterTime),
 21: ("Test #21 - Repeat time altered actions", "Repeat actions that were time-altered:\n\ndef accelerate(t, duration):\n\treturn t * (t/duration)\n\nmove = Move( (300,0), 5, time_func=accelerate)\nsprite.do(Repeat(move))\n\nThe other sprite is doing the same action without altering the time", SpriteRepeatAlterTime),

}

if __name__ == "__main__":
    director.init( resizable=True, caption='Los Cocos - Sprite test' )
#    director.window.set_fullscreen(True)
    director.run( get_sprite_test( 1 ) )
