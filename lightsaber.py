import numpy as np
from matrix import CustomEngine

GRAY = '#A9A9A9'
DARK_GRAY = '#696969'

class Lightsaber(CustomEngine):
    def __init__(self, color, z):
        super().__init__()
        self.color = color
        self.z = z # z-axis offset of lightsaber
        # Node connections to draw rectangles

    def draw(self, canvas, x, y, z, cx, cy):
        # Convert angles to radians, and correct X/Z axes
        ax, ay, az = np.radians(z), np.radians(y), np.radians(x)

        # 3D coordinates for lightsaber blade
        self.lightsaber = np.transpose(
                            [[-10, -50, self.z-10], [-10, -300, self.z-10],
                             [-10, -50, self.z+10], [-10, -300, self.z+10],
                             [ 10, -50, self.z-10], [ 10, -300, self.z-10],
                             [ 10, -50, self.z+10], [ 10, -300, self.z+10]]
                          )
        # 3D coordinates for lightsaber handle
        self.handle = np.transpose(
                            [[-10, -50, self.z-10], [-10, 50, self.z-10],
                             [-10, -50, self.z+10], [-10, 50, self.z+10],
                             [ 10, -50, self.z-10], [ 10, 50, self.z-10],
                             [ 10, -50, self.z+10], [ 10, 50, self.z+10]]
                      )
        # 3D coordinates for lightsaber hilt
        self.hilt = np.transpose(
                        [[-12, 50, self.z-12], [-15, 60, self.z-12],
                         [-12, 50, self.z+12], [-15, 60, self.z+12],
                         [ 12, 50, self.z-12], [ 15, 60, self.z-12],
                         [ 12, 50, self.z+12], [ 15, 60, self.z+12]]
                    )

        # Get 2D coordinates necessary to draw each 3D model
        models = []
        models.append(self.getFaceCoords(self.lightsaber, cx, cy, ax, ay, az))
        models.append(self.getFaceCoords(self.handle, cx, cy, ax, ay, az))
        models.append(self.getFaceCoords(self.hilt, cx, cy, ax, ay, az))
        # Sort models by average position on z axis (z-index)
        models.sort(key = lambda tup: tup[2])

        # Draw models in order of z-index
        for model in models:
            shape = model[0]
            if (shape == self.lightsaber).all():
                self.drawShape(canvas, model[1], self.color, "white")
            elif (shape == self.handle).all():
                self.drawShape(canvas, model[1], GRAY, DARK_GRAY)
            elif (shape == self.hilt).all():
                self.drawShape(canvas, model[1], DARK_GRAY, "black")

    # Draw each shape on tkinter given 2D coordinates
    def drawShape(self, canvas, faces, fill, outline):
        # Sort faces by average position on z axis
        faces.sort(key = lambda tup: tup[8])
        # Draw each face in order of z-index
        for f in faces:
            canvas.create_polygon(f[0], f[1], f[2], f[3], f[4], f[5], f[6],
                                  f[7], fill = fill, outline = outline)