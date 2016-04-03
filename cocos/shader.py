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
import six
from . import compat

from ctypes import byref, c_char, c_char_p, c_float, c_int, cast, create_string_buffer, POINTER

from pyglet import gl


class GLSLException(Exception):
    pass


def glsl_log(handle):
    if handle == 0:
        return ''
    log_len = c_int(0)

    gl.glGetObjectParameterivARB(handle, gl.GL_OBJECT_INFO_LOG_LENGTH_ARB,
                              byref(log_len))
    if log_len.value == 0:
        return ''

    log = create_string_buffer(log_len.value)  # does log_len include the NUL?

    chars_written = c_int(0)
    gl.glGetInfoLogARB(handle, log_len.value, byref(chars_written), log)

    return log.value


class Shader(object):
    s_tag = 0

    def __init__(self, name, prog):
        prog = compat.asciibytes(prog)
        self.name = name
        self.prog = prog
        self.shader = 0
        self.compiling = False
        self.tag = -1
        self.dependencies = []

    def __del__(self):
        self.destroy()

    def _source(self):
        if self.tag == Shader.s_tag:
            return []
        self.tag = Shader.s_tag

        r = []
        for d in self.dependencies:
            r.extend(d._source())
        r.append(self.prog)

        return r

    def _compile(self):
        if self.shader:
            return
        if self.compiling:
            return
        self.compiling = True

        self.shader = gl.glCreateShaderObjectARB(self.shaderType())
        if self.shader == 0:
            raise GLSLException('faled to create shader object')

        prog = c_char_p(self.prog)
        length = c_int(-1)
        gl.glShaderSourceARB(self.shader,
                          1,
                          cast(byref(prog), POINTER(POINTER(c_char))),
                          byref(length))
        gl.glCompileShaderARB(self.shader)

        self.compiling = False

        compile_status = c_int(0)
        gl.glGetObjectParameterivARB(self.shader, gl.GL_OBJECT_COMPILE_STATUS_ARB, byref(compile_status))

        if not compile_status.value:
            err = glsl_log(self.shader)
            gl.glDeleteObjectARB(self.shader)
            self.shader = 0
            raise GLSLException('failed to compile shader', err)

    def _attachTo(self, program):
        if self.tag == Shader.s_tag:
            return

        self.tag = Shader.s_tag

        for d in self.dependencies:
            d._attachTo(program)

        if self.isCompiled():
            gl.glAttachObjectARB(program, self.shader)

    def addDependency(self, shader):
        self.dependencies.append(shader)
        return self

    def destroy(self):
        if self.shader != 0:
            gl.glDeleteObjectARB(self.shader)

    def shaderType(self):
        raise NotImplementedError()

    def isCompiled(self):
        return self.shader != 0

    def attachTo(self, program):
        Shader.s_tag = Shader.s_tag + 1
        self._attachTo(program)

    # ATI/apple's glsl compiler is broken.
    def attachFlat(self, program):
        if self.isCompiled():
            gl.glAttachObjectARB(program, self.shader)

    def compileFlat(self):
        if self.isCompiled():
            return

        self.shader = gl.glCreateShaderObjectARB(self.shaderType())
        if self.shader == 0:
            raise GLSLException('faled to create shader object')

        all_source = [b'\n'.join(self._source())]
        prog = (c_char_p * len(all_source))(*all_source)
        length = (c_int * len(all_source))(-1)
        gl.glShaderSourceARB(self.shader,
                          len(all_source),
                          cast(prog, POINTER(POINTER(c_char))),
                          length)
        gl.glCompileShaderARB(self.shader)

        compile_status = c_int(0)
        gl.glGetObjectParameterivARB(self.shader, gl.GL_OBJECT_COMPILE_STATUS_ARB, byref(compile_status))

        if not compile_status.value:
            err = glsl_log(self.shader)
            gl.glDeleteObjectARB(self.shader)
            self.shader = 0
            raise GLSLException('failed to compile shader', err)

    def compile(self):
        if self.isCompiled():
            return

        for d in self.dependencies:
            d.compile()

        self._compile()


class VertexShader(Shader):
    def shaderType(self):
        return gl.GL_VERTEX_SHADER_ARB


class FragmentShader(Shader):
    def shaderType(self):
        return gl.GL_FRAGMENT_SHADER_ARB


class ShaderProgram(object):
    @classmethod
    def simple_program(cls, name, vertex_code, fragment_code):
        """Intended to cut boilerplate when doing simple shaders

           name : string with program name
           vertex_code : None or string with the vertex shader code
           fragment_code : None or string with the fragment shader code
        """
        shader_p = cls()
        if vertex_code:
            shader_p.setShader(VertexShader(name + '_vp', vertex_code))
        if fragment_code:
            shader_p.setShader(FragmentShader(name + '_fp', fragment_code))
        # link now to allow fail early
        shader_p.prog()
        return shader_p

    def __init__(self, vertex_shader=None, fragment_shader=None):
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.program = 0

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.program != 0:
            gl.glDeleteObjectARB(self.program)

    def setShader(self, shader):
        if isinstance(shader, FragmentShader):
            self.fragment_shader = shader
        if isinstance(shader, VertexShader):
            self.vertex_shader = shader
        if self.program != 0:
            gl.glDeleteObjectARB(self.program)

    def link(self):
        if self.vertex_shader is not None:
            self.vertex_shader.compileFlat()
        if self.fragment_shader is not None:
            self.fragment_shader.compileFlat()

        self.program = gl.glCreateProgramObjectARB()
        if self.program == 0:
            raise GLSLException('failed to create program object')

        if self.vertex_shader is not None:
            self.vertex_shader.attachFlat(self.program)
        if self.fragment_shader is not None:
            self.fragment_shader.attachFlat(self.program)

        gl.glLinkProgramARB(self.program)

        link_status = c_int(0)
        gl.glGetObjectParameterivARB(self.program, gl.GL_OBJECT_LINK_STATUS_ARB, byref(link_status))
        if link_status.value == 0:
            err = glsl_log(self.program)
            gl.glDeleteObjectARB(self.program)
            self.program = 0
            raise GLSLException('failed to link shader', err)

        self.__class__._uloc_ = {}
        self.__class__._vloc_ = {}

        return self.program

    def prog(self):
        if self.program:
            return self.program
        return self.link()

    def install(self):
        p = self.prog()
        if p != 0:
            gl.glUseProgramObjectARB(p)

    def uninstall(self):
        gl.glUseProgramObjectARB(0)

    def uniformLoc(self, var):
        var = compat.asciibytes(var)
        try:
            return self.__class__._uloc_[var]
        except:
            if self.program == 0:
                self.link()
            self.__class__._uloc_[var] = v = gl.glGetUniformLocationARB(self.program, var)
            return v

    def uset1F(self, var, x):
        gl.glUniform1fARB(self.uniformLoc(var), x)

    def uset2F(self, var, x, y):
        gl.glUniform2fARB(self.uniformLoc(var), x, y)

    def uset3F(self, var, x, y, z):
        gl.glUniform3fARB(self.uniformLoc(var), x, y, z)

    def uset4F(self, var, x, y, z, w):
        gl.glUniform4fARB(self.uniformLoc(var), x, y, z, w)

    def uset1I(self, var, x):
        gl.glUniform1iARB(self.uniformLoc(var), x)

    def uset2I(self, var, x, y):
        gl.glUniform2iARB(self.uniformLoc(var), x, y)

    def uset3I(self, var, x, y, z):
        gl.glUniform3iARB(self.uniformLoc(var), x, y, z)

    def usetM4F(self, var, matrix, transpose=False):
        # some matrixs readed from openGl will come as the transpose of the
        # matrix we want to feed, so there it comes handy the transpose param
        gl.glUniformMatrix4fvARB(self.uniformLoc(var), 1, transpose,
                              (c_float * 16)(*matrix))

    def usetTex(self, var, unit, target, tx):
        """
        var : name of variable to write
        unit : texture unit
        target : target for glBindTexture
        tx : texture ID
        """
        gl.glUniform1iARB(self.uniformLoc(var), unit)
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(target, tx)

__all__ = ['VertexShader', 'FragmentShader', 'ShaderProgram', 'GLSLException']
