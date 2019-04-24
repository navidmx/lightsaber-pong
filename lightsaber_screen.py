import socket
import random
import threading
import math
import copy
from queue import Queue
from lightsaber import Lightsaber
from laser import Laser

HOST = socket.gethostbyname(socket.gethostname())
PORT = 15277

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(2) # Accept max two connections (each player)

BLUE = '#00BFFF'
RED  = '#F32929'

X_OFFSET = 0.40
Y_OFFSET = 0.60

print("-- Hosting game on %s:%d --" % (HOST, PORT))

class Struct(object): pass
data = Struct()

# Store data for both players
data.p1, data.p2 = { 'online' : False }, { 'online' : False }

clientele     = dict()
serverChannel = Queue(100)
names         = ["Skywalker", "Vader"]
playerNum     = 0

# Convert phone's x, y, z units to angles
convert = lambda x, y, z: (-x * 90, 0, -z * 90)

def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(64).decode("UTF-8")
            # print(msg)
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            return

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None).split()
        # Break message into necessary components
        player = msg[0]
        command = msg[1].split("(")[0]
        args = msg[1].split("(")[1][:-1].split(",")
        # Apply commands to correct player
        if player == "Skywalker": player = data.p1
        elif player == "Vader": player = data.p2
        # Read change position command
        if (command == "changePos"):
            player['x'], player['y'], player['z'] = \
                convert(float(args[0]), float(args[1]), float(args[2]))
        # Send messages to all other players
        for cID in clientele:
            if cID != player:
                msg = ''.join(msg)
                # clientele[cID].send(msg.encode())
                # print("> Sent to %s:" % cID, msg)
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
        if playerNum == 1:
            data.p1['online'] = True
            data.p1['x'], data.p1['y'], data.p1['z'] = 0, 0, 0
        if playerNum == 2:
            data.p2['online'] = True
            data.p2['x'], data.p2['y'], data.p2['z'] = 0, 0, 0

# Create threads to accept new connections and send/receive messages
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()
threading.Thread(target=acceptConnections).start()

##################
#    Graphics    #
##################

from tkinter import *

def init(data):
    # Initialize player 1
    data.p1['model'] = Lightsaber(BLUE)
    data.p1['score'] = 0
    data.p1['cx'], data.p1['cy'] = data.width * 0.50, data.height * 0.75

    # Initialize player 2
    data.p2['model'] = Lightsaber(RED)
    data.p2['score'] = 0
    data.p2['cx'], data.p2['cy'] = data.width * 0.50, data.height * 0.55

    # Store in-game lasers
    data.lasers = []
    data.counter = 0

    # Switch for whether screen 2 opened
    data.p2['opened'] = False

# Check window re-sizing (player 1)
def configure(event, data):
    data.width = event.width
    data.height = event.height

def mousePressed(event, data): pass

def keyPressed(event, data): pass

def timerFired(data):
    if data.p1['online']:
        data.counter += 1
        if data.counter % 20 == 0:
            # Create new laser
            data.lasers.append(Laser(data.width, X_OFFSET, data.height * 0.2,
                            data.height * 0.4))
        for laser in data.lasers:
            laser.move()

def checkCollisions(data, player):
    lasers = copy.deepcopy(data.lasers)
    keepLasers = []
    for i in range(len(lasers)):
        angle = math.cos(math.radians(player['x'] + 90))
        botY = lasers[i].points[2][1]
        medX = ((lasers[i].points[2][0] + lasers[i].points[3][0]) / 2) - \
               data.width / 2
        # Area for collision
        if data.height * 0.5 < botY < data.height * 0.6:
            collided = angle / medX > 0
            if collided:
                lasers[i].speed = -lasers[i].speed
                player['score'] += 1
        width = abs(lasers[i].points[3][0] - lasers[i].points[2][0])
        print(i, width)
        if botY <= data.height * 0.6 and width > 10:
            keepLasers.append(lasers[i])
        else:
            player['score'] -= 1
    data.lasers = keepLasers

def drawScene(canvas, data):
    # Color of perspective lines
    color = '#696969'
    canvas.create_line(0, data.height, data.width * X_OFFSET,
                  data.height * Y_OFFSET, fill=color)
    canvas.create_line(data.width, data.height, data.width * Y_OFFSET,
                  data.height * Y_OFFSET, fill=color)
    canvas.create_line(data.width * X_OFFSET, 0, data.width * X_OFFSET,
                  data.height * Y_OFFSET, fill=color)
    canvas.create_line(data.width * Y_OFFSET, 0, data.width * Y_OFFSET,
                  data.height * Y_OFFSET, fill=color)
    canvas.create_line(data.width * X_OFFSET, data.height * Y_OFFSET,
                  data.width * Y_OFFSET, data.height * Y_OFFSET, fill=color)

def drawText(canvas, data, player = None):
    if player == None:
        # Draw host and port to join
        canvas.create_text(data.width/2, data.height/2-15, text="Join game at",
                           fill="gray", font=('Helvetica', 18))
        canvas.create_text(data.width/2, data.height/2+15, text="%s:%d" % (HOST,
                           PORT), fill="white", font=('Helvetica', 36, 'bold'))
    else:
        # Draw smaller host/port if player connected
        canvas.create_text(data.width / 2, 10, text="%s:%d" % (HOST, PORT),
                        fill="gray", font=('Helvetica', 16))
        # Draw angles from phone (for debugging)
        x, y, z, score = player['x'], player['y'], player['z'], player['score']
        canvas.create_text(data.width-40, 20, text="X: %0.2f" % x, fill="white")
        canvas.create_text(data.width-40, 40, text="Y: %0.2f" % y, fill="white")
        canvas.create_text(data.width-40, 60, text="Z: %0.2f" % z, fill="white")
        canvas.create_text(40, 40, text="Score: %d" % score, fill="white")

def simulatePlayer(data, player):
    global playerNum
    player['online'] = True
    player['x'], player['y'], player['z'] = 0, 0, 0
    player['x'] += random.randint(-20, 20)
    player['z'] += random.randint(-20, 20)
    playerNum = 2

def redrawAll(canvas, data):
    # Window-responsive origins for player 1 and player 2
    c1x, c1y = data.width * 0.50, data.height * 0.75
    c2x, c2y = data.width * 0.50, data.height * 0.55

    # Draw background
    canvas.create_rectangle(0, 0, data.width, data.height, fill='black')

    # Draw lasers
    for laser in data.lasers:
        laser.draw(canvas)

    simulatePlayer(data, data.p1)
    # simulatePlayer(data, data.p2)

    # Draw models if player 1 online
    if data.p1['online']:
        # Draw perspective scene and game text
        drawScene(canvas, data)
        drawText(canvas, data, data.p1)
        if data.p2['online']:
            # Open second window
            if not data.p2['opened']:
                runPlayerTwo(600, 450)
                data.p2['opened'] = True
            checkCollisions(data, data.p2)
            # Draw player 2 lightsaber (if online)
            data.p2['model'].draw(canvas, data.p2['x'], data.p2['y'],
                                  data.p2['z'], c2x, c2y, 0.5)

        checkCollisions(data, data.p1)
        # Draw player 1 lightsaber
        data.p1['model'].draw(canvas, data.p1['x'], data.p1['y'], data.p1['z'],
                              c1x, c1y, 1)
    else:
        # Draw join game text
        drawText(canvas, data)

def redrawAllTwo(canvas, data, dim):
    # Window-responsive origins for player 1 and player 2
    c1x, c1y = dim.width * 0.50, dim.height * 0.75
    c2x, c2y = dim.width * 0.50, dim.height * 0.55

    # Draw background
    canvas.create_rectangle(0, 0, dim.width, dim.height, fill='black')

    # Draw scene
    drawScene(canvas, dim)

    # Mirror angles and draw lightsaber 1
    data.p1['model'].draw(canvas, -data.p1['x'], data.p1['y'], -data.p1['z'],
                          c2x, c2y, 0.5)

    # Draw lightsaber 2
    data.p2['model'].draw(canvas, data.p2['x'], data.p2['y'], data.p2['z'],
                          c1x, c1y, 1)

    drawText(canvas, dim, data.p2)

# NOTE:
# run() functions primarily from 15-112 starter code, with several changes
# to account for sockets and multiple screens (using toplevel)
# Starter code: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html

def runPlayerOne(width, height, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Check if user changes window size
    def configureWrapper(event, canvas, data):
        configure(event, data)
        redrawAllWrapper(canvas, data)

    # data.server = server
    # data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # Milliseconds
    init(data)
    root = Tk()
    root.title("Lightsaber Pong – Player 1")
    # Create a canvas without any margin or border
    canvas = Canvas(root, bd = 0, highlightthickness = 0, width = data.width,
                    height = data.height)
    canvas.pack(fill=BOTH, expand=1)
    canvas.bind("<Configure>", lambda event:
                               configureWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("-- Player 1 closed --")

def runPlayerTwo(width, height):
    # Create second window with a second data set that only stores instance
    # important variables (like the different window size) called "dim"
    dim = Struct()
    dim.width = width
    dim.height = height

    def redrawAllWrapper(canvas, data, dim):
        canvas.delete(ALL)
        redrawAllTwo(canvas, data, dim)
        canvas.update()

    # Check if user changes window size
    def configureWrapper(event, canvas, dim):
        configure(event, dim)
        redrawAllWrapper(canvas, data, dim)

    def timerFiredWrapper(canvas, data, dim):
        timerFired(data)
        redrawAllWrapper(canvas, data, dim)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data, dim)

    top = Toplevel()
    top.title("Lightsaber Pong – Player 2")
    # Create a canvas without any margin or border
    canvas = Canvas(top, bd = 0, highlightthickness = 0, width = dim.width,
                    height = dim.height)
    canvas.pack(fill=BOTH, expand=1)
    canvas.bind("<Configure>", lambda event:
                               configureWrapper(event, canvas, dim))
    timerFiredWrapper(canvas, data, dim)
    print("-- Player 2 closed --")

runPlayerOne(800, 600)