import random

class TreapNode:
    def __init__(self, key, helper = None):
        self.key = key
        self.priority = random.randrange(0, 1000, 1)
        self.left = None
        self.right = None
        self.helper = helper

class Treap:
    def __init__(self):
        self.root = None

    def leftRotate(self, x):
        y = x.right
        t2 = y.left
        y.left = x
        x.right = t2
        return y

    def rightRotate(self, y):
        x = y.left
        t2 = x.right
        x.right = y
        y.left = t2
        return x

    # Given two edges, check if e1 is to the left of e2
    # Edges must overlap in y
    def edgeToLeft(self, e1, e2):
        y = min(e1.origin.y, e2.origin.y)
        if e1.origin.x - e1.twin.origin.x == 0:
            x1 = e1.origin.x
        else:
            m1 = (e1.origin.y - e1.twin.origin.y) / (e1.origin.x - e1.twin.origin.x)
            if m1 == 0:
                x1 = min(e1.origin.x, e1.twin.origin.x)
            else:
                b1 = e1.origin.y - (m1 * e1.origin.x)
                x1 = (y - b1) / m1
        if e2.origin.x - e2.twin.origin.x == 0:
            x2 = e2.origin.x
        else:
            m2 = (e2.origin.y - e2.twin.origin.y) / (e2.origin.x - e2.twin.origin.x)
            if m2 == 0:
                x2 = min(e2.origin.x, e2.twin.origin.x)
            else:
                b2 = e2.origin.y - (m2 * e2.origin.x)
                x2 = (y - b2) / m2
        return x1 < x2

    # Given a point and an edge, check if the point is to the left of the edge
    # Point must be in y range of edge
    def pointToLeft(self, v, e):
        if e.origin.x - e.twin.origin.x == 0:
            x = e.origin.x
        else:
            m = (e.origin.y - e.twin.origin.y) / (e.origin.x - e.twin.origin.x)
            if m == 0:
                x = min(e.origin.x, e.twin.origin.x)
            else:
                b = e.origin.y - (m * e.origin.x)
                x = (v.y - b) / m
        return v.x < x

    def search(self, key):
        return self.searchP(self.root, key)

    def searchP(self, root, key):
        if root == None or root.key == key:
            return root
        
        if self.edgeToLeft(key, root.key):
            return self.searchP(root.left, key)
        
        return self.searchP(root.right, key)

    def searchLeftEdge(self, v):
        return self.searchLeftEdgeP(self.root, v)
    
    def searchLeftEdgeP(self, root, v):
        if root == None:
            return None
        if self.pointToLeft(v, root.key):
            return self.searchLeftEdgeP(root.left, v)
        if root.right == None:
            return root
        temp = self.searchLeftEdgeP(root.right, v)

        return root if temp == None or self.edgeToLeft(root.key, temp.key) else temp

    def insert(self, node):
        self.root = self.insertP(self.root, node)

    def insertP(self, root, node):
        if root == None:
            return node
        
        if self.edgeToLeft(node.key, root.key):
            root.left = self.insertP(root.left, node)

            if root.left.priority > root.priority:
                root = self.rightRotate(root)
        else:
            root.right = self.insertP(root.right, node)

            if root.right.priority > root.priority:
                root = self.leftRotate(root)
        return root

    def delete(self, key):
        self.root = self.deleteP(self.root, key)
        return self.root

    def deleteP(self, root, key):
        if root == None:
            return root
        
        if self.edgeToLeft(key, root.key):
            root.left = self.deleteP(root.left, key)
        elif self.edgeToLeft(root.key, key):
            root.right = self.deleteP(root.right, key)
        elif root.left == None:
            root = root.right
        elif root.right == None:
            root = root.left
        elif root.left.priority < root.right.priority:
            root = self.leftRotate(root)
            root.left = self.deleteP(root.left, key)
        else:
            root = self.rightRotate(root)
            root.right = self.deleteP(root.right, key)
        
        return root