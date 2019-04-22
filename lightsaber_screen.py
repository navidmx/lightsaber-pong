import socket
import threading
from queue import Queue
from lightsaber import Lightsaber
from laser import Laser

hostname = socket.gethostname()
HOST     = socket.gethostbyname(hostname)
PORT     = 15251

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(2) # Accept max two connections (each player)

BLUE = '#00BFFF'
RED  = '#F32929'

print("-- Hosting game on " + HOST + ":" + str(PORT) + " --")

clientele     = dict()
serverChannel = Queue(100)
names         = ["Skywalker", "Vader"]
playerNum     = 0

# Default gravitational angles
x, y, z = 0, -1, 0

def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(64).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            return

# Convert x, y, z units to angles
def convert(x, y, z):
    angleX = -x * 90
    angleY = 0
    angleZ = -z * 90
    return (angleX, angleY, angleZ)

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        # print("> Received:", msg)
        msg = msg.split()
        command = msg[1].split("(")[0]
        args = msg[1].split("(")[1][:-1].split(",")
        if (command == "changePos"):
            global x, y, z
            x, y, z = convert(float(args[0]), float(args[1]), float(args[2]))
            # print("X: %0.2f, Y: %0.2f, Z: %0.2f" % (x, y, z))
        for cID in clientele:
            if cID != msg[0]:
                clientele[cID].send(msg.encode())
                print("> Sent to %s:" % cID, msg)
        serverChannel.task_done()

def acceptConnections():
    global playerNum
    while True:
        client, address = server.accept()
        # myID is the key to the client in the clientele dictionary
        myID = names[playerNum]
        print(myID, playerNum)
        for cID in clientele:
            clientele[cID].send(("newPlayer %s\n" % myID).encode())
            client.send(("newPlayer %s\n" % cID).encode())
        clientele[myID] = client
        client.send(("myIDis %s \n" % myID).encode())
        print("Connection recieved from Player %d, %s" % (playerNum + 1, myID))
        threading.Thread(target = handleClient, args = 
                         (client ,serverChannel, myID, clientele)).start()
        playerNum += 1

# Create threads to accept new connections and send/receive messages
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()
threading.Thread(target=acceptConnections).start()

##################
#    Graphics    #
##################

from tkinter import *

def init(data):
    data.p1 = {
        'online': False,
        'model': Lightsaber(BLUE, 0),
        'x': data.width * 0.50,
        'y': data.height * 0.75
    }
    data.p2 = {
        'online': False,
        'model': Lightsaber(RED, -100),
        'x': data.width * 0.50,
        'y': data.height * 0.50
    }
    data.lasers = []
    data.counter = 0
    data.x_offset = 0.40
    data.y_offset = 0.60

def configure(event, data):
    data.width = event.width
    data.height = event.height

def mousePressed(event, data): pass

def keyPressed(event, data): pass

def timerFired(data):
    data.counter += 1
    if data.counter % 20 == 0:
        # Create new laser at random x/y with random speed
        data.lasers.append(Laser(-20, 50, 200))
    for laser in data.lasers:
        laser.move()

def drawScene(c, data):
    color = "gray"
    c.create_line(0, data.height, data.width * data.x_offset,
                  data.height * data.y_offset, fill = color)
    c.create_line(data.width, data.height, data.width * data.y_offset,
                  data.height * data.y_offset, fill = color)
    c.create_line(data.width * data.x_offset, 0, data.width * data.x_offset,
                  data.height * data.y_offset, fill = color)
    c.create_line(data.width * data.y_offset, 0, data.width * data.y_offset,
                  data.height * data.y_offset, fill = color)
    c.create_line(data.width * data.x_offset, data.height * data.y_offset,
                  data.width * data.y_offset, data.height * data.y_offset,
                  fill = color)

def redrawAll(canvas, data):
    global x, y, z

    # Draw background
    canvas.create_rectangle(0, 0, data.width, data.height, fill = 'black')

    # Draw scene
    drawScene(canvas, data)

    # Draw lasers
    for laser in data.lasers:
        laser.draw(canvas, data.p1['x'], data.p1['y'])

    # Draw models if player 1 online
    if data.p1['online']:

        # Draw player 2 lightsaber (if online)
        if data.p2['online']:
            data.p2['model'].draw(canvas, x, y, z, data.p2.x, data.p2.y)

        # Draw player 1 lightsaber
        data.p1['model'].draw(canvas, x, y, z, data.p1.x, data.p1.y)

    # Draw angles from phone (for debugging)
    canvas.create_text(data.width - 40, 20,
                       text="X: %0.2f" % x, fill="white")
    canvas.create_text(data.width - 40, 40,
                       text="Y: %0.2f" % y, fill="white")
    canvas.create_text(data.width - 40, 60,
                       text="Z: %0.2f" % z, fill="white")

def runPlayerOne(width, height, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Check if user changes window size
    def configureWrapper(event, canvas, data):
        configure(event, data)
        redrawAllWrapper(canvas, data)

    class Struct(object): pass
    data = Struct()
    # data.server = server
    # data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # Milliseconds
    init(data)
    root = Tk()
    root.title("Player 1")
    # Create a canvas without any margin or border
    canvas = Canvas(root, bd=0, highlightthickness=0, width=data.width,
                    height=data.height)
    canvas.pack(fill=BOTH, expand=1)
    canvas.bind("<Configure>", lambda event:
                            configureWrapper(event, canvas, data))
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("-- Game closed --")

runPlayerOne(800, 600)