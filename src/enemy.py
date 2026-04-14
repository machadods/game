import pygame # Importa a bilbioteca Pygame para usar as ferramentas de jogo
import random # Importa a biblioteca Pygame para usar as ferramentas de jogo e random para gerar números aleatórios

class Enemy(pygame.sprite.Sprite): # Cria a classe Enemy que herda de Sprite (ganha poder de objetos de jogo)
    def __init__(self, x, y): # função que nasce o inimigo, recebendo sua posição.
        super().__init__() # Ativa as funções internas da classe Sprite do pygame
        self.image = pygame.Surface((40, 40)) # Cria uma superfície de 40x40 pixels para representar o inimigo
        self.image.fill((200, 50, 50)) # Cor vermelha para o inimigo
        self.rect = self.image.get_rect(center=(x,y)) # O rect é criado com o centro na posição (x,y) passada como argumento

        self.world_pos = pygame.math.Vector2(x, y) # 'Posição Real no Universo' (mundo infinito)
        self.speed = random.randint(80, 140) # Velocidade aleatória entre 80 e 140 pixels por segundo

    def  update(self, player, delta): # 'delta' é o tempo em segundos desde a última atualização (usado para movimento suave independente do FPS)
        direction = player.world_pos - self.world_pos # Vetor direção do inimigo para o jogador

        if direction.length() > 0: # Evita divisão por zero
            direction = direction.normalize() # Normaliza o vetor para que tenha tamanho 1 (apenas direção) 
        
        self.world_pos += direction * self.speed * delta # Aplica o movimento baseado na direção, velocidade e tempo delta
        self.rect.center = (self.world_pos.x, self.world_pos.y) # Atualiza a posição do rect para a nova posição do mundo