class Dot(object):

    def __init__(self, PID, x, y):
        self.PID = PID
        self.x = x
        self.y = y
        self.size = 30

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def teleport(self, x, y):
        self.x = x
        self.y = y

    def changePID(self, PID):
        self.PID = PID

    def drawDot(self, canvas, color):
        r = self.size
        canvas.create_oval(self.x-r, self.y-r, 
                           self.x+r, self.y+r, fill=color)
        canvas.create_text(self.x, self.y, text=self.PID, fill="white")