import socket
import time

import RPi.GPIO as GPIO

LEFT_DIR_PIN_1 = 13 # Your pin numbers here
LEFT_DIR_PIN_2 = 15
LEFT_PWM_PIN = 33

RIGHT_DIR_PIN_1 = 16
RIGHT_DIR_PIN_2 = 18
RIGHT_PWM_PIN = 12

UP_DIR_PIN_1 = 13
UP_DIR_PIN_2 = 13
UP_PWM_PIN = 13

GPIO.setmode(GPIO.BOARD)

# Set up the pins for output
GPIO.setup(LEFT_DIR_PIN_1, GPIO.OUT)
GPIO.setup(LEFT_DIR_PIN_2, GPIO.OUT)
GPIO.setup(LEFT_PWM_PIN, GPIO.OUT)

# Stop the motor
GPIO.output(LEFT_DIR_PIN_1, GPIO.LOW)
GPIO.output(LEFT_DIR_PIN_2, GPIO.LOW)

#Initialize the power
left = GPIO.PWM(LEFT_PWM_PIN, 100) # 100 khz duty cycle


# Set up the pins for ouptut
GPIO.setup(RIGHT_DIR_PIN_1, GPIO.OUT)
GPIO.setup(RIGHT_DIR_PIN_2, GPIO.OUT)
GPIO.setup(RIGHT_PWM_PIN, GPIO.OUT)

# Stop the motor
GPIO.output(RIGHT_DIR_PIN_1, GPIO.LOW)
GPIO.output(RIGHT_DIR_PIN_2, GPIO.LOW)

# Initialize the power
right = GPIO.PWM(RIGHT_PWM_PIN, 100) # 100 khz duty cycle


# Set up the pins for ouptut
GPIO.setup(UP_DIR_PIN_1, GPIO.OUT)
GPIO.setup(UP_DIR_PIN_2, GPIO.OUT)
GPIO.setup(UP_PWM_PIN, GPIO.OUT)

# Stop the motor
GPIO.output(UP_DIR_PIN_1, GPIO.LOW)
GPIO.output(UP_DIR_PIN_2, GPIO.LOW)

# Initialize the power
up = GPIO.PWM(UP_PWM_PIN, 100) # 100 khz duty cycle


left_forward = 0 # Integer representing the motor controller state. (1 = forward, 0 = stop, -1 = backward)
left_power = 0

right_forward = 0
right_power = 0

up_forward = 0
up_power = 0

def leftForward():
    global left_forward
    if left_forward != 1:
        GPIO.output(LEFT_DIR_PIN_1, GPIO.HIGH)
        GPIO.output(LEFT_DIR_PIN_2, GPIO.LOW)
        left_forward = 1
def leftBackward():
    global left_forward
    if left_forward != -1:
        GPIO.output(LEFT_DIR_PIN_1, GPIO.LOW)
        GPIO.output(LEFT_DIR_PIN_2, GPIO.HIGH)
        left_forward = -1
def leftStop():
    global left_forward
    if left_forward != 0:
        GPIO.output(LEFT_DIR_PIN_1, GPIO.LOW)
        GPIO.output(LEFT_DIR_PIN_1, GPIO.LOW)
def rightForward():
    global right_forward
    if right_forward != 1:
        GPIO.output(LEFT_DIR_PIN_1, GPIO.HIGH)
        GPIO.output(LEFT_DIR_PIN_2, GPIO.LOW)
        right_forward = 1
def rightBackward():
    global right_forward
    if right_forward != -1:
        GPIO.output(LEFT_DIR_PIN_1, GPIO.LOW)
        GPIO.output(LEFT_DIR_PIN_2, GPIO.HIGH)
        right_forward = -1
def rightStop():
    global right_forward
    if right_forward != 0:
        GPIO.output(RIGHT_DIR_PIN_1, GPIO.LOW)
        GPIO.output(RIGHT_DIR_PIN_1, GPIO.LOW)
def upForward():
    global up_forward
    if up_forward != 1:
        GPIO.output(UP_DIR_PIN_1, GPIO.HIGH)
        GPIO.output(UP_DIR_PIN_2, GPIO.LOW)
        up_forward = 1
def upBackward():
    global up_forward
    if up_forward != -1:
        GPIO.output(UP_DIR_PIN_1, GPIO.LOW)
        GPIO.output(UP_DIR_PIN_2, GPIO.HIGH)
        up_forward = -1
def upStop():
    global up_forward
    if up_forward != 0:
        GPIO.output(UP_DIR_PIN_1, GPIO.LOW)
        GPIO.output(UP_DIR_PIN_1, GPIO.LOW)

def applyControls(controls):
    if controls["left"] > 0.0:
        leftForward()
    elif controls["left"] < 0.0:
        leftBackward()
    else:
        leftStop()
    left.start(round(abs(controls["left"]*100)))

    if controls["right"] > 0.0:
        rightForward()
    elif controls["right"] < 0.0:
        rightBackward()
    else:
        rightStop()
    right.start(round(abs(controls["right"]*100)))

    if controls["up"] > 0.0:
        rightForward()
    elif controls["up"] < 0.0:
        rightBackward()
    else:
        rightStop()
    up.start(round(abs(controls["up"]*100)))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("169.254.38.172", 12347))

while True:
    try:
        received = sock.recvfrom(4096)[0].decode()
        exec(received)
        print(received)
    except BaseException as error:
        print("Error: "+str(error))
