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

import pytest

from cocos.director import director
from cocos.scene import Scene
director.init()

rec = []

class Test_run(object):
    
    def test_0_initial_state(self):
        assert director.scene is None
        assert director.next_scene is None
        assert len(director.scene_stack) == 0

    def test_1_run_once_and_twice(self):
        scene0 = Scene()
        old_stack = list(director.scene_stack)
        director.run(scene0)
        
        # check first run 
        assert director.scene is scene0
        assert director.next_scene is None
        assert director.scene_stack == old_stack 

        # a second run must be rejected, we don't want to call twice
        # event_loop.run
##        scene1 = Scene()
##
##        pytest.raises(DirectorRunTwiceException, "director.run(scene1)")  

        

    def test_2_push_delegates_to_on_push(self):
        scene0 = director.scene
        scene1 = Scene()
        
        # clear the mockup event recorder
        director._utest_recorded_events = []
        
        director.push(scene1)

        # ... and check it called on_push with the correct parameters
        evtype, args = director._utest_recorded_events[0]
        assert evtype == "on_push"
        assert args == (scene1,)

    def test_3_pop_delegates_to_on_pop(self):
        # clear the mockup event recorder
        director._utest_recorded_events = []

        director.pop()

        # ... and check it called on_pop with the correct parameters
        evtype, args = director._utest_recorded_events[0]
        assert evtype == "on_pop"
        assert args == ()

    def test_4_on_push_on_pop_and_current_scene(self):
        scene0 = director.scene
        scene1 = Scene()
        scene2 = Scene()

        director.on_push(scene1)
        
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        assert director.scene is scene1

        director.on_push(scene2)
        director.on_draw()

        assert director.scene is scene2

        director.on_pop()
        director.on_draw()

        assert director.scene is scene1

        director.on_pop()
        director.on_draw()

        assert director.scene is scene0
        
    def test_5_on_push_calls_on_enter_on_exit(self):
        global rec
        
        scene0 = Scene()
        scene1 = Scene()

        def on_exit():
            global rec
            rec.append('on_exit_called')

        def on_enter():
            global rec
            rec.append('on_enter_called')

        scene0.on_exit = on_exit
        scene1.on_enter = on_enter
            
        rec = []
        director.on_push(scene0)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        rec = []
        director.on_push(scene1)
        director.on_draw()

        assert rec[0]=='on_exit_called'
        assert rec[1]=='on_enter_called'

    def test_6_on_pop_calls_on_enter_on_exit(self):
        global rec
        
        scene0 = Scene()
        scene1 = Scene()

        def on_exit():
            global rec
            rec.append('on_exit_called')

        def on_enter():
            global rec
            rec.append('on_enter_called')

        scene0.on_enter = on_enter
        scene1.on_exit = on_exit
            
        rec = []
        director.on_push(scene0)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        director.on_push(scene1)
        director.on_draw()

        rec = []
        director.on_pop()
        director.on_draw()

        assert rec[0]=='on_exit_called'
        assert rec[1]=='on_enter_called'

    def test_7_replace(self):
        global rec
        
        scene0 = Scene()
        scene1 = Scene()
        scene2 = Scene()
        
        def on_exit():
            global rec
            rec.append('on_exit_called')

        def on_enter():
            global rec
            rec.append('on_enter_called')

        scene1.on_exit = on_exit
        scene2.on_enter = on_enter

        director.on_push(scene0)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()
        director.on_push(scene1)
        director.on_draw()

        rec = []
        director.replace(scene2)
        director.on_draw()

        # final scene ok
        assert director.scene is scene2
        
        # old scene on_exit called, new scene on_enter called
        assert rec[0]=='on_exit_called'
        assert rec[1]=='on_enter_called'

        # underlaying scene ok
        director.on_pop()
        director.on_draw()

        assert director.scene is scene0
        
##    def test_8_pop_from_empty_stack_termitate_app(self):


class TestRunningScene(object):
    """When a scene becomes the active scene the director
    must make sure that this scene has no parent anymore.
    This allows nodes to traverse up the tree and find the
    current running scene.
    """
    def test_0_replace(self):
        scene = Scene()
        director.run(scene)

        new_scene = Scene()
        new_scene.parent = not_None_value
        director.replace(new_scene)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        assert new_scene.parent is None

    def test_1_push(self):
        old_scene = Scene()
        director.run(old_scene)

        new_scene = Scene()
        new_scene.parent = not_None_value
        director.on_push(new_scene)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        assert new_scene.parent is None

    def test_2_pop(self):
        scene = Scene()
        director.run(scene)

        new_scene = Scene()
        director.on_push(new_scene)
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        scene.parent = not_None_value
        director.on_pop()
        # pyglet mockup 1 don't tickle on_draw, we call
        # directly so the push / pop operation completes
        director.on_draw()

        assert scene.parent is None

class NotNone(object):
    pass
not_None_value = NotNone()  