from cocos.skeleton import Bone, Skeleton

def Point2(*args): return args

root_bone = Bone('body', 70, -180.0, Point2(0.00, 0.00)).add(
    Bone('upper_arm', 30, 130.782409248, Point2(31.00, -67.00))    .add(
        Bone('lower_arm', 30, 83.3315481551, Point2(-2.00, -37.00))
)
)


skeleton = Skeleton( root_bone )