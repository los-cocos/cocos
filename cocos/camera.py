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
"""Camera object"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

from pyglet import gl

from cocos.director import director
from cocos.euclid import Point3

__all__ = ['Camera']


class Camera(object):
    """
    Camera used in every `CocosNode`.
    Useful to look at the object from different views.
    The OpenGL gluLookAt() function is used to locate the
    camera.

    If the object is transformed by any of the scale, rotation or
    position attributes, then they will override the camera.
    """

    def __init__(self):
        self.restore()

    @classmethod
    def get_z_eye(cls):
        """Returns the best distance for the camera for the current window size

        cocos2d uses a Filed Of View (fov) of 60
        """
        width, height = director.get_window_size()
        eye_z = height / 1.1566
        return eye_z

    def restore(self):
        """Restore the camera to the initial position
        and sets it's ``dirty`` attribute in False and ``once`` in true.

        If you use the camera, for a while and you want to stop using it
        call this method.
        """

        width, height = director.get_window_size()

        # tuple (x,y,z) that says where is the eye of the camera.
        # used by ``gluLookAt()``
        self._eye = Point3(width / 2.0, height / 2.0, self.get_z_eye())

        # tuple (x,y,z) that says where is pointing to the camera.
        # used by ``gluLookAt()``
        self._center = Point3(width / 2.0, height / 2.0, 0.0)

        # tuple (x,y,z) that says the up vector for the camera.
        # used by ``gluLookAt()``
        self._up_vector = Point3(0.0, 1.0, 0.0)

        #: whether or not the camera is 'dirty'
        #: It is dirty if it is not in the original position
        self.dirty = False

        #: optimization. Only renders the camera once
        self.once = False

    def locate(self, force=False):
        """Sets the camera using gluLookAt using its eye, center and up_vector

        :Parameters:
            `force` : bool
                whether or not the camera will be located even if it is not dirty
        """
        if force or self.dirty or self.once:
            gl.glLoadIdentity()
            gl.gluLookAt(self._eye.x, self._eye.y, self._eye.z,             # camera eye
                      self._center.x, self._center.y, self._center.z,    # camera center
                      self._up_vector.x, self._up_vector.y, self._up_vector.z  # camera up vector
                      )
            self.once = False

    def _get_eye(self):
        return self._eye

    def _set_eye(self, eye):
        self._eye = eye
        self.dirty = True

    eye = property(_get_eye, _set_eye, doc='''Eye of the camera in x,y,z coordinates

    :type: flaat,float,float
    ''')

    def _get_center(self):
        return self._center

    def _set_center(self, center):
        self._center = center
        self.dirty = True

    center = property(_get_center, _set_center, doc='''Center of the camera in x,y,z coordinates

    :type: flaat,float,float
    ''')

    def _get_up_vector(self):
        return self._up_vector

    def _set_up_vector(self, up_vector):
        self._up_vector = up_vector
        self.dirty = True

    up_vector = property(_get_up_vector, _set_up_vector, doc='''Up vector of the camera in x,y,z coordinates

    :type: flaat,float,float
    ''')
