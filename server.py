#!/usr/bin/env python
# coding: utf-8

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time
import sys
import pygame
import os
from pygame.locals import *

sys.path.append('./classes')
from joueur import Joueur

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


# MAIN
def main_function():
    """Main function of the game"""

    my_server = MyServer(localaddr=(sys.argv[1], int(sys.argv[2])))
    my_server.launch_game()


if __name__ == '__main__':
    main_function()
    sys.exit(0)
