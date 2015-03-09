import sys
import pygame
import os
import time
from pygame.locals import *
from PodSixNet.Connection import ConnectionListener
import random

# FUNCTIONS
def load_png(name):
    """Load image and return image object"""
    fullname=os.path.join('.',name)
    try:
        image=pygame.image.load(fullname)
        if image.get_alpha is None:
            image=image.convert()
        else:
            image=image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image,image.get_rect()

# CLASSES
class Joueur(pygame.sprite.Sprite, ConnectionListener):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/joueur1_droite.png')
        self.rect.bottomleft = [0, 738]
        self.speed = [0,0]

    def up(self):
        if self.speed[1] > -5:
            self.speed[1] -= 1

    def left(self):
        if self.speed[0] > -5:
            self.speed[0] -= 1

    def right(self):
        if self.speed[0] < 5:
            self.speed[0] += 1
    
    def Network_Joueur(self,data):
        self.rect.center = data['center']

    def update(self):
        self.Pump()
