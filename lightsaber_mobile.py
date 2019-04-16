from scene import *
import socket
import threading
from queue import Queue

# Setup sockets server
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
HOST = "128.237.171.234"
PORT = 15122

# Connect to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST,PORT))
print("Joining game...")

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

class LightsaberView (Scene):
    
    def setup(self):
        # Set up scene
        self.background_color = "#111111"
        self.counter = 0
        # Create x/y/z position labels
        self.x_pos = LabelNode('0', ('Futura', 40), parent = self)
        self.y_pos = LabelNode('0', ('Futura', 40), parent = self)
        self.z_pos = LabelNode('0', ('Futura', 40), parent = self)
        self.x_pos.position = (self.size.w/2, self.size.h/2 + 50)
        self.y_pos.position = (self.size.w/2, self.size.h/2)
        self.z_pos.position = (self.size.w/2, self.size.h/2 - 50)
        self.x_pos.z_position = 1
        self.y_pos.z_position = 1
        self.z_pos.z_position = 1
        sendMsg("connect('phone')\n")

    def update(self):
        self.counter += 1
        if self.counter % 5 == 0:
            g = gravity()

            # Update position labels (on phone)
            self.x_pos.text = str("X: %0.2f" % g.x)
            self.y_pos.text = str("Y: %0.2f" % g.y)
            self.z_pos.text = str("Z: %0.2f" % g.z)

            # Send position labels (to computer)
            sendMsg("changePos(%f,%f,%f)\n" % (g.x, g.y, g.z))

serverMsg = Queue(100)

def sendMsg(msg):
    print ("Sending: ", msg,)
    server.send(msg.encode())
    # serverMsg.task_done()

if __name__ == '__main__':
    run(LightsaberView(), PORTRAIT, show_fps=True)

threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()