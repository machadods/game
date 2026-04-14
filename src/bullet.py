import pygame

class Bullet(pygame.sprite.Sprite): # Cria a classe Bullet que herda de Sprite (ganha poder de objetos de jogo)
    def __init__(self, pos, direction): # função que nasce a bala, recebendo sua posição e direção.
        super().__init__() # Ativa as funções internas da classe Sprite do pygame
        self.image = pygame.Surface((10, 10)) # Cria uma superfície de 10x10 pixels para representar a bala
        self.image.fill((255, 255, 0)) # Cor amarela para a bala
        self.rect = self.image.get_rect(center=pos) # O rect é criado com o centro na posição passada como argumento

        self.direction = direction.normalize() # Normaliza a direção para que tenha tamanho 1 (apenas direção)
        self.speed = 600 # Velocidade da bala em pixels por segundo
    
    def update(self, delta): # 'delta' é o tempo em segundos desde a última atualização (usado para movimento suave independente do FPS)
        self.rect.centerx += self.direction.x * self.speed * delta # Aplica o movimento baseado na direção, velocidade e tempo delta
        self.rect.centery += self.direction.y * self.speed * delta # Aplica o movimento baseado na direção, velocidade e tempo delta


