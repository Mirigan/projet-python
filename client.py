#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image_droite, self.rect = load_png('images/joueur1_droite.png')
		self.image_gauche, self.rect = load_png('images/joueur1_gauche.png')
		self.image = self.image_droite
		self.rect.bottomleft = [x, y]

	def Network_joueur(self,data):
		self.rect.center = data['center']

	def Network_orientation(self, data):
		if data['orientation']:
			self.image=self.image_gauche
		else:
			self.image=self.image_droite

	def update(self):
		self.Pump()

class Joueur2(pygame.sprite.Sprite, ConnectionListener):

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image_droite, self.rect = load_png('images/joueur2_droite.png')
		self.image_gauche, self.rect = load_png('images/joueur2_gauche.png')
		self.image = self.image_droite
		self.rect.bottomleft = [x, y]

	def Network_joueur2(self,data):
		self.rect.center = data['center']

	def Network_orientationJoueur2(self, data):
		if data['orientation']:
			self.image=self.image_gauche
		else:
			self.image=self.image_droite

	def update(self):
		self.Pump()

class Plateforme(pygame.sprite.Sprite, ConnectionListener):

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

class TirsGroup(pygame.sprite.RenderClear, ConnectionListener):

	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_tirs(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']: # we're missing sprites
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Tir())				
		elif num_sprites > data['length']: # we've got too many
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			sprite.update(centers[indice_sprite])
			indice_sprite += 1

	def update(self):
		self.Pump()

class Ennemi(pygame.sprite.Sprite):

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_gauche.png')
		self.rect.center = [x, y]
		self.speed = self.speed = [3, 8]
		self.isLeft = False

	def update(self,center):
		self.rect.center = center

class EnnemisGroup(pygame.sprite.RenderClear, ConnectionListener):

	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_ennemis(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']: # we're missing sprites
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Ennemi(0,0))
		elif num_sprites > data['length']: # we've got too many
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			sprite.rect.center = centers[indice_sprite]
			indice_sprite += 1

	def update(self):
		self.Pump()

class Ennemi2(pygame.sprite.Sprite):

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_droite.png')
		self.rect.bottomleft = [x, y]
		self.speed = self.speed = [3, 8]
		self.isLeft = False

	def update(self,center):
		self.rect.center = center

class Ennemis2Group(pygame.sprite.RenderClear, ConnectionListener):

	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_ennemis2(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']: # we're missing sprites
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Ennemi2(0,0))
		elif num_sprites > data['length']: # we've got too many
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			sprite.rect.center = centers[indice_sprite]
			indice_sprite += 1

	def update(self):
		self.Pump()

# PODSIXNET
class Client(ConnectionListener):
	def __init__(self, host, port):
		self.run = False
		self.mort = False
		self.regles = True
		self.score = 0
		self.life = 5
		self.difficulty = "Very Easy"
		self.Connect((host, port))
	
	def Network_mort(self, data):
		print('GAME OVER !')
		print('Score : '+str(self.score))
		self.mort = data['mort']
	
	def Network_full(self, data):
		print('Serveur complet !')
		sys.exit(0)

	def Network_error(self, data):
		print 'error:', data['error'][1]
		connection.Close()

	def Network_disconnected(self, data):
		print 'Server disconnected'
		sys.exit()
	
	def Network_run(self,data):
		self.run = data['run']
	
	def Network_son(self,data):
		pygame.mixer.Sound(data['son']).play()
	
	def Network_score(self,data):
		self.score = data['score']
	
	def Network_life(self,data):
		self.life = data['life']
	
	def Network_difficulty(self,data):
		self.difficulty = data['difficulty']

	def Network_regles(self,data):
		self.regles = data['regles']
# MAIN
def main_function():

	# Initialization
	game_client = Client(sys.argv[1], int(sys.argv[2]))
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1,1)

	# Objects creation
	background_image, background_rect = load_png('images/fond.png')
	wait_image, wait_rect = load_png('images/wait1.png')
	wait_rect.center = background_rect.center
	gameOver_image, gameOver_rect = load_png('images/game_over.png')
	gameOver_rect.center = background_rect.center
	regles_image, regles_rect = load_png('images/rules.png')
	regles_rect.center = background_rect.center
	screen.blit(background_image, background_rect)
	joueur = Joueur(0,750)
	joueur2 = Joueur2(0,750)

	joueur_sprite = pygame.sprite.RenderClear(joueur)
	joueur_sprite.add(joueur2)
	ennemis_sprites = EnnemisGroup()
	ennemis2_sprites = Ennemis2Group()
	tirs_sprites = TirsGroup()

	shooting = 0
	rythm = 0
	counter = 0

	plateforme = Plateforme(0, 770)
	plateforme_sprite = pygame.sprite.RenderClear(plateforme)
	plateforme = Plateforme(300,770)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(600,770)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(900,770)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(0,120)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(SCREEN_WIDTH-300,120)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(0,0)
	plateforme.rect.center = [SCREEN_WIDTH/2, 240]
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(100,380)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(SCREEN_WIDTH-400,380)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(0,0)
	plateforme.rect.center = [SCREEN_WIDTH/2, 630]
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(0,510)
	plateforme_sprite.add(plateforme)
	plateforme = Plateforme(SCREEN_WIDTH-300,510)
	plateforme_sprite.add(plateforme)


	pygame.mixer.music.load("sounds/theme.wav")
	pygame.mixer.music.play(-1)
	
	font = pygame.font.Font(None, 36)
	life=5
	score=0
	difficulty = "Very Easy"
 	textScore = font.render("Score : "+str(score), 1, (255, 255, 255))
 	textDifficulty = font.render("Difficulty : "+difficulty, 1, (255, 255, 255))
 	textLife = font.render("Life : "+str(life), 1, (255, 255, 255))
 	scorePos = textScore.get_rect()
 	scorePos.left = 10
 	difficultyPos = textDifficulty.get_rect()
 	difficultyPos.centerx = SCREEN_WIDTH/2
 	lifePos = textLife.get_rect()
 	lifePos.right = SCREEN_WIDTH-10
 	screen.blit(textScore, scorePos)
 	screen.blit(textDifficulty, difficultyPos)
 	screen.blit(textLife, lifePos)


	# MAIN LOOP
	while game_client.mort == False:
		clock.tick(60) # max speed is 60 frames per second
		connection.Pump()
		game_client.Pump()

		if game_client.run:

			# Events handling
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return # closing the window exits the program
		if game_client.run:
			keys = pygame.key.get_pressed()
			connection.Send({'action':'key','key':keys})
			# updates
			joueur_sprite.update()
			plateforme_sprite.update()
			ennemis_sprites.update()
			ennemis2_sprites.update()
			tirs_sprites.update()


			# drawings
			screen.blit(background_image, background_rect)
			if score != game_client.score:
				score=game_client.score
				textScore = font.render("Score : "+str(score), 1, (255, 255, 255))
			if life != game_client.life:
				life=game_client.life
				textLife = font.render("Life : "+str(life), 1, (255, 255, 255))
			if difficulty != game_client.difficulty:
				difficulty = game_client.difficulty
				textDifficulty = font.render("Difficulty : "+difficulty, 1, (255, 255, 255))
			screen.blit(textScore, scorePos)
			screen.blit(textDifficulty, difficultyPos)
 			screen.blit(textLife, lifePos)

			
			plateforme_sprite.draw(screen)
			if game_client.regles:
				screen.blit(regles_image, regles_rect)
			joueur_sprite.draw(screen)
			ennemis_sprites.draw(screen)
			ennemis2_sprites.draw(screen)
			tirs_sprites.draw(screen)

		else: # game is not running
			screen.blit(wait_image, wait_rect)
		pygame.display.flip()
		
	font = pygame.font.Font(None, 74)
	textScore = font.render("Score : "+str(score), 1, (255, 255, 255))
	textRetry = font.render("Better luck next time", 1, (255, 255, 255))
	scorePos.center = [SCREEN_WIDTH/2-60,100]
	retryPos = textRetry.get_rect()
	retryPos.center = [SCREEN_WIDTH/2,SCREEN_HEIGHT-100]
	while True:
		clock.tick(5)
		screen.blit(background_image, background_rect)
		screen.blit(gameOver_image, gameOver_rect)
		screen.blit(textScore, scorePos)
		screen.blit(textRetry, retryPos)
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return
		pygame.display.flip()


if __name__ == '__main__':
	main_function()
	sys.exit(0)
