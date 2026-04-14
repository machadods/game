#C:\Users\wagner62215896\Documents\main.py


import pygame
import random
from settings import WIDTH, HEIGHT, FPS
from src.player import Player
from src.coin import Coin
from src.camera import Camera
from src.enemy import Enemy
from src.bullet import Bullet


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TESTE")
clock = pygame.time.Clock()
running = True

# 1. INSTANCIA A CÂMERA
camera = Camera(WIDTH, HEIGHT)

#Grupo de jogadores
players = pygame.sprite.Group()

#Grupo de coins
coins =pygame.sprite.Group()

#Grupo de inimigos
enemies = pygame.sprite.Group()

#Grupo de balas
bullets = pygame.sprite.Group()

# Cria o jogador e adiciona ao grupo de jogadores
player = Player("player_1")
players.add(player)

# Gerar minerios em posições aleatórias
for a in range(50):
    x_aleatorio = random.randint(-5000, 5000)
    y_aleatorio = random.randint(-5000, 5000)
    coin = Coin(x_aleatorio, y_aleatorio)
    coins.add(coin)

# Gerar inimigos em posições aleatórias
for a in range(10): # Gera 10 inimigos em posições aleatórias
    x_aleatorio = random.randint(-5000, 5000) # Gera uma posição aleatória para o inimigo (pode ser fora da tela)
    y_aleatorio = random.randint(-5000, 5000) # Gera uma posição aleatória para o inimigo (pode ser fora da tela)
    enemy = Enemy(x_aleatorio, y_aleatorio) # Cria o inimigo com a posição aleatória
    enemies.add(enemy) # Adiciona o inimigo ao grupo de inimigos

# LOOP PRINCIPAL
while running:
    delta = clock.tick(FPS)/1000

    # 2. TRATAMENTO DE EVENTOS
    for evento in pygame.event.get():

        # Verifica se o jogador fechou a janela ou pressionou ESC para sair
        if evento.type == pygame.QUIT:
            running = False
        # Verifica se o jogador pressionou a tecla ESC para sair
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                running = False

        # Verifica se o jogador clicou com o mouse para atirar
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Converte a posição do mouse para o "mundo" considerando a posição da câmera
            world_mouse = pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(camera.camera.topleft)

            # Calcula a direção do tiro (do player para o mouse)
            direction = world_mouse -player.world_pos

            # Cria a bala e adiciona ao grupo de balas
            bullet = Bullet(player.world_pos, direction)
            bullets.add(bullet)
        

    # ATUALIZAÇÃO DE LÓGICA
    players.update(delta)
    coins.update()
    enemies.update(player, delta)
    bullets.update(delta)

    if player.invincible_timer > 0: # Se o timer de invencibilidade for maior que 0, reduz ele com o tempo
        player.invincible_timer -= delta # Reduz o timer de invencibilidade com o tempo

    # TIRO ACERTA INIMIGO
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)

    # inimigo encosta no player
    if player.invincible_timer <= 0: # Verifica se o jogador não está invencível
        if pygame.sprite.spritecollide(player, enemies, False):
            player.lives -= 1 # Reduz uma vida do jogador
            player.invincible_timer = 1.0 # 1 segundo de invencibilidade
            print("Tomou dano!") # Mensagem de debug para indicar que o jogador tomou dano

    if player.lives <= 0:
        print("Game Over!")

        player.lives = 3
        player.world_pos = pygame.math.Vector2(0,0)

    
    # 3. ATUALIZA A POSIÇÃO DA CÂMERA BASEADA NO PLAYER
    camera.update(player)

    colisao = pygame.sprite.spritecollide(player,coins,True)
    if colisao:
        print('Capturou a minério!')
        
    # DESENHO (A ordem importa!)
    screen.fill((45, 156, 200)) # Fundo

    for coin in coins:
        screen.blit(coin.image, camera.apply(coin))

    for enemy in enemies:
        screen.blit(enemy.image, camera.apply(enemy))

    for bullet in bullets:
        screen.blit(bullet.image, camera.apply(bullet))
    
    # Desenha o player
    screen.blit(player.image, camera.apply(player))
    
    # --- DESENHO DO RADAR (No final do bloco de desenho no main.py) ---
    radar_pos = (150, 150) # Posição do centro do radar na tela
    radar_raio = 100       # Tamanho do círculo do radar
    escala_radar = 0.05    # O quanto o radar "enxerga" longe (5% da distância real)

    # Desenha o fundo do radar (Círculo preto transparente)
    radar_surface = pygame.Surface((radar_raio*2, radar_raio*2), pygame.SRCALPHA)
    pygame.draw.circle(radar_surface, (0, 0, 0, 150), (radar_raio, radar_raio), radar_raio)
    screen.blit(radar_surface, (radar_pos[0] - radar_raio, radar_pos[1] - radar_raio))
    pygame.draw.circle(screen, (255, 255, 255), radar_pos, radar_raio, 2) # Borda

    for coin in coins:
        # Calcula a distância do minério em relação ao player
        rel_x = (coin.rect.centerx - player.rect.centerx) * escala_radar
        rel_y = (coin.rect.centery - player.rect.centery) * escala_radar

        # Verifica se o ponto está dentro do círculo do radar (Pitágoras)
        distancia = (rel_x**2 + rel_y**2)**0.5
        if distancia < radar_raio:
            ponto_x = int(radar_pos[0] + rel_x)
            ponto_y = int(radar_pos[1] + rel_y)
            # Desenha o minério como um pontinho amarelo no radar
            pygame.draw.circle(screen, (255, 215, 0), (ponto_x, ponto_y), 2)

    # Desenha um pontinho branco no centro do radar (Representa VOCÊ)
    pygame.draw.circle(screen, (255, 255, 255), radar_pos, 3)

    pygame.display.flip()

pygame.quit()