"""A thin wrapper for OpenGL pbuffer objets. For implementation use only"""
import ctypes, sys

if sys.platform=='darwin':
#### Darwin (Carbon, AGL)
    class Pbuffer (object):
        def __init__ (self, *args, **kwargs):
            raise Exception ("AGL Pbuffers not implemented")
elif sys.platform in ('win32', 'cygwin'):
#### Win32 (WGL)
    class Pbuffer (object):
        def __init__ (self, *args, **kwargs):
            raise Exception ("WGL Pbuffers not implemented")
else:
#### GLX based systems
    from pyglet.gl.glx import *

    class Pbuffer (object):
        """
        Wrapper for OpenGL pbuffer extensions. 
        See http://oss.sgi.com/projects/ogl-sample/registry/SGIX/pbuffer.txt for details
        
        Caveats:

         - Only GLX version implemented
         - not tested, may not be working
        """

        def __init__ (self, window, attrs=[], width=None, height=None):
            """Create new pbuffer with given size, on same display as `window'
            
            (`width', `height') is the same as the window, if not specified
            
            attrs is a list of alternating GLX_PBUFFER_<attr>, <value>. For example,
            [GLX_DEPTH, 32, GLX_DOUBLEBUFFER, 1]
            """
            self.window = window

            # Get configuration options
            conf_attrs = (ctypes.c_int * (len(attrs)+1))(*(attrs+[0]))
            num = ctypes.c_int (0)
            conf = glXChooseFBConfig (window._x_display, 0, conf_attrs, ctypes.byref(num))

            # Pbuffer configuration
            if width is None: width = window.width
            if height is None: height = window.height
            pbuf_attrs = (ctypes.c_int * 5)(
                GLX_PBUFFER_WIDTH, width,
                GLX_PBUFFER_WIDTH, height, 0)
            self.width = width
            self.height = height
            # Create a pbuffer with a suitable configuration
            self.pbuf = None
            for c in range (num.value):
                pbuf = glXCreatePbuffer (window._x_display, conf[c], pbuf_attrs)
                if pbuf:
                    self.pbuf = pbuf
                    break
            if self.pbuf is None:
                raise Exception ("No valid configuration for pbuffer found")
            # Create a context for the buffer
            self.ctx = glXCreateNewContext (window._x_display, conf[c], GLX_RGBA_TYPE, self.window._context._context, True)
            if not self.ctx:
                raise Exception ("Failed to create context for this buffer")

        def switch_to(self):
            """Set this pbuffer as current GL context"""
            ok = glXMakeContextCurrent (self.window._x_display, self.pbuf, self.pbuf, self.ctx)
            if not ok:
                raise Exception("Failed to switch GL context")

