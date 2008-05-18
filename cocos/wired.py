from pyglet.gl import *
from pyglet import window, image

import shader

__all__ = ['wired']

test_v = '''
varying vec3 position;
void main() 
{ 
  gl_Position = ftransform(); 
  position = gl_Position.xyz;
}
'''

test_f = '''
varying vec3 position;
void main() 
{ 
    vec4 color = vec4(position,1.0);
    gl_FragColor = color;
} 
'''


def load_shader():
    s = shader.ShaderProgram()
    s.setShader(shader.VertexShader('test_v', test_v))
    s.setShader(shader.FragmentShader('test_f', test_f))
    return s

wired = load_shader()
