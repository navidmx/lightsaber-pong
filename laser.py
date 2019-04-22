import numpy as np
from matrix import CustomEngine

class Laser(CustomEngine):
    def __init__(self, x, y, z):
        super().__init__()
        self.x, self.y, self.z = x, y, z
        self.speed = 5

    def move(self):
        self.z -= self.speed

    def draw(self, canvas, cx, cy):
        self.laser = np.transpose(
                        [[-5, -5, self.z],      [-5, -5, self.z],
                         [-5, -5, self.z + 20], [-5, -5, self.z + 20],
                         [ 5, -5, self.z],      [ 5, -5, self.z],
                         [ 5, -5, self.z + 20], [ 5, -5, self.z + 20]]
                    )
        model = self.getFaceCoords(self.laser, cx, cy, 0, 0, 0)
        self.drawShape(canvas, model[1])

    # Draw each shape on tkinter given 2D coordinates
    def drawShape(self, canvas, faces):
        # Sort faces by average position on z axis
        faces.sort(key = lambda tup: tup[8])
        print(faces[0])
        # Draw each face in order of z-index
        for f in faces:
            canvas.create_polygon(f[0], f[1], f[2], f[3], f[4], f[5], f[6],
                                  f[7], fill = "red", outline = "white")