import random
import numpy as np

class Laser(object):
    def __init__(self, width, height, offset, y, endY):
        w, self.h = 5, 15 # Width and height of lasers
        self.speed = random.randint(3,5) # Set random speed
        self.width, self.height = width, height
        self.endY = endY

        startW = width * (1 - 2 * offset)
        # Create random starting x
        x = (width - 2 * w) * offset + random.randint(0, int(startW))

        # Create top left/right coordinates of laser
        topLX, topLY = x - w, y
        topRX, topRY = x + w, y

        # Get slope of each laser's sides by comparing starting/ending point
        self.endLX = ((topLX - (width * offset)) / startW) * (width * 0.5) + width * 0.25
        self.endRX = ((topRX - (width * offset)) / startW) * (width * 0.5) + width * 0.25
        self.slopeL = (topLY - endY) / (topLX - self.endLX)
        self.slopeR = (topRY - endY) / (topRX - self.endRX)

        # Create bottom left/right coordinates of laser with slope/height
        botLX, botLY = topLX + (self.h / self.slopeL), topLY + self.h
        botRX, botRY = topRX + (self.h / self.slopeR), topRY + self.h

        self.points = [[topLX, topLY], [topRX, topRY],
                       [botRX, botRY], [botLX, botLY]]

    def __eq__(self, other):
        return self.endLX == other.endLX and self.endRX == other.endRX

    def getFinalPos(self):
        speed, slopeL, slopeR = self.speed, self.slopeL, self.slopeR
        points = self.points
        while not (self.height * 0.5 < points[2][1] < self.height * 0.6):
            changeLX = speed / slopeL
            changeRX = speed / slopeR
            points[0][0] += changeLX
            points[1][0] += changeRX
            points[2][0] = points[1][0] + (self.h / slopeR)
            points[3][0] = points[0][0] + (self.h / slopeL)
            for point in points:
                point[1] += speed * 6/5
            speed += 1
        return (((points[2][0] + points[3][0]) / 2) - self.width / 2)

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