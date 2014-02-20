from __future__ import division, print_function, unicode_literals

import cocos.euclid as eu
import unittest

import copy
try:
    import cPickle as pickle
except Exception:
    import pickle
import io

class Test_Vector2(unittest.TestCase):
    def test_instantiate(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)
        self.assertEqual(repr(v2), "Vector2(%.2f, %.2f)" % xy)

    def test_instantiate_default(self):
        v2 = eu.Vector2()
        self.assertEqual(repr(v2), "Vector2(%.2f, %.2f)" % (0, 0))

    def test_copy(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)

        copied = v2.__copy__()
        self.assertEqual(repr(v2), repr(copied))
        self.assertFalse(copied is v2)

    def test_deepcopy(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)

        copied = copy.deepcopy(v2)
        self.assertEqual(repr(v2), repr(copied))
        self.assertFalse(copied is v2)
        self.assertFalse(hasattr(copied, '__dict__'))

    # they need __getstate__  and  __setstate__  implemented
    def test_pickle_lower_protocols(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)

        s = pickle.dumps(v2, 0)
        copied = pickle.loads(s)
        self.assertEqual(repr(v2), repr(copied))
        self.assertFalse(copied is v2)        
        self.assertFalse(hasattr(copied, '__dict__'))

        s = pickle.dumps(v2, 1)
        copied = pickle.loads(s)
        self.assertEqual(repr(v2), repr(copied))
        self.assertFalse(copied is v2)        
        self.assertFalse(hasattr(copied, '__dict__'))

    # don't need __getstate__ / __setstate__ implemented 
    def test_pickle_protocol_2(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)

        s = pickle.dumps(v2, 2)
        copied = pickle.loads(s)
        self.assertEqual(repr(v2), repr(copied))
        self.assertFalse(copied is v2)        
        self.assertFalse(hasattr(copied, '__dict__'))

    def test_eq_v2(self):
        xy = (1.0, 2.0)
        self.assertTrue(eu.Vector2(*xy), eu.Vector2(*xy))

        other = (1.0, 3.0)
        self.assertTrue( eu.Vector2(*xy) != eu.Vector2(*other))

    def test_eq_tuple(self):
        xy = (1.0, 2.0)
        self.assertEqual(eu.Vector2(*xy), xy)

        other = (1.0, 2.0, 3.0)
        self.assertRaises( AssertionError,
                           lambda a, b: a == b, eu.Vector2(*xy), other)

        other = 1.0
        self.assertRaises( AssertionError,
                           lambda a, b: a == b, eu.Vector2(*xy), other)

    def test_len(self):
        xy = (1.0, 2.0)
        self.assertEqual(len(eu.Vector2(*xy)), 2)
        
    def test_index_access__get(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)
        self.assertEqual( v2[0], xy[0])
        self.assertEqual(v2[1], xy[1])
        self.assertRaises(IndexError,
                          lambda a: v2[a], 2)

    def test_index_access__set(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)
        v2[0] = 7.0
        self.assertEqual(repr(v2), "Vector2(%.2f, %.2f)" % (7.0, 2.0))
        v2[1] = 8.0
        self.assertEqual(repr(v2), "Vector2(%.2f, %.2f)" % (7.0, 8.0))
        def f():
            v2[2] = 9.0 
        self.assertRaises(IndexError, f)

    def test_iter(self):
        xy = [1.0, 2.0]
        v2 = eu.Vector2(*xy)
        sequence = [e for e in v2]
        self.assertEqual(sequence, xy)
        
    def test_swizzle_get(self):
        xy = (1.0, 2.0)
        v2 = eu.Vector2(*xy)
        self.assertEqual(v2.x, xy[0])
        self.assertEqual(v2.y, xy[1])
        self.assertEqual(v2.xy, xy)
        self.assertEqual(v2.yx, (xy[1], xy[0]))

        exception = None
        try:
            v2.z == 11.0
        except Exception as a:
            exception = a
        assert isinstance(exception, AttributeError)
        
    def test_sub__v2_v2(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)
        self.assertEqual(va-vb, eu.Vector2(2.0, 5.0))
        
    def test_sub__v2_t2(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)
        self.assertEqual(va-b, eu.Vector2(2.0, 5.0))

    def test_rsub__t2_v2(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)
        self.assertEqual(a-vb, eu.Vector2(2.0, 5.0))

    # in py3 or py2 with 'from __future__ import division'
    # else the integer division is used, as in old euclid.py
    def test_default_div(self):
        xy = (4, 7)
        v2 = eu.Vector2(*xy)

        c = v2 / 3
        self.assertTrue(c.x == 4.0 / 3, c.y == 7.0 / 3)

    def test_integer_division(self):
        xy = (4, 7)
        v2 = eu.Vector2(*xy)

        c = v2 // 3
        self.assertTrue(c.x == 4 // 3, c.y == 7 // 3)
    
    def test_add(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)

        self.assertTrue(isinstance(va+vb, eu.Vector2))
        self.assertEqual(repr(va+vb), 'Vector2(%.2f, %.2f)' % (4.0, 9.0))

        c = (11.0, 17.0)
        pc = eu.Point2(*c)
        d = (13.0, 23.0)
        pd = eu.Point2(*d)
        
        self.assertTrue(isinstance(va+pc, eu.Point2))
        self.assertTrue(isinstance(pc+pd, eu.Vector2))

        self.assertTrue(isinstance(va + b, eu.Vector2))
        self.assertEqual(va + vb, va + b)

    def test_inplace_add(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)
        va += b
        self.assertEqual((va.x, va.y) , (4.0, 9.0))

        va = eu.Vector2(*a)
        va += b
        self.assertEqual((va.x, va.y) , (4.0, 9.0))
        


class Test_Vector3(unittest.TestCase):

    def test_instantiate(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)
        self.assertEqual(repr(v3), "Vector3(%.2f, %.2f, %.2f)" % xyz)

    def test_instantiate_default(self):
        v3 = eu.Vector3()
        self.assertEqual(repr(v3), "Vector3(%.2f, %.2f, %.2f)" % (0, 0, 0))

    def test_copy(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)

        copied = v3.__copy__()
        self.assertEqual(repr(v3), repr(copied))
        self.assertFalse(copied is v3)

    def test_deepcopy(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)

        copied = copy.deepcopy(v3)
        self.assertEqual(repr(v3), repr(copied))
        self.assertFalse(copied is v3)        

    # they need __getstate__  and  __setstate__  implemented
    def test_pickle_lower_protocols(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)

        s = pickle.dumps(v3, 0)
        copied = pickle.loads(s)
        self.assertEqual(repr(v3), repr(copied))
        self.assertFalse(copied is v3)        
        self.assertFalse(hasattr(copied, '__dict__'))

        s = pickle.dumps(v3, 1)
        copied = pickle.loads(s)
        self.assertEqual(repr(v3), repr(copied))
        self.assertFalse(copied is v3)        
        self.assertFalse(hasattr(copied, '__dict__'))

    # no need for __getstate__ and __setstate__
    def test_pickle_protocol_2(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)

        s = pickle.dumps(v3, 2)
        copied = pickle.loads(s)
        self.assertEqual(repr(v3), repr(copied))
        self.assertFalse(copied is v3)        

    def test_eq_v3(self):
        xyz = (1.0, 2.0, 3.0)
        self.assertTrue(eu.Vector3(*xyz), eu.Vector3(*xyz))

        other = (1.0, 3.0, 7.0)
        self.assertTrue( eu.Vector3(*xyz) != eu.Vector3(*other))

    def test_eq_tuple(self):
        xyz = (1.0, 2.0, 3.0)
        self.assertEqual(eu.Vector3(*xyz), xyz)

        other = (1.0, 2.0, 3.0, 4.0)
        self.assertRaises( AssertionError,
                           lambda a, b: a == b, eu.Vector3(*xyz), other)

        other = 1.0
        self.assertRaises( AssertionError,
                           lambda a, b: a == b, eu.Vector3(*xyz), other)

    def test_len(self):
        xyz = (1.0, 2.0, 3.0)
        self.assertEqual(len(eu.Vector3(*xyz)), 3)
        
    def test_index_access__get(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)
        self.assertEqual( v3[0], xyz[0])
        self.assertEqual(v3[1], xyz[1])
        self.assertEqual(v3[2], xyz[2])
        self.assertRaises(IndexError,
                          lambda a: v3[a], 3)

    def test_index_access__set(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)
        v3[0] = 7.0
        self.assertEqual(repr(v3), "Vector3(%.2f, %.2f, %.2f)" % (7.0, 2.0, 3.0))
        v3[1] = 8.0
        self.assertEqual(repr(v3), "Vector3(%.2f, %.2f, %.2f)" % (7.0, 8.0, 3.0))
        v3[2] = 9.0
        self.assertEqual(repr(v3), "Vector3(%.2f, %.2f, %.2f)" % (7.0, 8.0, 9.0))
        def f():
            v3[3] = 9.0 
        self.assertRaises(IndexError, f)

    def test_iter(self):
        xyz = [1.0, 2.0, 3.0]
        v3 = eu.Vector3(*xyz)
        sequence = [e for e in v3]
        self.assertEqual(sequence, xyz)
        
    def test_swizzle_get(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Vector3(*xyz)
        self.assertEqual(v3.x, xyz[0])
        self.assertEqual(v3.y, xyz[1])
        self.assertEqual(v3.z, xyz[2])

        self.assertEqual(v3.xy, (xyz[0], xyz[1]))
        self.assertEqual(v3.xz, (xyz[0], xyz[2]))
        self.assertEqual(v3.yz, (xyz[1], xyz[2]))

        self.assertEqual(v3.yx, (xyz[1], xyz[0]))
        self.assertEqual(v3.zx, (xyz[2], xyz[0]))
        self.assertEqual(v3.zy, (xyz[2], xyz[1]))

        self.assertEqual(v3.xyz, xyz)
        self.assertEqual(v3.xzy, (xyz[0], xyz[2], xyz[1]) )
        self.assertEqual(v3.zyx, (xyz[2], xyz[1], xyz[0]) )
        self.assertEqual(v3.zxy, (xyz[2], xyz[0], xyz[1]) )
        self.assertEqual(v3.yxz, (xyz[1], xyz[0], xyz[2]) )
        self.assertEqual(v3.yzx, (xyz[1], xyz[2], xyz[0]) )

        exception = None
        try:
            v3.u == 11.0
        except Exception as a:
            exception = a
        assert isinstance(exception, AttributeError)

    def test_sub__v3_v3(self):
        a = (3.0, 7.0, 9.0)
        b = (1.0, 2.0, 3.0)
        va = eu.Vector3(*a)
        vb = eu.Vector3(*b)
        self.assertEqual(va-vb, eu.Vector3(2.0, 5.0, 6.0))
        
    def test_sub__v3_t3(self):
        a = (3.0, 7.0, 9.0)
        b = (1.0, 2.0, 3.0)
        va = eu.Vector3(*a)
        vb = eu.Vector3(*b)
        self.assertEqual(va-b, eu.Vector3(2.0, 5.0, 6.0))

    def test_rsub__t3_v3(self):
        a = (3.0, 7.0, 9.0)
        b = (1.0, 2.0, 3.0)
        va = eu.Vector3(*a)
        vb = eu.Vector3(*b)
        self.assertEqual(a-vb, eu.Vector3(2.0, 5.0, 6.0))

class Test_Point2(unittest.TestCase):
    def test_swizzle_get(self):
        xy = (1.0, 2.0)
        v2 = eu.Point2(*xy)
        self.assertEqual(v2.x, xy[0])
        self.assertEqual(v2.y, xy[1])
        self.assertEqual(v2.xy, xy)
        self.assertEqual(v2.yx, (xy[1], xy[0]))

        exception = None
        try:
            v2.z == 11.0
        except Exception as a:
            exception = a
        assert isinstance(exception, AttributeError)

class Test_Point3(unittest.TestCase):
    def test_swizzle_get(self):
        xyz = (1.0, 2.0, 3.0)
        v3 = eu.Point3(*xyz)
        self.assertEqual(v3.x, xyz[0])
        self.assertEqual(v3.y, xyz[1])
        self.assertEqual(v3.z, xyz[2])

        self.assertEqual(v3.xy, (xyz[0], xyz[1]))
        self.assertEqual(v3.xz, (xyz[0], xyz[2]))
        self.assertEqual(v3.yz, (xyz[1], xyz[2]))

        self.assertEqual(v3.yx, (xyz[1], xyz[0]))
        self.assertEqual(v3.zx, (xyz[2], xyz[0]))
        self.assertEqual(v3.zy, (xyz[2], xyz[1]))

        self.assertEqual(v3.xyz, xyz)
        self.assertEqual(v3.xzy, (xyz[0], xyz[2], xyz[1]) )
        self.assertEqual(v3.zyx, (xyz[2], xyz[1], xyz[0]) )
        self.assertEqual(v3.zxy, (xyz[2], xyz[0], xyz[1]) )
        self.assertEqual(v3.yxz, (xyz[1], xyz[0], xyz[2]) )
        self.assertEqual(v3.yzx, (xyz[1], xyz[2], xyz[0]) )
    
if __name__ == '__main__':
    unittest.main()
