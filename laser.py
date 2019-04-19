import numpy as np
import math
from matrix import CustomEngine

class Laser(CustomEngine):
    def __init__(self, x, y, z, speed):
        self.x, self.y, self.z = x, y, z
        self.speed = speed

    def move(self):
        self.z += self.speed
        self.y += self.speed/2

    def draw(self, canvas, cx, cy):
        self.laser = np.transpose(
                        [[-5, -5, self.z],      [-5, -5, self.z],
                         [-5, -5, self.z + 20], [-5, -5, self.z + 20],
                         [ 5, -5, self.z],      [ 5, -5, self.z],
                         [ 5, -5, self.z + 20], [ 5, -5, self.z + 20]]
                    )
        self.drawFaces(canvas, self.laser, "red", "white", cx, cy)