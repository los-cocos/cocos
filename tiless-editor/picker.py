import pdb
from bisect import bisect, insort
from cocos.batch import BatchNode

class Picker(object):
    """ A picker to find your children quickly  """
    def __init__(self):
        self.xChildren = {}
        self.yChildren = {}
        self.xs = []
        self.ys = []

    def _insert1d (self, child, ps, pChildren, p1, p2):
        p1pos = bisect(ps, p1)
        if p1pos == 0:
            ps.insert(0, p1)
            pChildren[p1] = set()
        elif ps[p1pos - 1] != p1:
            ps.insert(p1pos, p1)
            pChildren[p1] = pChildren[ps[p1pos - 1]].copy()
        else:
            p1pos -= 1
        p2pos = bisect(ps, p2)
        if ps[p2pos - 1] != p2:
            ps.insert(p2pos, p2)
            pChildren[p2] = pChildren[ps[p2pos - 1]].copy()
        else:
            p2pos -= 1
        for i in range(p1pos, p2pos):
            pChildren[ps[i]].add(child)

    def insert(self, child, x1, y1, x2, y2):
        """ Add a child """
        self._insert1d(child, self.xs, self.xChildren, x1, x2)
        self._insert1d(child, self.ys, self.yChildren, y1, y2)

    def childrenAt(self, x, y):
        xPos = bisect(self.xs, x)
        if xPos == 0: return set()
        yPos = bisect(self.ys, y)
        if yPos == 0: return set()
        return self.xChildren[self.xs[xPos-1]].intersection(self.yChildren[self.ys[yPos-1]])

    def _delete1d(self, child, ps, pChildren, p1, p2):
        p1Pos = bisect(ps, p1) - 1
        p2Pos = bisect(ps, p2) - 1
        for i in range(p1Pos, p2Pos):
            pChildren[ps[i]].remove(child)
        if pChildren[ps[p1Pos]] == pChildren[ps[p1Pos - 1]]:
            del pChildren[ps[p1Pos]]
            ps.pop(p1Pos)
            p2Pos -=1
        if pChildren[ps[p2Pos]] == pChildren[ps[p2Pos - 1]]:
            del pChildren[ps[p2Pos]]
            ps.pop(p2Pos)
        
    def delete(self, child, x1, y1, x2, y2):
        """ Delete all occurrences of child between x1, y1, x2, y1 """
        self._delete1d(child, self.xs, self.xChildren, x1, x2)
        self._delete1d(child, self.ys, self.yChildren, y1, y2)

from cocos.euclid import Matrix3, Vector2
class NodePicker(Picker):
    """ Wrap a CocosNode, and keep its children in a Picker """
    def __init__(self):
        self.children = {}
        super(NodePicker, self).__init__()

    def hotspot(self, child):
        x = - child.image_anchor_x * child.scale
        y = - child.image_anchor_y * child.scale
        m = Matrix3.new_rotate(child.rotation)
        p1 = m * Vector2(x, y)
        p2 = m * Vector2(x + child.width, y)
        p3 = m * Vector2(x, y + child.height)
        p4 = m * Vector2(x + child.width, y + child.height)
        x1 = min(p1.x, p2.x, p3.x, p4.x)
        y1 = min(p1.y, p2.y, p3.y, p4.y)
        x2 = max(p1.x, p2.x, p3.x, p4.x)
        y2 = max(p1.y, p2.y, p3.y, p4.y)
        return int(child.x + x1), int(child.y + y1), int(child.x + x2), int(child.y + y2)

    def add(self, child):
        self.children[child] = self.hotspot(child)
        self.insert(child, *self.children[child])

    def remove(self, child):
        self.delete(child, *self.children[child])

    def update(self, child):
        self.remove(child)
        self.add(child)

class PickerBatchNode(BatchNode):

    def __init__(self):
        self.picker = NodePicker()
        super(PickerBatchNode, self).__init__()

    def add(self, child, z=0, name=None):
        child.register(self, 'position')
        child.register(self, 'rotation')
        child.register(self, 'scale')
        self.picker.add(child)
        super(PickerBatchNode, self).add(child, z, name)

    def remove(self, child):
        child.unregister(self, 'position')
        child.unregister(self, 'rotation')
        child.unregister(self, 'scale')
        self.picker.remove(child)
        super(PickerBatchNode, self).remove(child)

    def on_notify(self, node, attribute):
        self.picker.update(node)

    def childrenAt(self, x, y):
        return self.picker.childrenAt(x, y)

if __name__ == '__main__':
    import unittest
    class TestPicker(unittest.TestCase):
        def testPicker(self):
            t = Picker()
            t.insert("A", 1, 2, 3, 4)
            t.insert("B", 2, 3, 4, 5)
            t.insert("C", 3, 4, 5, 6)
            t.insert("D", 1, 1, 6, 6)
            self.assertEquals(set(["A", "D"]), t.childrenAt(2.5, 2.5))
            t.delete("D", 1, 1, 6, 6)
            self.assertEquals(set(["A"]), t.childrenAt(2.5, 2.5))
            t.delete("B", 2, 3, 4, 5)
            t.insert("B", 1, 1, 3, 3)
            self.assertEquals(set(["A", "B"]), t.childrenAt(2.5, 2.5))

    unittest.main()

