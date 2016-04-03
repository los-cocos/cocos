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

import math
try:
    import cPickle as pickle
except ImportError:
    import pickle

import cocos
from cocos import euclid

import pyglet
from pyglet  import gl

import copy


class Skin(cocos.cocosnode.CocosNode):
    def __init__(self, skeleton):
        super(Skin, self).__init__()
        self.skeleton = skeleton


class ColorSkin(Skin):
    def __init__(self, skeleton, color):
        super(ColorSkin, self).__init__(skeleton)
        self.color = color

    def draw(self):
        self.skeleton.propagate_matrix()
        gl.glPushMatrix()
        self.transform()
        self.skeleton.visit_children(lambda bone: self.draw_bone(bone))
        bones = self.skeleton.visit_children(
            lambda bone: (bone.label, bone.parent_matrix * bone.matrix))
        bones = dict(bones)
        gl.glPopMatrix()

    def draw_bone(self, bone):
        p1 = bone.get_start()
        p2 = bone.get_end()

        gl.glColor4ub(*self.color)
        gl.glLineWidth(5)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(*p1)
        gl.glVertex2f(*p2)
        gl.glEnd()


class BitmapSkin(Skin):
    skin_parts = []

    def __init__(self, skeleton, skin_def, alpha=255):
        super(BitmapSkin, self).__init__(skeleton)
        self.alpha = alpha
        self.skin_parts = skin_def
        self.regenerate()

    def move(self, idx, dx, dy):
        sp = self.skin_parts
        pos = sp[idx][1]
        sp[idx] = sp[idx][0], (pos[0] + dx, pos[1] + dy), sp[idx][2], \
            sp[idx][3], sp[idx][4], sp[idx][5]
        self.regenerate()

    def get_control_points(self):
        return [(i, p[0]) for i, p in enumerate(self.skin_parts)]

    def regenerate(self):
        # print self.skin_parts
        self.parts = [(name, position, scale,
                      pyglet.resource.image(image, flip_y=flip_y, flip_x=flip_x))
                      for name, position, image, flip_x, flip_y, scale
                      in self.skin_parts]

    def draw(self):
        self.skeleton.propagate_matrix()
        gl.glPushMatrix()
        self.transform()

        bones = self.skeleton.visit_children(
            lambda bone: (bone.label, bone.parent_matrix * bone.matrix))
        bones = dict(bones)

        for bname, position, scale, image in self.parts:
            matrix = bones[bname]
            self.blit_image(matrix, position, scale, image)
        gl.glPopMatrix()

    def blit_image(self, matrix, position, scale, image):
        x, y = image.width * scale, image.height * scale
        # dx = self.x + position[0]
        # dy = self.y + position[1]
        dx, dy = position
        gl.glEnable(image.target)
        gl.glBindTexture(image.target, image.id)
        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # blit img
        points = [
            (-dx, -dy),
            (x - dx, -dy),
            (x - dx, y - dy),
            (-dx, y - dy)
            ]
        a, b, _, c, d, _, e, f, _, g, h, _ = image.texture.tex_coords
        textures = [a, b, c, d, e, f, g, h]
        np = [matrix * euclid.Point2(*p) for p in points]

        gl.glColor4ub(255, 255, 255, self.alpha)
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(a, b)
        gl.glVertex2f(*np[0])
        gl.glTexCoord2f(c, d)
        gl.glVertex2f(*np[1])
        gl.glTexCoord2f(e, f)
        gl.glVertex2f(*np[2])
        gl.glTexCoord2f(g, h)
        gl.glVertex2f(*np[3])
        gl.glEnd()
        gl.glColor4ub(255, 255, 255, 255)
        # pyglet.graphics.draw(4, GL_QUADS,
        #     ("v2f", new_points),
        #     ("t2f", textures),
        #     ("c4B", [255, 255, 255, self.alpha] * 4),
        #     )

        gl.glPopAttrib()
        gl.glDisable(image.target)

    def flip(self):
        nsp = []
        for name, position, image, flip_x, flip_y, scale in self.skin_parts:
            im = pyglet.resource.image(image, flip_y=flip_y, flip_x=flip_x)
            x = im.width*scale - position[0]
            y = position[1]
            nsp.append((name, (x, y), image, not flip_x, flip_y, scale))
        self.skin_parts = nsp
        self.regenerate()
        self.skeleton = self.skeleton.flipped()


class Animate(cocos.actions.IntervalAction):
    def init(self, animation, recenter=False, recenter_x=False, recenter_y=False):
        if recenter:
            recenter_x = recenter_y = True
        self.recenter_x = recenter_x
        self.recenter_y = recenter_y
        self.duration = animation.get_duration()
        self.animation = animation

    def start(self):
        nsk = copy.deepcopy(self.target.skeleton)
        if self.recenter_x:
            self.target.x += nsk.translation.x
            nsk.translation.x = 0
        if self.recenter_y:
            self.target.y += nsk.translation.y
            nsk.translation.y = 0

        self.start_skeleton = nsk

    def update(self, t):
        self.animation.pose(self.target.skeleton, t, self.start_skeleton)

    def __reversed__(self):
        raise NotImplementedError("gimme some time")


class Skeleton(object):
    def __init__(self, bone):
        super(Skeleton, self).__init__()
        self.bone = bone
        self.matrix = euclid.Matrix3.new_identity()
        self.translation = euclid.Vector2(0, 0)

    def flipped(self):
        sk = Skeleton(self.bone.flipped())
        sk.translation.x = -self.translation.x
        sk.translation.y = self.translation.y
        sk.matrix = euclid.Matrix3.new_translate(*sk.translation)
        return sk

    def save(self, name):
        f = open(name, "wb")
        pickle.dump(self, f)
        f.close()

    def move(self, dx, dy):
        self.matrix.translate(dx, dy)
        self.translation.x += dx
        self.translation.y += dy

    def propagate_matrix(self):
        def visit(matrix, child):
            child.parent_matrix = matrix
            matrix = matrix * child.matrix
            for c in child.children:
                visit(matrix, c)
        visit(self.matrix, self.bone)

    def visit_children(self, func):
        result = []

        def inner(bone):
            result.append(func(bone))
            for b in bone.children:
                inner(b)
        inner(self.bone)
        return result

    def get_control_points(self):
        points = [self]
        self.propagate_matrix()
        points += self.visit_children(lambda bone: bone)
        return points

    def interpolated_to(self, next, delta):
        sk = Skeleton(self.bone.interpolated_to(next.bone, delta))
        sk.translation = (next.translation - self.translation) * delta + self.translation
        sk.matrix = euclid.Matrix3.new_translate(*sk.translation)
        return sk

    def pose_from(self, other):
        self.matrix = other.matrix
        self.translation = other.translation
        self.bone = copy.deepcopy(other.bone)


class Bone(object):
    def __init__(self, label, size, rotation, translation):
        self.size = size
        self.label = label
        self.children = []
        self.matrix = euclid.Matrix3.new_translate(*translation) * \
            euclid.Matrix3.new_rotate(math.radians(rotation))
        self.parent_matrix = euclid.Matrix3.new_identity()
        self.translation = euclid.Point2(*translation)
        self.rotation = math.radians(rotation)

    def move(self, dx, dy):
        self.translation.x += dx
        self.translation.y += dy
        self.matrix = euclid.Matrix3.new_translate(*self.translation) * \
            euclid.Matrix3.new_rotate(self.rotation)

    def flipped(self):
        bone = Bone(self.label, self.size, -math.degrees(self.rotation),
                    (-self.translation[0], self.translation[1]))
        for b in self.children:
            bone.add(b.flipped())
        return bone

    def rotate(self, angle):
        self.rotation += angle
        self.matrix.rotate(angle)

    def add(self, bone):
        self.children.append(bone)
        return self

    def get_end(self):
        return self.parent_matrix * self.matrix * euclid.Point2(0, -self.size)

    def get_start(self):
        return self.parent_matrix * self.matrix * euclid.Point2(0, 0)

    def interpolated_to(self, next, delta):
        ea = next.rotation % (math.pi*2)
        sa = self.rotation % (math.pi*2)

        angle = ((ea % (math.pi*2)) - (sa % (math.pi*2)))

        if angle > math.pi:
            angle += -math.pi * 2

        if angle < -math.pi:
            angle += math.pi * 2

        nr = (sa + angle*delta) % (math.pi*2)
        nr = math.degrees(nr)
        bone = Bone(self.label, self.size, nr, self.translation)
        for i, c in enumerate(self.children):
            nc = c.interpolated_to(next.children[i], delta)
            bone.add(nc)
        return bone

    def dump(self, depth=0):
        print("-" * depth, self)
        for c in self.children:
            c.dump(depth + 1)

    def repr(self, depth=0):
        repr = " "*depth*4 + "Bone('%s', %s, %s, %s)" % (
            self.label, self.size, math.degrees(self.rotation), self.translation)
        for c in self.children:
            repr += " "*depth*4 + ".add(\n" + c.repr(depth+1) + ")"
        repr += "\n"
        return repr


class Animation(object):
    def __init__(self, skeleton):
        self.frames = {}
        self.position = 0
        self.skeleton = skeleton

    def flipped(self):
        c = copy.deepcopy(self)
        for t, sk in c.frames.items():
            c.frames[t] = sk.flipped()
        return c

    def pose(self, who, t, start):
        dt = t * self.get_duration()
        self.position = dt
        ct, curr = self.get_keyframe()

        # print who.tranlation
        # if we are in a keyframe, pose that
        if curr:
            who.pose_from(curr)
            return

        # find previous, if not, use start
        pt, prev = self.get_keyframe(-1)
        if not prev:
            prev = start
            pt = 0

        # find next, if not, pose at prev
        nt, next = self.get_keyframe(1)
        if not next:
            who.pose_from(prev)
            return

        # we find the dt betwen prev and next and pose from it
        ft = (nt-dt) / (nt-pt)

        who.pose_from(next.interpolated_to(prev, ft))

    def get_duration(self):
        if self.frames:
            return max(max(self.frames), self.position)
        else:
            return self.position

    def get_markers(self):
        return self.frames.keys()

    def get_position(self):
        return self.position

    def get_keyframe(self, offset=0):
        if offset == 0:
            if self.position in self.frames:
                return self.position, self.frames[self.position]
            else:
                return None, None
        elif offset < 0:
            prevs = [t for t in self.frames if t < self.position]
            prevs.sort()
            if abs(offset) <= len(prevs):
                return prevs[offset], self.frames[prevs[offset]]
            else:
                return None, None
        elif offset > 0:
            next = [t for t in self.frames if t > self.position]
            next.sort()
            if abs(offset) <= len(next):
                return next[offset - 1], self.frames[next[offset - 1]]
            else:
                return None, None

    def next_keyframe(self):
        next = [t for t in self.frames if t > self.position]
        if not next:
            return False
        self.position = min(next)
        return True

    def prev_keyframe(self):
        prevs = [t for t in self.frames if t < self.position]
        if not prevs:
            return False
        self.position = max(prevs)
        return True

    def move_position(self, delta):
        self.position = max(self.position + delta, 0)
        return True

    def move_start(self):
        self.position = 0
        return True

    def move_end(self):
        if self.frames:
            self.position = max(self.frames)
        else:
            self.position = 0
        return True

    def insert_keyframe(self):
        if self.position not in self.frames:
            t, sk = self.get_keyframe(-1)
            if not sk:
                sk = self.skeleton
            self.frames[self.position] = copy.deepcopy(sk)
            return True
        return False

    def remove_keyframe(self):
        if self.position in self.frames:
            del self.frames[self.position]
            return True
        return False

    def insert_time(self, delta):
        new_frames = {}
        for t, sk in sorted(self.frames.items()):
            if t >= self.position:
                t += delta
            new_frames[t] = sk
        self.frames = new_frames

    def delete_time(self, delta):
        for t in self.frames:
            if self.position <= t < self.position + delta:
                return False

        new_frames = {}
        for t, sk in sorted(self.frames.items()):
            if t > self.position:
                t -= delta
            new_frames[t] = sk
        self.frames = new_frames
