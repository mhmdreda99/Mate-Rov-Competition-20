import socket
import pygame
import time

ADDRESS = ("169.254.38.172", 12347)

RESOLUTION = (640, 480)

pygame.init()

screen = pygame.display.set_mode(RESOLUTION)
font = pygame.font.SysFont("ROV_control_font", 25)

joymap = {1:("left", True),
          4:("right", True),
          2:("up", False),
          5:("up", True)} # Maps joystick axis id to settings and motor out: {axis_id:(control, inverted)}

instant_control = False # Whether or not controls will instantly reflect inputs. If False, controls will accumulate on the controls
control_buffer = {"left":0.0, "right":0.0, "up":0.0} # Control accumulation buffer
control_factor = 0.02 # Factor to control accumulation speed if not using instant control

max_motor_percent = 2.0 # Maximum percentage of all of the motors (0.0 being 0%, and 1.0 being 100%)

motor_percent_map = {"left":1.0, # Amount of energy (in motor percent) each control uses
                     "right":1.0, # Increase these according to the number of motors and the power usage percentage of the motor (if 4 motors of the same power are used, change to 4.0)
                     "up":2.0} # If any of these are higher than max_motor_percent, weird maths and unexpected results may occur

def translateRange(value, old_min, old_max, new_min, new_max):
    old_range = (old_max-old_min)
    if old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)  
        new_value = (((value-old_min)*new_range)/old_range)+new_min
    return new_value

def connectJoystick():
    global joystick

    pygame.joystick.quit()
    pygame.joystick.init() # Refresh joystick list

    while pygame.joystick.get_count() == 0:
        print("No joysticks detected. Retrying...")
        time.sleep(1.0)
        pygame.joystick.quit()
        pygame.joystick.init() # Refresh joystick list
    
    if pygame.joystick.get_count() < 1:
        print("Multiple joysticks found.")
        possible_joysticks = []
        for joystick_id in range(pygame.joystick.get_count()):
            possible_joystick = pygame.joystick.Joystick(joystick_id)
            print("Joystick %i: '%s'" % (joystick_id, possible_joystick.get_name()))
        id_entered = False
        while not id_entered:
            joystick_id = input("Enter the id of the joystick you want to use: ")
            try:
                joystick = possible_joysticks[int(joystick_id)]
                id_entered = True
            except:
                print("Invalid joystick id. Id must be in the range %i to %i." % (0, pygame.joystick.get_count()-1))
        print("Joystick chosen.")
    else:
        print("Joystick found.")
        joystick = pygame.joystick.Joystick(0)
    
    joystick.init()

    print("Initialized Joystick '%s' with id %i." % (joystick.get_name(), joystick.get_id()))

def debugJoystick():
    pygame.event.pump()
    
    try:
        print("Data of joystick '%s':\n    Joystick id: %i" % (joystick.get_name(), joystick.get_id()))
        for axis in range(joystick.get_numaxes()):
            print("    Axis %i: %f" % (axis, joystick.get_axis(axis)))
    except BaseException as error:
        print("Error while debugging joystick: %s" % error)

def connectRaspi():
    global sock

    try:
        sock.close()
        del sock
    except:
        pass
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendControls(controls):
    try:
        sock.sendto(("applyControls(%s);" % str(controls)).encode(), ADDRESS)
    except BaseException as error:
        print("Error while sending controls to Pi: %s. Attempting to reconnect..." % error)
        connectRaspi(first=False) # Don't re-send inital program on reconnect
        time.sleep(0.5) # Cooldown to prevent excessive reconnects
        sendControls(controls) # Recursively attempt to send data until it succeeds

def getControls():
    output = {"up":0.0, "left":0.0, "right":0.0}
    
    try:
        for axis in joymap.keys(): # Get and adjust value
            value = joystick.get_axis(axis)
            control, inverted = joymap[axis]
            if inverted:
                value *= -1
            if not instant_control:
                value *= control_factor
                control_buffer[control] += value
                if control_buffer[control] > 1.0:
                    control_buffer[control] = 1.0
                if control_buffer[control] < -1.0:
                    control_buffer[control] = -1.0
                value = control_buffer[control]
            output[control] += value
        total_percent = 0
        for control in output.keys(): # Verify and re-adjust values
            if output[control] > 1.0:
                output[control] = 1.0
            if output[control] < -1.0:
                output[control] = -1.0
            total_percent += abs(output[control]*motor_percent_map[control])
        if total_percent > max_motor_percent: # If we go over the maximum, decrease percentages on motors until it isn't over the maximum
            amount_over = total_percent-max_motor_percent
            in_use = 0 # Number of controls currently in use
            for control in output.keys():
                if abs(output[control]) > 0.0:
                    in_use += 1
            subtract_amount = amount_over/in_use # Divide the amount we've gone over by the number of controls in use
            for control in output.keys():
                if output[control] < 0.0:
                    output[control] += subtract_amount # Add instead of subtract if value is negative
                    if output[control] > 0.0:
                        output[control] = 0.0 # If this was negative, don't reverse it
                else:
                    output[control] -= subtract_amount
                    if output[control] < 0.0:
                        output[control] = 0.0 # If this was positive, don't reverse it
            
            
    except ConnectionRefusedError as error:
        print("Error while getting controls: %s" % error)
    return output.copy()

connectJoystick()
connectRaspi()

rect_width = 70
extent = int(screen.get_height()/2) # Extent from the middle that the bars can go (negative and positive)
max_height = screen.get_height()-extent # The height of the middle of the joystick visualization bars. Set to screen.get_height()-extent to align with the bottom of the window

running = True

clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    if not running: # Quit immediately after given the signal
        break
    output = getControls()
    i = 0
    screen.fill((0, 0, 0))
    for control in ["left", "right", "up"]:
        percent = str(round(output[control]*100, 2))+"%"
        percent_text = font.render(percent, True, (255, 255, 255))
        top_y = int(translateRange(output[control], 1.0, -1.0, max_height-extent, max_height+extent))
        red = int(translateRange(abs(output[control]), 0.0, 1.0, 0, 255))
        pygame.draw.rect(screen, (red, 255-red, 0), pygame.Rect(i*rect_width, top_y, rect_width, max_height-top_y))
        #screen.blit(percent_text, (int(i*rect_width), int((percent_text.get_height()/2)+middle)))
        screen.blit(percent_text, (int(i*rect_width), int(max_height+percent_text.get_height()/2)))
        i += 1
    sendControls(output)
    pygame.display.flip()
    clock.tick(120)
