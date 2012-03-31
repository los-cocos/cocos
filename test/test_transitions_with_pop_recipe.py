# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *
from cocos.scenes import *

import time

last_current_scene = 123 #anything != None
def report(t):
    global stage, scene1, scene2
    print '\nscene change'
    print 'time:%4.3f' % t
    print 'len(director.scene_stack):', len(director.scene_stack)
    current_scene = director.scene
    if current_scene is None:
        s_scene = 'None'
    elif current_scene is scene1:
        s_scene = 'scene1'
    elif current_scene is scene2:
        s_scene = 'scene2'
    else:
        s_scene = 'transition scene'
    print 'current scene:', s_scene, current_scene


def sequencer(dt):
    global t0, stage, last_current_scene
    t = time.time() - t0
    if last_current_scene != director.scene:
        last_current_scene = director.scene
        report(t)
    if stage == "run scene1" and t > 2.0:
        stage = "transition to scene2"
        print "\n%4.3f begin %s" % (t, stage)
        director.push(FadeTransition( scene2, 1))
    elif stage == "transition to scene2" and t >4.0:
        stage = "transition to the top scene in the stack"
        print "\n%4.3f begin %s" % (t, stage)
        director.replace(FadeTransitionWithPop(director.scene_stack[0], 1))

# Warn: if the parent transition overrides the finish method of TransitionScene
# you may need some extra adjusts.
# As to the present cocos revision (r1069), the only concrete transition scene
# that overrides finish is ZoomTransition, and it works well with the recipe.
class FadeTransitionWithPop(FadeTransition):
    def finish(self):
        director.pop()

class ZoomTransitionWithPop(ZoomTransition):
    def finish(self):
        director.pop()

class FlipX3DTransitionWithPop(FlipX3DTransition):
    def finish(self):
        director.pop()


#recipe
TransitionWithPop ="""
TransitionWithPop recipe

While you can apply any cocos transition scene to the scene changes
director.run
director.replace
director.push

they are not builtin scene transitions to apply when doing director.pop

But is easy to implement in your app with the following recipe:

    1. select one of the stock scene transitions, to be found in
       cocos/scenes/transitions.py, say ZzzTransition

    2. define a subclass
        class ZzzTransitionWithPop(ZzzTransition):
            def finish():
                director.pop()

    3. instead of director.pop(), use
            director.replace( ZzzTransitionWithPop(
                              director.scene_stack[0], <other params>))
       where <other params> are the ones needed in the original transition,
       excluding the 'dst' argument

"""

def usage():
    print"""
    A demo for the recipe TransitionWithPop, which shows how to replace a dry
    director.pop() with a more appealing transition to the same scene.
    There is a short multiline string in the code telling the recipe.

    Along the time you will see :

    around t=0.000 : scene1 shows (screen full green)
    around t=2.000 : begins normal transition to scene2 (director.push(...))
    around t=3.000 : transitions ends, scene2 in full view (screen full violet)
    around t=4.000 : starts transition with pop
    around t=5.000 : transition ends, scene1 in full view

    In the console a report about current scene and director.scene_stack changes
    The final scene should be scene1 and len(director.scene_stack) should be the
    same as before the first transition initiated; that's 0 for cocos rev>1066
    """

class TestScene(cocos.scene.Scene):
    def __init__(self):
        super(TestScene, self).__init__()
        self.schedule(sequencer)

def main():
    usage()
    print "\nactual timeline:"
    director.init( resizable=True )
    scene1 = TestScene()
    scene1.add(ColorLayer(80,160,32,255))

    scene2 = TestScene()
    scene2.add(ColorLayer(120,32,120,255))

    stage = "before director.run"
    print "\n%4.3f %s" % (0.0, stage)
    report(0)

    t0 = time.time()
    stage = "run scene1"
    print "\n%4.3f begin %s" % (0.0, stage)
    director.run(scene1)

if __name__ == '__main__':
    main()
