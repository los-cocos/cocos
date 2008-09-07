# -*- coding: utf-8 -*-
"""setup -- setuptools setup file for cocos2d.

$Author: eykd $
$Rev: 1016 $
$Date: 2008-04-05 16:22:08 -0500 (Sat, 05 Apr 2008) $
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.3.0"
__date__ = "2008-06-27"

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

__description__ = """cocos2d: A framework for building 2D games

cocos2d is a framework for building 2D games, demos, and other graphical/interactive applications. It is built over pyglet. It provides some conventions and classes to help you structure a "scene based application".

A cocos2d application consists of several scenes, and a workflow connecting the different scenes. It provides you with a "director" (a singleton) which handles that workflow between scenes. Each scene is composed of an arbitrary number of layers; layers take care of drawing to the screen (using the pyglet and OpenGL APIs), handling events and in general contain all of the game/application logic.

cocos2d simplifies the game development in these areas:

    * Defining a workflow for your game
    * Creating special effects in layers
    * Creating transitions between scenes
    * Managing sprites
    * Basic menus
    * and much more!
"""

setup(
    name = "cocos2d",
    version = __version__,
    author = "cocos2d Team",
    description = __description__,
    url = "http://cocos2d.org",

    packages = find_packages(),
    package_data={'cocos': ['resources/*']},

    install_requires=['pyglet>=1.1.1',],
    dependency_links=['http://code.google.com/p/pyglet/downloads/list',],

    include_package_data = True,
    zip_safe = False,
    )
