# mangle path to allow running the test from the tests folder
import sys
sys.path.insert(0, '..')

from collision import CollisionLayer, Circle

def test_collision_layer():
    st_obj1 = Circle((1,1), 5)
    st_obj2 = Circle((11,11), 5)
    st_obj3 = Circle((21,21), 5)
    st_obj4 = Circle((31,31), 5)

    def callback(*args, **kwargs):
        print 'args, kwargs', args, kwargs

    l = CollisionLayer(callback=callback)
    l.add(st_obj1, static=True)
    l.add(st_obj2, static=True)
    l.add(st_obj3, static=True)
    l.add(st_obj4, static=True)

    ac_obj = Circle((2,20), 5)
    l.add(ac_obj)
    l.step()

    ac_obj.position = (3,3)
    l.step()

def test_collision_layers():
    def callback(*args, **kwargs):
        print 'args, kwargs', args, kwargs

    l1 = CollisionLayer(callback=callback)
    l2 = CollisionLayer(callback=callback)

    st_obj1 = Circle((1,1), 5)
    st_obj2 = Circle((11,11), 5)
    ac_obj = Circle((2, 2), 5)

    l1.add(st_obj1, static=True)
    l1.add(ac_obj)

    l2.add(st_obj2, static=True)
    l2.add(ac_obj)

    l1.step()
    l2.step()

def main():
    test_collision_layer()
    test_collision_layers()

if __name__ == '__main__':
    main()
