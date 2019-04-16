import socket
import threading
from queue import Queue

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname)
PORT = 15136

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(4)

print("Hosting game on " + HOST + ":" + str(PORT) + "...")

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

def serverThread(clientele, serverChannel):
  while True:
    msg = serverChannel.get(True, None)
    print("> Received:", msg)
    msg = msg.split()
    command = msg[1].split("(")[0]
    args = msg[1].split("(")[1][:-1].split(",")
    if (command == "changePos"):
        x = args[0]
        y = args[1]
        z = args[2]
    for cID in clientele:
        if cID != msg[0]:
            clientele[cID].send(msg.encode())
            print("> Sent to %s:" % cID, msg)
    serverChannel.task_done()

clientele = dict()

serverChannel = Queue(100)

names = ["Luke", "Leia", "Han", "Chewie", "Kylo", "Yoda"]

from tkinter import *

def init(data):
    (data.x, data.y, data.z) = (0, 0, 0)
    data.playerNum = 0

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

def timerFired(data):
    client, address = server.accept()
    myID = names[data.playerNum]
    clientele[myID] = client
    print("Connection recieved from %s" % myID)
    # threading.Thread(target = handleClient, args = (client, serverChannel, myID, clientele)).start()
    data.playerNum += 1
    msg = serverChannel.get(True, None)
    print("> Received:", msg)
    msg = msg.split()
    command = msg[1].split("(")[0]
    args = msg[1].split("(")[1][:-1].split(",")
    if (command == "changePos"):
        data.x = args[0]
        data.y = args[1]
        data.z = args[2]
    for cID in clientele:
        if cID != msg[0]:
            clientele[cID].send(msg.encode())
            print("> Sent to %s:" % cID, msg)
    serverChannel.task_done()

def redrawAll(canvas, data):
    canvas.create_text(150, 100, text="X: " + str(data.x))
    canvas.create_text(150, 150, text="Y: " + str(data.y))
    canvas.create_text(150, 200, text="Z: " + str(data.z))

####################################
# Default run function
####################################

def run(width, height, serverMsg=None, server=None):
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
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(200, 200)
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()