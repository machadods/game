import pygame

BULLET_LIFETIME = 30.0   # segundos — funciona em qualquer região do mapa

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((10, 6))
        self.image.fill(color)
        self.radius = 5
        self.world_pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(center=(self.world_pos.x, self.world_pos.y))
        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.math.Vector2(0, -1)
        self.speed    = 400
        self.lifetime = BULLET_LIFETIME

    def update(self, delta):
        self.world_pos += self.direction * self.speed * delta
        self.rect.center = (self.world_pos.x, self.world_pos.y)
        self.lifetime -= delta
        if self.lifetime <= 0:
            self.kill()

