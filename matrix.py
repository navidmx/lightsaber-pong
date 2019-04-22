import numpy as np

D = 1 # Offset value (for depth)

class CustomEngine(object):
    def __init__(self):
        # Connections necessary to make faces of a rectangular prism
        self.faces = [[1, 5, 4, 0], # Back
                      [1, 0, 2, 3], # Left
                      [5, 7, 6, 4], # Right
                      [0, 4, 6, 2], # Bottom
                      [1, 5, 7, 3], # Top
                      [3, 7, 6, 2]] # Front

    # Get 2D coordinates of a shape's faces given 3D coordinates
    def getFaceCoords(self, shape, cx, cy, ax, ay, az):
        original = np.copy(shape) # Keep copy of shape for later comparison
        faceCoords = []

        # Rotate shape by given x/y/z angles (ax, ay, az)
        shape = self.rotateShape(shape, ax, ay, az)

        # Get translated coordinates for each point
        for f in self.faces:
            x1, y1 = self.translate(shape[0][f[0]], shape[1][f[0]], cx, cy)
            x2, y2 = self.translate(shape[0][f[1]], shape[1][f[1]], cx, cy)
            x3, y3 = self.translate(shape[0][f[2]], shape[1][f[2]], cx, cy)
            x4, y4 = self.translate(shape[0][f[3]], shape[1][f[3]], cx, cy)
            avgZ = np.average([shape[2][f[0]], shape[2][f[1]], shape[2][f[2]],
                               shape[2][f[3]]])
            faceCoords.append((x1, y1, x2, y2, x3, y3, x4, y4, avgZ))

        # Return model, faces, and the average z-index of model
        return (original, faceCoords, np.average(shape[2]))

    # Translate lightsaber to correct 2D position for tkinter
    def translate(self, x, y, cx, cy):
        return x + cx, y + cy

    # Rotate shape in all 3 dimensions given x/y/z rotations
    def rotateShape(self, shape, x, y, z):
        # Rotation matrices for all 3 axes
        rotX = np.asarray([[1, 0, 0],
                [0, np.cos(x), -np.sin(x)],
                [0, np.sin(x),  np.cos(x)]])
        rotY = np.asarray([[ np.cos(y), 0, np.sin(y)],
                [0, 1, 0],
                [-np.sin(y), 0, np.cos(y)]])
        rotZ = np.asarray([[ np.cos(z), np.sin(z), 0],
                [-np.sin(z), np.cos(z), 0],
                [0, 0, 1]])
        # @ – numpy's matrix multiplication operator
        return rotX @ rotY @ rotZ @ shape