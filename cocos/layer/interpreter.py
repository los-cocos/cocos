
__all__ = ['InterpreterLayer']

import pyglet

from pyglet.event import EventDispatcher
from pyglet.text import caret, document, layout
from pyglet.window import key

from cocos.director import director
from cocos.layer.base_layers import Layer
from cocos.layer.util_layers import ColorLayer
from cocos.interpreter import Interpreter


class InterpreterLayer(Layer, EventDispatcher):
    name = "py"

    prompt = ">>> "             #: first line prompt
    prompt_more = "... "        #: second line prompt

    history_file = '.cocos_history'
    history_size = 100

    is_event_handler = True     #: enable pyglet's events

    def __init__(self, ns_locals=None):
        super(InterpreterLayer, self).__init__()
        self.init_config()
        self.init_background()
        self.init_interpreter(ns_locals)
        self.init_text()

    def init_config(self):
        self.cfg = {'code.font_name': 'Arial',
                    'code.font_size': 12,
                    'code.color': (255, 255,255, 255),
                    'caret.color': (255, 255, 255),
                    'background.color': (32, 32, 32, 192),
                    'background.height': None,
                    'background.y': None,
                    }

    def init_background(self):
        color = self.cfg['background.color']
        height = self.cfg['background.height']
        bg_y = self.cfg['background.y']

        bg = ColorLayer(*color, height=height)
        if bg_y is not None:
            bg.y = bg_y
        self.add(bg, z=-1)

    def init_interpreter(self, ns_locals=None):
        if ns_locals is None:
            ns_locals = director.interpreter_locals
            ns_locals['self'] = self
        self.interpreter = Interpreter(stdout=self, ns_locals=ns_locals,
                                       history_file=self.history_file,
                                       history_size=self.history_size)

    def init_text(self):
        self.content = self.prompt
        self.prompt_start = 0
        self.prompt_end = len(self.content)

        # document
        self.document = document.FormattedDocument(self.content)
        self.document.set_style(0, len(self.document.text), {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })

        # batch
        self.batch = pyglet.graphics.Batch()

        # layout
        vw, vh = director.get_window_size()
        self.layout = layout.IncrementalTextLayout(self.document, vw, vh,
                                                   multiline=True,
                                                   batch=self.batch)
        self.layout.anchor_y = 'top'

        # caret
        self.caret = caret.Caret(self.layout, color=self.cfg['caret.color'] )
        self.caret.on_activate()


    #################
    # File API
    #################
    def write(self, text):
        self.layout.begin_update()
        self.document.insert_text(len(self.document.text), text, {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })
        self.layout.end_update()

    #################
    # Layer API
    #################
    def draw(self):
        super(InterpreterLayer, self).draw()
        self.batch.draw()

    def set_command(self, text):
        self.document.delete_text(self.prompt_end, len(self.document.text))
        self.write(text)
        self.caret.position = len(self.document.text)

    def get_command(self):
        return self.document.text[self.prompt_end:].strip()

    def write_prompt(self, first_line=True):
        self.prompt_start = len(self.document.text)
        if first_line:
            self.write(self.prompt)
        else:
            self.write(self.prompt_more)
        self.prompt_end = len(self.document.text)
        self.caret.position = len(self.document.text)

    #################
    # Layer Events
    #################
    def on_enter(self):
        super(InterpreterLayer, self).on_enter()
        vw, vh = director.get_window_size()
        self.on_resize(vw, vh)

    def on_resize(self, width, height):
        vw, vh = director.get_window_size()
        self.layout.begin_update()
        self.layout.height = vh
        self.layout.x = 2
        self.layout.width = vw - 4
        self.layout.y = vh
        self.layout.end_update()

        # XXX: hack
        x, y = director.window.width, director.window.height
        self.layout.top_group._scissor_width = x - 4

        self.caret.position = len(self.document.text)

    def on_exit(self):
        self.content = self.document.text
        self.interpreter.on_exit()
        super(InterpreterLayer, self).on_exit()

    #################
    # Text Events
    #################
    def on_text(self, text):
        if text == '\r':
            self.dispatch_event('on_command', self.get_command())
        else:
            self.caret.on_text(text)

    def on_text_motion(self, motion):
        if (motion == key.MOTION_LEFT
            and self.caret.position > self.prompt_end):
            self.caret.on_text_motion(motion)
        elif (motion == key.BACKSPACE
              and self.caret.position > self.prompt_end):
            self.caret.on_text_motion(motion)
        elif motion == key.MOTION_RIGHT:
            self.caret.on_text_motion(motion)
        elif motion == key.MOTION_DELETE:
            self.caret.on_text_motion(motion)
        elif motion == key.MOTION_UP:
            self.interpreter.dispatch_event('on_history_prev', self.get_command())
        elif motion == key.MOTION_DOWN:
            self.interpreter.dispatch_event('on_history_next', self.get_command())
        elif motion == key.MOTION_BEGINNING_OF_LINE:
            self.caret.position = self.prompt_start
        elif motion == key.MOTION_END_OF_LINE:
            self.caret.position = len(self.document.text)

    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select (motion)

    #################
    # Mouse Events
    #################
    def on_mouse_scroll(self, x, y, dx, dy):
        self.layout.view_y += dy * 16

    def on_mouse_press(self, x, y, button, modifiers):
        self.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    #################
    # Keyboard Events
    #################
    def on_key_press(self, symbol, modifiers):
        if symbol == key.A and modifiers & key.MOD_ACCEL:
            # go to start of line
            self.caret.position = self.prompt_end
        elif symbol == key.E and modifiers & key.MOD_ACCEL:
            # got to end of line
            self.caret.position = len(self.document.text)
        elif symbol == key.U and modifiers & key.MOD_ACCEL:
            # remove line
            self.document.delete_text(self.prompt_end, self.caret.position)
            self.caret.position = self.prompt_end
#        elif symbol == key.L and modifiers and key.MOD_ACCEL:
#            # clear screen
#            self.document.delete_text(0, self.prompt_start)
#            self.prompt_end -= self.prompt_start
#            self.prompt_start -= self.prompt_start
        elif symbol == key.TAB:
            self.dispatch_event('on_completion', self.get_command())
        elif symbol == key.PAGEUP:
            self.layout.view_y += 16
        elif symbol == key.PAGEDOWN:
            self.layout.view_y -= 16
        else:
            return pyglet.event.EVENT_UNHANDLED
        return pyglet.event.EVENT_HANDLED

    #################
    # Command Events
    #################
    def on_command(self, command):
        self.write('\n')
        self.interpreter.dispatch_event('on_command', command)

    def on_command_done(self):
        self.write_prompt()

    def on_completion(self, command):
        # recover the original command (the part before the first newline)
        command = command.split('\n')[0]
        # clear the command line
        self.document.delete_text(self.prompt_end, len(self.document.text))
        # request completion
        self.interpreter.dispatch_event('on_completion', command)

    def on_completed(self, completed, output):
        # write out the result of completion
        self.write(completed)
        self.caret.position = len(self.document.text)

        command = self.get_command()
        if command == completed:
            # there are many possibilities (completion was ambiguous)
            # so write out all possibilities
            self.write(output)

    def on_set_command(self, command):
        self.set_command(command)

InterpreterLayer.register_event_type('on_command')
InterpreterLayer.register_event_type('on_command_done')
InterpreterLayer.register_event_type('on_completion')
InterpreterLayer.register_event_type('on_completed')
InterpreterLayer.register_event_type('on_set_command')
