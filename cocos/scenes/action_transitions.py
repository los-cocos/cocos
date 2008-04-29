#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
'''Transitions between Scenes'''

import pyglet

from cocos.actions import *
import cocos.scene as scene
from cocos.director import director

__all__ = ['TransformScene',
            'RotoZoomTransition','JumpZoomTransition',

            'MoveInLTransition','MoveInRTransition',
            'MoveInBTransition','MoveInTTransition',
            'SlideInLTransition','SlideInRTransition',
            'SlideInBTransition','SlideInTTransition',

            'FlipXTransition', 'FlipYTransition',
            'ShuffleTransition',
            'ShrinkAndGrowTransition',
            'CornerMoveTransition',
            'EnvelopeTransition',
            ]

class TransformScene(scene.Scene):
    """
    A Scene that takes two scenes and makes a transition between them
    """
    
    def __init__(self, out_scene, in_scene, duration=2):
        super(TransformScene, self).__init__()

        self.in_scene = in_scene
        self.out_scene = out_scene
        self.dt = 0.0
        self.duration = duration

        self.start()
        self.schedule( self.step )

    def start(self):
        self.add( self.in_scene, z=1, name="in" )
        self.add( self.out_scene, z=0, name="out" )

    def step(self, dt):
        self.dt += dt
        if self.dt >= self.duration:
            self.unschedule(self.step)
            self.stop()
            director.replace( self.in_scene )

    def stop(self):
        self.out_scene.visible = True
        self.out_scene.position = (0,0)
        self.out_scene.scale = 1
        self.remove( self.in_scene )
        self.remove( self.out_scene )

    def flip_over( self ):
        self.in_scene.visible = True
        self.out_scene.visible = False
        
class RotoZoomTransition(TransformScene):
    """
    Slides out one scene while sliding in onother.
    """    

    def __init__( self, *args, **kwargs ):
        super(RotoZoomTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1.0

        self.in_scene.transform_anchor = (width // 2, height //2 )
        self.out_scene.transform_anchor = (width // 2, height //2 )

        rotozoom = ( ScaleBy(0.001, duration=self.duration/2.0 ) | \
                     Rotate(360 * 2, duration=self.duration/2.0 ) ) + \
                Delay( self.duration / 2.0 )

        self.out_scene.do(  rotozoom ) 
        self.in_scene.do( Reverse(rotozoom) )

class JumpZoomTransition(TransformScene):
    """
    Slides out one scene while sliding in onother.
    """    

    def __init__( self, *args, **kwargs ):
        super(JumpZoomTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.5
        self.in_scene.position = ( width, 0 )
        self.in_scene.transform_anchor = (width // 2, height //2 )
        self.out_scene.transform_anchor = (width // 2, height //2 )

        jump = JumpBy( (-width,0), width//4, 2, duration=self.duration / 4.0 )
        scalein = ScaleTo( 1, duration=self.duration / 4.0 )
        scaleout = ScaleTo( 0.5, duration=self.duration / 4.0 )

        jumpzoomout = scaleout + jump
        jumpzoomin = jump + scalein

        delay = Delay( self.duration / 2.0 )
        self.out_scene.do(  jumpzoomout + delay )
        self.in_scene.do( delay + jumpzoomin )


class MoveInLTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(MoveInLTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(-width,0)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( move )


class MoveInRTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(MoveInRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(width,0)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( move )


class MoveInTTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(MoveInTTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,height)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( move )


class MoveInBTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(MoveInBTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,-height)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( move )

class SlideInLTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(SlideInLTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(-width,0)
        move = MoveBy( (width,0), duration=self.duration)
        self.in_scene.do( move )
        self.out_scene.do( move )


class SlideInRTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(SlideInRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(width,0)
        move = MoveBy( (-width,0), duration=self.duration)
        self.in_scene.do( move )
        self.out_scene.do( move )


class SlideInTTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(SlideInTTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,height)
        move = MoveBy( (0,-height), duration=self.duration)
        self.in_scene.do( move )
        self.out_scene.do( move )


class SlideInBTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(SlideInBTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,-height)
        move = MoveBy( (0,height), duration=self.duration)
        self.in_scene.do( move )
        self.out_scene.do( move )


class FlipXTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(FlipXTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D( amplitude=0, duration=0, grid=(16,12), waves=2 )
        flip90 = OrbitCamera( angle_x=0,  delta_z=90, duration = self.duration / 2.0 )
        flipback90 = OrbitCamera( angle_x=0, angle_z=90, delta_z=90, duration = self.duration / 2.0 )

        self.in_scene.visible = False
        self.do( turnongrid + flip90 + CallFunc( self.flip_over ) + flipback90 + StopGrid() )


class FlipYTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(FlipYTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D( amplitude=0, duration=0, grid=(16,12), waves=2 )
        flip90 = OrbitCamera( angle_x=90, delta_z=-90, duration = self.duration / 2.0 )
        flipback90 = OrbitCamera( angle_x=90, angle_z=90, delta_z=90, duration = self.duration / 2.0 )

        self.in_scene.visible = False
        self.do( turnongrid + flip90 + CallFunc( self.flip_over ) + flipback90 + StopGrid() )


class ShuffleTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(ShuffleTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        shuffle = ShuffleTiles( grid=(16,12), duration=self.duration/2.0, seed=15 )
        self.in_scene.visible = False

        self.do( shuffle + CallFunc(self.flip_over) + Reverse(shuffle) + StopGrid() )


class ShrinkAndGrowTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(ShrinkAndGrowTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1

        self.in_scene.transform_anchor = ( 2*width / 3.0, height / 2.0 )
        self.out_scene.transform_anchor = ( width / 3.0, height / 2.0 )

        scale_out = ScaleTo( 0.01, duration=self.duration )
        scale_in = ScaleTo( 1.0, duration=self.duration )

        self.in_scene.do( Accelerate(scale_in) )
        self.out_scene.do( Accelerate(scale_out) )


class CornerMoveTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(CornerMoveTransition, self ).__init__( *args, **kwargs)

        self.in_scene.do( Reverse(MoveCornerDown( duration=self.duration ) ) + StopGrid() )


class EnvelopeTransition(TransformScene):
    def __init__( self, *args, **kwargs ):
        super(EnvelopeTransition, self ).__init__( *args, **kwargs)

        self.in_scene.visible = False

        move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=self.duration / 2.0 )
        self.do( move + CallFunc(self.flip_over) + Reverse(move) + StopGrid() )
