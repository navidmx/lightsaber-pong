import numpy as np
from matrix import CustomEngine

GRAY = '#A9A9A9'
DARK_GRAY = '#696969'

class Lightsaber(CustomEngine):
    def __init__(self, color, z, scale):
        super().__init__()
        self.z = 0
        self.color = color

    def draw(self, canvas, x, y, z, cx, cy, scale):
        # Convert angles to radians, and correct X/Z axes
        ax, ay, az = np.radians(z), np.radians(y), np.radians(x)
        w = 10 * scale
        h = 50 * scale

        # 3D coordinates for lightsaber blade
        self.lightsaber = np.transpose(
                            [[-w, -h, self.z-w], [-w, -6*h, self.z-w],
                             [-w, -h, self.z+w], [-w, -6*h, self.z+w],
                             [ w, -h, self.z-w], [ w, -6*h, self.z-w],
                             [ w, -h, self.z+w], [ w, -6*h, self.z+w]]
                          )
        # 3D coordinates for lightsaber handle
        self.handle = np.transpose(
                            [[-w, -h, self.z-w], [-w, h, self.z-w],
                             [-w, -h, self.z+w], [-w, h, self.z+w],
                             [ w, -h, self.z-w], [ w, h, self.z-w],
                             [ w, -h, self.z+w], [ w, h, self.z+w]]
                      )
        # 3D coordinates for lightsaber hilt
        self.hilt = np.transpose(
                        [[-(w+2), h, self.z-(w+2)], [-(w+3), (h+10), self.z-(w+2)],
                         [-(w+2), h, self.z+(w+2)], [-(w+3), (h+10), self.z+(w+2)],
                         [ (w+2), h, self.z-(w+2)], [ (w+3), (h+10), self.z-(w+2)],
                         [ (w+2), h, self.z+(w+2)], [ (w+3), (h+10), self.z+(w+2)]]
                    )
        # 3D coordinates for lightsaber mod1
        self.mod1 = np.transpose(
                            [[-w, -h, self.z-(w+2)], [-w, -h-5, self.z-(w+2)],
                             [-w, -h, self.z+(w+2)], [-w, -h-5, self.z+(w+2)],
                             [ w, -h, self.z-(w+2)], [ w, -h-5, self.z-(w+2)],
                             [ w, -h, self.z+(w+2)], [ w, -h-5, self.z+(w+2)]]
                    )

        # Get 2D coordinates necessary to draw each 3D model
        models = []
        models.append(self.getFaceCoords(self.lightsaber, cx, cy, ax, ay, az))
        models.append(self.getFaceCoords(self.handle, cx, cy, ax, ay, az))
        models.append(self.getFaceCoords(self.hilt, cx, cy, ax, ay, az))
        models.append(self.getFaceCoords(self.mod1, cx, cy, ax, ay, az))
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
            elif (shape == self.mod1).all():
                self.drawShape(canvas, model[1], DARK_GRAY, "black")

    # Draw each shape on tkinter given 2D coordinates
    def drawShape(self, canvas, faces, fill, outline):
        # Sort faces by average position on z axis
        faces.sort(key = lambda tup: tup[8])
        # Draw each face in order of z-index
        for f in faces:
            canvas.create_polygon(f[0], f[1], f[2], f[3], f[4], f[5], f[6],
                                  f[7], fill = fill, outline = outline)