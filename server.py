#!/usr/bin/env python
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time
import sys
import pygame
import os
from pygame.locals import *


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

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
        self.joueur = Joueur()
        self.tirs_group = pygame.sprite.RenderClear()

    def Close(self):
        self._server.del_client(self)

    def Network_key(self, data):
        touche = data['key']
        if (touche[K_LEFT]):
            self.joueur.left()
        if (touche[K_RIGHT]):
            self.joueur.right()
        if (touche[K_UP]):
            self.joueur.up()

    def send_joueur(self):
        self.Send({'action': 'joueur', 'center': self.joueur.rect.center})

    def send_tirs(self):
        centers = []
        sprites = self.tirs_group.sprites()
        for sprite in sprites:
            centers.append(sprite.rect.center)
        self.Send({'action': 'tirs', 'length': len(sprites), 'centers': centers})

    def update_joueur(self):
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
        print('Server launched')

    def Connected(self, channel, addr):
        self.clients.append(channel)
        channel.number = len(self.clients)
        print('New connection: %d client(s) connected' % len(self.clients))
        if len(self.clients) == 1:
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

    def send_tirs(self):
        for client in self.clients:
            client.send_tirs()

    def send_ennemi(self, ennemi_sprites):
        centers = []
        for sprite in ennemi_sprites.sprites():
            centers.append(sprite.rect.center)
        for channel in self.clients:
            channel.Send({'action': 'ennemi', 'length': len(centers), 'centers': centers})

            # UPDATE FUNCTIONS

    def update_joueurs(self):
        for client in self.clients:
            client.update_joueur()

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
        ennemi_sprites = pygame.sprite.RenderClear()

        shooting = 0
        rythm = 60
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
                    pygame.sprite.groupcollide(ennemi_sprites, channel.tirs_group, True, True,
                                               pygame.sprite.collide_circle_ratio(0.7))
                self.update_joueurs()
                self.send_joueurs()
                self.update_tirs()
                self.send_tirs()
                counter += 1
                if counter == rythm:
                    ennemi_sprites.add(Ennemi())
                    counter = 0
                    rythm -= 1 if rythm > 10 else 0
                ennemi_sprites.update()
                self.send_ennemi(ennemi_sprites)

                # drawings
                # screen.blit(background_image, background_rect)
                # self.draw_ships(screen)
                # self.draw_shots(screen)
                # foes_sprites.draw(screen)
            pygame.display.flip()


# CLASSES
class Joueur(pygame.sprite.Sprite):
    """Class for the player's ship"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/joueur1_droite.png')
        self.rect.bottomleft = [0, 738]
        self.speed = [0, 0]

    def up(self):
        if self.rect.top > 0:
            self.rect = self.rect.move([0, -4])

    def left(self):
        if self.rect.left > 0:
            self.rect = self.rect.move([-4, 0])

    def right(self):
        if self.rect.right < SCREEN_WIDTH:
            self.rect = self.rect.move([4, 0])

    def update(self):
        self.rect = self.rect.move(self.speed)


class Tir(pygame.sprite.Sprite):
    """Class for the player's shots"""

    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/grenade.png')
        self.rect.center = position

    def update(self):
        self.rect = self.rect.move([0, -10])
        if self.rect.top < 0:
            self.kill()

class Ennemi(pygame.sprite.Sprite):
    """Class for the baddies"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/momie.png')
        self.rect.center = [0, 0]

    def update(self):
        self.rect = self.rect.move([0, 2])
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# MAIN
def main_function():
    """Main function of the game"""

    my_server = MyServer(localaddr=(sys.argv[1], int(sys.argv[2])))
    my_server.launch_game()


if __name__ == '__main__':
    main_function()
    sys.exit(0)
