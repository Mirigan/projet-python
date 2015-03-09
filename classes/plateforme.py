#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""

import sys, pygame
import os
import time
from pygame.locals import *
from PodSixNet.Connection import ConnectionListener
import random

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

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

class Plateforme(pygame.sprite.Sprite, ConnectionListener):
    """Classe des Plateformes"""

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/plateforme.png')
        self.rect.bottomleft = [x,y]
        
	def update(self):
		self.Pump()
