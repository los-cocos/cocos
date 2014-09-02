from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


import cocos
from cocos.director import director

import pyglet
from pyglet import font, image
from pyglet.gl import *
from pyglet.window import key

from cocos.actions import *
from cocos.layer import *
from cocos.scenes.transitions import *
from cocos.sprite import *
from cocos import text


class HelloWorld(Layer):

    def __init__(self):

        super(HelloWorld, self).__init__()

        # see pyglet documentation for help on this lines
        self.text = pyglet.text.Label(
            'Hello, World!', font_name='', font_size=32, x=100, y=240, batch=self.batch)


class BackgroundLayer(Layer):

    def __init__(self, path_name):
        super(BackgroundLayer, self).__init__()

        self.image = image.load(path_name)

    def draw(self):
        texture = self.image.texture

        rx = director.window.width - 2 * director._offset_x
        ry = director.window.height - 2 * director._offset_y

        tx = float(rx) / texture.width
        ty = float(ry) / texture.height

        glEnable(GL_TEXTURE_2D)
        glBindTexture(texture.target, texture.id)

        x, y = director.get_window_size()
        glBegin(gl.GL_QUADS)
        glTexCoord2d(0, 0)
        glVertex2f(0, 0)
        glTexCoord2d(0, ty)
        glVertex2f(0, y)
        glTexCoord2d(tx, ty)
        glVertex2f(x, y)
        glTexCoord2d(tx, 0)
        glVertex2f(x, 0)
        glEnd()

        glDisable(GL_TEXTURE_2D)


class SpriteLayer(Layer):
    pass


class SpriteMoveTo(SpriteLayer):

    def on_enter(self):
        super(SpriteMoveTo, self).on_enter()

        self.stop()

        sprite = Sprite("grossini.png", (20, 100))
        self.add(sprite)

        sprite.do(MoveTo((580, 100), 3))

    def on_exit(self):
        super(SpriteMoveTo, self).on_exit()
        [self.remove(c) for c in self.get_chidren()]


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
        self.scene_p += 1
        if self.scene_p >= len(self.scenes):
            self.scene_p = len(self.scenes) - 1
        else:
            self.transition(self.transitions[self.scene_p % len(self.transitions)])

    def prev_scene(self):
        self.scene_p -= 1
        if self.scene_p < 0:
            self.scene_p = 0
        else:
            self.transition()

    def transition(self, transition=None):
        if transition:
            director.replace(transition(
                self.scenes[self.scene_p],
                duration=1
            )
            )
        else:
            director.replace(self.scenes[self.scene_p])

    def on_key_press(self, keyp, mod):
        if keyp in (key.PAGEDOWN,):
            self.next_scene()
        elif keyp in (key.PAGEUP,):
            self.prev_scene()


class RunScene(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, target):
        super(RunScene, self).__init__()

        self.target = target

    def on_key_press(self, keyp, mod):
        if keyp in (key.F1,):
            director.push(self.target)


class ControlLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_enter(self):
        super(ControlLayer, self).on_enter()

        ft_title = font.load("Arial", 32)
        ft_subtitle = font.load("Arial", 18)
        ft_help = font.load("Arial", 16)

        self.text_title = font.Text(ft_title, "Transition Demos",
                                    x=5,
                                    y=480,
                                    anchor_x=font.Text.LEFT,
                                    anchor_y=font.Text.TOP)

        self.text_subtitle = font.Text(ft_subtitle, transition_list[current_transition].__name__,
                                       x=5,
                                       y=400,
                                       anchor_x=font.Text.LEFT,
                                       anchor_y=font.Text.TOP)

        self.text_help = font.Text(ft_help, "Press LEFT / RIGHT for prev/next example, "
                                   "ENTER to restart example",
                                   x=320,
                                   y=20,
                                   anchor_x=font.Text.CENTER,
                                   anchor_y=font.Text.CENTER)

    def step(self, df):
        self.text_help.draw()

        self.text_subtitle.text = transition_list[current_transition].__name__
        self.text_subtitle.draw()
        self.text_title.draw()

    def on_key_press(self, k, m):
        global current_transition, control_p
        if k == key.LEFT:
            current_transition = (current_transition - 1) % len(transition_list)
        if k == key.RIGHT:
            current_transition = (current_transition + 1) % len(transition_list)
        if k == key.ENTER:
            director.replace(transition_list[current_transition](
                control_list[control_p],
                (control_list[(control_p + 1) % len(control_list)]),
                2)
            )
            control_p = (control_p + 1) % len(control_list)
            return True
        if k == key.ESCAPE:
            director.scene.end()
            return True


class GrossiniLayer(cocos.layer.Layer):

    def __init__(self):
        super(GrossiniLayer, self).__init__()

        g = Sprite('grossini.png', (320, 240))

        self.add(g)

        rot = Rotate(180, 5)

        g.do(Repeat(rot))


class GrossiniLayer2(cocos.layer.Layer):

    def __init__(self):
        super(GrossiniLayer2, self).__init__()

        rot = Rotate(180, 5)

        g = Sprite('grossinis_sister1.png', (490, 240))
        self.add(g)
        g.do(Repeat(rot))

        g = Sprite('grossinis_sister2.png', (150, 240))
        self.add(g)
        g.do(Repeat(rot))

if __name__ == "__main__":
    aspect = 1280 / float(800)
    director.init(resizable=True, width=640, height=480)
    director.window.set_fullscreen(False)
    x, y = director.get_window_size()
    #background = BackgroundLayer("background.png")
    #background = BackgroundLayer("coconut.jpg")
    background = cocos.layer.ColorLayer(0, 0, 0, 255)

    transition_list = [
        JumpZoomTransition
    ]
    current_transition = 0

    scenes = [
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          TitleSubTitleLayer("cocos2d", "a 2d game library"),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("cocos2d", [
                              "una libreria para hacer juegos 2d",
                              "programando en python",
                              ])
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Juegos y python", [
                              "Juegos en un lenguaje interpretado?",
                              "Depende del juego",
                              "Hay mucho que se puede hacer en 30ms",
                              ])
                          ),


        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Historia", [
                              "2000 : pygame",
                              "2005 : pyweek",
                              "2006 : pyglet",
                              "2008 : cocos2d"
                              ])
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Features", [
                              "Control de flujo",
                              "Sprites",
                              "Acciones",
                              "Efectos",
                              "Transiciones",
                              "Menus",
                              ])
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Features (2)", [
                              "Texto / HTML",
                              "Tiles"
                              "Bien Documentado",
                              "Interprete de python incluido",
                              "Licencia BSD",
                              "Basado en pyglet",
                              "OpenGL",
                              ]),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Conceptos", []).add(
                              Sprite("scene_sp.png", (x // 2, 100))),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Documentacion", [
                              "Tutoriales en video",
                              "Guia de programacion (1KLOT)",
                              "Documentacion de api [casi] completa",
                              "5KLOC de tests",
                              "Los test son ejemplos funcionales",
                              "FAQ [en progreso]",
                              ]),
                          ),

        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Comunidad", [
                              "5 juegos terminados",
                              "Varios proyectos en desarrollo",
                              "Contribuidores de todo el mundo",
                              "Lista de correo 'funcional'",
                              ]),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Control De Flujo", []),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Sprites", []),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Acciones", []),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Efectos", []),
                          ),
        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          BulletListLayer("Transiciones", []),
                          ),

        cocos.scene.Scene(cocos.layer.ColorLayer(0, 0, 0, 255),
                          TitleSubTitleLayer("cocos2d", "http://www.cocos2d.org"),
                          ),
    ]
    transitions = [None] * (len(scenes) - 1)
    all_t = ['RotoZoomTransition', 'JumpZoomTransition',

             'SlideInLTransition', 'SlideInRTransition',
             'SlideInBTransition', 'SlideInTTransition',

             'FlipX3DTransition', 'FlipY3DTransition', 'FlipAngular3DTransition',

             'ShuffleTransition',
             'TurnOffTilesTransition',
             'FadeTRTransition', 'FadeBLTransition',
             'FadeUpTransition', 'FadeDownTransition',

             'ShrinkGrowTransition',
             'CornerMoveTransition',
             'EnvelopeTransition',

             'SplitRowsTransition', 'SplitColsTransition',

             'FadeTransition', ]

    transitions = [getattr(cocos.scenes.transitions, all_t[i % len(all_t)])
                   for i in range(len(scenes) - 1)]

    TransitionControl(scenes, transitions)

    def color_name_scene(name, color):
        return cocos.scene.Scene(
            cocos.layer.ColorLayer(*color).add(
                cocos.text.Label(
                    name, (x // 2, y // 2),
                    font_name='Gill Sans', font_size=64,
                    anchor_x='center', anchor_y='center'
                )
            )
        )
    director.interpreter_locals["uno"] = color_name_scene("uno", (255, 0, 0, 255))
    director.interpreter_locals["dos"] = color_name_scene("dos", (0, 255, 0, 255))
    director.interpreter_locals["tres"] = color_name_scene("tres", (0, 0, 255, 255))

    director.run(scenes[0])
