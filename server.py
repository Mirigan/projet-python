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

# FUNCTIONS
def load_png(name):
    """Load image and return image object"""
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

		self.joueur = Joueur(0, 750)
		self.adversaire = Adversaire(0, 750)
		self.tirs_group = pygame.sprite.RenderClear()


    def Close(self):
        self._server.del_client(self)

    def Network_key(self, data):
        touche = data['key']
        if (touche[K_LEFT]):
            self.joueur.left()
            self.joueur.isLeft = True
        if (touche[K_RIGHT]):
            self.joueur.right()
            self.joueur.isLeft = False
        if (touche[K_UP]):
            self.joueur.up()
        self.Send({'action': 'orientation', 'orientation':self.joueur.isLeft})
        self._server.updateAdversaire(self)
        if(touche[K_SPACE]):
            if self.is_shooting == 0:
            	tir = Tir(self.joueur.rect.center)
            	tir.isLeft = self.joueur.isLeft
                self.tirs_group.add(tir)
                self.is_shooting = 40

    def send_joueur(self):
        self.Send({'action': 'joueur', 'center': self.joueur.rect.center})
        
    def send_adversaire(self):
        self.Send({'action': 'adversaire', 'center': self.adversaire.rect.center})

    def send_tirs(self):
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
        pygame.init()
        self.screen = pygame.display.set_mode((128, 128))
        self.platforme()
        print('Server launched')

    def Connected(self, channel, addr):
        if len(self.clients) == 1:
    		channel.joueur.rect.bottomright = [SCREEN_WIDTH,750]
      	else:
      		channel.adversaire.rect.bottomright = [SCREEN_WIDTH,750]
        self.clients.append(channel)
        channel.number = len(self.clients)
        print('New connection: %d client(s) connected' % len(self.clients))
        if len(self.clients) == 2:
            self.run = True
            '''wheels_image, wheels_rect = load_png('images/wheels.png')'''
            '''self.screen.blit(wheels_image, wheels_rect)'''

    def del_client(self, channel):
        print('client deconnected')
        self.clients.remove(channel)

    # SENDING FUNCTIONS
    def send_joueurs(self):
        for client in self.clients:
            client.send_joueur()
    
    def send_adversaires(self):
        for client in self.clients:
            client.send_adversaire()

    def send_tirs(self):
        for client in self.clients:
            client.send_tirs()

    def send_ennemis(self, ennemis_sprites):
        centers = []
        for sprite in ennemis_sprites.sprites():
            centers.append(sprite.rect.center)
        for channel in self.clients:
            channel.Send({'action': 'ennemis', 'length': len(centers), 'centers': centers})
    
    def send_ennemis2(self, ennemis2_sprites):
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
        for client in self.clients:
            client.update_tirs()

    def draw_joueurs(self, screen):
        for client in self.clients:
            screen.blit(client.joueur.image, client.joueur.rect)

    def draw_tirs(self, screen):
        for client in self.clients:
            client.tirs_group.draw(screen)

    def launch_game(self):
        # Init Pygame
        pygame.display.set_caption('Server')

        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        # Elements
        wait_image, wait_rect = load_png('images/wait.png')
        self.screen.blit(wait_image, wait_rect)
        ennemis_sprites = pygame.sprite.RenderClear()
        ennemis2_sprites = pygame.sprite.RenderClear()

        shooting = 0
        rythm = 90
        counter = 0

        while True:
            clock.tick(60)
            self.Pump()

            if self.run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                # updates
                for channel in self.clients:
                    pygame.sprite.groupcollide(ennemis_sprites, channel.tirs_group, True, True)
                    pygame.sprite.groupcollide(ennemis2_sprites, channel.tirs_group, True, True)
                self.update_joueurs()
                self.send_joueurs()
                self.send_adversaires()
                self.update_tirs()
                self.send_tirs()
                counter += 1
                if counter == rythm:
                    r = random.randint(1,4)
                    if r == 1 :
                     	ennemis_sprites.add(Ennemi(SCREEN_WIDTH+10,100))
                    elif r == 2:
                     	ennemis_sprites.add(Ennemi(SCREEN_WIDTH+10,680))
                    elif r == 3:
                     	ennemis2_sprites.add(Ennemi2(-10,100))
                    else:
                     	ennemis2_sprites.add(Ennemi2(-10,680))
                    counter = 0
                ennemis_sprites.update()
                self.send_ennemis(ennemis_sprites)
                ennemis2_sprites.update()
                self.send_ennemis2(ennemis2_sprites)

            # drawings
            # screen.blit(background_image, background_rect)
            # self.draw_ships(screen)
            # self.draw_shots(screen)
            # foes_sprites.draw(screen)
            pygame.display.flip()
            
    def platforme(self):
		plateforme = Plateforme(0, 780)
		list_plat.append(plateforme)
		plateforme = Plateforme(300, 780)
		list_plat.append(plateforme)
		plateforme = Plateforme(600, 780)
		list_plat.append(plateforme)
		plateforme = Plateforme(900, 780)
		list_plat.append(plateforme)
		plateforme = Plateforme(00, 130)
		list_plat.append(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH - 300, 130)
		list_plat.append(plateforme)
		plateforme = Plateforme(0, 0)
		plateforme.rect.center = [SCREEN_WIDTH / 2, 245]
		list_plat.append(plateforme)
		plateforme = Plateforme(100, 390)
		list_plat.append(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH - 400, 390)
		list_plat.append(plateforme)
		plateforme = Plateforme(0, 0)
		plateforme.rect.center = [SCREEN_WIDTH / 2, 505]
		list_plat.append(plateforme)
		plateforme = Plateforme(0, 650)
		list_plat.append(plateforme)
		plateforme = Plateforme(SCREEN_WIDTH - 300, 650)
		list_plat.append(plateforme)
	
    def updateAdversaire(self, channel):
		for c in self.clients:
			if c != channel:
				c.adversaire.rect.center = channel.joueur.rect.center
				c.adversaire.isLeft = channel.joueur.isLeft
				c.Send({'action': 'orientationAdversaire', 'orientation':c.adversaire.isLeft})


            
# CLASSES
class Joueur(pygame.sprite.Sprite):
    """Class for the player's ship"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/joueur1_droite.png')
        self.rect.bottomleft = [x, y]
        self.speed = [0, 8]
        self.isJump = False
        self.durationJump = 25
        self.timeJump = 0
        self.isLeft = False


    def up(self):
    	if self.isJump == False:
    		self.isJump = True
    		self.rect = self.rect.move([0, -15])

    def left(self):
    	self.image = pygame.transform.flip(self.image, True, False)
        if (self.collision_left(list_plat) == False):
            if self.rect.left > 0:
                self.rect = self.rect.move([-5, 0])

    def right(self):
    	self.image = pygame.transform.flip(self.image, True, False)
        if (self.collision_right(list_plat) == False):
            if self.rect.right < SCREEN_WIDTH:
                self.rect = self.rect.move([5, 0])

    def update(self):
		if (self.collision_bot(list_plat) == False):
			if self.isJump == True:
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
				self.isJump = False
				self.timeJump = 0


    def is_under(self, platform):
        return (pygame.Rect(self.rect.x, self.rect.y - 5, self.rect.width, self.rect.height).colliderect(platform.rect))

    def is_on(self, platform):
        return (pygame.Rect(self.rect.x, self.rect.y + 7, self.rect.width, self.rect.height).colliderect(platform.rect))

    def is_left(self, platform):
        return (pygame.Rect(self.rect.x + 6, self.rect.y, self.rect.width, self.rect.height).colliderect(platform.rect))

    def is_right(self, platform):
        return (pygame.Rect(self.rect.x - 4, self.rect.y, self.rect.width, self.rect.height).colliderect(platform.rect))

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

class Adversaire(pygame.sprite.Sprite):
    """Class for the player's ship"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/joueur1_droite.png')
        self.rect.bottomleft = [x, y]
        self.isLeft = False


    def update(self):
		pass


class Plateforme(pygame.sprite.Sprite):
    """Classe des Plateformes"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/plateforme.png')
        self.rect.bottomleft = [x, y]


class Tir(pygame.sprite.Sprite):
    """Class for the player's shots"""

    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/grenade.png')
        self.rect.center = position
        self.isLeft = False

    def update(self):
    	if self.isLeft:
        	self.rect = self.rect.move([-8, 0])
        else:
        	self.rect = self.rect.move([8, 0])
        if self.rect.top < 0:
            self.kill()


class Ennemi(pygame.sprite.Sprite):
    """Class for the baddies"""

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/enemy_gauche.png')
        self.rect.bottomright = [x, y]
        self.speed = [-3, 0]
        self.gravity = [0, 6]
        self.isLeft = False

    def update(self):
        self.rect = self.rect.move(self.speed)
        if self.collision_bot(list_plat) == False:
        	self.rect = self.rect.move(self.gravity)
        if self.rect.right < 0:
                self.kill()
        	
    def is_on(self, platform):
        return (pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height).colliderect(platform.rect))

    def collision_bot(self, list_plat):
        for plat in list_plat:
            if self.is_on(plat):
            	self.rect.bottom = plat.rect.top;
                return True
        return False

class Ennemi2(pygame.sprite.Sprite):
    """Class for the baddies"""

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/enemy_droite.png')
        self.rect.bottomleft = [x, y]
        self.speed = [3, 0]
        self.gravity = [0, 6]
        self.isLeft = False

    def update(self):
        self.rect = self.rect.move(self.speed)
        if self.collision_bot(list_plat) == False:
        	self.rect = self.rect.move(self.gravity)
        if self.rect.left > SCREEN_WIDTH:
                self.kill()
        	
    def is_on(self, platform):
        return (pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height).colliderect(platform.rect))

    def collision_bot(self, list_plat):
        for plat in list_plat:
            if self.is_on(plat):
            	self.rect.bottom = plat.rect.top;
                return True
        return False

# MAIN
def main_function():
    """Main function of the game"""

    my_server = MyServer(localaddr=(sys.argv[1], int(sys.argv[2])))
    my_server.launch_game()


if __name__ == '__main__':
	main_function()
	sys.exit(0)
