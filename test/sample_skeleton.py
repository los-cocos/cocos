from __future__ import division, print_function, unicode_literals

from cocos.skeleton import Bone, Skeleton
def Point2(*args): return args
root_bone = Bone('torso', 70, -180.0, Point2(0.00, 0.00)).add(
    Bone('brazo der', 40, 152.308491558, Point2(34.00, -67.00))    .add(
        Bone('antebrazo der', 40, 121.203546669, Point2(-4.00, -36.00))
)
).add(
    Bone('brazo izq', 40, 222.115898576, Point2(-10.00, -70.00))    .add(
        Bone('antebrazo izq', 40, 123.385130709, Point2(3.00, -47.00))
)
).add(
    Bone('muslo izq', 40, 225.0, Point2(-10.00, 5.00))    .add(
        Bone('pierna izq', 40, -60.5241109968, Point2(3.00, -44.00))
)
).add(
    Bone('muslo der', 40, 179.587915727, Point2(18.00, 5.00))    .add(
        Bone('pierna der', 40, -31.2908540886, Point2(4.00, -47.00))
)
).add(
    Bone('cabeza', 20, -9.90592089762, Point2(2.00, -94.00))
)


skeleton = Skeleton( root_bone )
