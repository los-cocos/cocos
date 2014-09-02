from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

import pyglet
from pyglet import font
from pyglet.gl import *
from pyglet.window import key

from cocos.actions import *
from cocos.layer import *
from cocos.scenes.transitions import *
from cocos.sprite import *
from cocos import text

import demo_grid_effects

basepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
pyglet.resource.path.append(basepath)
pyglet.resource.reindex()


def get_color_layer(idx):
    if idx % 2 == 0:
        return cocos.layer.ColorLayer(32, 32, 32, 255)
    else:
        return cocos.layer.ColorLayer(32, 64, 200, 255)


class TitleSubTitleLayer(cocos.layer.Layer):

    def __init__(self, title, subtitle):
        super(TitleSubTitleLayer, self).__init__()

        x, y = director.get_window_size()

        self.title = text.Label(
            title, (x // 2, y // 2 + 50), font_name='Gill Sans',
            font_size=64, anchor_x='center', anchor_y='center')
        self.add(self.title)

        self.subtitle = text.Label(
            subtitle, (x // 2, y // 2 - 30), font_name='Gill Sans',
            font_size=44, anchor_x='center', anchor_y='center')
        self.add(self.subtitle)


class BulletListLayer(cocos.layer.Layer):

    def __init__(self, title, lines):
        super(BulletListLayer, self).__init__()
        x, y = director.get_window_size()

        self.title = text.Label(
            title, (x // 2, y - 50), font_name='Gill Sans',
            font_size=64, anchor_x='center', anchor_y='center')
        self.add(self.title)

        start_y = (y // 12) * 8
        font_size = 52 // (len(lines) / 2.2 + 1)
        font_size = min(font_size, 52)
        line_font = font.load('Gill Sans', font_size)
        tot_height = 0
        max_width = 0
        rendered_lines = []
        step = 300 // max(len(lines), 1)
        i = 0
        for line in lines:
            line_text = text.Label(
                line, (x // 2, y - 150 - step * i), font_name='Gill Sans',
                font_size=font_size, anchor_x='center', anchor_y='center')
            i += 1
            self.add(line_text)


class TransitionControl(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, scenes, transitions=None):
        super(TransitionControl, self).__init__()

        self.transitions = transitions
        self.scenes = scenes
        for scene in scenes:
            if not self in scene.get_children():
                scene.add(self)

        self.scene_p = 0

    def next_scene(self):
        self.duration = None
        self.scene_p += 1
        if self.scene_p >= len(self.scenes):
            self.scene_p = len(self.scenes) - 1
        else:
            self.transition(self.transitions[self.scene_p % len(self.transitions) - 1])

    def prev_scene(self):
        self.duration = 0.5
        self.scene_p -= 1
        if self.scene_p < 0:
            self.scene_p = 0
        else:
#            self.transition()
            self.transition(self.transitions[self.scene_p % len(self.transitions)])

    def transition(self, transition=None):
        if transition:
            director.replace(transition(
                self.scenes[self.scene_p],
                duration=self.duration
            )
            )
        else:
            director.replace(self.scenes[self.scene_p])

    def on_key_press(self, keyp, mod):
        if keyp in (key.RIGHT,):
            self.next_scene()
        elif keyp in (key.LEFT,):
            self.prev_scene()


class RunScene(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, target):
        super(RunScene, self).__init__()

        self.target = target

    def on_key_press(self, keyp, mod):
        if keyp in (key.F1,):
            director.push(self.target)


if __name__ == "__main__":
    aspect = 1280 / float(800)
    director.init(resizable=True, width=640, height=480)
    director.window.set_fullscreen(False)
    x, y = director.get_window_size()

    pyglet.font.add_directory('..')

    scenes = [
        cocos.scene.Scene(
            TitleSubTitleLayer("cocos2d", "a 2d game library"),
        ),
        cocos.scene.Scene(
            BulletListLayer("cocos2d", [
                "a framework for",
                "building 2D games, demos",
                "and other graphical interactive applications",
                "developed 100% in python",
            ])
        ),
        cocos.scene.Scene(
            BulletListLayer("Games-Python", [
                "Games in an interpreted language?",
                "Depends on the game",
                "30ms is a lot",
            ])
        ),


        cocos.scene.Scene(
            BulletListLayer("Inspiration", [
                "2000 : pygame",
                "2005 : pyweek",
                "2006 : pyglet",
                "2008 : cocos2d"
            ])
        ),
        cocos.scene.Scene(
            BulletListLayer("Features", [
                "Flow Control",
                "Sprites",
                "Actions",
                "Effects",
                "Transitions",
                "Menus",
            ])
        ),
        cocos.scene.Scene(
            BulletListLayer("Features (2)", [
                "Text / HTML",
                "Tiles",
                "Well documented",
                "Embedded python interpreter",
                "BSD License",
                "pyglet-based",
                "OpenGL",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Concepts", []).add(
                Sprite("scene_en.png", (x / 2, 100))),
        ),
        cocos.scene.Scene(
            BulletListLayer("Documentation", [
                "Video Tutorial",
                "Programming guide",
                "(almost) complete API reference",
                "5KLOC of tests",
                "tests are readable samples",
                "FAQ [in progress]",

            ]),
        ),

        cocos.scene.Scene(
            BulletListLayer("Community", [
                "5 finished games",
                "Several projects in development",
                "Contributors from around the world",
                "Working mailing list",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Flow Control", [
                "director.run()",
                "director.push() / pop()",
                "director.replace",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Sprites", [
                "position",
                "scale",
                "rotation",
                "visible",
                "opacity",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Basic Actions", [
                "MoveBy/To",
                "ScaleBy/To",
                "RotateBy/To",
                "Hide/Show",
                "FadeIn/FadeOut",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("More Actions", [
                "Reverse",
                "Sequence",
                "Repeat",
                "Spawn",
                "Accelerate, AccelDeccel,Speed",
                "Delay",
                "CallFunc",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Effects: Theory", [
                "FrameBuffer Object",
                "PixelBuffer Object",
                "ColorBuffer",
                "Grid / Tiled",
                "Camera",
                #"PONER SCREENSHOTS / SLIDES PARA EXPLICAR TEORIA",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("More Effects", [
                "Ripple3D",
                "Lens",
                "Shaky",
                "Flip",
                "OrbitCamera",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("More Effects II", [
                "Actions",
                "Lens + Jump",
                "Reuse Grid",
            ]),
        ),
        cocos.scene.Scene(
            BulletListLayer("Coming soon", [
                "Particle system",
                "Pymunk integration",
                "Drawing primitives",
            ]),
        ),

        cocos.scene.Scene(
            TitleSubTitleLayer("cocos2d", "http://www.cocos2d.org"),
        ),
    ]

    i = 0
    for s in scenes:
        s.add(get_color_layer(i), z=-1)
        i = i + 1

    transitions = [None] * (len(scenes) - 1)
    all_t = [
        'ZoomTransition',

        'FlipX3DTransition',
        'FlipY3DTransition', 'FlipAngular3DTransition',

        'TurnOffTilesTransition',

        'ShrinkGrowTransition',

        'FadeTRTransition', 'FadeBLTransition',
        'FadeUpTransition', 'FadeDownTransition',

        'SplitRowsTransition', 'SplitColsTransition',

        'RotoZoomTransition',

        'FadeTransition',

        'CornerMoveTransition',
        'EnvelopeTransition',

        'MoveInLTransition', 'MoveInRTransition',
        'MoveInBTransition', 'MoveInTTransition',

        'ShuffleTransition',
        'JumpZoomTransition',

    ]

    transitions = [getattr(cocos.scenes.transitions, all_t[i % len(all_t)])
                   for i in range(len(scenes) - 1)]

    TransitionControl(scenes, transitions)

    def color_name_scene(name, color):
        return cocos.scene.Scene(
            cocos.layer.ColorLayer(*color).add(
                cocos.text.Label(
                    name, (x / 2, y / 2),
                    font_name='Gill Sans', font_size=64,
                    anchor_x='center', anchor_y='center'
                )
            )
        )
    director.interpreter_locals["one"] = color_name_scene("one", (255, 0, 0, 255))
    director.interpreter_locals["two"] = color_name_scene("two", (0, 255, 0, 255))
    director.interpreter_locals["three"] = color_name_scene("three", (0, 0, 255, 255))

    director.interpreter_locals["grid_scene"] = demo_grid_effects.start()

    director.run(scenes[0])
