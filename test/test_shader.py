from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

testinfo = "s, q"
tags = "shader, quadric"

from pyglet.gl import *

import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from cocos import shader

class TestLayer(cocos.layer.Layer):
    def draw(self):
        x,y = director.get_window_size()
        x = x//2
        y = y//2
        d = 100

        cuadric.install()
        glColor4ub(255,255,255,255)
        glBegin(GL_TRIANGLES)
        glTexCoord2f( 0.5,0 )
        glVertex2f( x+d,y+d )
        glTexCoord2f( 0,0 )
        glVertex2f( x,y+d )
        glTexCoord2f( 1,1 )
        glVertex2f( x+d,y )

        glTexCoord2f( 0.5,0 )
        glVertex2f( x-d,y-d )
        glTexCoord2f( 0,0 )
        glVertex2f( x,y-d )
        glTexCoord2f( 1,1 )
        glVertex2f( x-d,y )

        glTexCoord2f( 0.5,0 )
        glVertex2f( x+d,y-d )
        glTexCoord2f( 0,0 )
        glVertex2f( x,y-d )
        glTexCoord2f( 1,1 )
        glVertex2f( x+d,y )

        glTexCoord2f( 0.5,0 )
        glVertex2f( x-d,y+d )
        glTexCoord2f( 0,0 )
        glVertex2f( x,y+d )
        glTexCoord2f( 1,1 )
        glVertex2f( x-d,y )

        glTexCoord2f( 0.5,1)
        glVertex2f( x,y )
        glVertex2f( x,y+d )
        glVertex2f( x+d,y )

        glVertex2f( x,y )
        glVertex2f( x,y-d )
        glVertex2f( x+d,y )

        glVertex2f( x,y )
        glVertex2f( x,y+d )
        glVertex2f( x-d,y )

        glVertex2f( x,y )
        glVertex2f( x,y-d )
        glVertex2f( x-d,y )

        glEnd()
        cuadric.uninstall()

cuadric_t = '''
void main() {
    vec2 pos = gl_TexCoord[0].st;
    float res = pos.x*pos.x - pos.y;
    if (res<0.0) {
        gl_FragColor = vec4(1.0,1.0,1.0,1.0);
    } else {
        gl_FragColor = vec4(0.0,0.0,0.0,0.0);
    }
}
'''


cuadric = shader.ShaderProgram()
cuadric.setShader(shader.FragmentShader('cuadric_t', cuadric_t))

def main():
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)

if __name__ == '__main__':
    main()
