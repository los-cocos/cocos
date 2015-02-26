=======
cocos2d
=======

.. image:: https://travis-ci.org/ccanepa/unit_nk.png
   :target: https://travis-ci.org/ccanepa/unit_nk

| A framework for building 2D games, demos, and other graphical/interactive applications.
| Draws using OpenGL, which is hardware accelerated.
| Targets the Operating Systems linux, mac or windows on Pc-like hardware.

| Provides some conventions and classes to help you structure a "scene based application".
| A cocos2d application consists of several scenes, and a workflow connecting the different scenes.
| It provides you with a "director" (a singleton) which handles that workflow between scenes.
| Each scene is composed of an arbitrary number of layers;
| layers take care of drawing to the screen (using the pyglet and OpenGL APIs), handling events and in general contain all of the game/application logic.

cocos2d simplifies the game development in these areas:

* Flow control: Manage the flow control between different scenes in an easy way
* Sprites: Fast and easy sprites
* Actions: Just tell sprites what you want them to do. Composable actions like move, rotate, scale and much more
* Effects: Effects like waves, twirl, lens and much more
* Tiled Maps: Support for rectangular and hexagonal tiled maps
* Collision: Basic pure python support for collisions
* Transitions: Move from scene to scene with style
* Menus: Built in classes to create menus
* Text Rendering: Label and HTMLLabel with action support
* Built-in Python Interpreter: For debugging purposes
* Access to OpenGL functionality
* and much more! http://python.cocos2d.org

Requirements
------------

Software:

* python 2.6, 2.7 or 3.3+
* pyglet 1.2 or newer (http://www.pyglet.org)
* Linux, Windows or Mac OS/X

Hardware:

* To execute some effects you will need a video card with the:
    GL_EXT_framebuffer_object extension.


Installing
----------

Being a pure python package the usual options are available; you
can look at the INSTALL file for some details


Learning cocos2d
----------------

* Go to the online tutorials / documentation page:
  http://python.cocos2d.org/doc.html

  You will find:
   * the Programming Guide
   * the API Reference
   * some tutorial videos

  The tutorials are included in the source package.

* Lot of miniprograms that demonstrates the available objects and possible actions.
  There are a great starting point while learning and experimenting with cocos:
  you find a sample with the object that interest you exercising the features
  that you need, read the code, run, modify and re-run to experiment.
  
  Also, handy to know what is available in cocos: run all the tests and by
  looking at the code you know what to look at in the docs.

  You can find them at the test directory in the source distribution.
  After unpacking, to run the tests you can do::

      $ cd test
      $ python test_*.py

* More complex sample programs

  You can find it in the samples directory in the source distribution, and the
  most complex in subdirectories there, including a presentation done with
  Cocos himself.
  
  After unpacking, to run the samples you can do::
   
      $ cd samples
      $ python sample_name.py


Do you have any doubt?
    + http://groups.google.com/group/cocos-discuss


Did you find any bug?
    + http://groups.google.com/group/cocos-discuss
    + https://github.com/los-cocos/cocos


Current repository is at
    + https://github.com/los-cocos/cocos
