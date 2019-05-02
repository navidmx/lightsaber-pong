import socket, random, threading, math, copy, pyaudio, wave
from tkinter import *
from queue import Queue
from lightsaber import Lightsaber
from laser import Laser

HOST = socket.gethostbyname(socket.gethostname())
PORT = 15271

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(2) # Accept max two connections (each player)

# Create constants (colors, and screen offset)
BLUE = '#00BFFF'
RED  = '#F32929'
GRAY = '#808080'
X_OFFSET, Y_OFFSET = 0.40, 0.60

print("-- Hosting game on %s:%d --" % (HOST, PORT))

class Struct(object): pass
data = Struct()

# Store data for both players
data.p1, data.p2 = { 'online' : False }, { 'online' : False }
data.gameStarted, data.gameOver = False, False

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

##########################
#####    Graphics    #####
##########################

titleImg = ""

def init(data):
    gameTime = 20 # seconds
    # Initialize player 1
    data.p1['model'] = Lightsaber(BLUE)
    data.p1['score'], data.p1['time'] = 0, gameTime
    data.p1['cx'], data.p1['cy'] = data.width * 0.50, data.height * 0.75

    # Load saved high score for training mode
    hiscore = open('hiscore.txt', 'r')
    data.p1['hiscore'] = int(hiscore.read())
    hiscore.close()

    # Initialize player 2
    data.p2['model'] = Lightsaber(RED)
    data.p2['score'], data.p2['time'] = 0, gameTime
    data.p2['cx'], data.p2['cy'] = data.width * 0.50, data.height * 0.55

    # Store in-game lasers
    data.p1['lasers'], data.p2['lasers'] = [], []
    data.counter = 0

def configure(event, data):
    # Check window re-sizing
    data.width = event.width
    data.height = event.height

def mousePressed(event, data):
    if not data.gameStarted:
        # Mode: Train
        if data.box1X1 < event.x < data.box1X2 and \
            data.boxY1 < event.y < data.boxY2 and data.p1['online']:
            startGame(data, "Train")
        # Mode: AI
        elif data.box2X1 < event.x < data.box2X2 and \
            data.boxY1 < event.y < data.boxY2 and data.p1['online']:
            data.p2['ai'] = True
            data.p2['aiLasers'] = []
            data.p2['aiSteps'] = []
            startGame(data, "AI")
        # Mode: 2-Player
        elif data.box3X1 < event.x < data.box3X2 and \
            data.boxY1 < event.y < data.boxY2 and data.p2['online']:
            data.p2['ai'] = False
            startGame(data, "2-Player")

def keyPressed(event, data): pass

def startGame(data, mode):
    data.gameStarted = True
    if mode == "AI":
        data.p2['online'] = True
        data.p2['x'], data.p2['y'], data.p2['z'] = 0, 0, 0
        runPlayerTwo(600, 450)
    elif mode == "2-Player":
        runPlayerTwo(800, 600)

def timerFired(data):
    if data.gameStarted:
        data.counter += 1
        if data.counter % 20 == 0:
            data.p1['lasers'].append(Laser(data.width, data.height, X_OFFSET,
                                     data.height * 0.2, data.height * 0.4))
        for laser in data.p1['lasers']:
            laser.move()
        if data.counter % 10 == 0:
            data.p1['time'] -= 1
        checkCollisions(data, data.p1)
        if data.p1['time'] == 0:
            data.gameStarted = False
            data.gameOver = True

def timerFiredTwo(data, dim):
    if data.gameStarted:
        if data.counter % 20 == 0:
            data.p2['lasers'].append(Laser(dim.width, dim.height, X_OFFSET,
                                     dim.height * 0.2, dim.height * 0.4))
            if data.p2['ai']:
                addNewSteps(data, data.p2['lasers'][len(data.p2['lasers']) - 1])
        for laser in data.p2['lasers']:
            laser.move()
        if data.counter % 10 == 0:
            data.p2['time'] -= 1
        checkCollisions(dim, data.p2)
        if data.p2['ai']:
            runAI(data, dim)

def addNewSteps(data, laser):
    pass
    # print(laser)

def runAI(data, dim):
    pass
    # lasers = copy.deepcopy(data.p2['lasers'])
    # for i in range(len(lasers)):
    #     if lasers[i] not in data.p2['aiLasers']:
    #         botY = lasers[i].points[2][1]
    #         medX = lasers[i].getFinalPos()
    #         currAngle = math.cos(math.radians(data.p2['x'] + 90))
    #         finalAngle = 90
    #         for decAngle in range(0, 18000, 1):
    #             angle = decAngle / 100
    #             if (10 < angle < 85) or (95 < angle < 170):
    #                 correctAngles = []
    #                 if math.cos(math.radians(angle)) / medX > 0:
    #                     correctAngles.append(angle)
    #                 if len(correctAngles) > 0:
    #                     finalAngle = max(correctAngles)
    #         data.p2['x'] = finalAngle - 90
    #         data.p2['aiLasers'].append(lasers[i])

def checkCollisions(data, player):
    lasers = copy.deepcopy(player['lasers'])
    keepLasers = []
    for i in range(len(lasers)):
        angle = math.cos(math.radians(player['x'] + 90))
        botY = lasers[i].points[2][1]
        medX = ((lasers[i].points[2][0] + lasers[i].points[3][0]) / 2) - \
               data.width / 2
        # Area for collision
        if data.height * 0.5 < botY < data.height * 0.6:
            if medX != 0:
                collided = angle / medX > 0
                if collided:
                    lasers[i].speed = -lasers[i].speed
                    player['score'] += 1
        width = abs(lasers[i].points[3][0] - lasers[i].points[2][0])
        if botY <= data.height * 0.75 and width > 10:
            keepLasers.append(lasers[i])
    player['lasers'] = keepLasers

def playFile(audioFile):
    # Play file using PyAudio
    wav = wave.open(audioFile, 'rb')
    p = pyaudio.PyAudio()
    # Create a stream with pyAudio settings
    stream = p.open(format = p.get_format_from_width(wav.getsampwidth()),
                    channels = wav.getnchannels(), rate = wav.getframerate(),
                    output = True)
    # Play stream from beginning to end
    audio = wav.readframes(1024)
    while audio != '':
        stream.write(audio)
        audio = wav.readframes(1024)
    # Close stream
    stream.close()
    p.terminate() 

def roundRectangle(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [x1+r, y1, x1+r, y1,
              x2-r, y1, x2-r, y1,
              x2, y1, x2, y1+r,
              x2, y1+r, x2, y2-r,
              x2, y2-r, x2, y2,
              x2-r, y2, x2-r, y2,
              x1+r, y2, x1+r, y2,
              x1, y2, x1, y2-r,
              x1, y2-r, x1, y1+r,
              x1, y1+r, x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

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
    # Draw host/port if player connected
    canvas.create_text(data.width / 2, 10, text="%s:%d" % (HOST, PORT),
                    fill="gray", font=('Helvetica', 16))
    score, time = player['score'], player['time']
    if 'hiscore' in player and not data.p2['online']:
        hiscore = player['hiscore']
        if hiscore >= score:
            scoreFill = "white"
            scoreText = "SCORE"
            canvas.create_text(60, 80, text="HI SCORE", fill=GRAY, anchor=CENTER, font=('Helvetica', 14, 'bold'))
            canvas.create_text(60, 105, text=hiscore, fill=BLUE, anchor=CENTER, font=('Helvetica', 32, 'bold'))
        else:
            scoreText = "HI SCORE"
            scoreFill = BLUE
    else:
        scoreFill = "white"
        scoreText = "SCORE"
    # Draw score
    canvas.create_text(60, 20, text=scoreText, fill=GRAY, anchor=CENTER, font=('Helvetica', 14, 'bold'))
    canvas.create_text(60, 45, text=score, fill=scoreFill, anchor=CENTER, font=('Helvetica', 32, 'bold'))
    # Draw time
    canvas.create_text(data.width - 60, 20, text="TIME", fill=GRAY, anchor=CENTER, font=('Helvetica', 14, 'bold'))
    canvas.create_text(data.width - 60, 45, text=time, fill="white", anchor=CENTER, font=('Helvetica', 32, 'bold'))

def drawSplash(canvas, data):
    global titleImg
    canvas.create_image(data.width / 2, data.height*0.15, anchor=CENTER,
                        image = titleImg)
    if not data.gameOver:
        drawHomeScreen(canvas, data)
    else:
        drawGameOver(canvas, data)

def drawHomeScreen(canvas, data):
    canvas.create_text(data.width/2, data.height*0.15 + 100, anchor=CENTER,
        text="%s:%s" % (HOST,PORT), fill=BLUE, font=('Helvetica', 24, 'bold'))
    # Highlight boxes based on players joined
    borderP1, borderP2 = GRAY, GRAY
    p1Text, p2Text = "NOT CONNECTED", "NOT CONNECTED"
    modeTrain, modeAI, modeCompete = GRAY, GRAY, GRAY
    if data.p1['online']:
        borderP1, p1Text = BLUE, "CONNECTED"
        modeTrain, modeAI = "white", "white"
        if data.p2['online']:
            borderP2, p2Text = RED, "CONNECTED"
            modeCompete = "white"
    # Player boxes
    pY1, pY2 = data.height * 0.4, data.height * 0.5
    p1X1, p1X2 = data.width * 0.1, data.width * 0.48
    p2X1, p2X2 = data.width * 0.52, data.width * 0.9
    roundRectangle(canvas, p1X1, pY1, p1X2, pY2, 20, outline=borderP1)
    canvas.create_text((p1X1 + p1X2)/2, (pY1 + pY2)/2, text=p1Text,
        fill=borderP1, font=('Helvetica', 22, 'bold'))
    roundRectangle(canvas, p2X1, pY1, p2X2, pY2, 20, outline=borderP2)
    canvas.create_text((p2X1 + p2X2)/2, (pY1 + pY2)/2, text=p2Text,
        fill=borderP2, font=('Helvetica', 22, 'bold'))
    # Mode boxes
    data.boxY1, data.boxY2 = data.height * 0.55, data.height * 0.95
    data.box1X1, data.box1X2 = data.width * 0.1, data.width * 0.34
    data.box2X1, data.box2X2 = data.width * 0.38, data.width * 0.62
    data.box3X1, data.box3X2 = data.width * 0.66, data.width * 0.9
    roundRectangle(canvas, data.box1X1, data.boxY1, data.box1X2, data.boxY2,
                            20, outline=modeTrain)
    roundRectangle(canvas, data.box2X1, data.boxY1, data.box2X2, data.boxY2,
                            20, outline=modeAI)
    roundRectangle(canvas, data.box3X1, data.boxY1, data.box3X2, data.boxY2,
                            20, outline=modeCompete)
    # Mode titles
    canvas.create_text((data.box1X1 + data.box1X2)/2, data.boxY2 - 80,
        text="TRAIN", fill=modeTrain, font=('Helvetica', 22, 'bold'))
    canvas.create_text((data.box2X1 + data.box2X2)/2, data.boxY2 - 80,
        text="COMPETE (AI)", fill=modeAI, font=('Helvetica', 22, 'bold'))
    canvas.create_text((data.box3X1 + data.box3X2)/2, data.boxY2 - 80,
        text="COMPETE", fill=modeCompete, font=('Helvetica', 22, 'bold'))
    # Mode descriptions
    canvas.create_text((data.box1X1 + data.box1X2)/2, data.boxY2 - 40,
        text="Play against the timer and beat\nyour own high score.",
        fill=modeTrain, font=('Helvetica', 12), justify=CENTER)
    canvas.create_text((data.box2X1 + data.box2X2)/2, data.boxY2 - 40,
        text="Play against various difficulty\nAI's and beat them!",
        fill=modeAI, font=('Helvetica', 12), justify=CENTER)
    canvas.create_text((data.box3X1 + data.box3X2)/2, data.boxY2 - 40,
        text="Play against another phone with\nthe same time limit.",
        fill=modeCompete, font=('Helvetica', 12), justify=CENTER)

def drawGameOver(canvas, data):
    w, h = data.width, data.height
    if not data.p2['online']:
        if data.p1['score'] > data.p1['hiscore']:
            hiscore = open('hiscore.txt', 'w')
            hiscore.write(str(data.p1['score']))
            hiscore.close()
            canvas.create_text(w / 2, h / 2 - 25, text="HI SCORE!",
                fill=BLUE, font=('Helvetica', 22, 'bold'))
        else:
            canvas.create_text(w / 2, h / 2 - 25, text="SCORE",
                fill=GRAY, font=('Helvetica', 22, 'bold'))
        canvas.create_text(w / 2, h / 2 + 25, text=data.p1['score'],
            fill="white", font=('Helvetica', 72, 'bold'))
    else:
        canvas.create_text(w * 0.3, h / 2 + 25, text=data.p1['score'],
            fill="white", font=('Helvetica', 72, 'bold'))
        canvas.create_text(w * 0.7, h / 2 + 25, text=data.p2['score'],
            fill="white", font=('Helvetica', 72, 'bold'))
        if data.p2['ai']:
            canvas.create_text(w * 0.3, h / 2 - 25, text="PLAYER SCORE",
                fill=BLUE, font=('Helvetica', 22, 'bold'))
            canvas.create_text(w * 0.7, h / 2 - 25, text="AI SCORE",
                fill=RED, font=('Helvetica', 22, 'bold'))
        else:
            canvas.create_text(w * 0.3, h / 2 - 25, text="PLAYER 1 SCORE",
                fill=BLUE, font=('Helvetica', 22, 'bold'))
            canvas.create_text(w * 0.7, h / 2 - 25, text="PLAYER 2 SCORE",
                fill=RED, font=('Helvetica', 22, 'bold'))

def simulatePlayer(player, difficulty):
    global playerNum
    player['online'] = True
    player['x'], player['y'], player['z'] = 0, 0, 0
    player['x'] += random.randint(-20, 20)
    player['z'] += random.randint(-20, 20)
    playerNum = 1

def redrawAll(canvas, data):
    # Window-responsive origins for player 1 and player 2
    c1x, c1y = data.width * 0.50, data.height * 0.75
    c2x, c2y = data.width * 0.50, data.height * 0.55

    # Draw background
    canvas.create_rectangle(0, 0, data.width, data.height, fill='black')

    simulatePlayer(data.p1, 0)

    if not data.gameStarted:
        drawSplash(canvas, data)
    else:
        # Draw perspective scene and game text
        drawScene(canvas, data)
        drawText(canvas, data, data.p1)
        # Draw lasers
        for laser in data.p1['lasers']:
            laser.draw(canvas)
        # Draw player 1 lightsaber
        data.p1['model'].draw(canvas, data.p1['x'], data.p1['y'], data.p1['z'],
                                c1x, c1y, 1)

def redrawAllTwo(canvas, data, dim):
    # Window-responsive origins for player 1 and player 2
    c1x, c1y = dim.width * 0.50, dim.height * 0.75
    c2x, c2y = dim.width * 0.50, dim.height * 0.55
    # Draw background
    canvas.create_rectangle(0, 0, dim.width, dim.height, fill='black')
    # Draw scene and text
    drawScene(canvas, dim)
    drawText(canvas, dim, data.p2)
    # Mirror angles and draw lightsaber 1
    # data.p1['model'].draw(canvas, -data.p1['x'], data.p1['y'], -data.p1['z'],
                          # c2x, c2y, 0.5)
    # Draw lasers
    for laser in data.p2['lasers']:
        laser.draw(canvas)
    # Draw lightsaber 2
    data.p2['model'].draw(canvas, data.p2['x'], data.p2['y'], data.p2['z'],
                          c1x, c1y, 1)
    if data.gameOver: top.destroy()

# NOTE:
# run() functions primarily from 15-112 starter code, with several changes
# to account for sockets and multiple screens (using toplevel)
# Starter code: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html

def runPlayerOne(width, height, serverMsg=None, server=None):
    # song = "assets/theme.wav"
    # threading.Thread(target=playFile, args=(song,)).start()
    global titleImg
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

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
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    canvas.bind("<Configure>", lambda event:
                               configureWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    titleImg = PhotoImage(file="assets/title.gif")
    root.mainloop()
    print("-- Player 1 closed --")
    quit()

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
        timerFiredTwo(data, dim)
        redrawAllWrapper(canvas, data, dim)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data, dim)

    global top
    top = Toplevel()
    top.title("Lightsaber Pong – Player 2")
    # Create a canvas without any margin or border
    canvas = Canvas(top, bd = 0, highlightthickness = 0, width = dim.width,
                    height = dim.height)
    canvas.pack(fill=BOTH, expand=1)
    canvas.bind("<Configure>", lambda event:
                               configureWrapper(event, canvas, dim))
    timerFiredWrapper(canvas, data, dim)

runPlayerOne(800, 600)