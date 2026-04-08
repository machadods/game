import pygame
from settings import WIDTH, HEIGHT

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Retorna o rect da entidade deslocado pelo offset da câmera
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Centraliza a câmera no alvo (o jogador)
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        #suavização (Opcional: mude o 0.1 para valores menores para ser mais lento/suave)
        self.camera.x += (x - self.camera.x) *0.1
        self.camera.y += (y - self.camera.y) * 0.1

