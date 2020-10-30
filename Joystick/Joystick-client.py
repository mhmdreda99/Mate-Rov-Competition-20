import socket
import pygame
from pygame import locals
import time

#Creates instance of 'Socket'
s = socket.socket()

hostname = '169.254.237.79' #Server IP/Hostname
port = 8000 #Server Port

s.connect((hostname,port)) #Connects to server

pygame.init()
pygame.joystick.init()
print("Connected: ", pygame.joystick.get_count(), "joysticks")
j0 = pygame.joystick.Joystick(0)
j0.init()

while 1:
    for e in pygame.event.get():

        if e.type == pygame.JOYAXISMOTION:
            axis = "unknown"
            if (e.dict['axis'] == 0):
                axis = "X"

            if (e.dict['axis'] == 1):
                axis = "Y"

            if (e.dict['axis'] == 2):
                axis = "Throttle"

            if (e.dict['axis'] == 3):
                axis = "Z"

            if (axis != "unknown"):
                str = "Axis: %s; Value: %f" % (axis, e.dict['value'])
                if (axis == "X"):
                    posx = e.dict['value']
                    if posx == 1:
                        print("right")
                        x = 'd'
                        s.send(x.encode())

                    elif posx < -1:
                        print("LEFT")
                        x = 'a'
                        s.send(x.encode())

                elif axis == "Y":
                    posy = e.dict['value']
                    if posy < -1:
                        print("FORWARD")
                        x = 'w'
                        s.send(x.encode())

                    elif posy == 1:
                        print("BACKWARD")
                        x = 's'
                        s.send(x.encode())

        if e.type == pygame.locals.JOYBUTTONDOWN:
            if e.dict['button'] == 0:
                x = 'q'
                s.send(x.encode())
                print("up")
            elif e.dict['button'] == 1:
                x = 't'
                s.send(x.encode())
                print("Rotate right")
            elif e.dict['button'] == 2:
                x = 'e'
                s.send(x.encode())
                print("Down")
            elif e.dict['button'] == 3:
                x = 'r'
                s.send(x.encode())
                print("Rotate left")
            elif e.dict['button'] == 7:
                x = 'o'
                s.send(x.encode())
                print("ARM Open")
            elif e.dict['button'] == 5:
                x = 'c'
                s.send(x.encode())
                print("ARM Close")
            elif e.dict['button'] == 9:
                x = 'f'
                s.send(x.encode())
                print("Stop")
