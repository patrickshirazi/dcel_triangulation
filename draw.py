from DCEL import DCEL
import pygame
import math

def draw(dcel):
        global screen, xMin, xMax, yMin, yMax, scale, arrow
        pygame.init()
        screen = pygame.display.set_mode((900, 900))
        pygame.display.set_caption('DCEL')
        screen.fill((255,255,255))
        pygame.display.update()

        xMin = min([vertex.x for vertex in dcel.vertices])
        xMax = max([vertex.x for vertex in dcel.vertices])
        yMin = min([vertex.y for vertex in dcel.vertices])
        yMax = max([vertex.y for vertex in dcel.vertices])

        scale = min([700 / (xMax - xMin), 700 / (yMax - yMin)])
        
        arrow=pygame.Surface((50,50))
        arrow.fill((255,255,255))
        pygame.draw.line(arrow, (0,0,0), (0,0), (25,25))
        pygame.draw.line(arrow, (0,0,0), (0,50), (25,25))
        arrow.set_colorkey((255,255,255))

        for edge in dcel.edges:
            drawVertex(edge.origin)
            drawEdge(edge)

        pygame.display.update()

        running = True
        while running:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    running = False

def resize(point):
    return ((point[0] - xMin) * scale + 100, 900 - ((point[1] - yMin) * scale + 100))

def drawVertex(vertex):
    pygame.draw.circle(screen, (0,0,0), resize((vertex.x, vertex.y)), 5)

def drawEdge(edge):
    start = resize((edge.origin.x, edge.origin.y))
    end = resize((edge.twin.origin.x, edge.twin.origin.y))

    angle = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))
    offset = (3 * math.cos(math.radians(angle - 90)), 3 * math.sin(math.radians(angle - 90)))
    start = (start[0] + 20 * math.cos(math.radians(angle)) - offset[0], start[1] - 20 * math.sin(math.radians(angle)) + offset[1])
    end = (end[0] - 20 * math.cos(math.radians(angle)) - offset[0], end[1] + 20 * math.sin(math.radians(angle)) + offset[1])

    rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90
    pygame.draw.line(screen,(0,0,0),start,end,2)
    pygame.draw.polygon(screen, (0, 0, 0), ((end[0]+8*math.sin(math.radians(rotation)), end[1]+8*math.cos(math.radians(rotation))), (end[0]+8*math.sin(math.radians(rotation-150)), end[1]+8*math.cos(math.radians(rotation-150))), (end[0]+8*math.sin(math.radians(rotation+150)), end[1]+8*math.cos(math.radians(rotation+150)))))