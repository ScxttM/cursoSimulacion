from math import sqrt, pi, sin, cos, radians
from random import randint, random
from itertools import combinations

import numpy as np
import pygame
from pygame.locals import *

from particle import *
from settings import *

# Initialize
pygame.init()
screen = pygame.display.set_mode((X, Y), 0, 0)
pygame.display.set_caption("Aesthetic Collisions | FPS: ")

# Initialize global variables
fractal_progress = 0.0
clock = pygame.time.Clock()
ParticlesGroup = pygame.sprite.Group()
BoxesGroup = pygame.sprite.Group()

# Arrange the particles
big_polygon = [(X//2 + min(X, Y)//3 * cos(radians(t)),
                Y//2 + min(X, Y)//3 * sin(radians(t)))
               for t in np.arange(0, 360, 360/NUMBER_OF_PARTICLES)]
polygon_sprite_track = []  # To keep track of the order of the particles

# Spawn the particles
for i, eachC in enumerate(big_polygon):
    particle = Particle(
        1, PARTICLE_RADIUS, (255, 255, 255),
        np.array(eachC),
        np.array(toCartesian(
            PARTICLE_SPEED,
            360.0 - 360.0/NUMBER_OF_PARTICLES * (i + START_DIR)))
    )
    ParticlesGroup.add(particle)
    polygon_sprite_track.append(particle)


def new_polygon(biggon, ratio):
    # Generates the next layer of the fractal-like polygon pattern.
    smallgon = []
    E = len(biggon)
    for i in range(E):
        new_vertex = (biggon[i][0] * ratio + biggon[(i+1) % E][0] * (1-ratio),
                      biggon[i][1] * ratio + biggon[(i+1) % E][1] * (1-ratio))
        smallgon.append(new_vertex)
    return tuple(smallgon)


def refresh_grid():
    # Updates the grid that is used for optimizing collision checks.
    # Uses global variables.
    BoxesGroup.empty()
    width = round(X/GRID_SIZE)
    height = round(Y/GRID_SIZE)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            box = pygame.sprite.Sprite()
            box.rect = pygame.Rect((r*width, c*height), (width, height))
            BoxesGroup.add(box)


refresh_grid()

# ---------------------------- #
# ------ MAIN GAME LOOP ------ #
# ---------------------------- #
while True:
    # Update game clock
    milli = clock.tick()
    fps = clock.get_fps()

    # Get user input
    mpos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    for e in events:
        # Quitting the game
        if e.type == QUIT:
            pygame.quit()
            quit()
        if e.type == KEYDOWN:
            # Press G - Toggle show grid
            if e.key == K_g:
                SHOW_GRID = not SHOW_GRID

            # Press S - Screenshot
            if e.key == K_s:
                pygame.image.save(screen,
                                  './screenshots/%.5d.png' % randint(10000, 99999))

            # Press R - Reset
            if e.key == K_r:
                ParticlesGroup.empty()
                fractal_progress = 0

                polygon = [(X//2 + Y//3*cos(radians(t)), Y//2 + Y//3*sin(radians(t)))
                           for t in np.arange(0, 360, 360/NUMBER_OF_PARTICLES)]
                polygon_sprite_track = []
                for i, eachC in enumerate(polygon):
                    particle = Particle(
                        1, PARTICLE_RADIUS, (255, 255, 255),
                        np.array(eachC),
                        np.array(toCartesian(
                            PARTICLE_SPEED,
                            360.0 - 360.0/NUMBER_OF_PARTICLES * (i + START_DIR)))
                    )
                    ParticlesGroup.add(particle)
                    polygon_sprite_track.append(particle)

            # Press UP - Double number of polygons
            if e.key == K_UP:
                NUMBER_OF_SMALLGONS *= 2

            # Press DOWN - Halve number of polygons
            if e.key == K_DOWN:
                if NUMBER_OF_SMALLGONS > 1:
                    NUMBER_OF_SMALLGONS //= 2
                else:
                    NUMBER_OF_SMALLGONS = 1

            # Press RIGHT - Add a row and column to grid
            if e.key == K_RIGHT:
                GRID_SIZE += 1
                refresh_grid()

            # Press LEFT - Discard a row and column to grid
            if e.key == K_LEFT:
                GRID_SIZE -= 1
                if GRID_SIZE < 1:
                    GRID_SIZE = 1
                refresh_grid()

            # Change particle starting directions
            if e.key == K_1:
                START_DIR = 0
            if e.key == K_2:
                START_DIR = NUMBER_OF_PARTICLES//4
            if e.key == K_3:
                START_DIR = 1
            if e.key == K_4:
                START_DIR = NUMBER_OF_PARTICLES//2

    # Slow-down/Speed-up Controls
    if keys[K_0]:
        milli = 0
    if keys[K_9]:
        milli = 1
    if keys[K_MINUS]:
        milli /= 2
    if keys[K_EQUALS]:
        milli *= 2

    # Set Background
    screen.fill(BACKGROUND_COLOR)

    # Collision with each other (by Grid)
    by_box = pygame.sprite.groupcollide(BoxesGroup, ParticlesGroup, 0, 0)
    for eachBox in by_box:
        for eachP in combinations(by_box[eachBox], 2):
            eachP[0].testParticleCollision(eachP[1])

    # Update particles then draw to screen
    for each_particle in ParticlesGroup:
        # Hackish wall collisions to fix particles going off-screen
        each_particle.testWallCollision(screen.get_size())
        # Move particles
        each_particle.updatePosition(milli)
        # Draw particles to screen
        screen.blit(each_particle.image, each_particle.rect)

    # Increase fractal_progress
    fractal_progress += 0.1 * milli/1000
    fractal_progress = fractal_progress % 1

    # Find corners of the big polygon (connecting the particles together)
    for i, eachParticle in enumerate(polygon_sprite_track):
        big_polygon[i] = tuple(int(each) for each in eachParticle.position)

    # Get coordinates of the small polygons
    smallgons = [big_polygon]
    for i in range(NUMBER_OF_SMALLGONS):
        smallgons.append(new_polygon(smallgons[i], fractal_progress))

    # Draw the fractal-like polygons on the screen
    # -~i == (i + 1)
    for i, each in enumerate(smallgons):
        color = (int(DARK[0] + (LIGHT[0]-DARK[0])*sqrt(-~i/len(smallgons))),
                 int(DARK[1] + (LIGHT[1]-DARK[1])*sqrt(-~i/len(smallgons))),
                 int(DARK[2] + (LIGHT[2]-DARK[2])*sqrt(-~i/len(smallgons)))),
        int_coors = [(round(coor[0]), round(coor[1])) for coor in each]

        pygame.draw.lines(screen, color, True, int_coors, LINE_WIDTH)

    # Draw the grid which optimises collision checks
    if SHOW_GRID:
        for i in range(1, GRID_SIZE):
            pygame.draw.line(screen, (127, 0, 0),
                             [round(i * X/GRID_SIZE), 0],
                             [round(i * X/GRID_SIZE), Y],
                             1)
            pygame.draw.line(screen, (127, 0, 0),
                             [0, round(i * Y/GRID_SIZE)],
                             [X, round(i * Y/GRID_SIZE)],
                             1)

    # Update Display
    pygame.display.flip()

    # Update caption, show FPS
    pygame.display.set_caption(
        "Aesthetic Collisions | FPS: " + str(round(fps, 3)))
