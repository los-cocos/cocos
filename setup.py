# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for cocos2d.

Supports the usual 'setup.py install' for cocos.

As a release builder:

   last used: release 0.6.2, built from py2.7 + setuptools 5.7 (or 12.2)

   example operation for generating release without handling the docs:
       git clone https://github.com/los-cocos/cocos.git cocos_trunk
       cd cocos_trunk
       py -2.7 setup.py sdist >../sdist.log
       [ the generated package will be in cocos_trunk/dist ]

       Look at tools/building_release_notes.txt for more info about building
       release.
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.6.3"
__date__ = "2015 04 26"

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

import os

f = open('README.rst','rU')
long_description = f.read()
f.close()

install_requires=['six', ]
dependency_links = []
if os.environ.get("TRAVIS", False):
    # Travis CI run
    # We don't want to install pyglet
    pass
else:
    # normal install, add the pyglet dependency
    install_requires.append('pyglet>=1.2')

setup(
    name = "cocos2d",
    version = __version__,
    author = "cocos2d Team",
    license="BSD",
    description = "a 2D framework for games and multimedia",
    long_description=long_description,
    url = "http://python.cocos2d.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ("Topic :: Games/Entertainment"),
        ],
 
    packages = ['cocos', 'cocos/actions', 'cocos/audio', 'cocos/layer', 'cocos/scenes'],
    package_data={'cocos': ['resources/*.*']},

    install_requires=install_requires,
    dependency_links=dependency_links,

    include_package_data = True,
    zip_safe = False,
    )
