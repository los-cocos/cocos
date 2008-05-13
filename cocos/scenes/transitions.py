# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''Transitions between Scenes'''

__docformat__ = 'restructuredtext'

import pyglet

from cocos.actions import *
import cocos.scene as scene
from cocos.director import director
from cocos.layer import ColorLayer

__all__ = [ 'TransitionScene',
            'RotoZoomTransition','JumpZoomTransition',

            'MoveInLTransition','MoveInRTransition',
            'MoveInBTransition','MoveInTTransition',
            'SlideInLTransition','SlideInRTransition',
            'SlideInBTransition','SlideInTTransition',

            'FlipX3DTransition', 'FlipY3DTransition','FlipAngular3DTransition',

            'ShuffleTransition',
            'TurnOffTilesTransition',
            'FadeTRTransition', 'FadeBLTransition',
            'FadeUpTransition', 'FadeDownTransition',

            'ShrinkGrowTransition',
            'CornerMoveTransition',
            'EnvelopeTransition',

            'SplitRowsTransition', 'SplitColsTransition',

            'FadeTransition',
            ]

class TransitionScene(scene.Scene):
    """TransitionScene
    A Scene that takes two scenes and makes a transition between them.
    
    These scenes are children of the transition scene.
    """
    
    def __init__(self, out_scene, in_scene, duration=2):
        super(TransitionScene, self).__init__()

        self.in_scene = in_scene                #: scene that will replace the old one
        self.out_scene = out_scene              #: scene that will be replaced
        self.dt = 0.0
        self.duration = duration                #: duration in seconds of the transition

        self.start()
        self.schedule( self.step )
        
    def start(self):
        '''Adds the incoming scene with z=1 and the outgoing scene with z=0'''
        self.add( self.in_scene, z=1)
        self.add( self.out_scene, z=0)

    def step(self, dt):
        self.dt += dt
        if self.dt > self.duration:
            self.unschedule(self.step)
            self.finish()
            director.replace( self.in_scene )

    def finish(self):
        '''Called the time is over.
        It removes both the incoming and the outgoing scenes from the transition scene.
        '''
        self.remove( self.in_scene )
        self.remove( self.out_scene )
        self.restore_out()

    def hide_out_show_in( self ):
        '''Hides the outgoing scene and shows the incoming scene'''
        self.in_scene.visible = True
        self.out_scene.visible = False

    def hide_all( self ):
        '''Hides both the incoming and outgoing scenes'''
        self.in_scene.visible = False
        self.out_scene.visible = False

    def restore_out( self ):
        '''Restore the position, visible and scale attributes of the outgoing scene
        to the original values'''
        self.out_scene.visible = True
        self.out_scene.position = (0,0)
        self.out_scene.scale = 1
        
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

        self.out_scene.do(  rotozoom + CallFunc( self.restore_out) ) 
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
        self.out_scene.do(  jumpzoomout + delay + CallFunc( self.restore_out ) )
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
        self.out_scene.do( Accelerate(move,0.5) + CallFunc( self.restore_out) )


class SlideInRTransition(TransitionScene):
    '''Slide in the incoming scene from the right border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(width,0)
        move = MoveBy( (-width,0), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) + CallFunc( self.restore_out) )


class SlideInTTransition(TransitionScene):
    '''Slide in the incoming scene from the top border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInTTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,height)
        move = MoveBy( (0,-height), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) + CallFunc( self.restore_out) )


class SlideInBTransition(TransitionScene):
    '''Slide in the incoming scene from the bottom border.
    '''
    def __init__( self, *args, **kwargs ):
        super(SlideInBTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.position=(0,-height)
        move = MoveBy( (0,height), duration=self.duration)
        self.in_scene.do( Accelerate(move,0.5) )
        self.out_scene.do( Accelerate(move,0.5) + CallFunc( self.restore_out) )


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
        flip = turnongrid + \
                flip90 + \
                CallFunc(self.hide_all) + \
                FlipX3D(duration=0) + \
                CallFunc( self.hide_out_show_in ) + \
                flipback90 + \
                CallFunc(self.restore_out) 
        
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
        flip = turnongrid + \
                flip90 + \
                CallFunc(self.hide_all) + \
                FlipX3D(duration=0) + \
                CallFunc( self.hide_out_show_in ) + \
                flipback90 + \
                CallFunc( self.restore_out)
        
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
        flip = turnongrid + \
                flip90 + \
                CallFunc(self.hide_all) + \
                FlipX3D(duration=0) + \
                CallFunc( self.hide_out_show_in ) + \
                flipback90 + \
                CallFunc( self.restore_out)
        
        self.do( flip + StopGrid() )


class ShuffleTransition(TransitionScene):
    '''Shuffle the outgoing scene, and then reorder the tiles with the incoming scene.
    '''
    def __init__( self, *args, **kwargs ):
        super(ShuffleTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / float(height)
        x,y = int(12*aspect), 12

        shuffle = ShuffleTiles( grid=(x,y), duration=self.duration/2.0, seed=15 )
        self.in_scene.visible = False

        self.do( shuffle + \
                 CallFunc(self.hide_out_show_in) + \
                 Reverse(shuffle) + \
                StopGrid() + \
                CallFunc(self.restore_out) \
                )


class ShrinkGrowTransition(TransitionScene):
    '''Shrink the outgoing scene while grow the incoming scene
    '''
    def __init__( self, *args, **kwargs ):
        super(ShrinkGrowTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.scale = 0.001
        self.out_scene.scale = 1

        self.in_scene.transform_anchor = ( 2*width / 3.0, height / 2.0 )
        self.out_scene.transform_anchor = ( width / 3.0, height / 2.0 )

        scale_out = ScaleTo( 0.01, duration=self.duration )
        scale_in = ScaleTo( 1.0, duration=self.duration )

        self.in_scene.do( Accelerate(scale_in,0.5) )
        self.out_scene.do( Accelerate(scale_out,0.5) + CallFunc( self.restore_out) )


class CornerMoveTransition(TransitionScene):
    '''Moves the bottom-right corner of the incoming scene to the top-left corner
    '''
    def __init__( self, *args, **kwargs ):
        super(CornerMoveTransition, self ).__init__( *args, **kwargs)

        self.in_scene.do( Reverse(MoveCornerDown( duration=self.duration ) ) + StopGrid() )


class EnvelopeTransition(TransitionScene):
    '''From the outgoing scene:
        - moves the top-right corner to the center
        - moves the bottom-left corner to the center

      From the incoming scene:
        - performs the reverse action of the outgoing scene
    '''
    def __init__( self, *args, **kwargs ):
        super(EnvelopeTransition, self ).__init__( *args, **kwargs)

        self.in_scene.visible = False

        move = QuadMoveBy( delta0=(320,240), delta1=(-630,0), delta2=(-320,-240), delta3=(630,0), duration=self.duration / 2.0 )
#        move = Accelerate( move )
        self.do( move + \
                 CallFunc(self.hide_out_show_in) + \
                 Reverse(move) + \
                 StopGrid() + \
                 CallFunc(self.restore_out) \
                 )


class FadeTRTransition(TransitionScene):
    '''Fade the tiles of the outgoing scene from the left-bottom corner the to top-right corner.
    '''
    def __init__( self, *args, **kwargs ):
        super(FadeTRTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()
        aspect = width / float(height)
        x,y = int(12*aspect), 12

        a = self.get_action(x,y)

#        a = Accelerate( a)
        self.out_scene.do( a + StopGrid() )

    def start(self):
        # don't call super. overriding order
        self.add( self.in_scene, z=0)
        self.add( self.out_scene, z=1)

    def get_action(self,x,y):
        return FadeOutTRTiles( grid=(x,y), duration=self.duration )

class FadeBLTransition(FadeTRTransition):
    '''Fade the tiles of the outgoing scene from the top-right corner to the bottom-left corner.
    '''
    def get_action(self,x,y):
        return FadeOutBLTiles( grid=(x,y), duration=self.duration )

class FadeUpTransition(FadeTRTransition):
    '''Fade the tiles of the outgoing scene from the bottom to the top.
    '''
    def get_action(self,x,y):
        return FadeOutUpTiles( grid=(x,y), duration=self.duration )

class FadeDownTransition(FadeTRTransition):
    '''Fade the tiles of the outgoing scene from the top to the bottom.
    '''
    def get_action(self,x,y):
        return FadeOutDownTiles( grid=(x,y), duration=self.duration )

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
        self.add( self.in_scene, z=0)
        self.add( self.out_scene, z=1)


class FadeTransition(TransitionScene):
    '''Fade out the outgoing scene and then fade in the incoming scene.'''
    def __init__( self, *args, **kwargs ):
        super(FadeTransition, self ).__init__( *args, **kwargs)

        self.fadelayer = ColorLayer(0,0,0,0)

        self.in_scene.visible = False
        self.add( self.fadelayer, z=2 )


    def on_enter( self ):
        super( FadeTransition, self).on_enter()
        self.fadelayer.do( FadeIn( duration=self.duration/2.0) + \
                           CallFunc( self.hide_out_show_in) + \
                           FadeOut( duration=self.duration /2.0 ) + \
                           CallFunc( self.restore_out ) )
    def on_exit( self ):
        super( FadeTransition, self).on_exit()
        self.remove( self.fadelayer )

class SplitColsTransition(TransitionScene):
    '''Splits the screen in columns.
    The odd columns goes upwards while the even columns goes downwards.
    '''
    def __init__( self, *args, **kwargs ):
        super(SplitColsTransition, self ).__init__( *args, **kwargs)

        width, height = director.get_window_size()

        self.in_scene.visible = False
        flip_a =  self.get_action()
        flip = flip_a + \
                CallFunc( self.hide_out_show_in ) + \
                Reverse(flip_a) + \
                CallFunc(self.restore_out) 
        
        self.do( AccelDeccel(flip) + StopGrid() )

    def get_action( self ):
        return SplitCols( cols=3, duration=self.duration/2.0)

class SplitRowsTransition(SplitColsTransition):
    '''Splits the screen in rows.
    The odd rows goes to the left while the even rows goes to the right.
    '''
    def get_action( self ):
        return SplitRows( rows=3, duration=self.duration/2.0)
