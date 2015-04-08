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

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
#
import math
from math import pi, atan

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

from animator import *
import ui
from cocos.skeleton import Bone, Skeleton, Skin, Animation, Animate, ColorSkin, \
    BitmapSkin

class SkinControl(ui.BallWidget):
    def __init__(self, skin, idx, bone, delta):
        super(SkinControl, self).__init__(7, (0,0,255,255))
        self.skin = skin
        self.idx = idx
        self.bone = bone
        self.position = (bone.get_start()+bone.get_end())/2 + delta

    def on_dragged(self, dx, dy):
        super(SkinControl, self).on_dragged(dx, dy)
        self.skin.move(self.idx, dx, dy)

class BonePositionControl(ui.BallWidget):
    def __init__(self, bone, delta):
        super(BonePositionControl, self).__init__(10, (0,255,0,255))
        self.bone = bone
        self.position = (bone.get_start()) + delta

    def on_dragged(self, dx, dy):
        super(BonePositionControl, self).on_dragged(dx, dy)
        self.bone.move(dx, dy)


class SkeletonEditorUI(ui.UILayer):
    def __init__(self, skeleton, skin):
        super(SkeletonEditorUI, self).__init__()

        sk_file = imp.load_source("skeleton", args[0])
        if skin is None:
            self.user_skin = None
        else:
            skin_data = imp.load_source("skin", args[1]).skin
            self.skin_filename = skin
            self.user_skin = skin_data
        self.skeleton_file = skeleton
        self.skeleton = sk_file.skeleton
        
        self.add_skin_for_skeleton(self.skeleton, (255,255,255,255))


    def add_skin_for_skeleton(self, skeleton, color, z=-1, editable=False):
        if self.user_skin:
            skin = BitmapSkin(skeleton, self.user_skin, color[3])
        else:
            skin = ColorSkin(skeleton, color)
        self.skin = skin
        self.add( skin, z=z )
        xs, ys = director.get_window_size()
        skin.position = xs / 2 - 6, ys / 2 - 11
        self.generate_control_points()

    def on_key_press(self, k, mod):
        if k == key.S:
            f = open(self.skin_filename, "wt")
            f.write("\nskin = [\n")
            for p in self.skin.skin_parts:
                f.write("    %s,\n"%(p,))
            f.write("  ]\n")

            f.close()

            f = open(self.skeleton_file, "wt")
            f.write("""from cocos.skeleton import Bone, Skeleton\n
def Point2(*args): return args\n
root_bone = %s

skeleton = Skeleton( root_bone )"""%self.skeleton.bone.repr())
            f.close()

    def update_visual(self):
        self.add_skin_for_skeleton(self.skeleton, -1, True)

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
        super(SkeletonEditorUI, self).on_mouse_release(*args)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.hovering:
            cps = [ cp for cp in self.get_children()
                    if isinstance(cp, ui.BallWidget) and cp != self.hovering ]
            for cp in cps:
                self.remove(cp)
        super(SkeletonEditorUI, self).on_mouse_drag(x, y, dx, dy, button, modifiers)

    def generate_control_points(self):
        skinpos = euclid.Point2(*self.skin.position)
        for cp in self.skeleton.get_control_points():
            if isinstance(cp, Skeleton):
                self.add( SkeletonControl(cp, skinpos), z=3 )
            else:
                self.add( BoneControl(cp, skinpos), z=4 )
        bones = self.skeleton.visit_children(lambda bone: (bone.label, bone))
        bones = dict(bones)
        for bone in bones.values():
            self.add( BonePositionControl( bone, skinpos ), z=2 )
        for idx, name in self.skin.get_control_points():
            self.add( SkinControl(self.skin, idx, bones[name], skinpos ), z=5)




if __name__ == "__main__":
    import sys, imp
    director.init()

    parser = OptionParser()
    parser.add_option("-b", "--background", dest="background",
                  help="use file as background", default=False, metavar="FILE")
    parser.add_option("-s", "--scale", dest="scale",
                  help="scale image by", default=1, metavar="SCALE")


    (options, args) = parser.parse_args()


    def usage():
        return "python animator.py skeleton.py skin.py"
    if len(args) not in [2]:
        print(usage())
        print(parser.error("incorrect number of arguments"))
        sys.exit()
        

    animator = cocos.scene.Scene(SkeletonEditorUI(args[0], args[1]))
    if options.background:
        background = cocos.sprite.Sprite(options.background)
        x,y = director.get_window_size()
        animator.add( background, z=-10 )
        background.position = x / 2, y / 2
        background.scale = float(options.scale)

    director.run(animator)
