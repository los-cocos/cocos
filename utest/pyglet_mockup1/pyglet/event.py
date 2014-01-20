from __future__ import division, print_function, unicode_literals

# event
class EventDispatcher(object):
    @classmethod
    def register_event_type(cls, ev_name):
        pass

    def __init__(self, *args, **kwargs):
        self._utest_recorded_events = []

    def dispatch_event(self, event_type, *args):
        self._utest_recorded_events.append((event_type, args))
        
        
