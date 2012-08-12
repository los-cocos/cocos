# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for cocos2d.

$Author: eykd $
$Rev: 1016 $
$Date: 2011-08-14 23:00:00 -0300 (Wed, 14 August 2011) $
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.5.5"
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
        "Programming Language :: Python",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ("Topic :: Games/Entertainment"),
        ],
 
    packages = find_packages(),
    package_data={'cocos': ['resources/*']},

    install_requires=['pyglet>=1.1.4',],
    dependency_links=['http://code.google.com/p/pyglet/downloads/list',],

    include_package_data = True,
    zip_safe = False,
    )
