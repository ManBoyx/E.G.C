import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

# Initialisation de Pygame
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

# Définir une fonction pour dessiner une voiture
def draw_car():
    glBegin(GL_QUADS)
    glColor3fv((1, 0, 0))  # Rouge
    glVertex3f(-1, -0.5, -1)
    glVertex3f(1, -0.5, -1)
    glVertex3f(1, -0.5, 1)
    glVertex3f(-1, -0.5, 1)

    glColor3fv((0, 1, 0))  # Vert
    glVertex3f(-1, 0.5, -1)
    glVertex3f(1, 0.5, -1)
    glVertex3f(1, 0.5, 1)
    glVertex3f(-1, 0.5, 1)

    glEnd()

# Boucle principale du jeu
def game_loop():
    car_position = [0, 0, 0]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    car_position[0] -= 1
                if event.key == pygame.K_RIGHT:
                    car_position[0] += 1
                if event.key == pygame.K_UP:
                    car_position[2] -= 1
                if event.key == pygame.K_DOWN:
                    car_position[2] += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(car_position[0], car_position[1], car_position[2])
        draw_car()
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

game_loop()
