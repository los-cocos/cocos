#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2009 Nicolas Rougier
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
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
# -----------------------------------------------------------------------------
'''Defines a set of basic 2D shapes.

All shapes have:
----------------

- a position in 2D space
- a dimension in 2D space
- a x alignment ('left', 'center' or 'right')
- a y alignment ('top', 'center' or 'bottom')
- background color(s)
- background texture
- foreground color(s) (for the one pixel border)

Display Model:
--------------

Any shape is defined by the x, y, width and height attributes.  Borders are
drawn on the inside of the shape as a single pixel line in the specified border
color(s). Foreground or background color can be specified as a single tuple of 4
floats for uniform color, 2 tuples of 4 floats for radial color patterns (going
from inner to outer) or 4 tuples of 4 floats for an interpolated pattern between
the four corners. Note that the radial pattern does not work for triangle or
rectangle.

Available shapes:
-----------------

- Rectangle (with round corners or not)
- Ellipse (circle if width == height)
- Triangle
- Cross (with any number of branches)
- Star (with any number of branches)


Example usage:
--------------
 
   rectangle = Rectangle(x=100,y=100,width=100,height=100,radius=10)

   @window.event
   def on_draw():
       window.clear()
       rectangle.draw()

   @window.event
   def on_mouse_press(x,y,button,modifiers):
      if rectangle.hit_test(x,y):
         print 'Hit'

:requires: pyglet 1.1
'''
__docformat__ = 'restructuredtext'
__version__ = '1.0'
import math
import pyglet
from pyglet.gl import *
from pyglet import gl


# ------------------------------------------------------------------------------
def arc_circle(x, y, r1, r2, theta1, theta2, dtheta=10):
    ''' Return a list of vertices for the specified arc circle '''

    vertices = []
    if theta2 > theta1:
        while (theta1 <= theta2):
             theta_rad = theta1*math.pi/180
             vertices.append((x+r1*math.cos(theta_rad),
                              y-r2*math.sin(theta_rad)))
             theta1 += abs(dtheta)
    else:
        while (theta1 >= theta2):
             theta_rad = theta1*math.pi/180
             vertices.append((x+r1*math.cos(theta_rad),
                              y-r2*math.sin(theta_rad)))
             theta1 -= abs(dtheta)
    return vertices



# ------------------------------------------------------------------------------
class Shape(object):
    ''' Abstract shape.

    This is the common abstract class for all shape.
    '''

    # _________________________________________________________________ __init__
    def __init__(self, x=0, y=0, z=0, width=100, height=100,
                 foreground=(1.0,1.0,1.0,1.0), background=(1.0,1.0,1.0,0.25),
                 anchor_x='left', anchor_y='bottom', rotation=0,
                 texture = None, *args, **kwargs):
        '''Create a displayable shape.

        :Parameters:
            `x` : float
                X coordinate of the left edge of the shape.
            `y` : float
                Y coordinate of the top edge of the shape.
            `z` : float
                Z coordinate of the shape plane.
            `width` : int
                Width of the shape.
            `height` : int
                Height of the shape.
            `rotation` : float
                Rotation (degrees) of the shape around center.
            `foreground` : 4-tuple of float or 4x4-tuples of float
                Color(s) to render the shape border in. Alpha values can be
                specified in the fourth component.
            `background` : 4-tuple of float or 4x4-tuples of float
                Color(s) to render the shape interior in. Alpha values can be
                specified in the fourth component.
            `anchor_x` : str
                Horizontal alignment of the shape.
                See `Shape.anchor_x` for details.
            `anchor_y` : str
                Vertical alignment of the shape.
                See `Shape.anchor_y` for details.
        '''

        self._background_list = pyglet.graphics.vertex_list(1,'v2f','c4f','t2f')
        self._foreground_list = pyglet.graphics.vertex_list(1,'v2f','c4f')
        self._fill_mode = GL_POLYGON
        self._line_mode = GL_LINE_LOOP
        self._texture = texture
        self._x = x
        self._y = y
        self._z = z
        self._root_x = 0
        self._root_y = 0
        self._root_z = 0
        self._width = width
        self._height = height
        self._rotation = rotation
        self._foreground = foreground
        self._background = background
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y

    # __________________________________________________________________ __str__
    def __str__(self):
        s = '<Shape %dx%d+%d+%d>' % (self._width,self._height,self._x, self._y)
        return s

    # ________________________________________________________________________ x
    def _get_x(self):
        return self._x
    def _set_x(self, x):
        self._x = x
        self._update_position()
    x = property(_get_x, _set_x,
        doc='''Y coordinate of the shape.

        :type: int
        ''')

    # ________________________________________________________________________ y
    def _get_y(self):
        return self._y
    def _set_y(self, y):
        self._y = y
        self._update_position()
    y = property(_get_y, _set_y,
        doc='''Y coordinate of the shape.

        :type: int
        ''')

    # ________________________________________________________________________ z
    def _get_z(self):
        return self._z
    def _set_z(self, z):
        self._z = z
        self._update_position()
    z = property(_get_z, _set_z,
        doc='''Z coordinate of the shape.

        :type: int
        ''')
    
    # ____________________________________________________________________ width
    def _get_width(self):
        return self._width
    def _set_width(self, width):
        self._width = width
        self._update_shape()
    width = property(_get_width, _set_width, 
        doc='''Width of the shape.

        :type: int
        ''')

    # ___________________________________________________________________ height
    def _get_height(self):
        return self._height
    def _set_height(self, height):
        self._height = height
        self._update_shape()
    height = property(_get_height, _set_height,
        doc='''Height of the shape.
        
        :type: int
        ''')

    # _______________________________________________________________ foreground
    def _get_foreground(self):
        return self._foreground
    def _set_foreground(self, color):
        self._foreground = color
        self._update_shape()
    foreground = property(_get_foreground, _set_foreground,
         doc='''Color to render the shape border in.

         Alpha values can be specified in the fourth component.

         :type: tuple
         ''')

    # _______________________________________________________________ background
    def _get_background(self):
        return self._background
    def _set_background(self, color):
        self._background = color
        self._update_shape()
    background = property(_get_background, _set_background,
        doc='''Color to render the shape interior in.

        Alpha values can be specified in the fourth component.

        :type: tuple
        ''')

    # _________________________________________________________________ anchor_x
    def _get_anchor_x(self):
        return self._anchor_x
    def _set_anchor_x(self, anchor_x):
        self._anchor_x = anchor_x
        self._update_position()
    anchor_x = property(_get_anchor_x, _set_anchor_x,
        doc='''Horizontal alignment of the shape.

        The shape is positioned relative to `x` and `width` according to this
        property, which must be one of the alignment constants `LEFT`,
        `CENTER` or `RIGHT`.

        :type: str
        ''')

    # _________________________________________________________________ anchor_y
    def _get_anchor_y(self):
        return self._anchor_y
    def _set_anchor_y(self, anchor_y):
        self._anchor_y = anchor_y
        self._update_position()
    anchor_y = property(_get_anchor_y, _set_anchor_y,
        doc='''Vertical alignment of the shape.

        The shape is positioned relative to `y` according to this property,
        which must be one of the alignment constants `BOTTOM`, `CENTER`
        or `TOP`.

        :type: str
        ''')

    # _________________________________________________________________ rotation
    def _get_rotation(self):
        return self._rotation
    def _set_rotation(self, color):
        self._rotation = color
    rotation = property(_get_rotation, _set_rotation,
         doc='''Rotation (degrees) around center  of the shape.

         :type: float
         ''')

    # __________________________________________________________________ texture
    def _get_texture(self):
        return self._texture
    def _set_texture(self, texture):
        self._texture = texture
    background = property(_get_texture, _set_texture,
        doc='''Texture to render the shape interior 

        :type: pyglet texture object
        ''')

    # _________________________________________________________ _update_position
    def _update_position(self):
        ''' '''

        if self.anchor_x == 'center':
            self._root_x = self.x-self.width/2
        elif self.anchor_x == 'right':
            self._root_x = self.x-self.width
        else:
            self._root_x = self.x

        if self.anchor_y == 'center':
            self._root_y = self.y-self.height/2
        elif self.anchor_y == 'top':
            self._root_y = self.y-self.height
        else:
            self._root_y = self.y

    # ____________________________________________________________ _update_shape
    def _update_shape(self):
        ''' '''

        def interpolate(x,y,c0,c1,c2=None,c3=None):
            c = [0,0,0,0]
            if not c2:
                for i in range(4):
                    d = math.sqrt((x-0.5)*(x-0.5)+(y-0.5)*(y-0.5))*math.sqrt(2)
                    c[i] = d*c0[i]+(1-d)*c1[i]
            else:
                for i in range(4):
                    c[i] = x*(y*c0[i]+(1-y)*c3[i])+(1-x)*(y*c1[i]+(1-y)*c2[i])
            return c

        foreground_vertices, background_vertices = self.generate_vertices()
        x,y,w,h = 0, 0, float(self._width-1), float(self._height-1)
        if type(self._foreground[0]) in [list,tuple]:
            if len(self._foreground) == 2:
                f0,f1 = self._foreground
                f2,f3 = None,None
            else:
                f0,f1,f2,f3 = self._foreground
        else:
            f0=f1=f2=f3= self._foreground
        if type(self._background[0]) in [list,tuple]:
            if len(self._background) == 2:
                b0,b1 = self._background
                b2,b3 = None,None
            else:
                b0,b1,b2,b3 = self._background
        else:
            b0=b1=b2=b3 = self._background
        self._background_list.resize(len(background_vertices))
        self._foreground_list.resize(len(foreground_vertices))
        c,p = [],[]
        for v in foreground_vertices:
            p += v
            c += interpolate( (v[0]-x)/w, (v[1]-y)/h, f0,f1,f2,f3)
        self._foreground_list.vertices = p
        self._foreground_list.colors = c
        c,p,t = [],[],[]
        for v in background_vertices:
            p += v
            t += [(v[0]-x)/w, (v[1]-y)/h,]
            c += interpolate( (v[0]-x)/w, (v[1]-y)/h, b0,b1,b2,b3)
        self._background_list.vertices = p
        self._background_list.tex_coords = t
        self._background_list.colors = c

    # _________________________________________________________________ hit_test
    def hit_test(self, x, y):
        ''' Return whether (x,y) is inside shape

        The hit test is done using the select mode of OpenGL which may be
        rather costly for a unique shape. It is best to use this method
        once for a set of shapes.
        '''

        projection = (GLfloat*16)()
        glGetFloatv(GL_PROJECTION_MATRIX, projection)
        viewport = (GLint*4)()
        glGetIntegerv(GL_VIEWPORT, viewport)
        buffer = (GLuint*512)()
        glSelectBuffer(512, buffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(x, y, 1.0, 1.0, viewport)
        glMultMatrixf(projection)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.draw()
        hits = glRenderMode(GL_RENDER)
        names = [buffer[i*4+3] for i in range(hits)]
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        return id(self) in names

    # ____________________________________________________________________ draw
    def draw(self):
        ''' Draw the shape '''

        mode = GLint()
        glGetIntegerv(GL_RENDER_MODE,mode)
        mode = mode.value
        if mode == GL_SELECT:
            glPushName(id(self))
            glTranslatef(self._root_x+0.315, self._root_y+0.315, self.z)
            glRotatef(self._rotation,0,0,1)
            self._background_list.draw(self._fill_mode)
            glRotatef(-self._rotation,0,0,1)
            glTranslatef(-self._root_x-0.315, -self._root_y-0.315, -self.z)
            glPopName()
            return
        glDisable(GL_TEXTURE_2D)
        if self._texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture.id)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glTranslatef(self._root_x+0.315, self._root_y+0.315, self.z)
        glRotatef(self._rotation,0,0,1)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset (1, 1)
        self._background_list.draw(self._fill_mode)
        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth (1.0)
        self._foreground_list.draw(self._line_mode)
        glDisable(GL_LINE_SMOOTH)
        glDepthMask(GL_TRUE)
        glRotatef(-self._rotation,0,0,1)
        glTranslatef(-self._root_x-0.315, -self._root_y-0.315, -self.z)



# ------------------------------------------------------------------------------
class Rectangle(Shape):
    ''' Round rectangle shape.

    This is a class for rendering a round rectangle shape.
    '''

    # _________________________________________________________________ __init__
    def __init__(self, radius=0, *args, **kwargs):
        '''Create an (optionable) round rectangle.

        :Parameters:        
            `radius` : int or tuple of 4 int
                Radius of corners.
        '''
        self._radius = radius
        Shape.__init__(self,*args,**kwargs)
        self._update_position()
        self._update_shape()

    # __________________________________________________________________ __str__
    def __str__(self):
        s='<Rectangle %dx%d+%d+%d>' % (self._width,self._height,self._x,self._y)
        return s

    # ___________________________________________________________________ radius
    def _get_radius(self):
        return self._radius
    def _set_radius(self, radius):
        self._radius = radius
        self._update_shape()
    radius = property(_get_radius, _set_radius,
        doc='''Radius of corner(s)

        :type: int or tuple of 4 int
        ''')

    # ________________________________________________________ generate_vertices
    def generate_vertices(self):
        ''' '''

        x,y,w,h = 0,0,self._width-1,self._height-1
        if type(self._radius) in [tuple,list]:
            r = self._radius
        else:
            r = [self._radius,]*4
        vertices = []
        if r[0] != 0:
            vertices += (x,y+r[0]),
            vertices += arc_circle (x+r[0],y+r[0],r[0],r[0],-180,-270)[1:-1]
            vertices += (x+r[0], y),
        else:
            vertices += (x, y),
        if r[1] > 0:
            vertices += (x+w-r[1], y),
            vertices += arc_circle (x+w-r[1],y+r[1],r[1],r[1],90,0)[1:-1]
            vertices += (x+w, y+r[1]),
        else:
            vertices += (x+w, y),
        if r[2] > 0:
            vertices += (x+w, y+h-r[2]),
            vertices += arc_circle (x+w-r[2],y+h-r[2],r[2],r[2],0,-90)[1:-1]
            vertices += (x+w-r[2], y+h),
        else:
            vertices += (x+w, y+h),
        if r[3] > 0:
            vertices += (x+w-r[2], y+h),
            vertices += arc_circle (x+r[3],y+h-r[3],r[3],r[3],-90,-180)[1:-1]
            vertices += (x, y+h-r[2]),
        else:
            vertices += (x, y+h),
        return vertices, vertices

# ------------------------------------------------------------------------------
class Ellipse(Shape):
    ''' Ellipse shape.

    This is a class for rendering an ellipse.
    '''

    # _________________________________________________________________ __init__
    def __init__(self, theta1=0, theta2=360, *args, **kwargs):
        '''Create an ellipse '''

        self._theta1 = theta1
        self._theta2 = theta2
        Shape.__init__(self, *args, **kwargs)
        self._fill_mode = GL_TRIANGLES
        self._line_mode = GL_LINE_LOOP
        self._update_position()
        self._update_shape()

    # __________________________________________________________________ __str__
    def __str__(self):
        s = '<Ellipse %dx%d+%d+%d>' % (self._width,self._height,self._x,self._y)
        return s

    # ___________________________________________________________________ theta1
    def _get_theta1(self):
        return self._theta1
    def _set_theta1(self, theta1):
        self._theta1 = theta1
        self._update_shape()
    theta1 = property(_get_theta1, _set_theta1,
        doc='''Starting angle in degrees

        :type: float
        ''')

    # ___________________________________________________________________ theta2
    def _get_theta2(self):
        return self._theta2
    def _set_theta2(self, theta2):
        self._theta2 = theta2
        self._update_shape()
    theta2 = property(_get_theta2, _set_theta2,
        doc='''Ending angle in degrees

        :type: float
        ''')

    # ________________________________________________________ generate_vertices
    def generate_vertices(self):
        ''' '''

        x,y,w,h = 0,0,self._width-1,self._height-1
        vertices = arc_circle (x+w/2,y+h/2,w/2,h/2,self._theta1,self._theta2,5)
        v = []
        for i in range(len(vertices)-1):
            v += [vertices[i],]
            v += [vertices[i+1],]
            v += [(w/2,h/2),]
        if math.fmod(self._theta1,360) != math.fmod(self._theta2,360):
            vertices += [(w/2,h/2),]
        return vertices, v



# ------------------------------------------------------------------------------
class Triangle(Shape):
    ''' Triangle shape.

    This is a class for rendering a triangle.
    '''

    # _________________________________________________________________ __init__
    def __init__(self, direction='up', *args, **kwargs):
        '''Create an oriented triangle.

        :Parameters:
            `direction` : str
               The triangle is oriented relative to its center to this property,
               which must be one of the alignment constants `left`, `right`,
               `up` or `down`.
        '''

        self._direction = direction
        Shape.__init__(self,*args, **kwargs)
        self._update_position()
        self._update_shape()

    # __________________________________________________________________ __str__
    def __str__(self):
        s='<Triangle %dx%d+%d+%d>' % (self._width,self._height,self._x,self._y)
        return s

    # ________________________________________________________________ direction
    def _get_direction(self):
        return self._direction
    def _set_direction(self, direction):
        self._direction = direction
        self._update_shape()
    direction = property(_get_direction, _set_direction,
        doc='''Direction of triangle.

        The triangle is oriented relative to its center to this property,
        which must be one of the alignment constants `left`, `right`, `up`
        or `down`.

        :type: str
        ''')

    # ________________________________________________________ generate_vertices
    def generate_vertices(self):
        ''' '''

        x,y,w,h = 0,0,self._width-1,self._height-1
        if self._direction == 'left':
            vertices = [(x,y), (x,y+h), (x+w,y+h/2)]
        elif self._direction == 'right':
            vertices = [(x+w,y), (x+w,y+h), (x,y+h/2)]
        elif self._direction == 'down':
            vertices = [(x,y+h), (x+w,y+h), (x+w/2,y)]
        else:
            vertices = [(x,y), (x+w,y), (x+w/2,y+h)]
        return vertices, vertices



# ------------------------------------------------------------------------------
class Cross(Shape):
    ''' Cross shape.

    This is a class for rendering a cross.
    '''

    def __init__(self, thickness=0.5, branches=5, *args, **kwargs):
        '''Create a cross.

        :Parameters:
            `thickness` : float
                Thickness of the cross
            `branches` : int
                Number of branches
        '''
        self._thickness = thickness
        self._branches = branches
        Shape.__init__(self, *args, **kwargs)
        self._fill_mode = GL_QUADS
        self._update_position()
        self._update_shape()

    def __str__(self):
        s = '<Cross %dx%d+%d+%d>' % (self._width,self._height,self._x, self._y)
        return s

    def _get_branches(self):
        return self._branches
    def _set_branches(self, branches):
        self._branches = branches
        self._update_shape()
    branches = property(_get_branches, _set_branches,
        doc='''Number of branches of the cross.

        :type: int 
        ''')

    def _get_thickness(self):
        return self._thickness
    def _set_thickness(self, thickness):
        self._thickness = thickness
        self._update_shape()
    thickness = property(_get_thickness, _set_thickness,
        doc='''Thickness of the cross.

        :type: float
        ''')

    def generate_vertices(self):
        ''' '''

        x,y,w,h = 0,0,self._width-1,self._height-1
        b = self._branches
        t = self._thickness
        foreground_vertices = []
        for i in range(b):
            a1 = (i+0.0)*2*math.pi/b-math.pi/2
            a2 = (i+0.5)*2*math.pi/b-math.pi/2
            a3 = (i+1.0)*2*math.pi/b-math.pi/2
            dx = (math.cos(a1)*w/2*t-math.cos(a3)*w/2*t)/2
            dy = (math.sin(a1)*h/2*t-math.sin(a3)*h/2*t)/2
            foreground_vertices += [(w/2+math.cos(a1)*w/2*t,
                                     h/2+math.sin(a1)*h/2*t),
                                    (w/2+math.cos(a2)*w/2+dx,
                                     h/2+math.sin(a2)*h/2+dy),
                                    (w/2+math.cos(a2)*w/2-dx,
                                     h/2+math.sin(a2)*h/2-dy),
                                    (w/2+math.cos(a3)*w/2*t,
                                     h/2+math.sin(a3)*h/2*t)]
        background_vertices = [v for v in foreground_vertices]
        for i in range(b):
            a1 = (i+0.0)*2*math.pi/b-math.pi/2
            a2 = (i+0.5)*2*math.pi/b-math.pi/2
            a3 = (i+1.0)*2*math.pi/b-math.pi/2
            background_vertices += [(w/2+math.cos(a1)*w/2*t,
                                     h/2+math.sin(a1)*h/2*t),
                                    (w/2, h/2),
                                    (w/2, h/2),
                                    (w/2+math.cos(a3)*w/2*t,
                                     h/2+math.sin(a3)*h/2*t)]
        return foreground_vertices, background_vertices



# ------------------------------------------------------------------------------
class Star(Shape):
    ''' Star shape.

    This is a class for rendering a cross.
    '''

    def __init__(self, thickness=.4, branches=5, *args, **kwargs):
        '''Create a cross.

        :Parameters:
            `thickness` : int
                Thickness of the cross
            `branches` : int
                Number of branches
        '''
        self._thickness = thickness
        self._branches = branches
        Shape.__init__(self, *args, **kwargs)
        self._fill_mode = GL_TRIANGLES
        self._update_position()
        self._update_shape()

    def __str__(self):
        s = '<Star %dx%d+%d+%d>' % (self._width,self._height,self._x, self._y)
        return s

    def _get_thickness(self):
        return self._thickness
    def _set_thickness(self, thickness):
        self._thickness = thickness
        self._update_shape()
    thickness = property(_get_thickness, _set_thickness,
        doc='''Thickness of the star.

        Thickness must be between 0 and 1.

        :type: float 
        ''')

    def _get_branches(self):
        return self._branches
    def _set_branches(self, branches):
        self._branches = branches
        self._update_shape()
    branches = property(_get_branches, _set_branches,
        doc='''Number of branches of the star.

        :type: int 
        ''')

    def generate_vertices(self):
        ''' '''

        x,y,w,h = 0,0,self._width-1,self._height-1
        b = self._branches
        t = self._thickness
        foreground_vertices = []
        for i in range(b):
            a1 = (i+0.0)*2*math.pi/(b)-math.pi/2
            a2 = (i+0.5)*2*math.pi/(b)-math.pi/2
            a3 = (i+1.0)*2*math.pi/(b)-math.pi/2
            foreground_vertices += [(w/2+math.cos(a1)*w/2*t,
                                     h/2+math.sin(a1)*h/2*t),
                                    (w/2+math.cos(a2)*w/2.0,
                                     h/2+math.sin(a2)*h/2.0),
                                    (w/2+math.cos(a3)*w/2*t,
                                     h/2+math.sin(a3)*h/2*t)]
        background_vertices = [v for v in foreground_vertices]
        for i in range(b):
            a1 = (i+0.0)*2*math.pi/(b)-math.pi/2
            a2 = (i+0.5)*2*math.pi/(b)-math.pi/2
            a3 = (i+1.0)*2*math.pi/(b)-math.pi/2
            background_vertices += [(w/2+math.cos(a1)*w/2*t,
                                     h/2+math.sin(a1)*h/2*t),
                                    (w/2+math.cos(a2)*w/2*0,
                                     h/2+math.sin(a2)*h/2*0),
                                    (w/2+math.cos(a3)*w/2*t,
                                     h/2+math.sin(a3)*h/2*t)]
        return foreground_vertices, background_vertices

 



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    import pyglet

    image = pyglet.image.load('crate.bmp')
    texture = image.get_texture()

    pad = 110
    window = pyglet.window.Window(width=8*pad+5, height=7*pad+5, resizable=False)

    # Generate all shapes and configurations
    shapes = []
    kwargs = [{'y': 10+0*pad,'height':100,'width':100,
               'background':(0,0,0,0), 'foreground':(1,1,1,.5)},
              {'y': 10+1*pad,'height':100,'width':100,
               'background':(0,0,0,0),
               'foreground':[(1,1,1,.5),(1,1,1,.5),(1,1,1,0),(1,1,1,0)]},
              {'y': 10+2*pad,'height':100,'width':100,
               'background':(1,1,1,.25), 'foreground':(1,1,1,.5)},
              {'y': 10+3*pad,'height':100,'width':100, 'rotation':10,
               'background':[(0,0,1,.5),(1,1,1,1)],
               'foreground':(1,1,1,1)},
              {'y': 10+4*pad,'height':100,'width':100,
               'background':[(0,0,1,.5),(0,0,1,.5),(1,1,1,1),(1,1,1,1)],
               'foreground':(1,1,1,1)},
              {'y': 10+5*pad,'height':100,'width':100,
               'texture':texture,
               'background':(1,1,1,1),'foreground':(1,1,1,1)},
              {'y': 10+6*pad,'height':100,'width':100,
               'texture':texture, 'foreground':(1,1,1,1),
               'background':[(0,0,1,.5),(0,0,1,.5),(1,1,1,1),(1,1,1,1)]}
              ]

    for kwarg in kwargs:
        shapes.append( Rectangle(x=10+0*pad,                     **kwarg) )
        shapes.append( Rectangle(x=10+1*pad, radius=25,          **kwarg) )
        shapes.append( Rectangle(x=10+2*pad, radius=(25,0,0,0),  **kwarg) )
        shapes.append( Ellipse  (x=10+3*pad,                     **kwarg) )
        shapes.append( Ellipse  (x=10+4*pad, theta2=270,         **kwarg) )
        shapes.append( Triangle (x=10+5*pad,                     **kwarg) )
        shapes.append( Cross    (x=10+6*pad,                     **kwarg) )
        shapes.append( Star     (x=10+7*pad,                     **kwarg) )

    @window.event
    def on_draw():
        window.clear()
        for shape in shapes: shape.draw()

    @window.event
    def on_mouse_press(x,y,button,modifiers):
        # Inefficient
        # for shape in shapes:
        #     if shape.hit_test(x,y):
        #         print 'Hit'

        # Better version
        # --------------
        projection = (GLfloat*16)()
        glGetFloatv(GL_PROJECTION_MATRIX, projection)
        viewport = (GLint*4)()
        glGetIntegerv(GL_VIEWPORT, viewport)
        buffer = (GLuint*512)()
        glSelectBuffer(512, buffer)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(x, y, 1.0, 1.0, viewport)
        glMultMatrixf(projection)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        for shape in shapes: shape.draw()
        hits = glRenderMode(GL_RENDER)
        names = [buffer[i*4+3] for i in range(hits)]
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        for shape in shapes:
            for name in names:
                if name == id(shape):
                    print shape
    pyglet.app.run()
