import socket
import random
import threading
from queue import Queue
from lightsaber import Lightsaber
from laser import Laser

HOST = socket.gethostbyname(socket.gethostname())
PORT = 15265

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(2) # Accept max two connections (each player)

BLUE = '#00BFFF'
RED  = '#F32929'

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
    data.p1['model'] = Lightsaber(BLUE, 0, 1)
    data.p1['cx'] = data.width * 0.50
    data.p1['cy'] = data.height * 0.75
    # Initialize player 2
    data.p2['model'] = Lightsaber(RED, 0, 0.4)
    data.p2['cx'] = data.width * 0.50
    data.p2['cy'] = data.height * 0.55
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
    data.counter += 1
    if data.counter % 20 == 0:
        # Create new laser at random x/y with random speed
        data.lasers.append(Laser(-20, 50, 200))
    for laser in data.lasers:
        laser.move()

def drawScene(canvas, data):
    # Window offset to draw perspective map
    x_offset = 0.40
    y_offset = 0.60
    # Color of perspective lines
    color = '#696969'
    canvas.create_line(0, data.height, data.width * x_offset,
                  data.height * y_offset, fill=color)
    canvas.create_line(data.width, data.height, data.width * y_offset,
                  data.height * y_offset, fill=color)
    canvas.create_line(data.width * x_offset, 0, data.width * x_offset,
                  data.height * y_offset, fill=color)
    canvas.create_line(data.width * y_offset, 0, data.width * y_offset,
                  data.height * y_offset, fill=color)
    canvas.create_line(data.width * x_offset, data.height * y_offset,
                  data.width * y_offset, data.height * y_offset, fill=color)

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
        x, y, z = player['x'], player['y'], player['z']
        canvas.create_text(data.width-40, 20, text="X: %0.2f" % x, fill="white")
        canvas.create_text(data.width-40, 40, text="Y: %0.2f" % y, fill="white")
        canvas.create_text(data.width-40, 60, text="Z: %0.2f" % z, fill="white")

def simulatePlayer(data, player):
    global playerNum
    player['online'] = True
    player['x'], player['y'], player['z'] = random.randint(-45, 45), 0, \
                                            random.randint(-45, 45)
    if playerNum == 1: playerNum = 2

def redrawAll(canvas, data):
    # Window-responsive origins for player 1 and player 2
    c1x, c1y = data.width * 0.50, data.height * 0.75
    c2x, c2y = data.width * 0.50, data.height * 0.55

    # Draw background
    canvas.create_rectangle(0, 0, data.width, data.height, fill='black')

    # Draw lasers
    # for laser in data.lasers:
    #     laser.draw(canvas, data.p1['cx'], data.p1['cy'])

    simulatePlayer(data, data.p2)

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
            # Draw player 2 lightsaber (if online)
            data.p2['model'].draw(canvas, data.p2['x'], data.p2['y'],
                                  data.p2['z'], c2x, c2y, 0.5)

        # Draw player 1 lightsaber
        data.p1['model'].draw(canvas, data.p1['x'], data.p1['y'], data.p1['z'],
                              c1x, c1y, 1)
    else:
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
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event: keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("-- Player 1 closed --")

def runPlayerTwo(width, height):
    # Create second window with a second data set that only stores instance
    # important variables (like the different window size)
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