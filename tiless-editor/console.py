
__all__ = ['Console']

from cocos.director import director
from cocos.layer.python_interpreter import PythonInterpreterLayer


class Console(PythonInterpreterLayer):
    def init_config(self):
        super(Console, self).init_config()
        x,y = director.get_window_size()
        self.cfg['background.height'] = y / 3
        self.cfg['background.y'] = y / 3 * 2

    #################
    # Layer Events
    #################
    def on_enter(self):
        super(Console, self).on_enter()
        vw, vh = director.get_window_size()
        self.on_resize(vw, vh / 3)

    def on_resize(self, width, height):
        vw, vh = director.get_window_size()
        self.layout.begin_update()
        self.layout.height = vh / 3
        self.layout.x = 2
        self.layout.width = vw - 4
        self.layout.y = vh
        self.layout.end_update()

        # XXX: hack
        x,y = director.window.width, director.window.height
        self.layout.top_group._scissor_width = x - 4

        self.caret.position = len(self.document.text)
