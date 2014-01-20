from __future__ import division, print_function, unicode_literals

# important: set cocos_utest=1 in the environment before run.
# that simplifies the pyglet mockup needed
# remember to erase or set to zero for normal runs
import os
assert os.environ['cocos_utest']

# set the desired pyglet mockup
import sys
sys.path.insert(0,'pyglet_mockup1')
import pyglet
assert pyglet.mock_level == 1 

import cocos
from cocos.director import director
from cocos.cocosnode import CocosNode
import cocos.actions as ac

import sys

director.init()

rec = []
next_done=0 #bitflags
class UAction(ac.Action):
##use actions names 1, 2 or '1', '2' ; then you instruct the .step method
##to set ._done using the global next_done
    def init(self, name):
        rec.append((name, 'init'))
        self.name = name

    def start(self):
        rec.append((self.name, 'start'))

    def step(self, dt):
        global rec, next_done
        rec.append((self.name, 'step', dt))
        if int(self.name) & next_done:
            print('setting %s _done to True'%self.name)
            self._done = True

    def stop(self):
        rec.append((self.name, 'stop'))

##    def done(self):
##        rec.append((self.name, 'done', 

class UIntervalAction(ac.IntervalAction):
    def init(self, name, duration):
        rec.append((name, 'init'))
        self.duration = duration
        self.name = name

    def start(self):
        rec.append((self.name, 'start'))

    def step(self, dt):
        rec.append((self.name, 'step', dt))
        super(UIntervalAction, self).step(dt)

    def update(self, fraction):
        rec.append((self.name, 'update', fraction))

    def stop(self):
        rec.append((self.name, 'stop'))

##    def done(self):
##        rec.append((self.name, 'done', 


class Test_sequence:
    """
    """
    def test_InstantAction_duration0_action(self):
        global rec
        node = CocosNode()
        name1 = '1'
        name2 = '2'
        duration1 = 0.0
        a = UIntervalAction(name1, duration1)
        b = UAction(name2)
        composite = a + b
        rec = []
        worker = node.do(composite)
        dt = 0.1
        node._step(dt)
        print(rec)
        assert rec[0] == (name1, 'start')
        assert rec[1] == (name1, 'step', dt)
        assert rec[2] == (name1, 'update', 1.0)
        assert rec[3] == (name1, 'stop')
        assert rec[4] == (name2, 'start')

        rec = []
        node._step(dt)
        for e in rec:
            assert e[0]==name2
