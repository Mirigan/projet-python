#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Very simple game with Pygame
"""

import sys, pygame
import os
import time
import math
from pygame.locals import *
from PodSixNet.Connection import connection, ConnectionListener
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

# CLASSES
class Joueur(pygame.sprite.Sprite, ConnectionListener):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/joueur1_droite.png')
        self.rect.bottomleft = [0, 738]
    
    def Network_Joueur(self,data):
        self.rect.center = data['center']

    def update(self):
        self.Pump()
        
class Plateforme(pygame.sprite.Sprite, ConnectionListener):
    """Classe des Plateformes"""

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/plateforme.png')
        self.rect.bottomleft = [x,y]
        
	def update(self):
		self.Pump()
		
class Tir(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/tir.png')

    def update(self,center):
        self.rect.center = center

# PODSIXNET
class Client(ConnectionListener):
    def __init__(self, host, port):
        self.run = False
        try:
         	self.Connect((host, port))
        except:
			sys.exit(-1)

    def Network_connected(self, data):
        self.run = True
        print('client connecte au serveur !')

	def Network(self, data):
		print('message de type %s recu' % data['action'])

	### Network event/message callbacks ###
	def Network_connected(self, data):
		print('connecte au serveur')
		self.run = True

	def Network_error(self, data):
		print 'error:', data['error'][1]
		connection.Close()

	def Network_disconnected(self, data):
		print 'Server disconnected'
		sys.exit()
 
# MAIN
def main_function():
	"""Main function of the game"""
	# Initialization
	game_client = Client(sys.argv[1], int(sys.argv[2]))
	

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1,1)

	# Objects creation
	background_image, background_rect = load_png('images/fond4.jpg')
	wait_image, wait_rect = load_png('images/wait1.png')
	wait_rect.center = background_rect.center
	screen.blit(background_image, background_rect)
	joueur = Joueur()
	plateforme = Plateforme(0, 768)
	plateforme_sprite = pygame.sprite.RenderClear(plateforme)
	plateforme = Plateforme(300,768)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(600,768)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(900,768)
	plateforme_sprite.add(plateforme)
	joueur_sprite = pygame.sprite.RenderClear(joueur)
	
    

	# MAIN LOOP
	while True:
		clock.tick(60) # max speed is 60 frames per second
		connection.Pump()
		game_client.Pump()

		if game_client.run:

			# Events handling
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return # closing the window exits the program

		if game_client.run:
			keystrokes = pygame.key.get_pressed()
			connection.Send({'action':'keys','keystrokes':keystrokes})

			# updates
			joueur_sprite.update()
			plateforme_sprite.update()

            # drawings
			screen.blit(background_image, background_rect)

			joueur_sprite.draw(screen)
			plateforme_sprite.draw(screen)

		else: # game is not running 
			screen.blit(wait_image, wait_rect)

		pygame.display.flip()  


if __name__ == '__main__':
    main_function()
    sys.exit(0)
