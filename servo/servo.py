import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import time
import math
from time import sleep
import libcamera
from picamera2 import Picamera2
import board
import busio
import adafruit_vl53l0x

camera = Picamera2()
camera_config = camera.create_still_configuration({"size":(1296, 972)}, transform = libcamera.Transform(vflip=True, hflip=True))
camera.configure(camera_config)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(8, GPIO.OUT)
s1 = GPIO.PWM(8, 50)

GPIO.setup(7, GPIO.OUT)
s2 = GPIO.PWM(7, 50)

s1.start(6.9)
s2.start(7.6)

n = 7.6
m = 6.9

#imag::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::;
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

vl53.signal_rate_limit= 0.1
vl53.measurement_timing_budget = 20000

angle_list = []
for i in range(130):
    angle = (i / 130) * 2 * math.pi
    angle_list.append(angle)


class Motor():
    def __init__(self,Ena,In1,In2):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        GPIO.setup(self.Ena,GPIO.OUT)
        GPIO.setup(self.In1,GPIO.OUT)
        GPIO.setup(self.In2,GPIO.OUT)
        self.pwm = GPIO.PWM(Ena, 1000)
        self.pwm.start(0)
    def forward(self):
        GPIO.output(self.In1,GPIO.HIGH)
        GPIO.output(self.In2,GPIO.LOW)
        self.pwm.ChangeDutyCycle(75)
    def backward(self):
        GPIO.output(self.In1,GPIO.LOW)
        GPIO.output(self.In2,GPIO.HIGH)
        self.pwm.ChangeDutyCycle(75)
    def sl_f(self):
        GPIO.output(self.In1,GPIO.HIGH)
        GPIO.output(self.In2,GPIO.LOW)
        self.pwm.ChangeDutyCycle(50)
    def sl_b(self):
        GPIO.output(self.In1,GPIO.LOW)
        GPIO.output(self.In2,GPIO.HIGH)
        self.pwm.ChangeDutyCycle(50)
    def stop(self):
        GPIO.output(self.In1,GPIO.LOW)
        GPIO.output(self.In2,GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
motor1= Motor(24,25,1)
motor2= Motor(27,17,4)

def img(file):
    image1 = Image.open(file)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"Gen_{timestamp}.jpg"
    image1.save(filename)
    return filename
    
#Lidar ..................................................................................
def lidar():
    distance_readings = []
    for angle in angle_list:
        distance = vl53.range // 2
        distance_readings.append((distance, angle))
    return distance_readings
#Lidar ..................................................................................

previous_move = None  # Initialize the previous move

def run(val):
    global previous_move
    # for fixing grid based movement
    def adjust_orientation(target_direction):
        if previous_move == "left":
            if target_direction == "forward":
                motor1.forward()
                motor2.backward()
                sleep(0.445)
                motor1.stop()
                motor2.stop()
            elif target_direction == "right":
                motor1.backward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()
            elif target_direction == "backward":
                motor1.backward()
                motor2.forward()
                sleep(0.43)
                motor1.stop()
                motor2.stop()
            elif target_direction == "left":
                motor1.forward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()

        elif previous_move == "right":
            if target_direction == "forward":
                motor1.backward()
                motor2.forward()
                sleep(0.43)
                motor1.stop()
                motor2.stop()
            elif target_direction == "left":
                motor1.backward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()
            elif target_direction == "backward":
                motor1.forward()
                motor2.backward()
                sleep(0.445)
                motor1.stop()
                motor2.stop()
            elif target_direction == "right":
                motor1.forward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()

        elif previous_move == "backward":
            if target_direction == "forward":
                motor1.backward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()
            elif target_direction == "left":
                motor1.forward()
                motor2.backward()
                sleep(0.445)
                motor1.stop()
                motor2.stop()
            elif target_direction == "right":
                motor1.backward()
                motor2.forward()
                sleep(0.43)
                motor1.stop()
                motor2.stop()
            elif target_direction == "backward":
                motor1.forward()
                motor2.forward()
                sleep(0.86)
                motor1.stop()
                motor2.stop()

        previous_move = target_direction

    if val == "forward":
        adjust_orientation("forward")
        motor1.forward()
        motor2.forward()
        sleep(0.7)
        motor1.stop()
        motor2.stop()
    elif val == "backward":
        adjust_orientation("backward")
        motor1.backward()
        motor2.backward()
        sleep(0.7)
        motor1.stop()
        motor2.stop()
    elif val == "right":
        adjust_orientation("right")
        motor1.forward()
        motor2.backward()
        sleep(0.445)
        motor1.forward()
        motor2.forward()
        sleep(0.7)
        motor1.stop()
        motor2.stop()
    elif val == "left":
        adjust_orientation("left")
        motor1.backward()
        motor2.forward()
        sleep(0.43)
        motor1.forward()
        motor2.forward()
        sleep(0.7)
        motor1.stop()
        motor2.stop()
    elif val == "capture":
        camera.start()
        camera.capture_file('temp_image')
        camera.stop()
        filename = img('temp_image')
        return filename
    elif val == "stop":
        motor1.stop()
        motor2.stop()
    elif val == "view":
        readings= lidar()
        motor1.sl_f()
        motor2.sl_b()
        sleep(2.40)
        motor1.stop()
        motor2.stop()
        camera.start()
        for i in range (0, 4):
            sleep(0.4)
            file = camera.capture_file(f'file{i}.jpg')
            motor1.forward()
            motor2.backward()
            sleep(0.445)
            motor1.stop()
            motor2.stop()
        camera.stop()
        return readings
    else:
        print("enter right value://")
    
    if val in ["forward", "backward", "left", "right"]:
        previous_move = val

def rt(cm):
    if cm == 'left':
        motor1.backward()
        motor2.forward()
        sleep(0.58)
        motor1.stop()
        motor2.stop()
    elif cm == 'right':
        motor1.forward()
        motor2.backward()
        sleep(0.5)
        motor1.stop()
        motor2.stop()
#imag::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::;

def edit(file):
    image = Image.open(file)
    draw= ImageDraw.Draw(image)
    font = ImageFont.truetype('DejaVuSans.ttf', size = 40)
    draw.rectangle([216,171,1080,801], outline = 'red', width = 4)
    draw.text([570, 85], 'Upward', fill = 'red', font=font)
    draw.text([540,887], 'Downward', fill = 'red', font=font)
    draw.text([1140, 486], 'Right', fill = 'red', font=font)
    draw.text([65, 486], 'Left', fill = 'red', font=font)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    edited_file = f"ed_{timestamp}.jpg"
    image.save(edited_file)
    return edited_file

def serv(value):
    global n, m
    if value == "upward":
        n -= 1.1
        if n <= 1:
            n = 2.1
        s2.ChangeDutyCycle(n)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "downward":
        n += 1.1
        if n >= 10.9:
            n = 9.8
        s2.ChangeDutyCycle(n)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "left":
        m += 1.1
        if m >= 11.3:
            m = 10.2
        s1.ChangeDutyCycle(m)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "right":
        m -= 1.1
        if m <= 1.4:
            m = 2.5
        s1.ChangeDutyCycle(m)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "ul":
        n -= 1.1
        m += 1.1
        if n <= 1:
            n = 2.1
        if m >= 11.3:
            m = 10.2
        s2.ChangeDutyCycle(n)
        s1.ChangeDutyCycle(m)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "ur":
        n -= 1.1
        m -= 1.1
        if n <= 1:
            n = 2.1
        if m <= 1.4:
            m = 2.5
        s2.ChangeDutyCycle(n)
        s1.ChangeDutyCycle(m)
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == 'goal_complete':
        camera.start()
        camera.capture_file('goal.jpg')
        camera.stop
        return 'goal.jpg'
    elif value == "capture":
        camera.start()
        camera.capture_file('test.jpg')
        camera.stop()
        ed = edit('test.jpg')
        return ed
    elif value == "stop":
        s2.ChangeDutyCycle(7.6)
        s1.ChangeDutyCycle(6.9)
        sleep(1)
        s1.stop()
        s2.stop()
        GPIO.cleanup()
    else:
        print("enter right command")
