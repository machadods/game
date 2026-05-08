# C:\Users\wagner62215896\Documents\src\player.py

import pygame
import os
from settings import WIDTH, HEIGHT, PLAYER_SIZE, SHIP_WORLD_UNITS


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



        # Carrega sprites base em PLAYER_SIZE (150x150)
        raw = {}
        for img in ['up.png', 'down.png', 'left.png', 'right.png']:
            path = os.path.join(BASE_DIR, 'assets', img)
            try:
                loaded = pygame.image.load(path).convert_alpha()
                raw[img] = pygame.transform.scale(loaded, PLAYER_SIZE)
            except Exception as e:
                print(f"Erro ao carregar {img}: {e}")
                surf = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
                surf.fill((35, 35, 35, 255))
                raw[img] = surf

        # Diagonais: rotate do sprite original 150x150 → bounding box ~213x213
        diag_sprites = {
            'up_left.png':    pygame.transform.rotate(raw['up.png'],    45),
            'up_right.png':   pygame.transform.rotate(raw['up.png'],   -45),
            'down_left.png':  pygame.transform.rotate(raw['down.png'], -45),
            'down_right.png': pygame.transform.rotate(raw['down.png'],  45),
        }

        # Tamanho real do bounding box após rotação (pygame define exatamente)
        pad = diag_sprites['up_left.png'].get_width()

        # Sprites cardinais: centraliza no mesmo tamanho do diagonal para consistência visual
        off = (pad - PLAYER_SIZE[0]) // 2
        for img in ['up.png', 'down.png', 'left.png', 'right.png']:
            padded = pygame.Surface((pad, pad), pygame.SRCALPHA)
            padded.blit(raw[img], (off, off))
            self.sprites[img] = padded

        self.sprites.update(diag_sprites)

        
        self.image = self.sprites['up.png']
        self.rect  = self.image.get_rect()
        self.radius       = SHIP_WORLD_UNITS     # colisão em world units
        self.world_units  = SHIP_WORLD_UNITS

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