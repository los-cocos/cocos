
import sys
import os
import code

import pyglet
from pyglet import graphics
from pyglet import text
from pyglet.text import caret, document, layout

import cocos
from cocos.director import director
from cocos.layer.base_layers import Layer
from cocos.layer.util_layers import ColorLayer

__all__ = ['Console']

class Output:
    def __init__(self, display, realstdout):
        self.out = display
        self.realstdout = realstdout
        self.data = ''

    def write(self, data):
        self.out(data)

class Interpreter(code.InteractiveInterpreter):
    def __init__(self, locals, display):
        self.write = display
        code.InteractiveInterpreter.__init__(self, locals=locals)

    def execute(self, input):
        old_stdout = sys.stdout
        sys.stdout = Output(self.write, old_stdout)
        more = self.runsource(input)
        sys.stdout = old_stdout
        return more

class Console(Layer):
    '''Runs an interactive Python interpreter as a child `Layer` of the current `Scene`.
    '''

    cfg = {'code.font_name':'Arial',
            'code.font_size':12,
            'code.color':(255,255,255,255),
            'caret.color':(255,255,255),
            }

    name = 'py'

    prompt = ">>> "             #: python prompt
    prompt_more = "... "        #: python 'more' prompt
    doing_more = False

    is_event_handler = True     #: enable pyglet's events

    def __init__(self, locals):
        super(Console, self).__init__()
        x,y = director.get_window_size()
        
        bg = ColorLayer( 32,32,32,192, height=y/3)
        bg.y = y/3*2
        self.add(bg, z=-1)
        self.content = self.prompt
        self.interpreter = Interpreter(locals, self._write)

        self.current_input = []

        self.history = ['']
        self.history_pos = 0


        vw,vh = cocos.director.director.get_window_size()

        # format the code
        self.document = document.FormattedDocument(self.content)
        self.document.set_style(0, len(self.document.text), {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })

        self.batch = graphics.Batch()

        # generate the document
        self.layout = layout.IncrementalTextLayout(self.document,
            vw, vh, multiline=True, batch=self.batch)
        self.layout.anchor_y= 'top'

        self.caret = caret.Caret(self.layout, color=self.cfg['caret.color'] )
        self.caret.on_activate()

        self.on_resize(vw, vh/3)

        self.start_of_line = len(self.document.text)

    def on_resize(self, x, y):
        vw, vh = director.get_window_size()
        self.layout.begin_update()
        self.layout.height = vh/3
        self.layout.x = 2
        self.layout.width = vw - 4
        self.layout.y = vh
        self.layout.end_update()

        # XXX: hack
        x,y = director.window.width, director.window.height
        self.layout.top_group._scissor_width=x-4

        self.caret.position = len(self.document.text)

    def evaluate(self, input, first_line=True):
        return self.interpreter.execute(input)
        
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            return self.caret.on_text('\t')
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.NUM_ENTER):
            # write the newline
            self._write('\n')

            line = self.document.text[self.start_of_line:]
            self.current_input.append(line)
            self.history_pos = len(self.history)
            if line.strip():
                self.history[self.history_pos-1] = line.strip()
                self.history.append('')

            more = False
            if not self.doing_more:
                self.evaluate('\n'.join(self.current_input))

            if self.doing_more and not line.strip():
                self.doing_more = False
                self.evaluate('\n'.join(self.current_input), False)

            more = more or self.doing_more
            if not more:
                self.current_input = []
                self._write(self.prompt)
            else:
                self.doing_more = True
                self._write(self.prompt_more)
            self.start_of_line = len(self.document.text)
            self.caret.position = len(self.document.text)
        elif symbol == pyglet.window.key.SPACE:
            pass
        else:
            return pyglet.event.EVENT_UNHANDLED
        return pyglet.event.EVENT_HANDLED

    def on_text(self, symbol):
        # squash carriage return - we already handle them above
        if symbol == '\r':
            return pyglet.event.EVENT_HANDLED
        elif symbol == '`':
            return pyglet.event.EVENT_HANDLED
        self._scroll_to_bottom()
        return self.caret.on_text(symbol)

    def on_text_motion(self, motion):
        at_sol = self.caret.position == self.start_of_line

        if motion == pyglet.window.key.MOTION_UP:
            # move backward in history, storing the current line of input
            # if we're at the very end of time
            line = self.document.text[self.start_of_line:]
            if self.history_pos == len(self.history)-1:
                self.history[self.history_pos] = line
            self.history_pos = max(0, self.history_pos-1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
            self.caret.position = len(self.document.text)
        elif motion == pyglet.window.key.MOTION_DOWN:
            # move forward in the history
            self.history_pos = min(len(self.history)-1, self.history_pos+1)
            self.document.delete_text(self.start_of_line,
                len(self.document.text))
            self._write(self.history[self.history_pos])
            self.caret.position = len(self.document.text)
        elif motion == pyglet.window.key.MOTION_BACKSPACE:
            # can't delete the prompt
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_LEFT:
            # can't move back beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        elif motion == pyglet.window.key.MOTION_PREVIOUS_WORD:
            # can't move back word beyond start of line
            if not at_sol:
                return self.caret.on_text_motion(motion)
        else:
            return self.caret.on_text_motion(motion)
        return pyglet.event.EVENT_HANDLED

    def _write(self, s):
        self.document.insert_text(len(self.document.text), s, {
            'font_name': self.cfg['code.font_name'],
            'font_size': self.cfg['code.font_size'],
            'color': self.cfg['code.color'],
        })
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        # on key press always move the view to the bottom of the screen
        x, y = director.get_window_size()
        if self.layout.height < self.layout.content_height:
            self.layout.anchor_y= 'top'
            self.layout.y = y
            self.layout.view_y = 0
        if self.caret.position < self.start_of_line:
            self.caret.position = len(self.document.text)

    def draw(self):
        super( Console, self).draw()
        self.batch.draw()
