import socket
import threading
from queue import Queue

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
HOST = IPAddr
PORT = 15130

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST,PORT))
print("Found game on " + IPAddr + ":" + str(PORT) + "...")

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(1024).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

from tkinter import *

def init(data):
    (data.x, data.y, data.z) = (0, 0, 0)
    connected = "connect('screen')"
    print ("Sending: ", connected,)
    data.server.send(connected.encode())

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

def timerFired(data):
    while (serverMsg.qsize() > 0):
        msg = serverMsg.get(False)
        try:
            print("Received:", msg, "\n")
            msg = msg.split()
            command = msg[1].split("(")[0]
            args = msg[1].split("(")[1][:-1].split(",")
            if (command == "changePos"):
                data.x = args[0]
                data.y = args[1]
                data.z = args[2]
            elif (command == "connect"):
                connect(args[0])
        except:
            print("Message failed.")
        serverMsg.task_done()

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

serverMsg = Queue(100)

def sendMsg(msg):
    print ("Sending: ", msg,)
    server.send(msg.encode())
    # serverMsg.task_done()

threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()

run(300, 300, serverMsg, server)