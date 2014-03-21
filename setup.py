# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for cocos2d.

   last used: release 0.6.0, built from py2.6 + setuptools 3.3

   operation:
       svn checkout http://los-cocos.googlecode.com/svn/trunk/ cocos_trunk
       cd cocos_trunk
       svn export . ../cocos_export
       cd ..\cocos_export
       py -2.6 setup.py sdist >../sdist.log
       [ the generated package will be in cocos_export/dist ]
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.6.0"
__date__ = "2012 08 12"

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

f = open('README','rU')
long_description = f.read()
f.close()

setup(
    name = "cocos2d",
    version = __version__,
    author = "cocos2d Team",
    license="BSD",
    description = "a 2D framework for games and multimedia",
    long_description=long_description,
    url = "http://cocos2d.org",
    download_url = "http://code.google.com/p/los-cocos/downloads/list",
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
 
    packages = ['cocos'],
    package_data={'cocos': ['resources/*.*']},

    install_requires=['six', 'pyglet>=1.2',],
    dependency_links=['hg+https://code.google.com/p/pyglet@0a75c2e7c35d/#egg=pyglet-1.2',],

    include_package_data = True,
    zip_safe = False,
    )
