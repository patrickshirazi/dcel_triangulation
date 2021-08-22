class Vertex:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.incidentEdge = None
        self.isMerge = False
        self.leftChain = False
    
    def __str__(self):
        return f'v{self.name} ({self.x}, {self.y}) {self.incidentEdge.name}\n'

class Face:
    def __init__(self, name):
        self.name = name
        self.outerComponent = None
        self.innerComponents = []

    def __str__(self):
        outerComponent = self.outerComponent.name if self.outerComponent else 'nil'
        innerComponents = ''
        for innerComponent in self.innerComponents:
            innerComponents += innerComponent.name + ' '
        if innerComponents == '': innerComponents = 'nil'
        return f'{self.name} {outerComponent} {innerComponents}\n'

class Edge:
    def __init__(self, name, origin = None, incidentFace = None):
        self.name = name
        self.origin = origin
        self.twin = None
        self.incidentFace = incidentFace
        self.next = None
        self.prev = None
        self.seen = False
    
    def __str__(self):
        return f'{self.name} v{self.origin.name} {self.twin.name} {self.incidentFace.name} {self.next.name} {self.prev.name}\n'

class DCEL:
    def __init__(self, vertices = None, faces = None, edges = None):
        self.vertices = vertices
        self.faces = faces
        self.edges = edges
    
    def __str__(self):
        output = ''
        for vertex in self.vertices:
            output += str(vertex)
        output += '\n'
        for face in self.faces:
            output += str(face)
        output += '\n'
        for edge in self.edges:
            output += str(edge)
        return output