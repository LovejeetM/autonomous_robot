import pygame
import math
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

pygame.init()

width, height = 576, 576
window = pygame.Surface((width, height))

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

gridsize = 64

# Initial position of the blue block
object_x = 0
object_y = 0

direction = 'forward'

readings = []

captured_blocks = set()

def polar(radius, radian):
    x = radius * math.cos(radian)
    y = radius * math.sin(radian)
    return x, y

def draw(surface, readings, width, height, offset_x, offset_y):
    global gridsize, object_x, object_y
    surface.fill(BLACK)
    font = pygame.font.SysFont('Arial', 20)
    
    block_number = 1
    
    for m in range(-height//2, height//2, 64):
        for n in range(-width//2, width//2, 64):
            grid_x = n + width//2 + offset_x % gridsize
            grid_y = m + height//2 + offset_y % gridsize
            pygame.draw.line(surface, WHITE, (grid_x, 0), (grid_x, height))
            pygame.draw.line(surface, WHITE, (0, grid_y), (width, grid_y))
            
            # Adding block numbers row-wise
            number_text = font.render(str(block_number), True, WHITE)
            surface.blit(number_text, (grid_x + 5 - offset_x % gridsize, grid_y + 5 - offset_y % gridsize))
            block_number += 1

    red_blocks = set()
    for radius, radian in readings:
        x, y = polar(radius, radian)
        grid_x = int((width / 2 + x + offset_x) // gridsize) * gridsize
        grid_y = int((height / 2 - y + offset_y) // gridsize) * gridsize
        if (grid_x, grid_y) in captured_blocks:
            color = GREEN
        else:
            color = RED
            red_blocks.add((grid_x, grid_y))
        pygame.draw.rect(surface, RED, (grid_x - offset_x % gridsize, grid_y - offset_y % gridsize, gridsize, gridsize))
    
    pygame.draw.rect(surface, BLUE, (width//2 - gridsize//2, height//2 - gridsize//2, gridsize, gridsize))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Direction-facing
    triangle_size = gridsize // 3
    center_x = width // 2
    center_y = height // 2
    
    if direction == 'forward':
        triangle_points = [
            (center_x, center_y - gridsize//2 + 5),
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x + triangle_size//2, center_y - triangle_size//2)
        ]
    elif direction == 'backward':
        triangle_points = [
            (center_x, center_y + gridsize//2 - 5),
            (center_x - triangle_size//2, center_y + triangle_size//2),
            (center_x + triangle_size//2, center_y + triangle_size//2)
        ]
    elif direction == 'left':
        triangle_points = [
            (center_x - gridsize//2 + 5, center_y),
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x - triangle_size//2, center_y + triangle_size//2)
        ]
    elif direction == 'right':
        triangle_points = [
            (center_x + gridsize//2 - 5, center_y),
            (center_x + triangle_size//2, center_y - triangle_size//2),
            (center_x + triangle_size//2, center_y + triangle_size//2)
        ]
    
    pygame.draw.polygon(surface, WHITE, triangle_points)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    return red_blocks

def save_image(surface, filename):
    return pygame.image.save(surface, filename)

#Rotation__________________________
def rotate_cube(new_direction):
    global direction
    direction = new_direction
    print(f"Blue cube is now facing {direction}")
#Rotation__________________________

#Rotate-Seperately------------------------------------------------
def rotate_and_save_image(rotation_direction):
    global object_x, object_y, width, height, window, readings
    
    # Rotate the cube
    rotate_cube(rotation_direction)
    
    # Redraw the window with the new direction
    red_blocks = draw(window, readings, width, height, object_x, object_y)
    
    # Save the updated image
    save_image(window, 'output-rotation.jpg')
    return 'output-rotation.jpg'
#Rotate-Seperately------------------------------------------------

def get_visible_grid_matrix(red_blocks):
    global width, height, gridsize
    matrix = [[1 for _ in range(9)] for _ in range(9)]
    
    for x in range(-4, 5):
        for y in range(-4, 5):
            grid_x = (width // 2 + x * gridsize) // gridsize * gridsize
            grid_y = (height // 2 + y * gridsize) // gridsize * gridsize
            
            if (grid_x, grid_y) in red_blocks:
                matrix[y + 4][x + 4] = 0
    
    return matrix

def move(direction, red_blocks, filename):
    global gridsize, object_x, object_y, width, height, window, readings

#======================================================================
    if direction in ['right', 'left', 'backward', 'forward']:
        rotate_cube(direction)
#======================================================================
    
    new_x, new_y = object_x, object_y
    if direction == 'right':
        new_x -= gridsize
    elif direction == 'left':
        new_x += gridsize
    elif direction == 'backward':
        new_y -= gridsize
    elif direction == 'forward':
        new_y += gridsize
    
    grid_x = (width // 2 - new_x) // gridsize * gridsize
    grid_y = (height // 2 - new_y) // gridsize * gridsize
    
    if (grid_x, grid_y) not in red_blocks:
        object_x, object_y = new_x, new_y
    else:
        print("Move blocked by red block.")
    
    red_blocks = draw(window, readings, width, height, object_x, object_y)
    save_image(window, filename)
    
    grid_matrix = get_visible_grid_matrix(red_blocks)
    print("output saved")
    return grid_matrix

#Green-Blocks=======================================================================
def capture_and_turn_green():
    global direction, object_x, object_y, captured_blocks, width, height, gridsize
    
    offset_x = 0
    offset_y = 0
    
    if direction == 'right':
        neighbor_x = (width // 2 - object_x) // gridsize * gridsize - gridsize
        neighbor_y = (height // 2 - object_y) // gridsize * gridsize
    elif direction == 'left':
        neighbor_x = (width // 2 - object_x) // gridsize * gridsize + gridsize
        neighbor_y = (height // 2 - object_y) // gridsize * gridsize
    elif direction == 'backward':
        neighbor_x = (width // 2 - object_x) // gridsize * gridsize
        neighbor_y = (height // 2 - object_y) // gridsize * gridsize - gridsize
    elif direction == 'forward':
        neighbor_x = (width // 2 - object_x) // gridsize * gridsize
        neighbor_y = (height // 2 - object_y) // gridsize * gridsize + gridsize
    
    if (neighbor_x, neighbor_y) in readings:
        captured_blocks.add((neighbor_x, neighbor_y))
        print(f"Captured block at ({neighbor_x}, {neighbor_y}) and turned it green.")
    
    red_blocks = draw(window, readings, width, height, object_x, object_y)
    save_image(window, 'output.jpg')
#Green-Blocks=======================================================================

#for adding new readings===========================================================================
def add_points(new_points):
    global readings, object_x, object_y
    for radius, radian in new_points:
        x, y = polar(radius, radian)
        adjusted_x = x
        adjusted_y = y
        readings.append((adjusted_x, adjusted_y))
#for adding new readings===========================================================================

red_blocks = draw(window, readings, width, height, object_x, object_y)
save_image(window, 'output.jpg')

grid_matrix = get_visible_grid_matrix(red_blocks)

# Path finding code ..............................................................................

def get_goal_coordinates(goal_number):
    row = (goal_number - 1) // 9
    col = (goal_number - 1) % 9
    return row, col

def find_path_and_instructions(matrix, goal_number):
    start = (4, 4)  # Center of 9x9 matrix
    goal = get_goal_coordinates(goal_number)

    grid = Grid(matrix=matrix)
    start_node = grid.node(start[0], start[1])
    end_node = grid.node(goal[0], goal[1])

    # Set walkable attribute based on matrix values
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            grid.node(row, col).walkable = matrix[row][col] == 1

    finder = AStarFinder()
    path, _ = finder.find_path(start_node, end_node, grid)

    directions = []
    for i in range(1, len(path)):
        current = path[i-1]
        next = path[i]
        if next.x > current.x:
            directions.append("backward")
        elif next.x < current.x:
            directions.append("forward")
        elif next.y > current.y:
            directions.append("right")
        elif next.y < current.y:
            directions.append("left")
    return directions

# Path finding code ..............................................................................


#for testing loop
'''while True:
    inp = input("Enter 'stop' to end or 'add' to add readings: ")
    if inp == 'stop':
        break
    elif inp == 'add':
        new_points_input = input("Enter new readings as [(radius1, angle1), (radius2, angle2), ...]: ")
        new_points = eval(new_points_input)
        add_points(new_points)
        red_blocks = draw(window, readings, width, height, object_x, object_y)
        save_image(window, 'output.jpg')
        grid_matrix = get_visible_grid_matrix(red_blocks)
        for row in grid_matrix:
            print(row)
    else:
        while True:
            goal_number = int(input('Enter your move goal number, 1-81 or 0 to end: '))
            if goal_number == 0:
                break
            else:
                instructions = find_path_and_instructions(grid_matrix, goal_number)
                print("Instructions to reach the goal:")
                for instruction in instructions:
                    print(instruction)
                for instruction in instructions:
                    grid_matrix = move(instruction, red_blocks, f'o_{instruction}.jpg')
'''
