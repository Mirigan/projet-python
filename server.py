#!/usr/bin/env python
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time
import sys
import pygame
import os
import random
from pygame.locals import *
from compiler.pyassem import isJump


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
list_plat = []
life = 5

def load_png(name):

	fullname = os.path.join('.', name)
	try:
		image = pygame.image.load(fullname)
		if image.get_alpha is None:
			image = image.convert()
		else:
			image = image.convert_alpha()
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	return image, image.get_rect()


class ClientChannel(Channel):
	def __init__(self, *args, **kwargs):
		Channel.__init__(self, *args, **kwargs)
		self.number = 0
		self.is_shooting = 0
		'''Création des joueurs'''
		self.joueur = Joueur(0, 750)
		self.joueur_sprites = pygame.sprite.RenderClear(self.joueur)
		self.joueur2 = pygame.sprite.RenderClear()
		


	def Close(self):
		self._server.del_client(self)

	def Network_key(self, data):
		touche = data['key']
		'''Effectue les mouvements du joueur'''
		if (touche[K_LEFT]):
			self.joueur.left()
			self.joueur.isLeft = True
		if (touche[K_RIGHT]):
			self.joueur.right()
			self.joueur.isLeft = False
		if (touche[K_UP]):
			self.joueur.up()
		'''Envoi au client l'orientation du joueur'''
		self.Send({'action': 'orientation', 'orientation':self.joueur.isLeft})
		self._server.updateJoueur2(self)
		'''Crée un tire en fonction de l'orientation du personnage'''
		if(touche[K_SPACE]):
			if self.is_shooting == 0:
				if self.joueur.isLeft:
					tir = Tir((self.joueur.rect.centerx-13,self.joueur.rect.centery-8))
				else:
					tir = Tir((self.joueur.rect.centerx+13,self.joueur.rect.centery-8))
				tir.isLeft = self.joueur.isLeft
				for client in self._server.clients:
					client.Send({'action': 'son', 'son': 'sounds/gun.wav'})
				self._server.tirs_sprites.add(tir)
				self.is_shooting = 30

	def send_joueur(self):
		'''Envoi au client sa position'''
		self.Send({'action': 'joueur', 'center': self.joueur.rect.center})
		
	def send_joueur2(self):
		'''Envoi au client la position de l'autre joueur'''
		self.Send({'action': 'joueur2', 'center': self.joueur2.rect.center})

	def send_tirs(self):
		'''Envoi au client la position de tous les tirs'''
		centers = []
		sprites = self.tirs_group.sprites()
		for sprite in sprites:
			centers.append(sprite.rect.center)
		self.Send({'action': 'tirs', 'length': len(sprites), 'centers': centers})

	def update_joueurs(self):
		self.joueur.update()
		self.is_shooting -= 1 if self.is_shooting > 0 else 0


	def update_tirs(self):
		self.tirs_group.update()


class MyServer(Server):
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		self.clients = []
		self.run = False
		self.fin = False
		self.counter = -1200
		pygame.init()
		self.platforme_sprite = pygame.sprite.RenderClear()
		self.screen = pygame.display.set_mode((128, 128))
		self.platforme()
		print('Server launched')

	def Connected(self, channel, addr):
		self.clients.append(channel)
		'''Définie la position de départ des joueur'''
		channel.joueur.rect.bottomright = [SCREEN_WIDTH/2,750]
		channel.number = len(self.clients)
		print('New connection: %d client(s) connected' % len(self.clients))
		'''Indique aux clients que le jeu est lancé'''
		if len(self.clients) >= 2:
			if self.counter>=-300:
				channel.Send({'action': 'regles', 'regles':False})
			self.run = True
			for client in self.clients:
				client.Send({'action': 'run', 'run': True})

	def del_client(self, channel):
		print('client deconnected')
		self.clients.remove(channel)
		if len(self.clients) == 1:
			self.run = False
			for client in self.clients:
			   	client.Send({'action': 'run', 'run': False})
		'''Arrete le serveur si la partie est terminé et que tout les clients ce sont déconnectés'''
		if len(self.clients) == 0 and self.fin:
		   	sys.exit(0)

	def send_joueurs(self):
		'''Envoi leur position a tous les joueurs'''
		for client in self.clients:
			client.send_joueur()
	
	def send_joueur2(self):
		'''Envoi à tous les joueurs la position des autres joueurs'''
		for client in self.clients:
			joueur2 = []
			for sprite in client.joueur2.sprites():
				joueur2.append((sprite.rect.centerx,sprite.rect.centery,sprite.isLeft))
			client.Send({'action': 'joueur2', 'length': len(joueur2), 'joueur2': joueur2})

	def send_tirs(self):
		'''Envoi la position des tirs a tous les joueurs'''
		centers = []
		for sprite in self.tirs_sprites.sprites():
			centers.append(sprite.rect.center)
		for channel in self.clients:
			channel.Send({'action': 'tirs', 'length': len(centers), 'centers': centers})

	def send_ennemis(self, ennemis_sprites):
		'''Envoi la position des ennemis a tous les joueurs'''
		centers = []
		for sprite in ennemis_sprites.sprites():
			centers.append(sprite.rect.center)
		for channel in self.clients:
			channel.Send({'action': 'ennemis', 'length': len(centers), 'centers': centers})
	
	def send_ennemis2(self, ennemis2_sprites):
		'''Envoi la position des ennemis (second type d'ennemi) a tous les joueurs'''
		centers = []
		for sprite in ennemis2_sprites.sprites():
			centers.append(sprite.rect.center)
		for channel in self.clients:
			channel.Send({'action': 'ennemis2', 'length': len(centers), 'centers': centers})

		# UPDATE FUNCTIONS

	def update_joueurs(self):
		for client in self.clients:
			client.update_joueurs()

	def update_tirs(self):
		self.tirs_sprites.update()

	def draw_joueurs(self, screen):
		for client in self.clients:
			screen.blit(client.joueur.image, client.joueur.rect)

	def draw_tirs(self, screen):
		for client in self.clients:
			client.tirs_group.draw(screen)

	def launch_game(self):
		
		pygame.display.set_caption('Server')

		clock = pygame.time.Clock()
		pygame.key.set_repeat(1, 1)

		
		wait_image, wait_rect = load_png('images/wait.png')
		self.screen.blit(wait_image, wait_rect)
		ennemis_sprites = pygame.sprite.RenderClear()
		ennemis2_sprites = pygame.sprite.RenderClear()
		self.tirs_sprites = pygame.sprite.RenderClear()

		rythm = 90
		score = 0
		
		global life

		while True:
			clock.tick(60)
			self.Pump()

			if self.run:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return
					   
				pygame.sprite.groupcollide(self.platforme_sprite, self.tirs_sprites, False, True)

				self.update_joueurs()
				self.send_joueurs()
				self.send_joueur2()
				self.update_tirs()
				self.send_tirs()
				self.counter += 1
				'''Permet d'arreter l'affichage des règles'''
				if self.counter==-300:
					for c in self.clients:
						c.Send({'action': 'regles', 'regles':False})
				'''Fait apparaitre un ennemi a l'une des 6 positions aléatoire'''
				if self.counter >= rythm:
					r = random.randint(1,6)
					if r == 1 :
					 	ennemis_sprites.add(Ennemi(SCREEN_WIDTH+10,100))
					elif r == 2:
					 	ennemis_sprites.add(Ennemi(SCREEN_WIDTH+10,500))
					elif r == 3:
					 	ennemis_sprites.add(Ennemi(SCREEN_WIDTH+10,750))
					elif r == 4:
					 	ennemis2_sprites.add(Ennemi2(-10,100))
					elif r == 5:
					 	ennemis2_sprites.add(Ennemi2(-10,500))
					else:
					 	ennemis2_sprites.add(Ennemi2(-10,750))					 	
					self.counter = 0
				ennemis_sprites.update()
				self.send_ennemis(ennemis_sprites)
				ennemis2_sprites.update()
				self.send_ennemis2(ennemis2_sprites)
				
				'''Augmente le score quand un ennemi est éliminé et envoi au client le nouveau score'''
				if pygame.sprite.groupcollide(ennemis_sprites, self.tirs_sprites, True, True):
					score += 1
					for c in self.clients:
						c.Send({'action': 'score', 'score':score})
				if pygame.sprite.groupcollide(ennemis2_sprites, self.tirs_sprites, True, True):
					score += 1
					for c in self.clients:
						c.Send({'action': 'score', 'score':score})
				'''Diminiue le nombre de vies lorsqu'un joueur touche un ennemi'''
				for client in self.clients:
					if pygame.sprite.groupcollide(ennemis_sprites, client.joueur_sprites, True, False):
						life -= 1
					if pygame.sprite.groupcollide(ennemis2_sprites, client.joueur_sprites, True, False):
						life -= 1
				'''Envoi à chaque client le nombre de vies restantes'''
				for c in self.clients:							
					c.Send({'action': 'life', 'life':life})
				
				'''Indique aux clients que la partie est finie s'ils n'ont plus de vie'''
				if life <= 0:
					self.run = False
					self.fin = True
					for c in self.clients:
						c.Send({'action': 'mort', 'mort':True})
				
				'''Augmente le niveau de difficulte (vitesse d'apparition des ennemi) en fonction du score'''
				if score == 50:
					rythm=80
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Easy'})	
				elif score == 100:
					rythm=70
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Medium'})	
				elif score == 150:
					rythm=60
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Hard'})	
				elif score == 250:
					rythm=30
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Very Hard'})
				elif score == 350:
					rythm=20
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Insane'})	
				elif score == 450:
					rythm=10
					for c in self.clients:
						 	c.Send({'action': 'difficulty', 'difficulty':'Impossible'})		

			pygame.display.flip()
			
	def platforme(self):
		'''Initialise les plateformes'''
		plateforme = Plateforme(0, 770)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(300, 770)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(600, 770)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(900, 770)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(00, 120)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH - 300, 120)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(0, 0)
		plateforme.rect.center = [SCREEN_WIDTH / 2, 240]
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(100, 380)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH-400, 380)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(0, 0)
		plateforme.rect.center = [SCREEN_WIDTH / 2, 630]
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(0, 510)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH - 300, 510)
		list_plat.append(plateforme)
		self.platforme_sprite.add(plateforme)
	
	def updateJoueur2(self, channel):
		'''Récupere les positions et orientations des autres joueurs'''
		j2 = []
		for c in self.clients:
			if c != channel:
				j2.append(c.joueur)
		if len(channel.joueur2.sprites()) < len(j2):
			'''Ajoute de nouveaux joueurs'''
			for additional_sprite in range(len(j2) - len(channel.joueur2.sprites())):
				channel.joueur2.add(Joueur2(0,0))
		elif len(channel.joueur2.sprites()) > len(j2):
			'''Supprime les joueurs en trop'''
			deleted = 0
			for sprite in channel.joueur2.sprites():
				channel.joueur2.remove(sprite)
				deleted += 1
				if deleted == len(channel.joueur2.sprites()) - len(j2):
					break
		indice_sprite = 0
		for sprite in channel.joueur2.sprites():
			'''Met à jour la position des joueurs et leur orientation'''
			sprite.rect = j2[indice_sprite].rect
			sprite.isLeft = j2[indice_sprite].isLeft
			indice_sprite += 1


			
class Joueur(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/joueur1_droite.png')
		self.rect.bottomleft = [x, y]
		self.speed = [0, 8]
		self.isJump = False
		self.durationJump = 25
		self.timeJump = 0
		self.isLeft = False

	'''Fait sauter le joueur s'il n'est pas déja entrain de sauter'''
	def up(self):
		if self.isJump == False:
			self.isJump = True
			self.rect = self.rect.move([0, -15])

	'''Fait se déplacer le joueur vers la gauche s'il ne rencontre pas de plateforme ou le bords de la fenetre'''
	def left(self):
		self.image = pygame.transform.flip(self.image, True, False)
		if (self.collision_left(list_plat) == False):
			if self.rect.left > 0:
				self.rect = self.rect.move([-5, 0])
	
	'''Fait se déplacer le joueur vers la droitee s'il ne rencontre pas de plateforme ou le bords de la fenetre'''
	def right(self):
		self.image = pygame.transform.flip(self.image, True, False)
		if (self.collision_right(list_plat) == False):
			if self.rect.right < SCREEN_WIDTH:
				self.rect = self.rect.move([5, 0])

	def update(self):
		if (self.collision_bot(list_plat) == False):
			'''Fait 'tomber' le joueur s'il n'est pas sur une plateforme '''
			if self.isJump == True:
				'''S'il est en train de sauter, deplace le joueur en fonction de la durer du saut total et du temps déja écoulé'''
				if self.timeJump < self.durationJump:
					self.timeJump += 1
					if (self.collision_top(list_plat) == False):
						if self.rect.top > 0:
							self.rect = self.rect.move([0, -(self.durationJump - self.timeJump)])
						else:
							self.timeJump = self.durationJump
					else:
						self.timeJump = self.durationJump
			self.rect = self.rect.move(self.speed)
		else:
			'''Permet au joueur d'effectuer un nouveau saut'''
			self.isJump = False
			self.timeJump = 0


	def is_under(self, platform):
		'''Verifie si le joueur touche le bas d'une plateforme'''
		return (pygame.Rect(self.rect.x, self.rect.y - 9, self.rect.width, self.rect.height).colliderect(platform.rect))

	def is_on(self, platform):
		'''Verifie si le joueur touche le haut d'une plateforme'''
		return (pygame.Rect(self.rect.x, self.rect.y + 9, self.rect.width, self.rect.height).colliderect(platform.rect))

	def is_left(self, platform):
		'''Verifie si le joueur touche la gauche d'une plateforme'''
		return (pygame.Rect(self.rect.x + 6, self.rect.y, self.rect.width, self.rect.height).colliderect(platform.rect))

	def is_right(self, platform):
		'''Verifie si le joueur touche la droite d'une plateforme'''
		return (pygame.Rect(self.rect.x - 6, self.rect.y, self.rect.width, self.rect.height).colliderect(platform.rect))

	'''Vérifie si le joueur est en colision avec une plateforme'''
	def collision_top(self, list_plat):
		for plat in list_plat:
			if self.is_under(plat):
				return True
		return False

	def collision_bot(self, list_plat):
		for plat in list_plat:
			if self.is_on(plat):
				self.rect.bottom = plat.rect.top;
				return True
		return False
	
	def collision_right(self, list_plat):
		for plat in list_plat:
			if self.is_left(plat):
				return True
		return False

	def collision_left(self, list_plat):
		for plat in list_plat:
			if self.is_right(plat):
				return True
		return False

class Joueur2(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/joueur1_droite.png')
		self.rect.bottomleft = [x, y]
		self.isLeft = False


	def update(self):
		pass


class Plateforme(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/plateforme.png')
		self.rect.bottomleft = [x, y]


class Tir(pygame.sprite.Sprite):
	
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/tir.png')
		self.rect.center = position
		self.isLeft = False

	def update(self):
		'''Fait se déplacer le tir en fonction de sa direction'''
		if self.isLeft:
			self.rect = self.rect.move([-10, 0])
		else:
			self.rect = self.rect.move([10, 0])
		if self.rect.right < 0:
			self.kill()
		if self.rect.left>SCREEN_WIDTH:
			self.kill()


class Ennemi(pygame.sprite.Sprite):

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_gauche.png')
		self.rect.bottomright = [x, y]
		self.speed = [-3, 0]
		self.gravity = [0, 6]
		self.isLeft = False

	def update(self):
		'''Fait se déplacer un ennemi'''
		self.rect = self.rect.move(self.speed)
		if self.collision_bot(list_plat) == False:
			self.rect = self.rect.move(self.gravity)
		if self.rect.right < 0:
			'''Enleve une vie au joueur si l'ennemi quite l'écran'''
			global life
			life -= 1
			self.kill()
	
	'''Vérifie si l'ennemi est en colision avec une plateforme'''
	def is_on(self, platform):
		return (pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height).colliderect(platform.rect))

	def collision_bot(self, list_plat):
		for plat in list_plat:
			if self.is_on(plat):
				self.rect.bottom = plat.rect.top;
				return True
		return False

class Ennemi2(pygame.sprite.Sprite):

	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_png('images/enemy_droite.png')
		self.rect.bottomleft = [x, y]
		self.speed = [3, 0]
		self.gravity = [0, 6]
		self.isLeft = False

	def update(self):
		'''Fait se déplacer un ennemi'''
		self.rect = self.rect.move(self.speed)
		if self.collision_bot(list_plat) == False:
			self.rect = self.rect.move(self.gravity)
		if self.rect.left > SCREEN_WIDTH:
			'''Enleve une vie au joueur si l'ennemi quite l'écran'''
			global life
			life -= 1
			self.kill()
	
	'''Vérifie si l'ennemi est en colision avec une plateforme'''	
	def is_on(self, platform):
		return (pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height).colliderect(platform.rect))

	def collision_bot(self, list_plat):
		for plat in list_plat:
			if self.is_on(plat):
				self.rect.bottom = plat.rect.top;
				return True
		return False

def main_function():

	try:
		my_server = MyServer(localaddr=(sys.argv[1], int(sys.argv[2])))
	except:
		print('Syntaxe: python serverDemo.py <IP server> <port server>')
		sys.exit(-1)	
	my_server.launch_game()


if __name__ == '__main__':
	main_function()
	sys.exit(0)
