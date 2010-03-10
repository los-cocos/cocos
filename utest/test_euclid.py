import cocos.euclid as eu
import unittest

class Test_Vectors(unittest.TestCase):
    def test_vector2_rsub(self):
        a = (3.0, 7.0)
        b = (1.0, 2.0)
        va = eu.Vector2(*a)
        vb = eu.Vector2(*b)
        self.assertEquals(a-vb, eu.Vector2(2.0, 5.0))

    def test_vector3_rsub(self):
        a = (3.0, 7.0, 9.0)
        b = (1.0, 2.0, 3.0)
        va = eu.Vector3(*a)
        vb = eu.Vector3(*b)
        self.assertEquals(a-vb, eu.Vector3(2.0, 5.0, 6.0))
        
    
if __name__ == '__main__':
    unittest.main()
