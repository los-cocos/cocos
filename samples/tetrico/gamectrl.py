from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# stdlib
import copy
import random

# pyglet related
import pyglet
from pyglet.window import key

# cocos2d related
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.euclid import Point2

# tetrico related
from constants import *
from status import status

__all__ = ['GameCtrl']

#
# Controller ( MVC )
#

class GameCtrl( Layer ):

    is_event_handler = True #: enable pyglet's events

    def __init__(self, model):
        super(GameCtrl,self).__init__()

        self.used_key = False
        self.paused = True

        self.model = model
        self.elapsed = 0

    def on_key_press(self, k, m ):
        if self.paused:
            return False

        if self.used_key:
            return False

        if k in (key.LEFT, key.RIGHT, key.DOWN, key.UP, key.SPACE):
            if k == key.LEFT:
                self.model.block_left()
            elif k == key.RIGHT:
                self.model.block_right()
            elif k == key.DOWN:
                self.model.block_down()
            elif k == key.UP:
                self.model.block_rotate()
            elif k == key.SPACE:
                # let the player move the block after it was dropped
                self.elapsed = 0
                self.model.block_drop()
            self.used_key = True
            return True
        return False

    def on_text_motion(self, motion):
        if self.paused:
            return False

        if self.used_key:
            return False

        if motion in (key.MOTION_DOWN, key.MOTION_RIGHT, key.MOTION_LEFT):
            if motion == key.MOTION_DOWN:
                self.model.block_down()
            elif motion == key.MOTION_LEFT:
                self.model.block_left()
            elif motion == key.MOTION_RIGHT:
                self.model.block_right()

            self.used_key = True
            return True
        return False

    def pause_controller( self ):
        '''removes the schedule timer and doesn't handler the keys'''
        self.paused = True
        self.unschedule( self.step )

    def resume_controller( self ):
        '''schedules  the timer and handles the keys'''
        self.paused = False
        self.schedule( self.step )

    def step( self, dt ):
        '''updates the engine'''
        self.elapsed += dt
        if self.elapsed > status.level.speed:
            self.elapsed = 0
            self.model.block_down( sound=False)

    def draw( self ):
        '''draw the map and the block'''
        self.used_key = False
