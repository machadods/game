import pygame # Importa a bilbioteca Pygame para usar as ferramentas de jogo
import random # Importa a biblioteca Pygame para usar as ferramentas de jogo e random para gerar números aleatórios
import os # Importa a biblioteca OS para lidar com arquivos e diretórios
from settings import WIDTH, HEIGHT, ENEMY_SIZE
from src.bullet import Bullet

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

class Enemy(pygame.sprite.Sprite): # Cria a classe Enemy que herda de Sprite (ganha poder de objetos de jogo)
    def __init__(self, x, y, bullets_group): # função que nasce o inimigo, recebendo sua posição.
        super().__init__()
        self.speed = 200
        self.name = "Enemy"
        self.score = 0
        self.sprites = {}
        self.lives = 3
        self.shoot_cooldown = 0
        self.shoot_delay = 1.0  # 1 segundo entre tiros
        self.shoot_range = 1200  # distância pra começar a atirar
        self.bullets_group = bullets_group


        for img in ['assets/enemy/up.png', 'assets/enemy/down.png', 'assets/enemy/left.png', 'assets/enemy/right.png']: # Lista de imagens para o inimigo (direções)
            path = os.path.join(BASE_DIR, img) # agora 
            try:
                loaded = pygame.image.load(path).convert_alpha()
                self.sprites[img] = pygame.transform.scale(loaded, ENEMY_SIZE)
            except Exception as e:
                print(f"Erro ao carregar {img}: {e}")
                # Caso falte alguma imagem, cria um bloco cinza
                surf = pygame.Surface(ENEMY_SIZE)
                surf.fill((35,35,35))
                self.sprites[img] = surf

        self.base_image = self.sprites['assets/enemy/up.png']
        self.image = self.base_image

        # Gera as Diagoanis automaticamente (Gira as imagens base em 45°)
        up_base = self.sprites['assets/enemy/up.png'] 
        self.sprites['assets/enemy/up_left.png'] = pygame.transform.rotate(up_base, 45)
        self.sprites['assets/enemy/up_right.png'] = pygame.transform.rotate(up_base, -45)
        
        # Gira a imagem down para cima as diagonais inferiores
        down_base = self.sprites['assets/enemy/down.png'] 
        self.sprites['assets/enemy/down_left.png']= pygame.transform.rotate(down_base, -45)
        self.sprites['assets/enemy/down_right.png']= pygame.transform.rotate(down_base, 45)

        # abaixo definimos com self.image =
        self.image = self.sprites['assets/enemy/up.png']
        self.rect = self.image.get_rect()
        self.radius = self.rect.width // 4 

        #Posição Real no Universso(Mundo infinito) 
        self.world_pos = pygame.math.Vector2(x, y)
        self.rect.center = (x, y)

    # a função a seguir é dividida em 4 partes: MOVIMENTO, ROTACIONAR, DISTÂNCIA para o player (para atirar) e COOLDOWN para atirar, e TIRO (criação da bala), cada parte tem um comentário explicando o que faz, para fazer o inimigo explodir o player com tiros deve mudar em player.py 

    def update(self, player, delta, enemies):
        direction = player.world_pos - self.world_pos

        if direction.length() > 0:
            direction = direction.normalize()

        # 🔴 FORÇA DE SEPARAÇÃO
        separation = pygame.math.Vector2(0, 0)
        for other in enemies:
            if other != self:
                dist = self.world_pos.distance_to(other.world_pos)
                if dist < 80:  # distância mínima entre inimigos
                    if dist > 0:
                        push = self.world_pos - other.world_pos
                        separation += push.normalize() * (80 - dist) / 80

        # mistura movimento + separação
        final_direction = direction + separation * 2  # peso da separação

        if final_direction.length() > 0:
            final_direction = final_direction.normalize()

        # movimento final
        self.world_pos += final_direction * self.speed * delta
        self.rect.center = (self.world_pos.x, self.world_pos.y)

        # ROTACIONAR
        if direction.length() > 0:
            angle = final_direction.angle_to(pygame.math.Vector2(0, -1))
            self.image = pygame.transform.rotate(self.base_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)

        # DISTÂNCIA para o player (para atirar)
        distance = (player.world_pos - self.world_pos).length()

        # COOLDOWN
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= delta

        # TIRO
        if distance <= self.shoot_range and self.shoot_cooldown <= 0:
            direction = player.world_pos - self.world_pos

            if direction.length() > 0:
                direction = direction.normalize()

                spawn_pos = self.world_pos + direction * 30  # evita nascer dentro
                b = Bullet(spawn_pos, direction, (255, 0, 0))
                b.owner = "enemy"
                self.bullets_group.add(b)

            self.shoot_cooldown = self.shoot_delay
            print("Enemy ATIROU")