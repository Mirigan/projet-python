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

class Joueur(pygame.sprite.Sprite, ConnectionListener):
	''' Le joueur utilisé par le client'''

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image_droite, self.rect = load_png('images/joueur1_droite.png')
		self.image_gauche, self.rect = load_png('images/joueur1_gauche.png')
		self.image = self.image_droite
		self.rect.bottomleft = [x, y]

	def Network_joueur(self,data):
		'''Permet de modifier la position du joueur'''
		self.rect.center = data['center']

	def Network_orientation(self, data):
		''' Permet de modifier l'orientation du joueur en fonction du déplacement (gauche/droite)'''
		if data['orientation']:
			self.image=self.image_gauche
		else:
			self.image=self.image_droite

	def update(self):
		self.Pump()

class Joueur2(pygame.sprite.Sprite, ConnectionListener):
	''' Les joueurs utilisés par les autres clients'''

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image_droite, self.rect = load_png('images/joueur2_droite.png')
		self.image_gauche, self.rect = load_png('images/joueur2_gauche.png')
		self.image = self.image_droite
		
class Joueur2Group(pygame.sprite.RenderClear, ConnectionListener):
	''' Le groupe contenant tous les autres joueurs '''
	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_joueur2(self,data):
		num_sprites = len(self.sprites())
		joueur2 = data['joueur2']
		if num_sprites < data['length']: 
			'''Ajoute de nouveaux joueurs'''
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Joueur2())				
		elif num_sprites > data['length']: 
			'''Supprime les joueurs en trop'''
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			'''Met à jour la position des autres joueurs'''
			sprite.rect.center =[joueur2[indice_sprite][0],joueur2[indice_sprite][1]] 
			if joueur2[indice_sprite][2]:
				sprite.image=sprite.image_gauche
			else:
				sprite.image=sprite.image_droite
			indice_sprite += 1

	def update(self):
		self.Pump()

class Plateforme(pygame.sprite.Sprite, ConnectionListener):
	''' Une plateforme '''

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/plateforme.png')
		self.rect.bottomleft = [x,y]

	def update(self):
		self.Pump()

class Tir(pygame.sprite.Sprite):
	" Un tir "
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/tir.png')

	def update(self,center):
		self.rect.center = center

class TirsGroup(pygame.sprite.RenderClear, ConnectionListener):
	''' Le groupe contenant tous les tirs '''
	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_tirs(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']: 
			'''Ajoute de nouveaux tirs'''
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Tir())				
		elif num_sprites > data['length']: 
			'''Supprime les tirs en trop'''
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			'''Met à jour la position des tirs'''
			sprite.update(centers[indice_sprite])
			indice_sprite += 1

	def update(self):
		self.Pump()

class Ennemi(pygame.sprite.Sprite):
	''' Un ennemi '''
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_gauche.png')
		self.rect.center = [x, y]
		self.speed = self.speed = [3, 8]
		self.isLeft = False

	def update(self,center):
		self.rect.center = center

class EnnemisGroup(pygame.sprite.RenderClear, ConnectionListener):
	''' Le groupe contenant le premier type d'ennemis '''

	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_ennemis(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']:
			'''Ajoute de nouveaux ennemis'''
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Ennemi(0,0))
		elif num_sprites > data['length']:
			'''Supprime les ennemis en trop'''
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			'''Met à jour la position des ennemis'''
			sprite.rect.center = centers[indice_sprite]
			indice_sprite += 1

	def update(self):
		self.Pump()

class Ennemi2(pygame.sprite.Sprite):
	''' Un second type d'ennemi '''
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_droite.png')
		self.rect.bottomleft = [x, y]
		self.speed = self.speed = [3, 8]
		self.isLeft = False

	def update(self,center):
		self.rect.center = center

class Ennemis2Group(pygame.sprite.RenderClear, ConnectionListener):
	''' Le groupe contenant le second type d'ennemis '''
	def __init__(self):
		pygame.sprite.RenderClear.__init__(self)

	def Network_ennemis2(self,data):
		num_sprites = len(self.sprites())
		centers = data['centers']
		if num_sprites < data['length']:
			'''Ajoute de nouveaux ennemis'''
			for additional_sprite in range(data['length'] - num_sprites):
				self.add(Ennemi2(0,0))
		elif num_sprites > data['length']:
			'''Supprime les ennemis en trop'''
			deleted = 0
			for sprite in self.sprites():
				self.remove(sprite)
				deleted += 1
				if deleted == num_sprites - data['length']:
					break
		indice_sprite = 0
		for sprite in self.sprites():
			'''Met à jour la position des ennemis'''
			sprite.rect.center = centers[indice_sprite]
			indice_sprite += 1

	def update(self):
		self.Pump()

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
		'''Met fin au jeu'''
		print('GAME OVER !')
		print('Score : '+str(self.score))
		self.mort = data['mort']
	
	def Network_full(self, data):
		'''Ferme le programme quand le server est complet'''
		print('Server full !')
		sys.exit(0)

	def Network_error(self, data):
		print 'error:', data['error'][1]
		connection.Close()

	def Network_disconnected(self, data):
		print 'Server disconnected'
		sys.exit()
	
	def Network_run(self,data):
		'''Indique s'il y a 2 joueurs de connecté au server ou non'''
		self.run = data['run']
	
	def Network_son(self,data):
		'''Joue le son en parametre'''
		pygame.mixer.Sound(data['son']).play()
	
	def Network_score(self,data):
		'''Met à jour le score'''
		self.score = data['score']
	
	def Network_life(self,data):
		'''Met à jour le nombre de vies restantes'''
		self.life = data['life']
	
	def Network_difficulty(self,data):
		'''Met à jour la difficulté'''
		self.difficulty = data['difficulty']

	def Network_regles(self,data):
		'''Indique si les regles doivent êtres affichées ou non'''
		self.regles = data['regles']

def main_function():

	try:
		game_client = Client(sys.argv[1], int(sys.argv[2]))
	except:
		print('Syntaxe: python client.py <IP server> <port server>')
		sys.exit(-1)
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	pygame.key.set_repeat(1,1)

	'''Création des objet'''
	background_image, background_rect = load_png('images/fond.png')
	wait_image, wait_rect = load_png('images/wait1.png')
	wait_rect.center = background_rect.center
	gameOver_image, gameOver_rect = load_png('images/game_over.png')
	gameOver_rect.center = background_rect.center
	regles_image, regles_rect = load_png('images/rules.png')
	regles_rect.center = background_rect.center
	screen.blit(background_image, background_rect)
	joueur = Joueur(0,750)

	joueur_sprite = pygame.sprite.RenderClear(joueur)
	joueur2_sprites = Joueur2Group()
	ennemis_sprites = EnnemisGroup()
	ennemis2_sprites = Ennemis2Group()
	tirs_sprites = TirsGroup()

	'''Initialisation des plateformes'''
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

	'''Lancement de la music de fond'''
	pygame.mixer.music.load("sounds/theme.wav")
	pygame.mixer.music.play(-1)
	
	'''Initialisation de l'affichage (score, vie, difficulté)'''
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
 	lifePos.right = SCREEN_WIDTH-50
 	screen.blit(textScore, scorePos)
 	screen.blit(textDifficulty, difficultyPos)
 	screen.blit(textLife, lifePos)


	while game_client.mort == False:
		clock.tick(60) 
		connection.Pump()
		game_client.Pump()

		if game_client.run:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return
		if game_client.run:
			keys = pygame.key.get_pressed()
			connection.Send({'action':'key','key':keys})

			joueur_sprite.update()
			plateforme_sprite.update()
			joueur2_sprites.update()
			ennemis_sprites.update()
			ennemis2_sprites.update()
			tirs_sprites.update()



			screen.blit(background_image, background_rect)
			'''Met à jour l'affichage si les valeurs ont changées'''
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
			joueur2_sprites.draw(screen)
			joueur_sprite.draw(screen)
			ennemis_sprites.draw(screen)
			ennemis2_sprites.draw(screen)
			tirs_sprites.draw(screen)

		else:
			screen.blit(wait_image, wait_rect)
		pygame.display.flip()
	
	'''Mise en place de l'écran de fin'''
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
