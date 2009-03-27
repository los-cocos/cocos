

__all__ = ['Timer']

import pyglet
import director



class Timer(object):
    def __init__(self):

        x,y = director.director.get_window_size()
        x -= 0
        y -= 0

        self.running = True
        self.down = True

        pyglet.font.add_directory('.')
        self.label = pyglet.text.Label('00:00',
            font_name='DS-Digital Bold',
            font_size=32,
            bold='True',
            x=x,
            y=y,
            anchor_x='right', anchor_y='top')
        self.reset()

        pyglet.clock.schedule( self.step )
        
    def reset(self):
        self.time = 60 * 45
        self.label.color = (128,128,128,255)
    def step(self, dt):
        if self.running:
            if self.down:
                self.time -= dt
            else:
                self.time += dt

            if self.time < 3*60:
                self.down = False

            m, s = divmod(self.time, 60)
            self.label.text = '%02d:%02d' % (m, s)
            if self.time < 60*5:
                self.label.color = (255,0,0,255)

    def draw(self):
        self.label.draw()
