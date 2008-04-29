#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Transitions between Scenes'''

__docformat__ = 'restructuredtext'

import pyglet

from cocos.actions import *
import cocos.scene as scene
from cocos.director import director

__all__ = [ 'TransitionScene',
            'RotoZoomTransition','JumpZoomTransition',

            'MoveInLTransition','MoveInRTransition',
            'MoveInBTransition','MoveInTTransition',
            'SlideInLTransition','SlideInRTransition',
            'SlideInBTransition','SlideInTTransition',

            'FlipX3DTransition', 'FlipY3DTransition','FlipAngular3DTransition',

            'ShuffleTilesTransition',
            'TurnOffTilesTransition',
            'CurtainTransition',

            'ShrinkAndGrowTransition',
            'CornerMoveTransition',
            'EnvelopeTransition',
            ]

class TransitionScene(scene.Scene):
    """TransitionScene
    A Scene that takes two scenes and makes a transition between them
    """
    
    def __init__(self, out_scene, in_scene, duration=2):
        super(TransitionScene, self).__init__()

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

    def hide_out_show_in( self ):
        self.in_scene.visible = True
        self.out_scene.visible = False

    def hide_all( self ):
        self.in_scene.visible = False
        self.out_scene.visible = False
        
class RotoZoomTransition(TransitionScene):
    '''Rotate and zoom out the outgoing scene, and then rotate and zoom in the incoming 
    '''

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

class JumpZoomTransition(TransitionScene):
    '''Zoom out and jump the outgoing scene, and then jump and zoom in the incoming 
    '''

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


class MoveInLTransition(TransitionScene):
    '''Move in from to the left the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(MoveInLTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(-width,0)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( (Accelerate(move,0.5) ) )


class MoveInRTransition(TransitionScene):
    '''Move in from to the right the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(MoveInRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(width,0)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )


class MoveInTTransition(TransitionScene):
    '''Move in from to the top the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(MoveInTTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,height)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )


class MoveInBTransition(TransitionScene):
    '''Move in from to the bottom the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(MoveInBTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,-height)
        move = MoveTo( (0,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )

class SlideInLTransition(TransitionScene):
    '''Slide in the incoming scene from the left border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInLTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(-width,0)
        move = MoveBy( (width,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) )


class SlideInRTransition(TransitionScene):
    '''Slide in the incoming scene from the right border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(width,0)
        move = MoveBy( (-width,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) )


class SlideInTTransition(TransitionScene):
    '''Slide in the incoming scene from the top border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInTTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,height)
        move = MoveBy( (0,-height), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) )


class SlideInBTransition(TransitionScene):
    '''Slide in the incoming scene from the bottom border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInBTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,-height)
        move = MoveBy( (0,height), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) )


class FlipX3DTransition(TransitionScene):
    '''Flips the screen horizontally.
    The front face is the outgoing scene and the back face is the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(FlipX3DTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D( amplitude=0, duration=0, grid=(1,1), waves=2 )
        flip90 = OrbitCamera( angle_x=0,  delta_z=90, duration = self.duration / 2.0 )
        flipback90 = OrbitCamera( angle_x=0, angle_z=90, delta_z=90, duration = self.duration / 2.0 )

        self.in_scene.visible = False
        flip = turnongrid + flip90 + CallFunc(self.hide_all) + FlipX3D(duration=0) + \
            CallFunc( self.hide_out_show_in ) + flipback90 
        self.do( flip + StopGrid() )


class FlipY3DTransition(TransitionScene):
    '''Flips the screen vertically.
    The front face is the outgoing scene and the back face is the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(FlipY3DTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D( amplitude=0, duration=0, grid=(1,1), waves=2 )
        flip90 = OrbitCamera( angle_x=90, delta_z=-90, duration = self.duration / 2.0 )
        flipback90 = OrbitCamera( angle_x=90, angle_z=90, delta_z=90, duration = self.duration / 2.0 )

        self.in_scene.visible = False
        flip = turnongrid + flip90 + CallFunc(self.hide_all) + FlipX3D(duration=0) + \
            CallFunc( self.hide_out_show_in ) + flipback90 
        self.do( flip + StopGrid() )

class FlipAngular3DTransition(TransitionScene):
    '''Flips the screen half horizontally and half vertically.
    The front face is the outgoing scene and the back face is the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(FlipAngular3DTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        turnongrid = Waves3D( amplitude=0, duration=0, grid=(1,1), waves=2 )
        flip90 = OrbitCamera( angle_x=45,  delta_z=90, duration = self.duration / 2.0 )
        flipback90 = OrbitCamera( angle_x=45, angle_z=90, delta_z=90, duration = self.duration / 2.0 )

        self.in_scene.visible = False
        flip = turnongrid + flip90 + CallFunc(self.hide_all) + FlipX3D(duration=0) + \
            CallFunc( self.hide_out_show_in ) + flipback90 
        self.do( flip + StopGrid() )


class ShuffleTilesTransition(TransitionScene):
    '''Shuffle the outgoing scene, and then reorder the tiles with the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(ShuffleTilesTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / float(height)
        x,y = int(12*aspect), 12

        shuffle = ShuffleTiles( grid=(x,y), duration=self.duration/2.0, seed=15 )
        self.in_scene.visible = False

        self.do( shuffle + CallFunc(self.hide_out_show_in) + Reverse(shuffle) + StopGrid() )


class ShrinkAndGrowTransition(TransitionScene):
    '''Shrink the outgoing scene while grow the incoming scene
    '''
    def __init__( self, *args, **kwargs ):
        super(ShrinkAndGrowTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1

        self.in_scene.transform_anchor = ( 2*width / 3.0, height / 2.0 )
        self.out_scene.transform_anchor = ( width / 3.0, height / 2.0 )

        scale_out = ScaleTo( 0.01, duration=self.duration )
        scale_in = ScaleTo( 1.0, duration=self.duration )

        self.in_scene.do( Accelerate(scale_in,0.5) )
        self.out_scene.do( Accelerate(scale_out,0.5) )


class CornerMoveTransition(TransitionScene):
    '''Move the bottom-right corner of the incoming scene to the top-left corner
    '''
    def __init__( self, *args, **kwargs ):
        super(CornerMoveTransition, self ).__init__( *args, **kwargs)

        self.in_scene.do( Reverse(MoveCornerDown( duration=self.duration ) ) + StopGrid() )


class EnvelopeTransition(TransitionScene):
    '''Shrink the outgoing scene and then grow the incoming scene
    '''
    def __init__( self, *args, **kwargs ):
        super(EnvelopeTransition, self ).__init__( *args, **kwargs)

        self.in_scene.visible = False

        move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=self.duration / 2.0 )
#        move = Accelerate( move )
        self.do( move + CallFunc(self.hide_out_show_in) + Reverse(move) + StopGrid() )


class CurtainTransition(TransitionScene):
    '''Fade the tiles of the outgoing scene from the left-bottom corner the to top-right corner.
    '''
    def __init__( self, *args, **kwargs ):
        super(CurtainTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / float(height)
        x,y = int(12*aspect), 12

        a = FadeOutTiles( grid=(x,y), duration=self.duration )
#        a = Accelerate( a)
        self.out_scene.do( a + StopGrid() )

    def start(self):
        # don't call super. overriding order
        self.add( self.in_scene, z=0, name="in" )
        self.add( self.out_scene, z=1, name="out" )

class TurnOffTilesTransition(TransitionScene):
    '''Turn off the tiles of the outgoing scene in random order
    '''
    def __init__( self, *args, **kwargs ):
        super(TurnOffTilesTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / float(height)
        x,y = int(12*aspect), 12

        a = TurnOffTiles( grid=(x,y), duration=self.duration )
#        a = Accelerate( a)
        self.out_scene.do( a + StopGrid() )

    def start(self):
        # don't call super. overriding order
        self.add( self.in_scene, z=0, name="in" )
        self.add( self.out_scene, z=1, name="out" )

