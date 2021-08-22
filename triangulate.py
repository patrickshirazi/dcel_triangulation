from DCEL import Vertex, Face, Edge, DCEL
from Treap import Treap, TreapNode
import draw

import math
from collections import deque

def doesIntersect(p1, q1, p2, q2):
    a1 = (q1.x - p1.x) * (p2.y - p1.y) - (p2.x - p1.x) * (q1.y - p1.y)
    a2 = (q1.x - p1.x) * (q2.y - p1.y) - (q2.x - p1.x) * (q1.y - p1.y)
    a3 = (q2.x - p2.x) * (p1.y - p2.y) - (p1.x - p2.x) * (q2.y - p2.y)
    a4 = (q2.x - p2.x) * (q1.y - p2.y) - (q1.x - p2.x) * (q2.y - p2.y)

    if ((a1 < 0 and a2 > 0) or (a1 > 0 and a2 < 0)) and ((a3 < 0 and a4 > 0) or (a3 > 0 and a4 < 0)):
        return True
    elif a1 == 0 and (p2.x < max(p1.x, q1.x) and p2.x > min(p1.x, q1.x) and p2.y < max(p1.y, q1.y) and p2.y > min(p1.y, q1.y)):
        return True
    elif a2 == 0 and (q2.x < max(p1.x, q1.x) and q2.x > min(p1.x, q1.x) and q2.y < max(p1.y, q1.y) and q2.y > min(p1.y, q1.y)):
        return True
    elif a3 == 0 and (p1.x < max(p2.x, q2.x) and p1.x > min(p2.x, q2.x) and p1.y < max(p2.y, q2.y) and p1.y > min(p2.y, q2.y)):
        return True
    elif a4 == 0 and (q1.x < max(p2.x, q2.x) and q1.x > min(p2.x, q2.x) and q1.y < max(p2.y, q2.y) and q1.y > min(p2.y, q2.y)):
        return True
    return False

def ConstructSimplePolygon(points):
    # construct face record
    face1 = Face('f1')
    face2 = Face('f2')
    faces = [face1, face2]

    # construct vertex record
    vertices = []
    rotation = 0
    for i in range(len(points)):
        vertices.append(Vertex(i+1, float(points[i][0]), float(points[i][1])))
        rotation += (float(points[(i+1)%len(points)][0]) - float(points[i][0])) * (float(points[(i+1)%len(points)][1]) + float(points[i][1]))

    # construct edge record
    edges = []
    for i in range(len(vertices)):
        edge = Edge(f'e{i+1},{(i+1)%len(vertices)+1}', vertices[i], face1)
        twinedge = Edge(f'e{(i+1)%len(vertices)+1},{i+1}', vertices[(i+1)%len(vertices)], face2)

        edge.twin = twinedge
        twinedge.twin = edge

        # check if new edges intersect previous edges
        for j in range(0, len(edges), 2):
            if doesIntersect(edge.origin, twinedge.origin, edges[j].origin, edges[j+1].origin): raise Exception('Input does not represent a simple polygon')

        edges.append(edge)
        edges.append(twinedge)

        # update incident edge for the vertices
        vertices[i].incidentEdge = edge

    for i in range(0, len(edges), 2):
        edges[i].prev = edges[(i-2)%len(edges)]
        edges[i].next = edges[(i+2)%len(edges)]
        edges[i+1].prev = edges[(i+3)%len(edges)]
        edges[i+1].next = edges[(i-1)%(len(edges))]

    # determine bounded vs unbounded face, rotation > 0 -> clockwise
    if rotation > 0:
        face1.innerComponents.append(edges[0])
        face2.outerComponent = edges[1]
    else:
        face1.outerComponent = edges[0]
        face2.innerComponents.append(edges[1])

    return DCEL(vertices, faces, edges)

def diagonalInside(vj, vk, helper):
    if vj.x - vk.x == 0:
        x = vj.x
    else:
        m = (vj.y - vk.y) / (vj.x - vk.x)
        if m == 0:
            return False
        else:
            b = vj.y - (m * vj.x)
            x = (helper.y - b) / m
    return helper.x < x if vj.leftChain else helper.x > x

def connect(P, v1, v2):
    edge = Edge(f'e{v1.name},{v2.name}', v1)
    twinedge = Edge(f'e{v2.name},{v1.name}', v2)
    edge.twin = twinedge
    twinedge.twin = edge

    if v1.incidentEdge.incidentFace == None:
        if v1.leftChain:
            e1 = v1.incidentEdge.twin
        else:
            e1 = v1.incidentEdge.prev
    elif v1.incidentEdge.incidentFace.outerComponent == None:
        if v1.leftChain:
            e1 = v1.incidentEdge.twin
        else:
            e1 = v1.incidentEdge.next.twin
    else:
        e1 = v1.incidentEdge.prev

    twinedge.next = e1.next
    e1.next.prev = twinedge
    edge.prev = e1
    e1.next = edge
    if v1.leftChain:
        v1.incidentEdge = twinedge.next
    else:
        v1.incidentEdge = edge

    if v2.incidentEdge.incidentFace == None:
        if v2.leftChain:
            e2 = v2.incidentEdge.twin
        else:
            e2 = v2.incidentEdge.prev
    elif v2.incidentEdge.incidentFace.outerComponent == None:
        if v2.leftChain:
            e2 = v2.incidentEdge.twin
        else:
            e2 = v2.incidentEdge.next.twin
    else:
        e2 = v2.incidentEdge.prev
    edge.next = e2.next
    e2.next.prev = edge
    twinedge.prev = e2
    e2.next = twinedge
    if v1.leftChain:
        v2.incidentEdge = twinedge
    else:
        v2.incidentEdge = edge.next

    P.edges.append(edge)
    P.edges.append(twinedge)

def TriangulateMonotonePolygon(P):
    top = max(P.vertices, key=lambda v: (v.y, -v.x))
    if top.incidentEdge.twin.origin.x < top.incidentEdge.prev.origin.x:
        leftedge = top.incidentEdge
        rightedge = top.incidentEdge.prev
    else:
        leftedge = top.incidentEdge.twin.next
        rightedge = top.incidentEdge.twin
    
    u = [top]
    while leftedge != rightedge:
        if leftedge.twin.origin.y >= rightedge.origin.y:
            leftedge.twin.origin.leftChain = True
            u.append(leftedge.twin.origin)
            leftedge = leftedge.next
        else:
            rightedge.origin.leftChain = False
            u.append(rightedge.origin)
            rightedge = rightedge.prev

    s = deque([])
    s.append(u[0])
    s.append(u[1])
    for i in range(2, len(u)-1):
        if u[i].leftChain != s[-1].leftChain:
            s.popleft()
            while len(s) > 0:
                connect(P, u[i], s.popleft())
            s.append(u[i-1])
            s.append(u[i])
        else:
            prev = s.pop()
            temp = []
            while len(s) > 0 and diagonalInside(u[i], s[-1], prev):
                prev = s.pop()
                connect(P, u[i], prev)
            s.append(prev)
            s.append(u[i])
    s.pop()
    while len(s) > 1:
        connect(P, u[len(u)-1], s.pop())
    
    # fix face information
    P.faces = [P.faces[0] if P.faces[0].outerComponent == None else P.faces[1]] # Keep outer face
    P.faces[0].name = 'f1'
    for e in P.edges: e.seen = False
    for e in P.edges:
        if not (e.seen or (e.incidentFace != None and e.incidentFace.outerComponent == None)):
            e.seen = True
            face = Face(f'f{len(P.faces)+1}')
            face.outerComponent = e
            e.incidentFace = face
            curr = e.next
            while curr != e:
                curr.incidentFace = face
                curr.seen = True
                curr = curr.next
            P.faces.append(face)

def isAbove(p, q):
    return (p.y > q.y) or (p.y == q.y and p.x < q.x)

def isBelow(p, q):
    return (p.y < q.y) or (p.y == q.y and p.x > q.x)

def connectVertices(P, v1, v2):
    edge = Edge(f'e{v1.name},{v2.name}', v1)
    twinedge = Edge(f'e{v2.name},{v1.name}', v2)
    edge.twin = twinedge
    twinedge.twin = edge

    if v1.incidentEdge.incidentFace.outerComponent == None:
        if v1.incidentEdge.twin.next == v1.incidentEdge.prev.twin.prev.twin:
            e1 = v1.incidentEdge.twin.next.twin
        else:
            e1 = v1.incidentEdge.twin
    else:
        if v1.incidentEdge.prev == v1.incidentEdge.twin.next.twin:
            e1 = v1.incidentEdge.prev
        elif v1.incidentEdge.prev == v1.incidentEdge.twin.next.twin:
            e1 = v1.incidentEdge.prev
        else:
            e1 = v1.incidentEdge.twin.next.twin
    twinedge.next = e1.next
    e1.next.prev = twinedge
    edge.prev = e1
    e1.next = edge

    if v2.incidentEdge.incidentFace.outerComponent == None:
        if v2.incidentEdge.twin.next == v2.incidentEdge.prev.twin.prev.twin:
            e2 = v2.incidentEdge.twin.next.twin
        else:
            e2 = v2.incidentEdge.twin
    else:
        if v2.incidentEdge.prev == v2.incidentEdge.twin.next.twin:
            e2 = v2.incidentEdge.prev
        elif v2.incidentEdge.prev == v2.incidentEdge.twin.next.twin:
            e2 = v2.incidentEdge.prev
        else:
            e2 = v2.incidentEdge.twin.next.twin
    edge.next = e2.next
    e2.next.prev = edge
    twinedge.prev = e2
    e2.next = twinedge

    P.edges.append(edge)
    P.edges.append(twinedge)

def MakeMonotone(P):
    Q = sorted(P.vertices, key=lambda v: (v.y, -v.x), reverse=True)
    T = Treap()
    for v in Q:
        if v.incidentEdge.incidentFace.outerComponent == None:
            n1 = v.incidentEdge.next.origin
            n2 = v.incidentEdge.prev.origin
        else:
            n1 = v.incidentEdge.prev.origin
            n2 = v.incidentEdge.next.origin
        # classify and handle edges
        if isAbove(v, n1) and isAbove(v, n2):
            if math.degrees(math.atan2(n1.y-v.y, n1.x-v.x) - math.atan2(n2.y-v.y, n2.x-v.x)) > 0: # -pi <= atan2 <= pi
                HandleStartVertex(P, T, v)
            else:
                HandleSplitVertex(P, T, v)
        elif isBelow(v, n1) and isBelow(v, n2):
            if math.degrees(math.atan2(n1.y-v.y, n1.x-v.x) - math.atan2(n2.y-v.y, n2.x-v.x)) > 0:
                HandleEndVertex(P, T, v)
            else:
                v.isMerge = True
                HandleMergeVertex(P, T, v)
        else:
            HandleRegularVertex(P, T, v)

    # fix face information
    P.faces = [P.faces[0] if P.faces[0].outerComponent == None else P.faces[1]] # Keep outer face
    P.faces[0].name = 'f1'
    for e in P.edges: e.seen = False
    for e in P.edges:
        if not (e.seen or (e.incidentFace != None and e.incidentFace.outerComponent == None)):
            e.seen = True
            face = Face(f'f{len(P.faces)+1}')
            face.outerComponent = e
            e.incidentFace = face
            curr = e.next
            while curr != e:
                curr.incidentFace = face
                curr.seen = True
                curr = curr.next
            P.faces.append(face)
    


def HandleStartVertex(P, T, v):
    ei = v.incidentEdge.prev if v.incidentEdge.incidentFace.outerComponent == None else v.incidentEdge.twin
    nei = TreapNode(ei, helper=v)
    T.insert(nei)

def HandleEndVertex(P, T, v):
    eim1 = v.incidentEdge if v.incidentEdge.incidentFace.outerComponent == None else v.incidentEdge.twin.next
    neim1 = T.search(eim1)
    if neim1.helper.isMerge:
        connectVertices(P, v, neim1.helper)
    T.delete(eim1)

def HandleSplitVertex(P, T, v):
    nej = T.searchLeftEdge(v)

    connectVertices(P, v, nej.helper)

    nej.helper = v

    ei = v.incidentEdge.prev if v.incidentEdge.incidentFace.outerComponent == None else v.incidentEdge.twin
    nei = TreapNode(ei, helper=v)
    T.insert(nei)
    

def HandleMergeVertex(P, T, v):
    eim1 = v.incidentEdge if v.incidentEdge.incidentFace.outerComponent == None else v.incidentEdge.twin.next
    neim1 = T.search(eim1)
    if neim1.helper.isMerge:
        connectVertices(P, v, neim1.helper)
    T.delete(eim1)

    nej = T.searchLeftEdge(v)
    if nej.helper.isMerge:
        connectVertices(P, v, nej.helper)
    nej.helper = v

def HandleRegularVertex(P, T, v):
    ei = v.incidentEdge.prev if v.incidentEdge.incidentFace.outerComponent == None else v.incidentEdge.twin
    if isAbove(v, ei.origin): # interior to the right
        eim1 = ei.next
        neim1 = T.search(eim1)
        if neim1.helper.isMerge:
            connectVertices(P, v, neim1.helper)
        T.delete(eim1)
        nei = TreapNode(ei, helper=v)
        T.insert(nei)
    else:
        nej = T.searchLeftEdge(v)
        if nej.helper.isMerge:
            connectVertices(P, v, nej.helper)
        nej.helper = v

def Triangulate(P):
    MakeMonotone(dcel)

    for face in dcel.faces:
        if face.outerComponent == None: continue
        P = DCEL()
        P.vertices = []
        P.faces = [dcel.faces[0], face]
        P.edges = []

        startedge = face.outerComponent
        twinedge = Edge(startedge.twin.name, startedge.twin.origin, dcel.faces[0])
        startedge.twin = twinedge
        twinedge.twin = startedge
        P.edges.append(startedge)
        P.edges.append(twinedge)
        startedge.origin.incidentEdge = startedge
        P.vertices.append(startedge.origin)
        curr = startedge.next
        while curr != startedge:
            twinedge = Edge(curr.twin.name, curr.twin.origin, dcel.faces[0])
            curr.twin = twinedge
            twinedge.twin = curr
            P.edges.append(curr)
            P.edges.append(twinedge)
            curr.origin.incidentEdge = curr
            P.vertices.append(curr.origin)
            curr = curr.next
        for i in range(0, len(P.edges), 2):
            P.edges[i+1].prev = P.edges[(i+3)%len(P.edges)]
            P.edges[i+1].next = P.edges[(i-1)%(len(P.edges))]
        TriangulateMonotonePolygon(P)
        dcel.edges = list(set(dcel.edges).union(set([e for e in P.edges if e.incidentFace.outerComponent != None and e.twin.incidentFace.outerComponent != None])))
    
    dcel.faces = [dcel.faces[0] if dcel.faces[0].outerComponent == None else dcel.faces[1]] # Keep outer face
    dcel.faces[0].name = 'f1'
    for e in dcel.edges: e.seen = False
    for e in dcel.edges:
        if not (e.seen or (e.incidentFace != None and e.incidentFace.outerComponent == None)):
            e.seen = True
            face = Face(f'f{len(dcel.faces)+1}')
            face.outerComponent = e
            e.incidentFace = face
            curr = e.next
            while curr != e:
                curr.incidentFace = face
                curr.seen = True
                curr = curr.next
            dcel.faces.append(face)

if __name__ == '__main__':
    f = open('inputx.txt', 'r')
    points = [line.rstrip().split() for line in f.readlines() if line.rstrip().split()]
    
    dcel = ConstructSimplePolygon(points)

    Triangulate(dcel)

    print(dcel)
    # f = open('output.txt', 'w')
    # f.write(dcel.__str__())
    # f.close()
    draw.draw(dcel)