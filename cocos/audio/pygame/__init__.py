# pygame - Python Game Library
# Copyright (C) 2000-2001  Pete Shinners
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Pete Shinners
# pete@shinners.org

"""Top-level Pygame module.

Pygame is a set of Python modules designed for writing games.
It is written on top of the excellent SDL library. This allows you
to create fully featured games and multimedia programs in the Python
language. The package is highly portable, with games running on
Windows, MacOS, OS X, BeOS, FreeBSD, IRIX, and Linux.
"""

from __future__ import division, print_function, unicode_literals
import six

__docformat__ = 'restructuredtext'
__version__ = '$Id: __init__.py 899 2006-08-04 16:52:18Z aholkner $'

import os
import sys


class MissingModule:
    def __init__(self, name, info='', urgent=0):
        self.name = name
        self.info = str(info)
        self.urgent = urgent
        if urgent:
            self.warn()

    def __getattr__(self, var):
        if not self.urgent:
            self.warn()
            self.urgent = 1
        MissingPygameModule = "%s module not available" % self.name
        raise NotImplementedError(MissingPygameModule)

    if six.PY2:
        def __nonzero__(self):
            return 0
    else:
        def __bool__(self):
            return 0

    def warn(self):
        if self.urgent:
            type = 'import'
        else:
            type = 'use'
        message = '%s %s: %s' % (type, self.name, self.info)
        try:
            import warnings
            if self.urgent:
                level = 4
            else:
                level = 3
            warnings.warn(message, RuntimeWarning, level)
        except ImportError:
            print(message)

# we need to import like this, each at a time. the cleanest way to import
# our modules is with the import command (not the __import__ function)

# first, the "required" modules
# from pygame.array import *
from cocos.audio.pygame.base import *
from cocos.audio.pygame.version import *
__version__ = ver

# next, the "standard" modules
# we still allow them to be missing for stripped down pygame distributions

try:
    import cocos.audio.pygame.mixer
except (ImportError, IOError) as msg:
    mixer = MissingModule("mixer", msg, 0)

# there's also a couple "internal" modules not needed
# by users, but putting them here helps "dependency finder"
# programs get everything they need (like py2exe)

try:
    import cocos.audio.pygame.mixer_music
    del cocos.audio.pygame.mixer_music
except (ImportError, IOError):
    pass

# cleanup namespace
del os, sys,  # TODO rwobject, surflock, MissingModule, copy_reg
