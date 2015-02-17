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

# PODSIXNET
class Client(ConnectionListener):
	def __init__(self, host, port):
		self.run = False
		self.Connect((host, port))

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

			touches=pygame.key.get_pressed()
			connection.Send({"action":"key","key":touches})

			# updates    

			# drawings
			screen.blit(background_image, background_rect)

			pygame.display.flip()


if __name__ == '__main__':
    main_function()
    sys.exit(0)
