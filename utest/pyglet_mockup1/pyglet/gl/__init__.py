# gl
from __future__ import division, print_function, unicode_literals


GL_BLEND = 3042
GL_ZERO = 0     # /usr/include/GL/gl.h:147
GL_ONE = 1  # /usr/include/GL/gl.h:148
GL_SRC_COLOR = 768  # /usr/include/GL/gl.h:149
GL_ONE_MINUS_SRC_COLOR = 769    # /usr/include/GL/gl.h:150
GL_SRC_ALPHA = 770  # /usr/include/GL/gl.h:151
GL_ONE_MINUS_SRC_ALPHA = 771    # /usr/include/GL/gl.h:152
GL_DST_ALPHA = 772  # /usr/include/GL/gl.h:153
GL_ONE_MINUS_DST_ALPHA = 773    # /usr/include/GL/gl.h:154
GL_DST_COLOR = 774  # /usr/include/GL/gl.h:159
GL_ONE_MINUS_DST_COLOR = 775    # /usr/include/GL/gl.h:160
GL_SRC_ALPHA_SATURATE = 776     # /usr/include/GL/gl.h:161
GL_NONE = 0     # /usr/include/GL/gl.h:205

GL_TEXTURE_WRAP_S = 10242 	# /usr/include/GL/gl.h:947
GL_TEXTURE_WRAP_T = 10243 	# /usr/include/GL/gl.h:948
GL_CLAMP_TO_EDGE = 33071 	# /usr/include/GL/gl.h:1079

GL_MODELVIEW = 5888 	# /usr/include/GL/gl.h:748
GL_PROJECTION = 5889 	# /usr/include/GL/gl.h:749


def glEnable(arg):
    pass

def glBlendFunc(a1, a2):
    pass

def glViewport(a1, a2, a3, a4):
    pass

def gluPerspective(a1, a2, a3, a4):
    pass

def gluLookAt(a1, a2, a3, a4, a5, a6, a7, a8, a9):
    pass

def glScissor(a1, a2, a3, a4):
    pass

def glMatrixMode(a1):
    pass

def glLoadIdentity():
    pass

def glPushMatrix():
    pass

def glPopMatrix():
    pass

def glBindTexture(a1, a2):
    pass

def glTexParameteri(a1, a2, a3):
    pass

def glTranslatef(a1, a2, a3):
    pass
