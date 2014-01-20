from __future__ import division, print_function, unicode_literals

# unit test to run with py.test
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

from cocos.director import director
from cocos.cocosnode import CocosNode
import cocos.actions as ac

fe = 1.0e-6 # used to compare floats; a==b <-> abs(a-b)<fe

director.init()

rec = []

class UIntervalAction(ac.IntervalAction):
    # Interval action that records calls to its methods
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



# test AccelDecel operator

class Test_AccelDeccel:
    def setUp(self):
        global rec
        rec = []
        
    def test_update_1_called(self):
        global rec
        duration = 2.0
        original_action = UIntervalAction('original', duration)
        modified_action = ac.AccelDeccel(original_action)

        node = CocosNode()
        node.do(modified_action)
        dt = duration * 1.0
        rec = []
        node._step(dt)
        print('rec:', rec)
        update_record = rec[-1]
        assert update_record[1] == 'update'
        assert update_record[2] == 1.0

# con la formula de cocos 0.5 aplicando accel-decel nos da
#   0.0 -> 0.0024726231566347743
#   1.0 -> 0.99752737684336534
