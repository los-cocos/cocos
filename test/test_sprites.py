#
# Los Cocos: Sprite Example
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
from cocos.layer import Layer, AnimationLayer
from cocos.scene import Scene

import foo      # Bezier configurations


def get_sprite_example( index ):
    d = examples[index]
    return Scene( FontLayer( title = d[0], subtitle=d[1]), d[2]( index ) )


class FontLayer( Layer ):
    def __init__( self, title="Sprite Exmaple #", subtitle ="Goto()"  ):
        super( FontLayer, self ).__init__()

        self.title = title
        self.subtitle = subtitle

        ft_title = font.load( None, 32 )
        ft_subtitle = font.load( None, 18 )
        ft_help = font.load( None, 16 )

        self.text_title = font.Text(ft_title, self.title,
            x=5,
            y=480,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)

        self.text_subtitle = font.Text(ft_subtitle, self.subtitle,
            x=5,
            y=400,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)

        self.text_help = font.Text(ft_help,"Press LEFT / RIGHT for prev/next example, ENTER to restart example",
            x=320,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)

    def step( self, dt ):
        self.text_title.draw()
        self.text_subtitle.draw()
        self.text_help.draw()

class SpriteLayer( AnimationLayer ):

    def __init__( self, index=1 ):
        super(SpriteLayer, self ).__init__()
        self.index = index

    def on_key_release( self, keys, mod ):
        # LEFT: go to previous scene
        # RIGTH: go to next scene
        # ENTER: restart scene
        if keys == key.LEFT:
            self.index -= 1
            if self.index < 1:
                self.index = len( examples )
        elif keys == key.RIGHT:
            self.index += 1
            if self.index > len( examples ):
                self.index = 1

        if keys in (key.LEFT, key.RIGHT, key.ENTER):
            director.replace( get_sprite_example( self.index ) )
            return True

class SpriteGoto( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (320,100,0) )

        self.add( sprite )

        sprite.do( Goto( (620,100,0), 5 ) )


class SpriteMove( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (320,100,0) )

        self.add( sprite )

        move = Move( (150,0,0), 3 )

        sprite.do( move )


class SpriteRepeatMove( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )

        move = Move( (150,0,0), 0.5 )
        rot = Rotate( 360, 0.5 )

        sprite.do( Repeat( Sequence( rot + move , rot , move , rot , move , rot), 3 )  )

class SpriteScale( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (320,100,0) )

        self.add( sprite )

        sprite.do( Scale( 10, 5 ) )

class SpriteRotate( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (320,100,0) )

        self.add( sprite )

        sprite.do( Rotate( 360, 2 ) )

class SpriteJump( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )

        sprite.do( Jump(y=100, x=400, jumps=4, duration=3 ) )

class SpriteBezier( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )

        sprite.do( Bezier( foo.curva, 5 ) )


class SpriteSpawn( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )

        jump = Jump(100,400,4,5)
        rotate = Rotate( -720, 5 )
        sprite.do( jump | rotate )


class SpriteSequence( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        bz = Bezier( foo.curva, 3 )
        move = Move( (0,-250,0), 3 )
        jump = Jump(100,-400,4,3)

        sprite.do( bz + move + jump )

class SpriteDelay( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        move = Move( (250,0,0), 3 )
        jump = Jump(100,-250,4,3)

        sprite.do( move + Delay(5) + jump )

class SpriteBlink( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        blink = Blink( 10, 2 )

        sprite.do( blink )
        
class SpriteRepeat( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        jump = Jump(100,400,4,3, mode=RepeatMode )

        sprite.do( Repeat( jump, 3 ) )

class SpriteRepeat2( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        jump = Jump(100,400,4,3, mode=PingPongMode )
#        jump = Jump(100,400,4,3 )

        sprite.do( Repeat( jump, 3 ) )


class SpriteRepeatSeq( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        jump = Jump(100,400,4,2)
        move = Move( (0,100,0), 1 )
        jump2 = Jump(50,-200,4,2)

        sprite.do( Repeat( jump + move + jump2 , 4 ) )


class SpriteRepeatSeq2( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")
        sprite.place( (120,100,0) )

        self.add( sprite )
        
        jump = Jump(50,200,4,1)
        move = Move( (0,100,0), 0.5 )
        jump2 = Jump(50,-200,4,1)

        sprite.do( Repeat( Repeat(jump,3) + Repeat(move,3) + Repeat(jump2,3), 3 ) )


class SpriteTrigger( SpriteLayer ):
    def on_enter( self ):
        sprite = ActionSprite("grossini.png")

        sprite.place( (120,100,0) )

        self.add( sprite )
        
        move = Move( (100,0,0), 2 )

        sprite.do( move + CallFunc( self.say_hello )  )

    def say_hello( self ):
        print "HELLO BABY"
        sprite2 = ActionSprite("grossinis_sister1.png")
        sprite2.place( (270,110,0) )
        self.add( sprite2 )


class SpriteReuseAction( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite("grossinis_sister1.png")
        sprite2 = ActionSprite("grossinis_sister2.png")

        sprite1.place( (120,250,0) )
        sprite2.place( (20,100,0) )

        self.add( sprite1, sprite2 )

        jump = Jump( 150, 400, 4, 4 )
        sprite1.do( jump )
        sprite2.do( jump )

    def say_hello( self ):
        print "HELLO BABY"
        sprite2 = ActionSprite("grossinis_sister1.png")
        sprite2.place( (270,110,0) )
        self.add( sprite2 )

class SpriteReuseSequence( SpriteLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite("grossinis_sister1.png")
        sprite2 = ActionSprite("grossinis_sister2.png")

        sprite1.place( (120,250,0) )
        sprite2.place( (20,100,0) )

        self.add( sprite1, sprite2 )

        jump = Jump(50,200,4,2)
        move = Move( (0,100,0), 2)
        jump2 = Jump(50,-200,4, 2)

        rotate = Rotate( -360, 2 )

        seq = Repeat(jump + move + jump2,3)

        sprite1.do( seq )
        sprite2.do( seq )
        sprite2.do( Repeat( rotate) )


examples = {
 1: ("Example #1 - Goto", "sprite.do( Goto( (x,y,0), duration ) )", SpriteGoto ),
 2: ("Example #2 - Move", "sprite.do( Move( (delta-x,delta-y,0), duration ) )", SpriteMove ),
 3: ("Example #3 - Scale", "sprite.do( Scale( zoom-factor, duration) )", SpriteScale ),
 4: ("Example #4 - Rotate", "sprite.do( Rotate( degrees, duration) )", SpriteRotate ),
 5: ("Example #5 - Jump", "sprite.do( Jump( y, x, jumps, duration) )", SpriteJump),
 6: ("Example #6 - Bezier", "sprite.do( Bezier( bezier_conf, duration) )", SpriteBezier),
 7: ("Example #7 - Spawn", "Run 2 (or more) actions at the same time:\n\nsprite.do( Jump() | Rotate() )\nor:\nsprite.do( Spawn( Jump(), Rotate() ) )\nor:\nsprite.do( Jump() )\nsprite.do( Rotate() )", SpriteSpawn),
 8: ("Example #8 - Sequence", "Run actions sequentialy:\n\nsprite.do( Bezier() + Move() + Jump() )\nor:\nsprite.do( Sequence( Bezier(), Move(), Jump() ) )", SpriteSequence),
 9: ("Example #9 - Blink", "Show and hide an sprite\nsprite.do( Blink( times, duration ) )\n\nShow() and Hide() are actions too.", SpriteBlink),
 10: ("Example #10 - Delay","Delays between actions\nsprite.do(Move() + Delay( seconds ) + Jump() )\n\nRandomDelay() is an action too.", SpriteDelay ),
 11: ("Example #11 - Repeat", "Run the same action in 'RepeatMode'\nsprite.do( Repeat( Jump( mode=RepeatMode) )", SpriteRepeat),
 12: ("Example #12 - Repeat a-la PingPong", "Run the same action in 'PingPongMode' (default mode)\nsprite.do( Repeat( Jump( mode=PingPongMode) )", SpriteRepeat2),
 13: ("Example #13 - Repeat a Sequence", "Run a sequence many times\nsprite.do( Repeat( jump + move + jump2 )", SpriteRepeatSeq),
 14: ("Example #14 - Repeat a Sequence 2", "Run a sequence of duplicate Actions\nsprite.do( Repeat( rotate + move + rotate + move + rotate + move + rotate ) )", SpriteRepeatMove ),
 15: ("Example #15 - Repeat Sequence of Repeats", "Run a sequence of repeats\nsprite.do( Repeat( Repat(jump) + Repeat(move) + Repeat(jump2) )", SpriteRepeatSeq2),
 16: ("Example #16 - Triggers","Call a python function\nsprite.do( move + CallFunc( self.say_hello) )\n\nCallFuncS() is the action passes the sprite as the 1st parameter", SpriteTrigger ),
 17: ("Example #17 - Reusable Actions","Run the same action in different sprites\njump = Jump(150,400,4,4)\nsprite1.do( jump )\nsprite2.do( jump )", SpriteReuseAction),
 18: ("Example #18 - Reusable Actions #2","Run a sequence of actions in different sprites\nThe other sprites can run other actions in parallel.\nseq=Repeat(action1+action2+action3)\nsprite1.do(seq)\nsprite2.do(seq)\nsprite2.do( Repeat( rotate) )", SpriteReuseSequence),

}

if __name__ == "__main__":
    director.init()
    director.run( get_sprite_example( 1 ) )
