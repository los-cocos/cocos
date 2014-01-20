from __future__ import division, print_function, unicode_literals

class Clock(object):
    def schedule(self, *args):
        pass
    def schedule_interval(self, *args):
        pass
    def schedule_interval_soft(self, *args):
        pass
    def schedule_once(self, *args):
        pass
    def unschedule(self, *args):
        pass

_default = Clock()

def schedule(func, *args, **kwargs):
    _default.schedule(func, *args, **kwargs)

def schedule_interval(func, interval, *args, **kwargs):
    _default.schedule_interval(func, interval, *args, **kwargs)

def schedule_interval_soft(func, interval, *args, **kwargs):
    _default.schedule_interval_soft(func, interval, *args, **kwargs)

def schedule_once(func, delay, *args, **kwargs):
    _default.schedule_once(func, delay, *args, **kwargs)

def unschedule(func):
    _default.unschedule(func)
