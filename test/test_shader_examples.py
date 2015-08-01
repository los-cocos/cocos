# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "shader, uniform"

import time

from pyglet.gl import *

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.window import key

from cocos import shader

def load_texture(fname):
    pic = pyglet.image.load(fname,
                        file=pyglet.resource.file(fname))
    texture = pic.get_texture()
    # if the texture always uses the same texparameri it would be good to
    # set them here, otherwise we may need to add that functionality in draw
    #...
    return texture

class TestLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, textures, available_programs, base_color):
        super(TestLayer, self).__init__()
        self.textures = textures
        self.texture_selector = 0
        self.texture = textures[self.texture_selector]

        self.available_programs = available_programs
        self.program_selector = 0
        self.shader_program = available_programs[self.program_selector]

        self.base_color = base_color
        self.color = base_color
        self.schedule(self.update)

    def on_enter(self):
        super(TestLayer, self).on_enter()
        self.start_time = time.time()

    def draw(self):
        x,y = director.get_window_size()
        x = x//2
        y = y//2
        d = 100

        if self.shader_program:
            # bind the shader program and initialize his params
            self.shader_program.set_state(self)
        else:
            # Do not use glEnable(GL_TEXTURE_2D) when using shaders.
            # See https://www.opengl.org/wiki/GLSL_:_common_mistakes#Enable_Or_Not_To_Enable
            glEnable(GL_TEXTURE_2D)
            # if this were the only texture used in the scene it would be better
            # to bind only once, outside draw, by example in load_texture()
            glBindTexture(GL_TEXTURE_2D, self.texture.id)

        glPushMatrix()
        self.transform()

        glBegin(GL_TRIANGLES)

        # up-left triangle, tinted with green gradient if colors used
        glColor4ub(0,255,0,255)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(x+d, y+d)

        glColor4ub(255,255,255,255)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x-d, y+d)

        glColor4ub(255,255,255,255)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(x+d, y-d)

        # down-right triangle, tinted with blue gradient if colors used
        glColor4ub(255,255,255,255)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x-d, y+d)

        glColor4ub(0,0,255,255)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(x-d, y-d)

        glColor4ub(255,255,255,255)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(x+d, y-d)

        glEnd()
        glPopMatrix()

        if self.shader_program:
            self.shader_program.unset_state()
        else:
            #unbind texture
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
        

    def update(self, dt):
        multiplier = 0.5 + 0.5 * ((time.time() - self.start_time) % 2.0 / 2.0)
        self.blackness = 1.0 - multiplier
        self.color = tuple([ c*multiplier for c in self.base_color])

    def on_key_press(self, k, m ):
        if k in [key.LEFT, key.RIGHT]:
            if k == key.LEFT:
                self.program_selector -= 1
            elif k == key.RIGHT:
                self.program_selector += 1
            self.program_selector = self.program_selector % len(self.available_programs)
            self.shader_program = self.available_programs[self.program_selector]
            print('program:', self.shader_program)
        if k in [key.DOWN, key.UP]:
            if k == key.DOWN:
                self.texture_selector -= 1
            elif k == key.UP:
                self.texture_selector += 1
            self.texture_selector = self.texture_selector % len(self.textures)
            self.texture = self.textures[self.texture_selector]



class ProgramUntexturedFixedHardcodedColor(shader.ShaderProgram):
    """
    Renders the geometry with a solid color hardcoded in the fragment program

    Texture info, like texture coords in each vertex or actual active textures
    is ignored.

    Any color info except the harcoded color is ignored.

    gl_FragColor is a predefined output variable for fragment shaders; it must
    be set in the fragment code or the object will be invisible.
    """
    vertex_code = None

    fragment_code = '''
    void main() {
        gl_FragColor = vec4(1.0, 1.0, 0.0, 1.0);
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('yellow', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
    def unset_state(self):
        self.uninstall()


class ProgramUntexturedProgramableColor(shader.ShaderProgram):
    """
    Renders the geometry with a solid programable color

    Texture info, like texture coords in each vertex or actual active textures
    is ignored.

    Any color info except the one given by the provider is ignored.

    The desired color is specified by passing in the set_state a provider
    object which has a 'color' member; it must be a 4-tuple of floats
    between 0 and 1.

    gl_FragColor is a predefined output variable for fragment shaders; it must
    be set in the fragment code or the object will be invisible.
    """
    vertex_code = None

    fragment_code = '''
    uniform vec4 color;

    void main() {
        gl_FragColor = color;
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('prog_color', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
        self.uset4F('color', *provider.color)
    def unset_state(self):
        self.uninstall()


class ProgramUntexturedInterpolatedColor(shader.ShaderProgram):
    """
    Renders the geometry with color interpolated from the vertexs

    gl_Position is a predefined output variable in vertex shaders, should be
    writen with the vertex desired homogeneous coordinate, which for traditional
    rendering are the coods after appling the modelview and projection transform

    ftransform is a predefined function in vertex shaders, it gives the vertex
    homogeneous coords as would have been calculated by the fixed pipeline.

    gl_FragColor is a predefined output variable for fragment shaders; it must
    be set in the fragment code or the object will be invisible.

    gl_FrontColor is a predefined vertex shader output varying variable, that
    can be readed, interpolated, as gl_Color in the fragment shader
    """
    vertex_code = '''
    void main()
    {
        gl_FrontColor = gl_Color;
        gl_Position = ftransform();
    }
    '''

    fragment_code = '''
    void main()
    {
        gl_FragColor = gl_Color;
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('gradient', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
    def unset_state(self):
        self.uninstall()


class ProgramTexturedNoTint(shader.ShaderProgram):
    """
    Renders the geometry using texture info and ignoring additional color info

    The desired texture is specified by passing in the set_state a provider with
    a 'texture' member.
    """
    vertex_code = '''
    void main()
    {
        gl_TexCoord[0] = gl_MultiTexCoord0;
        gl_Position = ftransform();
    }
    '''

    fragment_code = '''
    uniform sampler2D tex;

    void main()
    {
        vec4 texel_color = texture2D(tex, gl_TexCoord[0].st);
        gl_FragColor = texel_color;
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('texture_only', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
        self.usetTex('tex', 0, GL_TEXTURE_2D, provider.texture.id)
    def unset_state(self):
        self.uninstall()


class ProgramTexturedTinted(shader.ShaderProgram):
    """Combines the texture and color info to render the geometry

    They sre many was of combining two colors, this is easy.
    """
    vertex_code = '''
    void main()
    {
        gl_FrontColor = gl_Color;
        gl_TexCoord[0] = gl_MultiTexCoord0;
        gl_Position = ftransform();
    }
    '''

    fragment_code = '''
    uniform sampler2D tex;

    void main()
    {
        vec4 texel_color = texture2D(tex, gl_TexCoord[0].st);
        gl_FragColor = texel_color * gl_Color;
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('texture_tinted', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
        self.usetTex('tex', 0, GL_TEXTURE_2D, provider.texture.id)
    def unset_state(self):
        self.uninstall()


class ProgramTexturedTintedProgramableDarkness(shader.ShaderProgram):
    """Combines the texture and color info, and then it darks by a programable factor

    The desired blackness is specified by passing in the set_state a provider
    with a 'blackness' member.

    The 'blackness' is a float between 0 and 1, 0 means no darkening, 1 full black

    They are many was of combining two colors, this is easy.
    """
    vertex_code = '''
    void main()
    {
        gl_FrontColor = gl_Color;
        gl_TexCoord[0] = gl_MultiTexCoord0;
        gl_Position = ftransform();
    }
    '''

    fragment_code = '''
    uniform sampler2D tex;
    uniform float blackness;

    void main()
    {
        vec4 texel = texture2D(tex, gl_TexCoord[0].st);
        texel *= gl_Color;
        texel = vec4(texel.rgb * (1.0 - blackness), texel.a);
        gl_FragColor = texel;
    }
    '''
    @classmethod
    def create(cls):
        return cls.simple_program('texture_tinted_darkened', cls.vertex_code, cls.fragment_code)
    def set_state(self, provider):
        self.install()
        self.usetTex('tex', 0, GL_TEXTURE_2D, provider.texture.id)
        self.uset1F('blackness', provider.blackness)
    def unset_state(self):
        self.uninstall()


def get_available_programs():
    return [
        None,
        ProgramUntexturedFixedHardcodedColor.create(),
        ProgramUntexturedProgramableColor.create(),
        ProgramUntexturedInterpolatedColor.create(),
        ProgramTexturedNoTint.create(),
        ProgramTexturedTinted.create(),
        ProgramTexturedTintedProgramableDarkness.create(),
        ]


description = """
Shows the efect of different example shaders.
Use arrow keys - Left, Right change shaders, Up, Down textures.
"""


def main():
    print(description)
    director.init()
    textures = [
        load_texture('grossinis_sister1.png'),
        load_texture('fire.png'),
        ]
    available_programs = get_available_programs()
    test_layer = TestLayer (textures, available_programs, (1.0, 0.0, 1.0, 1.0))
    main_scene = cocos.scene.Scene(cocos.layer.ColorLayer(255, 214, 173, 255),
                                   test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
