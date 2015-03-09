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


# MAIN
def main_function():
    """Main function of the game"""

    my_server = MyServer(localaddr = (sys.argv[1],int(sys.argv[2])))
    my_server.launch_game()


if __name__ == '__main__':
    main_function()
    sys.exit(0)
