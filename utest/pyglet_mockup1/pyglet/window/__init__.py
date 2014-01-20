# window
from __future__ import division, print_function, unicode_literals


key = None


class Window(object):
    params = {
                'width': 640,
                'height': 480,
                'caption': None,
                'resizable': False,
                'style': 0,#WINDOW_STYLE_DEFAULT,
                'fullscreen': False,
                'visible': True,
                'vsync': True,
                'display': None,
                'screen': None,
                'config': None,
                'context': None
                }

    def __init__(self, **kwargs):
        self.values = dict(self.params)
        for k in kwargs:
            if k not in self.values:
                raise KeyError
            else:
                self.values[k] = kwargs[k]
        self.width = self.values['width']
        self.height = self.values['height']

    def push_handlers(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    
            
        
