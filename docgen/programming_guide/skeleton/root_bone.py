from cocos.skeleton import Bone, Skeleton

def Point2(*args): return args

root_bone = Bone('body', 70, -180.0, Point2(0, 0))


skeleton = Skeleton( root_bone )