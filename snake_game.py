import pygame
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Game Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 1
SNAKE_SPEED = 10
WHITE = (1, 1, 1)
GREEN = (0, 1, 0)
RED = (1, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0,0,1)
GRAVITY = 0.05
JUMP_FORCE = 0.5
FRICTION = 0.9
NUM_OBSTACLES = 5

# Initialize GLUT
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

# Initialize Pygame window and OpenGL
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("3D Snake Game")

# Initialize OpenGL settings
def init():
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, 0, -20)

init()

# --- Helper Functions ---
def draw_cube(position, color):
    vertices = [
        [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5],
        [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5],
        [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
    ]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glColor3fv(color)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()

def generate_random_position():
    return (random.randint(-5, 5) * GRID_SIZE,
            random.randint(-5, 5) * GRID_SIZE,
            random.randint(-5, 5) * GRID_SIZE)

# --- Game Classes ---
class Snake:
    def __init__(self):
        self.body = [(0, 0, 0)]
        self.direction = (GRID_SIZE, 0, 0)
        self.velocity = [0, 0, 0]  # x, y, z velocities
        self.is_jumping = False
        self.score = 0

    def move(self):
        # Apply gravity
        self.velocity[1] -= GRAVITY

        # Apply friction (only when on the ground)
        if not self.is_jumping:
            self.velocity[0] *= FRICTION
            self.velocity[2] *= FRICTION

        # Update position based on direction and velocity
        new_x = self.body[0][0] + self.direction[0] + self.velocity[0]
        new_y = self.body[0][1] + self.direction[1] + self.velocity[1]
        new_z = self.body[0][2] + self.direction[2] + self.velocity[2]

        self.body.insert(0, (new_x, new_y, new_z))
        self.body.pop()

        # Collision detection with ground (basic)
        if self.body[0][1] <= -5 * GRID_SIZE: #Basic ground detection
            self.body[0] = (self.body[0][0], -5 * GRID_SIZE, self.body[0][2])
            self.velocity[1] = 0
            self.is_jumping = False
    def jump(self):
        if not self.is_jumping:
            self.velocity[1] = JUMP_FORCE
            self.is_jumping = True

    def grow(self):
        self.body.append(self.body[-1])
        self.score += 10

    def check_collision(self, obstacles):
        if self.body[0] in self.body[1:]:  # Self-collision
            return True
        for obstacle in obstacles:  # Obstacle collision
            if (int(self.body[0][0]), int(self.body[0][1]), int(self.body[0][2])) == (int(obstacle.position[0]), int(obstacle.position[1]), int(obstacle.position[2])):
               return True
        return False

    def draw(self):
        for segment in self.body:
            draw_cube(segment, GREEN)

class Food:
    def __init__(self):
        self.position = generate_random_position()
        self.position = (self.position[0], -5*GRID_SIZE + GRID_SIZE , self.position[2]) #Food is always on ground level

    def draw(self):
        draw_cube(self.position, RED)

class Obstacle:
    def __init__(self):
       self.position = generate_random_position()
       self.position = (self.position[0], -5*GRID_SIZE + GRID_SIZE, self.position[2])

    def draw(self):
        draw_cube(self.position, BLUE)

# --- Game Initialization ---
snake = Snake()
food = Food()
obstacles = [Obstacle() for _ in range(NUM_OBSTACLES)]
running = True
clock = pygame.time.Clock()

# --- Main Game Loop ---
while running:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -20)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                snake.direction = (-GRID_SIZE, 0, 0)
            elif event.key == pygame.K_RIGHT:
                snake.direction = (GRID_SIZE, 0, 0)
            elif event.key == pygame.K_UP:
                snake.direction = (0, 0, GRID_SIZE) # move forward
            elif event.key == pygame.K_DOWN:
                snake.direction = (0, 0, -GRID_SIZE) # move backward
            elif event.key == pygame.K_SPACE:
                snake.jump()

    # --- Game Logic ---
    snake.move()

    # Food Collision
    if (int(snake.body[0][0]), int(snake.body[0][1]), int(snake.body[0][2])) == (int(food.position[0]), int(food.position[1]), int(food.position[2])): #compare as integers
        snake.grow()
        food = Food() # Respawn food

    # Collision Detection
    if snake.check_collision(obstacles):
        running = False

    # --- Drawing ---
    snake.draw()
    food.draw()
    for obstacle in obstacles:
        obstacle.draw()

    # --- Refresh Display ---
    pygame.display.flip()
    clock.tick(SNAKE_SPEED)

pygame.quit()