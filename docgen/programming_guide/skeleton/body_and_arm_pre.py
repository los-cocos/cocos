from cocos.skeleton import Bone, Skeleton

def Point2(*args): return args

root_bone = Bone('body', 70, -180.0, Point2(0, 0)).add(
    Bone('upper_arm', 30, 120, (0, -70)).add(
        Bone('lower_arm', 30, 30, (0, -30))
    )
)

skeleton = Skeleton(root_bone)