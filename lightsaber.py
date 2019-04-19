import math
import numpy as np
from tkinter import *
from matrix import CustomEngine

GRAY = '#A9A9A9'
DARK_GRAY = '#696969'
BLUE = '#00BFFF'

class Lightsaber(CustomEngine):
    def __init__(self):
        self.epsilon = lambda d: d * 1
        # Node connections to draw rectangles

    def draw(self, canvas, x, y, z, cx, cy):
        self.ax = math.radians(z)
        self.ay = math.radians(y)
        self.az = math.radians(x)
        self.cx, self.cy = cx, cy

        # Coordinates for lightsaber blade, automatically transposed/translated
        self.lightsaber = np.transpose([[-10, -50, -10], [-10, -300, -10],
                                        [-10, -50,  10], [-10, -300,  10],
                                        [ 10, -50, -10], [ 10, -300, -10],
                                        [ 10, -50,  10], [ 10, -300,  10]])
        self.lightsaber = self.rotateShape(self.lightsaber)
        self.drawFaces(canvas, self.lightsaber, BLUE, "white", cx, cy)

        # Coordinates for lightsaber handle, automatically transposed
        self.handle = np.transpose([[-10, -50, -10], [-10, 50, -10],
                                    [-10, -50,  10], [-10, 50,  10],
                                    [ 10, -50, -10], [ 10, 50, -10],
                                    [ 10, -50,  10], [ 10, 50,  10]])
        self.handle = self.rotateShape(self.handle)
        self.drawFaces(canvas, self.handle, GRAY, DARK_GRAY, cx, cy)

        # Coordinates for lightsaber handle, automatically transposed
        self.hilt = np.transpose([[-12, 50, -12], [-15, 60, -12],
                                  [-12, 50,  12], [-15, 60,  12],
                                  [ 12, 50, -12], [ 15, 60, -12],
                                  [ 12, 50,  12], [ 15, 60,  12]])
        self.hilt = self.rotateShape(self.hilt)
        self.drawFaces(canvas, self.hilt, DARK_GRAY, "black", cx, cy)

    def rotateShape(self, shape):
        shape = self.rotateX(self.epsilon(self.ax), shape)
        shape = self.rotateY(self.epsilon(self.ay), shape)
        shape = self.rotateZ(self.epsilon(self.az), shape)
        return shape