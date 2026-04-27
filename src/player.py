# C:\Users\wagner62215896\Documents\src\player.py

import pygame
import os
from settings import WIDTH, HEIGHT, PLAYER_SIZE


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# a Class Player é onde o jogador é criado, a função __init__ é onde o jogador nasce, recebendo seu nome, e a função update é onde o jogador se move, a função é dividida em 3 partes: MOVIMENTO, SELEÇÃO DE IMAGEM e NORMALIZAÇÃO (matemática e velocidade), cada parte tem um comentário explicando o que faz. O MOVIMENTO é onde o jogador se move baseado nas teclas pressionadas, a SELEÇÃO DE IMAGEM é onde a imagem do jogador muda baseada na direção que ele está se movendo, e a NORMALIZAÇÃO é onde o vetor de direção é normalizado para garantir que a velocidade do jogador seja constante em todas as direções. A função draw é onde o jogador é desenhado na tela, a função recebe a superfície onde o jogador deve ser desenhado e usa o método blit para desenhar a imagem do jogador na posição correta. O método blit é usado para desenhar uma imagem em outra superfície, neste caso, a imagem do jogador é desenhada na superfície do jogo.

class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.score = 0
        self.sprites = {}
        self.lives = 3
        self.invincible_timer = 0



        for img in ['up.png', 'down.png', 'left.png', 'right.png']:
            path = os.path.join(BASE_DIR, 'assets', img)
            try:
                loaded = pygame.image.load(path).convert_alpha()
                self.sprites[img] = pygame.transform.scale(loaded, PLAYER_SIZE)
            except Exception as e:
                print(f"Erro ao carregar {img}: {e}")
                # Caso falte alguma imagem, cria um bloco cinza
                surf = pygame.Surface(PLAYER_SIZE)
                surf.fill((35,35,35))
                self.sprites[img] = surf

        # Gera as Diagoanis automaticamente (Gira as imagens base em 45°)
        up_base = self.sprites['up.png'] 
        self.sprites['up_left.png'] = pygame.transform.rotate(up_base, 45)
        self.sprites['up_right.png'] = pygame.transform.rotate(up_base, -45)
        
        # Gira a imagem down para cima as diagonais inferiores
        down_base = self.sprites['down.png'] 
        self.sprites['down_left.png']= pygame.transform.rotate(down_base, -45)
        self.sprites['down_right.png']= pygame.transform.rotate(down_base, 45)

        
        self.image = self.sprites['up.png']
        self.rect = self.image.get_rect()
        self.radius = self.rect.width // 10

        #Posição Real no Universso(Mundo infinito)
        self.world_pos = pygame.math.Vector2(WIDTH/2, HEIGHT/2)
        self.rect.center = (WIDTH/2, HEIGHT/2)


    
# a def update é onde o jogador se move, a função é dividida em 3 partes: MOVIMENTO, SELEÇÃO DE IMAGEM e NORMALIZAÇÃO (matemática e velocidade), cada parte tem um comentário explicando o que faz. O MOVIMENTO é onde o jogador se move baseado nas teclas pressionadas, a SELEÇÃO DE IMAGEM é onde a imagem do jogador muda baseada na direção que ele está se movendo, e a NORMALIZAÇÃO é onde o vetor de direção é normalizado para garantir que a velocidade do jogador seja constante em todas as direções.
# o sistema de colisão deve ficar apos assim


    def update(self,delta):
        
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0,0) # cria um vetor

        # Define a direção baseada na teclas
        if keys[pygame.K_UP] or keys[pygame.K_w]:direction.y = -1  # Cima é NEGATIVO               
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:direction.y = 1 # Baixo é POSITIVO

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:direction.x = -1  # Esquerda é X negativo
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:direction.x = 1  # Direita é X positivo

        # Seleção da imagem
        sprite_key = ''
        if direction.y == -1: sprite_key = "up"
        elif direction.y == 1: sprite_key = "down"

        if direction.x == -1:
            sprite_key += "_left" if sprite_key else "left"
        elif direction.x == 1:
            sprite_key += "_right" if sprite_key else "right"
        
        if sprite_key:
            nome_img = f"{sprite_key}.png"
            if nome_img in self.sprites:  
                self.image = self.sprites[nome_img]


        # Normalização (matemática e velocidade)
        if direction.length() > 0:
            direction = direction.normalize() # Faz o tamanho do vetor ser sempre 1


        # Faz sentido no codigo

        # Aplicando movimento
        velocidade_final = 300 * delta
        self.world_pos += direction * velocidade_final
        
        # Matém o jogador na tela
        self.rect.center = (self.world_pos.x, self.world_pos.y)

# a def draw é onde o jogador é desenhado na tela, a função recebe a superfície onde o jogador deve ser desenhado e usa o método blit para desenhar a imagem do jogador na posição correta. O método blit é usado para desenhar uma imagem em outra superfície, neste caso, a imagem do jogador é desenhada na superfície do jogo.    
    def draw(self, surface):
        surface.blit(self.image, self.rect)