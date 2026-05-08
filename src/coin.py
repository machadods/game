import pygame
import math

OURO       = (255, 215,  0)
OURO_DARK  = (184, 134, 11)
SIZE       = 18   # moeda menor para não poluir visualmente

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, planet=None, angle=0.0, radius=0.0):
        super().__init__()
        self.image     = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        c              = SIZE // 2
        pygame.draw.circle(self.image, OURO_DARK, (c, c), c)
        pygame.draw.circle(self.image, OURO,      (c, c), c - 2)
        self.rect      = self.image.get_rect()
        self.world_pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(x), int(y))

        # Referência orbital — se tiver planeta pai, a moeda orbita junto
        self.planet = planet
        self.angle  = angle   # ângulo relativo ao planeta (radianos)
        self.radius = radius  # distância da superfície + offset

    def update(self):
        if self.planet is not None:
            # Segue o planeta mantendo ângulo e raio fixos
            self.world_pos.x = self.planet.x + math.cos(self.angle) * self.radius
            self.world_pos.y = self.planet.y + math.sin(self.angle) * self.radius
        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
