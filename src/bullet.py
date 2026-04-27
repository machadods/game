import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.Surface((10, 6))
        self.image.fill(color)
        self.radius = 5
        self.world_pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(center=(self.world_pos.x, self.world_pos.y))
        self.direction = direction.normalize()
        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.math.Vector2(0, -1)
        self.speed = 400

    def update(self, delta): # 'delta' é o tempo em segundos desde a última atualização (usado para movimento suave independente do FPS)
        self.world_pos += self.direction * self.speed * delta
        self.rect.center = (self.world_pos.x, self.world_pos.y)
        
        if abs(self.world_pos.x) > 200000 or abs(self.world_pos.y) > 200000:
            self.kill()

