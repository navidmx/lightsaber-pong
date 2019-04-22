import numpy as np

D = 1 # Offset value (for depth)

# All 3D cube-drawing and matrix tools
class CustomEngine(object):

    def __init__(self):
        # Connections necessary to make faces of a rect. prism
        self.faces = [[1, 5, 4, 0], # back
                      [1, 5, 7, 3], # top
                      [1, 0, 2, 3], # left
                      [5, 7, 6, 4], # right
                      [0, 4, 6, 2], # bottom
                      [3, 7, 6, 2]] # front

    def getFaceCoords(self, shape, cx, cy, ax, ay, az):
        original = np.copy(shape)
        self.cx, self.cy = cx, cy
        faceCoords = []

        '''
        for f in self.faces:
            x1, y1 = self.project(shape, shape[0][f[0]], shape[1][f[0]],
                                  shape[2][f[0]], ax, ay, az)
            x2, y2 = self.project(shape, shape[0][f[1]], shape[1][f[1]],
                                  shape[2][f[1]], ax, ay, az)
            x3, y3 = self.project(shape, shape[0][f[2]], shape[1][f[2]],
                                  shape[2][f[2]], ax, ay, az)
            x4, y4 = self.project(shape, shape[0][f[3]], shape[1][f[3]],
                                  shape[2][f[3]], ax, ay, az)
            faceCoords.append((x1, y1, x2, y2, x3, y3, x4, y4))
        '''
        
        shape = self.rotateShape(shape, ax, ay, az)
        for f in self.faces:
            x1, y1 = self.project(shape, shape[0][f[0]], shape[1][f[0]],
                                         shape[2][f[0]])
            x2, y2 = self.project(shape, shape[0][f[1]], shape[1][f[1]],
                                         shape[2][f[1]])
            x3, y3 = self.project(shape, shape[0][f[2]], shape[1][f[2]],
                                         shape[2][f[2]])
            x4, y4 = self.project(shape, shape[0][f[3]], shape[1][f[3]],
                                         shape[2][f[3]])
            faceCoords.append((x1, y1, x2, y2, x3, y3, x4, y4))

        return (original, faceCoords, np.average(shape[2]))

    def project(self, shape, x, y, z):
        return x + self.cx, y + self.cy

    '''
    def project(self, shape, x, y, z, ax, ay, az):
        rotX = np.asarray([[1, 0, 0], [0, np.cos(ax), np.sin(ax)],
                           [0, -np.sin(ax), np.cos(ax)]])
        rotY = np.asarray([[np.cos(ay), 0, -np.sin(ay)], [0, 1, 0],
                           [np.sin(ay), 0, np.cos(ay)]])
        rotZ = np.asarray([[np.cos(az), np.sin(az), 0], [-np.sin(az),
                           np.cos(az), 0], [0, 0, 1]])
        offset = [[x], [y], [z - 200]]
        final = rotX @ rotY @ rotZ @ offset
        dx, dy, dz = final[0][0], final[1][0], final[2][0]
        ez = -200
        x = (ez/dz) * dx + self.cx
        y = (ez/dz) * dy + self.cy
        return x, y
    '''
    def rotateShape(self, shape, x, y, z):
        shape = self.rotateX(x, shape)
        shape = self.rotateY(y, shape)
        shape = self.rotateZ(z, shape)
        return shape

    def rotateX(self, x, shape):
        return np.matmul([[1, 0, 0],
                          [0, np.cos(x), -np.sin(x)],
                          [0, np.sin(x),  np.cos(x)]], shape)

    def rotateY(self, y, shape):
        return np.matmul([[ np.cos(y), 0, np.sin(y)],
                          [0, 1, 0],
                          [-np.sin(y), 0, np.cos(y)]], shape)

    def rotateZ(self, z, shape):
        return np.matmul([[ np.cos(z), np.sin(z), 0],
                          [-np.sin(z), np.cos(z), 0],
                          [0, 0, 1]], shape)