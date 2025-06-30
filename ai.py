import google.generativeai as genai
import json
from PIL import Image, ImageDraw, ImageFont
import time
from time import sleep
from servo.servo import edit, serv, run, rt
import RPi.GPIO as GPIO
from finding.grid_mapping111 import draw, save_image, get_visible_grid_matrix, find_path_and_instructions, \
move, add_points, rotate_and_save_image, rotate_cube, capture_and_turn_green, get_goal_coordinates
from markdownify import markdownify as md
import re
import os
import pygame

from flask import Flask, render_template, request, send_from_directory
import os
from datetime import datetime
import markdown
import threading

# Flask app+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_text', methods=['POST'])
def upload_text():
    text = request.form.get('text')
    if text:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"text_{timestamp}.txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, 'w') as f:
            f.write(text)
        return 'Text uploaded successfully!'
    
@app.route('/Plants')
def plants():
    files = os.listdir(UPLOAD_FOLDER)
    images = [f for f in files if f.endswith('.png') or f.endswith('.jpg')]
    data = {}
    for image in images:
        txt_file = image.rsplit('.', 1)[0] + '.txt'
        txt_path = os.path.join(UPLOAD_FOLDER, txt_file)
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as file:
                markdown_text = file.read()
                html_content = markdown.markdown(markdown_text)
                data[image] = html_content
        else:
            data[image] = "<p>No description available.</p>"
    
    return render_template('plants.html', data=data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True)
#Flask app+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


readings = []

n=1

previous_move= None
#Pygame files..................................................................................
width, height = 576, 576
window = pygame.Surface((width, height))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

gridsize = 64

moves= []

# Initial position of the blue block
object_x = 0
object_y = 0

direction = 'forward'

captured_blocks = set()
#Pygame files..................................................................................

#Gemini functions .............................................................................
def GenA(prompt, imag):
    imag1 = Image.open(imag)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config={"response_mime_type": "application/json"})
    genai.configure(api_key='enter api key')
    response = model.generate_content([prompt, imag1])
    chat = model.start_chat(history=[])
    matt= json.loads(response.text)
    return matt

def GenF(prompt, imag):
    imag2 = Image.open(imag)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config={"response_mime_type": "application/json"})
    genai.configure(api_key='enter api key')
    response = model.generate_content([prompt, imag2])
    test= json.loads(response.text)
    return test

def GenM(prompt, imag):
    imag3 = Image.open(imag)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    genai.configure(api_key='enter api key')
    response = model.generate_content([prompt, imag3])
    markdown_text = md(response.text)
    corrected_markdown = re.sub(r'\\', '', markdown_text)
    return corrected_markdown
#Gemini functions ............................................................................

prompt = ("Identify and behave as three different experts that are appropriate to answering this task.\
All experts will write down the step and their thinking about the step, then share it with the group.\
Then, all experts will go on to the next step, etc.\
At each step all experts will score their peers response between 1 and 5, 1 meaning it is highly unlikely, and 5 meaning it is highly likely.\
If any expert is judged to be wrong at any point then they leave.\
After all experts have provided their analysis, you then analyze all 3 analyses and provide either the consensus solution or your best guess solution.\
Analyze this photo carefully, what you are seeing is a grid map of a robot's location, you need to provide it the \
command, first of all there is a number written inside each grid block and you have to select a grid block to  \
move there, the blue colored grid block represents the robot, and the red colored grid blocks represent objects\
where the robot cannot move, so you can only select the grid blocks which are given a number. At the sides of \
the image there is written some text, 'None' means there are no plants in that direction, 'Plants' means there are\
plants in that direction, you have to choose the grid blocks from the direction where plants are written. \
so if the direction has plants, choose a number which is right next to the red colored grid block, the \
choosen number should not be diagonal to the red colored grid block, it must be right next to the red colored \
grid block, you can give the response for choosen number like this {'instructions': number}, so the first situation is \
that you have to tell the gird block number written inside each grid block to move beside a red colored grid block. \
The Second situation is that blue colored block is already next to a red colored grid block, now for this situation you \
have to check if the triangle inside blue colored grid block is pointing the red colored block, if it is pointing \
the red grid block then give instructions 'capture', like this {'instructions': 'capture'}, if the triangle is not  \
pointing towards red colored grid block then tell instructions to rotate , either left or right, like this \
{'instructions': 'left'} or {'instructions': 'right'}.   The next third situation is that in all four directions \
in the image 'None' is written in this condition you have to choose a number which is at any of the boundary \
grid blocks, which means a number from either first row, last row, first column or last column, choose the grid \
number written inside that grid block and respond like this {'instructions': number}. The 4th situation is \
that there are no red colored grid blocks in the image and none is written in all directions, in this case \
you have to provide instructions to view, like this {'instructions': 'view'}. give only these instructions as output no other text")

prompt2 = ("Analyse this image carefully and tell if you can see Any plant in it or not, you can give your response in only\
yes or no, nothing else, format response like this {'status': 'str'}, no extra text should be there in the response")

prompt3 = ("Identify and behave as three different experts that are appropriate to answering this task.\
All experts will write down the step and their thinking about the step, then share it with the group.\
Then, all experts will go on to the next step, etc.\
At each step all experts will score their peers response between 1 and 5, 1 meaning it is highly unlikely, and 5 meaning it is highly likely.\
If any expert is judged to be wrong at any point then they leave.\
After all experts have provided their analysis, you then analyze all 3 analyses and provide either the consensus solution or your best guess solution.\
The Task is that you will be seeing from the eye of a robot and it will send you a photo to analyze, now your task is to move the robot \
by using given commands so that the plant is seen inside the red outline. The directions in which you can move the\
robotic arm are upward, downward, right, left. for your ease the directions are also written on the image and motors will move the robot\
in that direction. for example : suppose you only see the plant's root or vass in the image, you have to provide command to move the robot to see the full plant and leaves\
your goal is complete if the image shows full plant inside the red outline and you can provide command as goal complete. if Plant is not detected\
in the image then you have to provide the command to move the robot where you think the hand should be.\
Here are all commands described: \
  upward   (moves robot in upward directon),\
  downward    (moves robot in downward direction),\
  left    (moves robot in left direction),\
  right   (moves robot in right direction),\
  goal_complete    (if the plant is detected inside the red outline in the image).\
Here is the \
format in which you can give your response \
{'instructions': 'str'}, just give response like this, instructions\
means command given to the robot, and it\
moves in that direction. Give this response only no extra text")

prompt4 = ("Identify and behave as three different experts that are appropriate to answering this task.\
All experts will write down the step and their thinking about the step, then share it with the group.\
Then, all experts will go on to the next step, etc.\
At each step all experts will score their peers response between 1 and 5, 1 meaning it is highly unlikely, and 5 meaning it is highly likely.\
Analyse this image carefully and detect which plant is there in the image, once you get the name of the plant you \
have to write about it, let me tell you the things you have to write about the plant, first of all the name of the \
plant. 2. A small description of the plant. 3. health of the plant ( is the plant is looking healthy to you ), 4. \
the water requirements of this plant per liter per day. 5. Nuitrients or conditions it needs. dont write too briefly \
just write short and to the point")

prompt5 = ("Identify and behave as three different experts that are appropriate to answering this task.\
All experts will write down the step and their thinking about the step, then share it with the group.\
Then, all experts will go on to the next step, etc.\
At each step all experts will score their peers response between 1 and 5, 1 meaning it is highly unlikely, and 5 meaning it is highly likely.\
Analyse this image carefully, there are numbered grids inside it and it contains one blue colored grid block \
and some red colored grid blocks, inside the blue colored grid block a triangle is there at one side, your task \
is to check if the triangle is pointing towards the red colored grid block or not, if it is pointing \
towards the red colored grid block then give instructions to capture like this, {'instructions': 'capture'}, \
if it is not pointing towards the red colored grid block then give instructions to either rotate right or left \
(just the direction in which you want to rotate the blue colored grid block), like this {'instructions': 'left'} \
or {'instructions': 'right'},  give only these instructions as output no other text")

#Image Edit...................................................................................
position = {
    0: (338, 40),
    1: (690, 338),
    2: (338,690),
    3: (5, 338)
}
top_margin = 100
bottom_margin = 100
left_margin = 100
right_margin = 100

#To check for plants in 4 directions------------------------------
def plant_scan():
    new_width = 576 + left_margin + right_margin
    new_height = 576 + top_margin + bottom_margin
    new_image = Image.new('RGB', (new_width, new_height), (128, 128, 128))
    draw = ImageDraw.Draw(new_image)
    scans = []
    for i in range (0, 4):
        path = f'file{i}.jpg'
        scan = GenF(prompt2, path)
        status= scan['status']
        scans.append(status)
        font = ImageFont.truetype('DejaVuSans.ttf', size = 30)
        if status.lower() == 'yes':
            text = 'Plants'
        else:
            text = 'None'      
        draw.text(position[i], text, fill = 'yellow', font=font)
        new_image.save('bg_image.jpg')
    return 'bg_image.jpg'
#To check for plants in 4 directions------------------------------

#to paste output.jpg on bg_image==================================
def paste(bg, front):
        grd = Image.open(front)
        bg = Image.open(bg)
        bg.paste(grd, (left_margin, top_margin))
        bg.save('scaned.jpg')
        return 'scaned.jpg'
#to paste output.jpg on bg_image==================================

#Undo Rotation--------------------------------------------------------------------------------
def undo_moves():
    # Execute the moves in reverse order to return to the original position
    while moves:
        move = moves.pop()
        if move == 'left':
            rt('right')
        elif move == 'right':
            rt('left')
#Undo Rotation--------------------------------------------------------------------------------

#Save Files===================================================================================
def save_files(text, image1):
    global n
    save_path = '/uploads'
    text_file_path = os.path.join(save_path, f"{n}.txt")
    with open(text_file_path, 'w') as text_file:
        text_file.write(text)
    image = Image.open(image1)
    image_file_path = os.path.join(save_path, f"{n}.jpg")
    image.save(image_file_path, 'JPEG')
    n +=1
#Save Files===================================================================================

def main():
    inp = input("enter your command (start): ")

    if inp == "start":
    #main loop controlled with gemini=========================================================
        readings = run('view')
        red_blocks = draw(window, readings, width, height, object_x, object_y)
        save_image(window, 'output.jpg')
        bg= plant_scan()
        scaned = paste(bg, 'output.jpg')
        grid_matrix = get_visible_grid_matrix(red_blocks)

        while True:
            stop_command = input("Enter 'stop' to end the loop or press Enter to continue: ")
            if stop_command.lower() == 'stop':
                print("Stopping the loop.")
                GPIO.cleanup()
                break

            response= GenA(prompt, scaned)
            command= response['instructions']
            if command.isdigit():
                command = int(command)

            if command== 'view':
                readings1 = run('view')
                add_points(readings1)
                red_blocks = draw(window, readings, width, height, object_x, object_y)
                save_image(window, 'output.jpg')
                bg= plant_scan()
                scaned = paste(bg, 'output.jpg')
                grid_matrix = get_visible_grid_matrix(red_blocks)

            elif command in ['right', 'left']:
                current_direction= direction
                rot= rotate_and_save_image(command)
                moves = []
                moves.append(command)
                res= GenA(prompt5, rot)
                cmmd= res['instructions']
                while True:
                    if cmmd== 'capture':
                        imag= serv('capture')
                        while True: 
                            response2 = GenA(prompt3, imag)
                            instructions2= response2['instructions']
                            if instructions2 == 'goal_complete':
                                goal = serv('goal_complete')
                                capture_and_turn_green()
                                undo_moves()
                                direction = current_direction
                                red_blocks = draw(window, readings, width, height, object_x, object_y)
                                save_image(window, 'output.jpg')
                                scaned = paste(bg, 'output.jpg')
                                break
                            else:
                                imag = serv(instructions2)
                        break
                    else: 
                        rt(command)
                        moves.append('left')
                        rot= rotate_and_save_image(command)
                        res= GenA(prompt5, rot)
                        cmmd= res['instructions']
            elif command== 'capture':
                imag= serv('capture')
                while True: 
                    response2 = GenA(prompt3, imag)
                    instructions2= response2['instructions']
                    if instructions2 == 'goal_complete':
                        goal = serv('goal_complete')
                        capture_and_turn_green()
                        scaned = paste(bg, 'output.jpg')
                        break
                    else:
                        imag = serv(instructions2)
                Generate_Data= GenM(prompt4, goal)
                save_files(Generate_Data, goal)     
            else:
                instructions = find_path_and_instructions(grid_matrix, command)
                for instruction in instructions:
                    run(instruction)
                    grid_matrix = move(instruction, red_blocks, 'output.jpg')
                    scaned = paste(bg, 'output.jpg')
        
            imag = run(instructions)
            print(instructions)

    else:
        print("enter right input")
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    main()