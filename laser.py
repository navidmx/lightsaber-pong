import random
import numpy as np

class Laser(object):
    def __init__(self, width, offset, y, endY):
        w, self.h = 5, 15 # Width and height of lasers
        self.speed = random.randint(3,5) # Set random speed

        startW = width * (1 - 2 * offset)
        # Create random starting x
        x = (width - 2 * w) * offset + random.randint(0, int(startW))

        # Create top left/right coordinates of laser
        topLX, topLY = x - w, y
        topRX, topRY = x + w, y

        # Get slope of each laser's sides by comparing starting/ending point
        self.endLX = ((topLX - (width * offset)) / startW) * width
        self.endRX = ((topRX - (width * offset)) / startW) * width
        self.slopeL = (topLY - endY) / (topLX - self.endLX)
        self.slopeR = (topRY - endY) / (topRX - self.endRX)

        # Create bottom left/right coordinates of laser with slope/height
        botLX, botLY = topLX + (self.h / self.slopeL), topLY + self.h
        botRX, botRY = topRX + (self.h / self.slopeR), topRY + self.h

        self.points = [[topLX, topLY], [topRX, topRY],
                       [botRX, botRY], [botLX, botLY]]

    def move(self):
        changeLX = self.speed / self.slopeL
        changeRX = self.speed / self.slopeR
        self.points[0][0] += changeLX
        self.points[1][0] += changeRX
        self.points[2][0] = self.points[1][0] + (self.h / self.slopeR)
        self.points[3][0] = self.points[0][0] + (self.h / self.slopeL)
        for point in self.points:
            point[1] += self.speed * 6/5
        self.speed += 1

    def draw(self, canvas):
        faces = [self.points[0][0], self.points[0][1],
                 self.points[1][0], self.points[1][1],
                 self.points[2][0], self.points[2][1],
                 self.points[3][0], self.points[3][1]]
        self.drawShape(canvas, faces, "red", "white")

    # Draw each shape on tkinter given 2D coordinates
    def drawShape(self, canvas, f, fill, outline):
        canvas.create_polygon(f[0], f[1], f[2], f[3], f[4], f[5], f[6],
                                f[7], fill = fill, outline = outline)