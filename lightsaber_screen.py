import socket
import threading
from queue import Queue

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname)
PORT = 15142

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(2) # Accept max two connections (each player)

print("-- Hosting game on " + HOST + ":" + str(PORT) + " --")

clientele = dict()
serverChannel = Queue(100)
names = ["Skywalker", "Vader"]
x, y, z = 0, 0, 0

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
    # print("> Received:", msg)
    msg = msg.split()
    command = msg[1].split("(")[0]
    args = msg[1].split("(")[1][:-1].split(",")
    if (command == "changePos"):
        global x, y, z
        x = float(args[0])
        y = float(args[1])
        z = float(args[2])
    for cID in clientele:
        if cID != msg[0]:
            clientele[cID].send(msg.encode())
            print("> Sent to %s:" % cID, msg)
    serverChannel.task_done()

def acceptConnections(playerNum):
    while True:
        client, address = server.accept()
        # myID is the key to the client in the clientele dictionary
        myID = names[playerNum]
        print(myID, playerNum)
        for cID in clientele:
            print (repr(cID), repr(playerNum))
            clientele[cID].send(("newPlayer %s\n" % myID).encode())
            client.send(("newPlayer %s\n" % cID).encode())
        clientele[myID] = client
        client.send(("myIDis %s \n" % myID).encode())
        print("connection recieved from %s" % myID)
        threading.Thread(target = handleClient, args = 
                            (client ,serverChannel, myID, clientele)).start()
        playerNum += 1

# Create threads to accept new connections and send/receive messages
threading.Thread(target=serverThread, args=(clientele, serverChannel)).start()
threading.Thread(target=acceptConnections, args=(0,)).start()

from tkinter import *

def init(data): pass

def mousePressed(event, data): pass

def keyPressed(event, data): pass

def timerFired(data): pass

def redrawAll(canvas, data):
    global x, y, z
    canvas.create_text(data.width/2, data.height/2 - 50, text="X: %0.2f" % x)
    canvas.create_text(data.width/2, data.height/2, text="Y: %0.2f" % y)
    canvas.create_text(data.width/2, data.height/2 + 50, text="Z: %0.2f" % z)

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
    data.timerDelay = 100 # Milliseconds
    init(data)
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("-- Game closed --")

run(500, 500)