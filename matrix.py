import numpy as np
import math

# All 3D cube-drawing and matrix tools
class CustomEngine():
    faces = [[1, 5, 4, 0], # back
             [1, 5, 7, 3], # top
             [1, 0, 2, 3], # left
             [5, 7, 6, 4], # right
             [0, 4, 6, 2], # bottom
             [3, 7, 6, 2]] # front

    def __init__(self):
        pass

    def drawFaces(self, canvas, shape, fill, outline, cx, cy):
        for face in CustomEngine.faces:
            print(shape[0][face[0]] + cx, shape[1][face[0]] + cy)
            canvas.create_polygon(
                shape[0][face[0]] + cx, shape[1][face[0]] + cy,
                shape[0][face[1]] + cx, shape[1][face[1]] + cy,
                shape[0][face[2]] + cx, shape[1][face[2]] + cy,
                shape[0][face[3]] + cx, shape[1][face[3]] + cy,
                fill = fill, outline = outline)

    def rotateX(self, x, shape):
        return np.matmul([[1,           0,            0],
                          [0, math.cos(x), -math.sin(x)],
                          [0, math.sin(x),  math.cos(x)]], shape)

    def rotateY(self, y, shape):
        return np.matmul([[ math.cos(y), 0, math.sin(y)],
                          [           0, 1,           0],
                          [-math.sin(y), 0, math.cos(y)]], shape)

    def rotateZ(self, z, shape):
        return np.matmul([[ math.cos(z), math.sin(z), 0],
                          [-math.sin(z), math.cos(z), 0],
                          [           0,           0, 1]], shape)