"""
Process tesnet output (grid.teo file)
and export elements, voronoi diagrams as geojson
"""
from triwaco.adore.tesnet import Tesnet
import numpy as np
import json

gridfile = 'GRID.TEO'

nextTab = np.array((1, 2, 0))  # next corner or side
prevTab = np.array((2, 0, 1))  # previous corner or side
sideTab = np.array(((2, 0), (0, 1), (1, 2)))  # corner numbers of sides

teo = Tesnet(gridfile)
nodes = teo.nodes()
elements = teo.elements() - 1  # change node number (1..nnodes) to array index (0..nnodes-1)


def center(e):
    """ return center of element e """
    return nodes[elements[e]].mean(axis=0)


def middle(e, s):
    """ return midpoint of side s of element e """
    n = sideTab[s]
    return nodes[elements[e][n]].mean(axis=0)


def det(a, b):
    """ return determinant of 2x2 matrix ab """
    return a[0] * b[1] - a[1] * b[0]


def area(a, b, c):
    """ return area of triangle abc """
    return det(b - a, c - a) / 2


def corner(e, n):
    """ return corner number of node n in element e """
    for i, a in enumerate(elements[e]):
        if a == n:
            return i


def set_ccw(e):
    """ make sure corners of element are arranged in counterclockwise order """
    a, b, c = nodes[e]
    if area(a, b, c) < 0:
        t = e[0]
        e[0] = e[1]
        e[1] = t


def voronoi(n):
    """ return voronoi polygon of node n """
    poly = []
    # first element sharing node n
    e = nonbr[n][0]
    start = e
    while e is not None:
        poly.append(center(e))
        s = corner(e, n)
        poly.append(middle(e, s))
        e = elnbr[e][s]
        if e == start:
            # done, close polygon
            poly.append(center(e))
            break
        if e is None:
            # boundary reached, restart
            e = start
            while e is not None:
                s = nextTab[corner(e, n)]
                poly.insert(0, middle(e, s))
                e = elnbr[e][s]
                if e is not None:
                    poly.insert(0, center(e))
                else:
                    poly.insert(0, nodes[n])
                    poly.append(nodes[n])
    return np.array(poly)


def to_geojson(fid, pts):
    """ return geojson representation of a polygon """
    return json.dumps({
        'type': 'Feature',
        'properties': {'fid': fid},
        'geometry': {
            'type': 'Polygon',
            'coordinates': pts
        }
    })


def element_to_geojson(fid, e):
    """ return geojson representation of an element """
    pts = nodes[e].tolist()
    return to_geojson(fid, [pts + [pts[0]]])


def voronoi_to_geojson(n):
    """ return voronoi polygon of node n as geojson """
    pts = voronoi(n).tolist()
    return to_geojson(n + 1, [pts])


# export nodes
with open('nodes.dat', 'w') as f:
    for x, y in nodes:
        f.write(f'{x},{y}\n')

# export elements
with open('elements.dat', 'w') as f:
    for a, b, c in elements:
        f.write(f'{a},{b},{c}\n')

# export Delaunay triangulation as geojson
with open('elements.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "features": [')
    for fid, e in enumerate(elements):
        if fid:
            f.write(',')
        f.write(element_to_geojson(fid + 1, e))
    f.write(']}\n')

# build topology
# arrange element corners counterclockwise and build neighbour arrays for nodes
nonbr = [[] for n in nodes]  # elements sharing this node
for i, e in enumerate(elements):
    set_ccw(e)
    for k in e:
        nonbr[k].append(i)

# build neighbour arrays for elements
elnbr = [[None] * 3 for e in elements]  # neighbours of elements (max 3 per element)
for i, e1 in enumerate(elements):
    n2 = e1[2]
    for j, n1 in enumerate(e1):
        for e2 in nonbr[n1]:
            if i != e2 and n2 in elements[e2]:
                elnbr[i][j] = e2
                break
        n2 = n1

# export Voronoi diagram as geojson
with open('voronoi.json', 'w') as f:
    f.write('{"type": "FeatureCollection", "features": [')
    nnodes = nodes.shape[0]
    for n in range(nnodes):
        if n:
            f.write(',')
        f.write(voronoi_to_geojson(n))
    f.write(']}\n')
