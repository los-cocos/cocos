# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
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
from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
#

import math
from math import pi, atan

try:
    import cPickle as pickle
except ImportError:
    import pickle

import glob
from optparse import OptionParser

import pyglet
from pyglet.gl import *
from pyglet.window import key

import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.actions import CallFuncS, CallFunc, IntervalAction
from cocos import euclid


import ui
from cocos.skeleton import Bone, Skeleton, Skin, Animation, Animate, BitmapSkin, \
    ColorSkin

def flatten( l ):
    res = []
    for e in l:
        res += list(e)
    return res

def v2a(x,y):
    if x == 0:
        if y > 0:
            return pi / 2
        elif (y < 0):
            return -pi / 2
        else:
            return 0
    elif y == 0:
        if x > 0:
            return 0
        else:
            return pi
    else:
        if x < 0:
            if y > 0:
                return atan(y / x) + pi
            else:
                return atan(y / x) - pi
        else:
            return atan( y / x )

class UpdateTimeline(cocos.actions.IntervalAction):
    def init(self, duration):
        self.duration = duration

    def update(self, t):
        self.target.position = self.duration * t

    def __reversed__(self):
        raise NotImplementedError("gimme some time")




class BoneControl(ui.BallWidget):
    def __init__(self, bone, delta):
        super(BoneControl, self).__init__(7, (255,0,0,255))
        self.bone = bone
        self.position = bone.get_end()+euclid.Point2(*delta)
        self.delta = delta

    def on_dragged(self, dx, dy):
        super(BoneControl, self).on_dragged(dx, dy)
        def angle_between( v1, v2 ):
            v1 = v1.normalized()
            v2 = v2.normalized()
            a1 = v2a( *v1 )
            a2 = v2a( *v2 )
            return a2-a1

        o = self.bone.get_start()
        e = self.bone.get_end()
        ne = euclid.Point2(
            self.x + dx -self.delta[0],
            self.y + dy - self.delta[1] )
        v1 = euclid.Point2( *(e-o) )
        v2 = euclid.Point2( *(ne-o) )

        alpha = angle_between(v1, v2)
        self.bone.rotate( alpha )

class SkeletonControl(ui.BallWidget):
    def __init__(self, skeleton, position):
        super(SkeletonControl, self).__init__(7, (0,0,255,255))
        self.skeleton = skeleton
        self.position = position+skeleton.translation

    def on_dragged(self, dx, dy):
        super(SkeletonControl, self).on_dragged(dx, dy)
        self.skeleton.move(dx, dy)


class BoneUILayer(ui.UILayer):
    def __init__(self, skeleton, savefile_name, skin=False):
        super(BoneUILayer, self).__init__()
        self.user_skin = skin
        self.count = 0
        self.savefile_name = savefile_name
        try:
            self.animation = pickle.load( open(savefile_name, "rb") )
        except IOError:
            self.animation = Animation(skeleton)
        self.timeline = ui.TimeLine(self.animation)
        self.add(self.timeline)
        self.tick_delta = 1.0 / 16
        self.skeleton = skeleton
        self.editable_skeleton = None
        self.animating = False
        self.animation.move_start()
        self.update_visual()
        
    def save(self):
        pickle.dump(self.animation, open(self.savefile_name,"wb") )

    def start_animation(self):
        self.clean_skins()
        self.animating = True
        self.clean_control_points()
        if self.user_skin:
            skin = BitmapSkin(self.skeleton, self.user_skin)
        else:
            skin = ColorSkin( self.skeleton, (255,255,255,255))
        self.add( skin )
        xs, ys = director.get_window_size()
        skin.position = xs / 2-6, ys / 2 - 11
        self.animation.move_start()
        skin.do( Animate(self.animation)
                 + CallFunc(lambda: self.remove(skin))
                 + CallFunc(self.stop_animation) )
        skin.do( UpdateTimeline(self.animation.get_duration()), target=self.animation)

    def stop_animation(self):
        self.animating = False
        self.update_visual()

    def add_skin_for_skeleton(self, skeleton, color, z=-1, editable=False):
        if self.user_skin:
            skin = BitmapSkin(skeleton, self.user_skin, alpha=color[3])
        else:
            skin = ColorSkin(skeleton, color)
        self.skin = skin
        self.add( skin, z=z )
        xs, ys = director.get_window_size()
        skin.position = xs / 2 - 6, ys / 2 - 11
        if editable:
            self.editable_skeleton = skeleton
            self.editable_skin = skin
            self.generate_control_points()

    def on_key_press(self, k, mods):
        if not self.animating:
            if k == key.S:
                self.save()
                self.count += 1
            elif k == key.LEFT:
                self.animation.move_position( -self.tick_delta )
            elif k == key.RIGHT:
                self.animation.move_position( self.tick_delta )
            elif k in (key.PLUS, key.NUM_ADD):
                self.animation.insert_keyframe()
            elif k in (key.MINUS, key.NUM_SUBTRACT):
                self.animation.remove_keyframe()
            elif k == key.PAGEDOWN:
                self.animation.next_keyframe()
            elif k == key.PAGEUP:
                self.animation.prev_keyframe()
            elif k == key.INSERT:
                self.animation.insert_time( self.tick_delta )
            elif k == key.DELETE:
                self.animation.delete_time( self.tick_delta )
            elif k == key.HOME:
                self.animation.move_start()
            elif k == key.END:
                self.animation.move_end()
            self.update_visual()

            if k == key.SPACE:
                self.start_animation()

        else:
            # what to do when animating
            pass



    def update_visual(self):
        self.editable_skeleton = None
        self.clean_control_points()
        self.clean_skins()

        _, curr = self.animation.get_keyframe()
        _, prev = self.animation.get_keyframe(-1)
        _, prev2 = self.animation.get_keyframe(-2)
        _, next = self.animation.get_keyframe(1)

        if curr:
            self.add_skin_for_skeleton(curr, (255,255,255,255), -1, True)
        if prev:
            self.add_skin_for_skeleton(prev, (255,255,255,32), -2)
        if prev2:
            self.add_skin_for_skeleton(prev2, (255,255,255,16), -3)
        if next:
            self.add_skin_for_skeleton(next, (0,0,255,32), -2)

    def clean_control_points(self):
        cps = [ cp for cp in self.get_children() if isinstance(cp, ui.BallWidget) ]
        for cp in cps:
            self.remove(cp)

    def clean_skins(self):
        skins = [ cp for cp in self.get_children() if isinstance(cp, Skin) ]
        for skin in skins:
            self.remove(skin)

    def on_mouse_release(self, *args):
        if self.dragging:
            self.clean_control_points()
            self.generate_control_points()
        super(BoneUILayer, self).on_mouse_release(*args)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.hovering:
            cps = [ cp for cp in self.get_children()
                    if isinstance(cp, ui.BallWidget) and cp != self.hovering ]
            for cp in cps:
                self.remove(cp)
        super(BoneUILayer, self).on_mouse_drag(x, y, dx, dy, button, modifiers)

    def generate_control_points(self):
        if self.editable_skeleton:
            skinpos = euclid.Point2(*self.editable_skin.position)
            for cp in self.editable_skeleton.get_control_points():
                if isinstance(cp, Skeleton):
                    self.add( SkeletonControl(cp, skinpos) )
                else:
                    self.add( BoneControl(cp, skinpos) )

class Editor(cocos.scene.Scene):
    def __init__(self, skeleton, savefile_name, skin=False):
        super(Editor, self).__init__()
        self.ui = BoneUILayer(skeleton, savefile_name, skin)
        self.add(self.ui)




if __name__ == "__main__":
    import sys, imp
    director.init()

    parser = OptionParser()
    parser.add_option("-b", "--background", dest="background",
                  help="use file as background", default=False, metavar="FILE")
    parser.add_option("-s", "--scale", dest="scale",
                  help="scale image by", default=1, metavar="SCALE")
    parser.add_option("-k", "--skin", dest="skin",
                  help="use skin file for skin", default=False, metavar="FILE")


    (options, args) = parser.parse_args()


    def usage():
        return "python animator.py skeleton.py animation_file.anim"
    if len(args)!=2:
        print(usage())
        print(parser.error("incorrect number of arguments"))
        sys.exit()

    sk_file = imp.load_source("skeleton", args[0])

    if options.skin:
        skin_data = imp.load_source("skin", options.skin).skin
        options.skin = skin_data

    animator = Editor(sk_file.skeleton, args[1], options.skin)
    if options.background:
        background = cocos.sprite.Sprite(options.background)
        x,y = director.get_window_size()
        animator.add( background, z=-10 )
        background.position = x / 2, y / 2
        background.scale = float(options.scale)

    director.run(animator)
