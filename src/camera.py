import pygame

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def resize(self, width, height):
        self.width  = width
        self.height = height

    def update(self, target):
        x = -target.rect.centerx + self.width  // 2
        y = -target.rect.centery + self.height // 2
        self.camera.x += (x - self.camera.x) * 0.1
        self.camera.y += (y - self.camera.y) * 0.1

