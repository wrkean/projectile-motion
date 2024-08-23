import pygame
import math
import random
import time

pygame.init()

screen = pygame.display.set_mode((720, 1470))
screen_rect = screen.get_rect()

# defy a ground to bounzee on
ground = pygame.Rect(0, 0, screen_rect.width, 200)
ground.midbottom = screen_rect.midbottom

pygame.time.Clock().tick(60)

# define ball attributes
radius = random.randint(10, 15)
colors = ["red", "green", "blue"]
current_ball = 0
ball_lasts = 9
initial_vel = random.randint(15, 20)
velo = initial_vel
GRAVITY = 0.25
angle = 70
theta = math.radians(angle)
vel_x = math.cos(theta) * initial_vel
vel_y = math.sin(theta) * initial_vel
expected_vel_x = math.cos(theta) * initial_vel
expected_vel_y = math.sin(theta) * initial_vel
ball_bounciness = 0.7
bounces = 0
thrown_time = time.time()
max_height = None

# define ball pos and calcukate distance
ball_x, ball_y = ground.x + radius, ground.y - radius
ej_x, ej_y = ground.x + radius, ground.y - radius
ball_pos = (ball_x, ball_y)
start_pos = (ball_x, ball_y)

dx = ball_pos[0] - start_pos[0]
dy = ball_pos[1] - start_pos[1]
distance = math.hypot(dy, dx)

# make a list of dictionaries to store individual ball's color and path (more dictionaries to be appended later)
color_path = [{"color": "red",
    "path": []}]
    
running = True

font = pygame.font.SysFont('Arial', 16)
min_y = 0
show_lines = True
    
def show_stats(screen, font):
    """shows the status of the current ball"""
    
    stats = {'Radius': radius,
        'Initial velocity': initial_vel,
        'Gravity (not to scale)': GRAVITY,
        'Trajectory angle (in degrees)': angle,
        'Trajectory angle (in radians)': theta,
        'Horizontal velocity': vel_x,
        'Vertical velocity': vel_y,
        'Ball bounciness': ball_bounciness,
        'Max height': max_height,
        'Ball distance':  distance,
        'Ball distance (x)': dx,
        'Ball distance (y)': dy,
        'Bounces': bounces,
        }
        
    for i, (key, value) in enumerate(stats.items()):
        stats_txt = font.render(f'{key}: {value:}', True, "white")
        if i <= 6:
            screen.blit(stats_txt, (25, i * 25))
        if i > 6:
            screen.blit(stats_txt, (1100, 25 * (i - 7)))
       
while running:
    now = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            show_lines = not show_lines
            
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, "green", ground)
    pygame.draw.circle(screen, colors[current_ball], ball_pos, radius)
    
    # calculate balls trajectory
    ball_x += vel_x
    ball_y -= vel_y
    ej_x += expected_vel_x
    ej_y -= expected_vel_y
    expected_trajectory = (ej_x, ej_y)
    ball_pos = (ball_x, ball_y)
    if vel_x > 0:
        vel_x -= 0.01
    else:
        vel_x += 0.01
    vel_y -= GRAVITY
    dx = ball_pos[0] - start_pos[0]
    dy = ball_pos[1] - start_pos[1]
    distance = math.hypot(dy, dx)
    
    # append ball path to "path" list inside current ball's dictionary that is inside of color_path
    color_path[current_ball]["path"].append(tuple(ball_pos))
    
    for pair in color_path:
        if len(color_path[current_ball]["path"]) > 1:
            pygame.draw.lines(screen, pair["color"], False, pair["path"], 1)
    
    # get the x and y value of the highest point
    highest_point = min(color_path[current_ball]["path"], key=lambda pos: pos[1])
    highest_x, highest_y = highest_point
    if show_lines:
        #pygame.draw.circle(screen, "white", (highest_x, highest_y), radius)
        pygame.draw.line(screen, "yellow", (highest_x, ground.y), (highest_x, highest_y), 1)
        pygame.draw.line(screen, "yellow", start_pos, (highest_x, highest_y) , 1)
        pygame.draw.line(screen, (130, 27, 174), start_pos, expected_trajectory, 1)
        mid_x = highest_x / 2
        mid_y = (screen_rect.height - (start_pos[1] - highest_y) + ground.height) / 2
        dhx = highest_x - start_pos[0]
        dhy = start_pos[1] - highest_y
        angle2 = math.degrees(math.atan2(dhy, dhx))
        highest_txt = font.render(f'Max Height: {screen_rect.height - min_y - ground.height:.0f}', True, "white")
        hypotenuse_txt = font.render(f'Hypotenuse: {math.hypot(highest_x - start_pos[0], start_pos[1] - highest_y):.0f}', \
        True, "white")    # sometimes inaccurate
        angle_txt = font.render(f'Angle: {angle2:.0f}°', True, "white")
        ej_txt = font.render(f'Expected trajectory (if not affected by gravity)', True, (130, 27, 174))
        screen.blit(hypotenuse_txt, (mid_x, mid_y))
        screen.blit(highest_txt, (highest_x, highest_y - 20))
        screen.blit(angle_txt, (start_pos[0] + 30, start_pos[1] - 10))
        screen.blit(ej_txt, (start_pos[0], start_pos[1] - 200))
     
    # check for edge and ground collisions and multiply velocity by balls bouzyniness
    if ball_x + radius > screen_rect.right:
        ball_x = screen_rect.right - radius
        vel_x = -vel_x
        vel_x *= ball_bounciness
        bounces += 1
    if ball_x - radius < screen_rect.left:
        ball_x = screen_rect.left + radius
        vel_x = -vel_x
        vel_x *= ball_bounciness
        bounces += 1
    if ball_y > ground.top - radius:
        ball_y = ground.top - radius
        vel_y = -vel_y
        vel_y *= ball_bounciness
        velo *= ball_bounciness
        bounces += 1
    if velo < 0.2:
        vel_y = 0
    if abs(vel_x) < 0.05:
        vel_x = 0
        
    # find minimum y value in the current ball's path
    min_y = min(color_path[current_ball]["path"], key=lambda pos: pos[1])[1]
    max_height = screen_rect.height - min_y - ground.height
    
    # after ball_lasts seconds, update variables
    if now - thrown_time >= ball_lasts:
        current_ball += 1
        if current_ball < len(colors):
            color_path.append({"color": colors[current_ball],
                "path": []})
            initial_vel = random.randint(15, 20)
            velo = initial_vel
            angle = random.randint(30, 75)
            theta = math.radians(angle)
            vel_x = math.cos(theta) * initial_vel
            vel_y = math.sin(theta) * initial_vel
            expected_vel_x = math.cos(theta) * initial_vel
            expected_vel_y = math.sin(theta) * initial_vel
            ball_x, ball_y = ground.x + radius, ground.y - radius
            ej_x, ej_y = ground.x + radius, ground.y - radius
            max_height = screen_rect.height - min_y - ground.height    # converts that minimum y value to height from ball to ground
            bounces = 0
            thrown_time = now
        else:
            max_height = screen_rect.height - min_y - ground.height
            running = False
            break
    
    show_stats(screen, font)
    
    pygame.display.flip()

# this for to keep the stats and display showing after program has ended
show_stats(screen, font)

while not running:
    pygame.display.flip()