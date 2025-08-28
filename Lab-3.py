import pygame
import numpy as np
import math

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Cube Transformations")

# Font for controls
font = pygame.font.SysFont("Arial", 18)

# Cube vertices in homogeneous coordinates
cube_vertices = np.array([
    [-1, -1, -1, 1],
    [ 1, -1, -1, 1],
    [ 1,  1, -1, 1],
    [-1,  1, -1, 1],
    [-1, -1,  1, 1],
    [ 1, -1,  1, 1],
    [ 1,  1,  1, 1],
    [-1,  1,  1, 1]
], dtype=float)

# Cube edges
edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]

# Transformation matrices
def translation(tx, ty, tz):
    return np.array([
        [1,0,0,tx],
        [0,1,0,ty],
        [0,0,1,tz],
        [0,0,0,1]
    ])

def scaling(sx, sy, sz):
    return np.array([
        [sx,0,0,0],
        [0,sy,0,0],
        [0,0,sz,0],
        [0,0,0,1]
    ])

def rotation_x(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [1,0,0,0],
        [0,c,-s,0],
        [0,s,c,0],
        [0,0,0,1]
    ])

def rotation_y(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c,0,s,0],
        [0,1,0,0],
        [-s,0,c,0],
        [0,0,0,1]
    ])

def rotation_z(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c,-s,0,0],
        [s,c,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ])

# Perspective projection
def project(point):
    factor = 200 / (point[2] + 5)
    x = int(WIDTH/2 + point[0]*factor)
    y = int(HEIGHT/2 - point[1]*factor)
    return (x, y)

# Main loop
vertices = cube_vertices.copy()
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0,0,0))

    # Draw instructions
    controls = [
        "Controls:",
        "Arrow Keys: Rotate cube",
        "W/S: Move up/down",
        "A/D: Move left/right",
        "Q/E: Move forward/backward",
        "Z/X: Scale up/down",
        "R/T: Rotate around Z"
    ]
    for i, line in enumerate(controls):
        text_surface = font.render(line, True, (255,255,255))
        screen.blit(text_surface, (10, 10 + i*20))

    # Handle events
    keys = pygame.key.get_pressed()
    transform = np.eye(4)

    if keys[pygame.K_LEFT]:
        transform = rotation_y(-0.05) @ transform
    if keys[pygame.K_RIGHT]:
        transform = rotation_y(0.05) @ transform
    if keys[pygame.K_UP]:
        transform = rotation_x(-0.05) @ transform
    if keys[pygame.K_DOWN]:
        transform = rotation_x(0.05) @ transform
    if keys[pygame.K_w]:
        transform = translation(0,0.1,0) @ transform
    if keys[pygame.K_s]:
        transform = translation(0,-0.1,0) @ transform
    if keys[pygame.K_a]:
        transform = translation(-0.1,0,0) @ transform
    if keys[pygame.K_d]:
        transform = translation(0.1,0,0) @ transform
    if keys[pygame.K_q]:
        transform = translation(0,0,0.1) @ transform
    if keys[pygame.K_e]:
        transform = translation(0,0,-0.1) @ transform
    if keys[pygame.K_z]:
        transform = scaling(1.05,1.05,1.05) @ transform
    if keys[pygame.K_x]:
        transform = scaling(0.95,0.95,0.95) @ transform
    if keys[pygame.K_r]:
        transform = rotation_z(0.05) @ transform
    if keys[pygame.K_t]:
        transform = rotation_z(-0.05) @ transform

    # Apply transformations
    vertices = (vertices @ transform.T)

    # Draw cube
    projected = [project(v) for v in vertices]
    for edge in edges:
        pygame.draw.line(screen, (0,255,0), projected[edge[0]], projected[edge[1]], 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
