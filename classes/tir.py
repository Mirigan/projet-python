class Tir(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/tir.png')

    def update(self,center):
        self.rect.center = center