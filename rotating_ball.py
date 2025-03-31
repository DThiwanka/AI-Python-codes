import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Circle with Physics Ball")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Circle properties
CIRCLE_RADIUS = 150
CIRCLE_CENTER_X = WIDTH // 2
CIRCLE_CENTER_Y = HEIGHT // 2
ROTATION_SPEED = 0.01  # Radians per frame

# Ball properties
BALL_RADIUS = 20
#Ball Starts inside the circle
ball_x = CIRCLE_CENTER_X + CIRCLE_RADIUS /2  # Initial position inside the circle
ball_y = CIRCLE_CENTER_Y
ball_speed_x = 2
ball_speed_y = 2
GRAVITY = 0.1
FRICTION = 0.99 # Damping
ELASTICITY = 0.8 #Bounciness
# Initialize variables
angle = 0  # Current rotation angle of the circle
running = True
clock = pygame.time.Clock()

def handle_collision(ball_x, ball_y, circle_x, circle_y, circle_radius, ball_radius,ball_speed_x,ball_speed_y, circle_angle):
    # Calculate the distance between the ball and the circle's center
    distance = math.sqrt((ball_x - circle_x)**2 + (ball_y - circle_y)**2)

    # Check for collision *inside* the circle
    if distance + ball_radius >= circle_radius:

        # Calculate the normal vector (direction from the circle center to the ball)
        normal_x = (ball_x - circle_x) / distance
        normal_y = (ball_y - circle_y) / distance

        # Calculate the dot product of the velocity vector and the normal vector
        dot_product = ball_speed_x * normal_x + ball_speed_y * normal_y

        # Calculate the reflection vector (bounce)
        reflection_x = ball_speed_x - 2 * dot_product * normal_x
        reflection_y = ball_speed_y - 2 * dot_product * normal_y

        # Apply circle's rotational velocity to the collision
        tangent_x = -normal_y  # Tangent is perpendicular to the normal
        tangent_y = normal_x

        circle_speed = ROTATION_SPEED * CIRCLE_RADIUS  # Linear speed at the edge
        reflection_x += tangent_x * circle_speed
        reflection_y += tangent_y * circle_speed



        # Update the ball's velocity, applying elasticity
        return reflection_x * ELASTICITY, reflection_y * ELASTICITY
    else:
        return ball_speed_x, ball_speed_y

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic
    angle += ROTATION_SPEED

    #Apply gravity
    ball_speed_y += GRAVITY

    #Apply air friction
    ball_speed_x *= FRICTION
    ball_speed_y *= FRICTION

    #check for collision against the sides of the screen
    if ball_x + BALL_RADIUS > WIDTH or ball_x - BALL_RADIUS < 0:
        ball_speed_x *= -1 # Reverse x velocity
    if ball_y + BALL_RADIUS > HEIGHT or ball_y - BALL_RADIUS < 0:
        ball_speed_y *= -1  #Reverse y velocity

    #check for collision with circle

    ball_speed_x, ball_speed_y = handle_collision(ball_x, ball_y, CIRCLE_CENTER_X, CIRCLE_CENTER_Y, CIRCLE_RADIUS, BALL_RADIUS, ball_speed_x, ball_speed_y, angle)
    # Add velocity components to position
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    # Drawing
    screen.fill(BLACK)

    # Draw the rotating circle

    rotated_surface = pygame.transform.rotate(pygame.Surface((CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2), pygame.SRCALPHA), math.degrees(angle))
    rotated_rect = rotated_surface.get_rect(center=(CIRCLE_CENTER_X, CIRCLE_CENTER_Y))
    pygame.draw.circle(screen, WHITE, (CIRCLE_CENTER_X, CIRCLE_CENTER_Y), CIRCLE_RADIUS, 2)  # Draw the actual circle
    #screen.blit(rotated_surface, rotated_rect.topleft)

    # Draw the ball
    pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)


    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()